"""Grounded Q&A over resume.json.

The assistant can only repeat facts that exist in the approved resume file.
No model is called, so it cannot invent anything. If nothing matches, it says so.
"""
import json
import math
import re
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "resume.json"

STOPWORDS = set(
    "a an the is are was were be been do does did of in on at to for from with and or "
    "about tell me what which who whom how can could would should her she his he they "
    "their roma any some please you your it its this that these those has have had as "
    "by if so than then there here where when why much many long really also know".split()
)

# Maps words recruiters use to the words used in the resume.
SYNONYMS = {
    "job": "experience", "jobs": "experience", "work": "experience", "worked": "experience",
    "employer": "experience", "company": "experience", "career": "experience",
    "history": "experience", "background": "experience",
    "study": "education", "studied": "education", "degree": "education",
    "college": "education", "university": "education", "qualification": "education",
    "tech": "skills", "technology": "skills", "technologies": "skills",
    "stack": "skills", "tools": "skills", "know": "skills", "knows": "skills",
    "built": "projects", "build": "projects", "project": "projects",
    "portfolio": "projects", "made": "projects",
    "speak": "languages", "spoken": "languages", "language": "languages",
    "looking": "role", "seeking": "role", "want": "role", "target": "role",
    "available": "availability", "join": "availability", "notice": "availability",
    "api": "rest", "apis": "rest",
}


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tokens(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9+#.]+", text.lower()):
        w = w.strip(".")
        if not w or w in STOPWORDS:
            continue
        w = SYNONYMS.get(w, w)
        out.append(_stem(w))
    return out


def specific_terms(text: str) -> list[tuple[str, str]]:
    """Content words that are NOT generic question words: (stem, original word)."""
    out = []
    for w in re.findall(r"[a-z0-9+#.]+", text.lower()):
        w = w.strip(".")
        if not w or w in STOPWORDS or w in SYNONYMS:
            continue
        out.append((_stem(w), w))
    return out


def is_todo(value) -> bool:
    return isinstance(value, str) and value.strip().upper().startswith("TODO")


def load_resume(path: Path = DATA_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_facts(resume: dict) -> list[dict]:
    """Flatten the resume into small citable facts. TODO items are skipped."""
    facts = []

    def add(fid, section, text, label):
        if text and not is_todo(text):
            facts.append({"id": fid, "section": section, "text": text, "label": label})

    p = resume["profile"]
    add("profile", "Summary", f"{p['name']}: {p['headline']}. {p['summary']}", "Summary")
    add("target", "Role", f"Roma is looking for {p['target_role']} roles.", "Target role")
    for i, r in enumerate(resume.get("remember", [])):
        add(f"remember-{i}", "Summary", r, "Key points")

    for e in resume.get("experience", []):
        head = f"{e['title']} at {e['company']}"
        add(e["id"], "Experience", head + (f" ({e['period']})" if not is_todo(e["period"]) else ""), head)
        for i, pt in enumerate(e["points"]):
            if not is_todo(pt):
                add(f"{e['id']}-{i}", "Experience", f"{head}: {pt}", head)

    for pr in resume.get("projects", []):
        stack = ", ".join(pr["stack"])
        add(pr["id"], "Projects", f"{pr['name']} ({stack}): {pr['summary']}", pr["name"])
        for i, pt in enumerate(pr["points"]):
            if not is_todo(pt):
                add(f"{pr['id']}-{i}", "Projects", f"{pr['name']}: {pt}", pr["name"])

    for group, items in resume.get("skills", {}).items():
        add(f"skills-{group}", "Skills", f"{group} skills: {', '.join(items)}.", f"Skills: {group}")

    for ed in resume.get("education", []):
        yr = f" ({ed['year']})" if not is_todo(ed["year"]) else ""
        add(ed["id"], "Education", f"{ed['degree']}, {ed['school']}{yr}", "Education")

    langs = resume.get("languages", [])
    if langs:
        add("languages", "Languages", f"Roma speaks {', '.join(langs)}.", "Languages")

    for i, qa in enumerate(resume.get("faq", [])):
        add(f"faq-{i}", "FAQ", qa["a"], "Approved answer")
        facts[-1]["extra"] = qa["q"]

    return facts


class Index:
    def __init__(self, facts: list[dict]):
        self.facts = facts
        self.doc_tokens = []
        df: dict[str, int] = {}
        for f in facts:
            toks = tokens(f["text"] + " " + f["section"] + " " + f.get("extra", ""))
            self.doc_tokens.append(toks)
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        n = max(len(facts), 1)
        self.idf = {t: math.log(1 + n / c) for t, c in df.items()}
        self.vocab = set(self.idf)

    def search(self, query: str, k: int = 3):
        q = set(tokens(query))
        scored = []
        for f, toks in zip(self.facts, self.doc_tokens):
            tset = set(toks)
            score = sum(self.idf[t] for t in q if t in tset)
            if score > 0:
                scored.append((score, f))
        scored.sort(key=lambda x: -x[0])
        return scored[:k]


MIN_SCORE = 0.9
GREETINGS = {"hi", "hello", "hey", "hii", "namaste"}


def answer(question: str, index: Index, contact_hint: str = "") -> dict:
    question = (question or "").strip()[:300]
    if not question:
        return {"answer": "Ask me anything about Roma's experience, projects, skills or education.",
                "sources": [], "grounded": False}

    if question.lower().strip("!. ") in GREETINGS:
        return {"answer": "Hi! I can answer questions about Roma's work, projects, skills and education, "
                          "using only what is on her approved resume.",
                "sources": [], "grounded": False}

    specific = specific_terms(question)
    unknown = [raw for stem, raw in specific if stem not in index.vocab]
    hits = index.search(question)
    nothing_specific_matched = bool(specific) and len(unknown) == len(specific)
    if not hits or hits[0][0] < MIN_SCORE or nothing_specific_matched:
        msg = "I don’t have verified information about that on Roma’s resumepython -m unittest -v"
        if contact_hint:
            msg += f" You can ask her directly: {contact_hint}"
        return {"answer": msg, "sources": [], "grounded": False}

    top = hits[0][0]
    chosen = [f for s, f in hits if s >= top * 0.5]
    seen, lines, sources = set(), [], []
    for f in chosen:
        if f["text"] in seen:
            continue
        seen.add(f["text"])
        lines.append(f["text"])
        sources.append({"id": f["id"], "section": f["section"], "label": f["label"]})
    text = " ".join(lines)
    if unknown:
        text += f" Her resume does not mention: {', '.join(unknown)}."
    return {"answer": text, "sources": sources, "grounded": True}

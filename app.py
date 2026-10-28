from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from grounded import Index, answer, build_facts, is_todo, load_resume

BASE = Path(__file__).parent
app = Flask(__name__)


def _clean(value):
    """Remove TODO placeholders so unverified text never reaches the page."""
    if isinstance(value, str):
        return None if is_todo(value) else value
    if isinstance(value, list):
        return [v for v in (_clean(x) for x in value) if v not in (None, [], {})]
    if isinstance(value, dict):
        return {k: v for k, v in ((k, _clean(x)) for k, x in value.items()) if v not in (None, [], {})}
    return value


def _state():
    resume = load_resume()
    return resume, Index(build_facts(resume))


@app.get("/")
def home():
    resume, _ = _state()
    page = _clean(resume)
    pdf_name = resume["profile"].get("resume_pdf", "")
    has_pdf = bool(pdf_name) and (BASE / "static" / pdf_name).exists()
    return render_template("index.html", r=page, has_pdf=has_pdf, pdf_name=pdf_name)


@app.post("/api/chat")
def chat():
    resume, index = _state()
    payload = request.get_json(silent=True) or {}
    contact = resume["profile"].get("email", "")
    contact = "" if is_todo(contact) else contact
    return jsonify(answer(payload.get("question", ""), index, contact))


@app.get("/download/resume")
def download():
    resume, _ = _state()
    name = resume["profile"].get("resume_pdf", "")
    return send_from_directory(BASE / "static", name, as_attachment=True)


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(debug=True)

(function () {
  const toggle = document.getElementById("chat-toggle");
  const box = document.getElementById("chat");
  const log = document.getElementById("log");
  const form = document.getElementById("form");
  const input = document.getElementById("q");

  function add(text, who, sources) {
    const div = document.createElement("div");
    div.className = "msg " + who;
    div.textContent = text;
    if (sources && sources.length) {
      const s = document.createElement("small");
      s.textContent = "From resume: " + [...new Set(sources.map(x => x.label))].join(", ");
      div.appendChild(s);
    }
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  async function ask(question) {
    add(question, "user");
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      add(data.answer, "bot", data.sources);
    } catch (e) {
      add("Something went wrong. Please try again.", "bot");
    }
  }

  toggle.addEventListener("click", () => {
    const open = box.hidden;
    box.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (open && !log.children.length) add("Hi! Ask me about Roma's work, projects, skills or education.", "bot");
  });
  document.querySelectorAll("[data-open-chat]").forEach(b =>
    b.addEventListener("click", () => { if (box.hidden) toggle.click(); input.focus(); }));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (q) { input.value = ""; ask(q); }
  });
  document.querySelectorAll(".chips button").forEach(b =>
    b.addEventListener("click", () => ask(b.textContent)));
})();

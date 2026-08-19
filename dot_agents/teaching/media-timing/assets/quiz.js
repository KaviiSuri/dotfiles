/* Reusable retrieval-practice widget.
 *
 * Usage in a lesson:
 *   <div class="quiz" data-quiz='[{"q":"...","a":["...","..."],"correct":0,"why":"..."}]'></div>
 *   <script src="../assets/quiz.js"></script>
 *
 * Design notes (these are pedagogical, not cosmetic — don't "tidy" them away):
 *  - Answers are revealed only AFTER a choice. Recall must happen from memory;
 *    seeing the answer first turns retrieval practice into re-reading.
 *  - Every option is rendered in the same monospace width so answer LENGTH
 *    never hints at correctness.
 *  - Wrong answers stay on screen with an explanation rather than resetting.
 *    The correction is the learning event.
 */
(function () {
  const style = document.createElement("style");
  style.textContent = `
    .quiz { border: 1px solid var(--rule); border-radius: 4px; padding: 1.2rem 1.3rem; margin: 2rem 0; background: #fbf9f2; }
    .quiz h3 { margin: 0 0 0.9rem; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
               color: var(--ink-soft); font-family: ui-monospace, Menlo, monospace; font-weight: 500; }
    .quiz .q { margin: 0 0 0.9rem; font-size: 0.97rem; }
    .quiz .opts { display: flex; flex-direction: column; gap: 0.4rem; }
    .quiz button { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.83rem;
                   text-align: left; padding: 0.55rem 0.8rem; border: 1px solid var(--rule);
                   background: var(--paper); border-radius: 3px; cursor: pointer; color: var(--ink); }
    .quiz button:hover:not(:disabled) { border-color: var(--ink-soft); }
    .quiz button:disabled { cursor: default; opacity: 0.55; }
    .quiz button.right { border-color: var(--good); background: #eef6f1; opacity: 1; color: var(--good); }
    .quiz button.wrong { border-color: var(--bad); background: #fbefec; opacity: 1; color: var(--bad); }
    .quiz .why { margin: 0.9rem 0 0; font-size: 0.88rem; color: var(--ink-soft); display: none; }
    .quiz .why.show { display: block; }
    .quiz .progress { margin-top: 1rem; font-size: 0.76rem; color: var(--ink-soft);
                      font-family: ui-monospace, Menlo, monospace; }
  `;
  document.head.appendChild(style);

  document.querySelectorAll(".quiz").forEach((root) => {
    const items = JSON.parse(root.dataset.quiz);
    let index = 0;
    let correct = 0;

    function render() {
      if (index >= items.length) {
        root.innerHTML =
          `<h3>Retrieval practice</h3><p class="q">Done — ${correct} of ${items.length} on first try.</p>` +
          `<p class="why show">Anything you missed is worth asking your teacher about. Come back to this
           lesson in a few days; spacing is what turns this into storage strength.</p>`;
        return;
      }
      const item = items[index];
      root.innerHTML =
        `<h3>Retrieval practice &mdash; ${index + 1} of ${items.length}</h3>` +
        `<p class="q">${item.q}</p><div class="opts"></div>` +
        `<p class="why"></p><p class="progress"></p>`;
      const opts = root.querySelector(".opts");
      const why = root.querySelector(".why");

      item.a.forEach((text, i) => {
        const b = document.createElement("button");
        b.textContent = text;
        b.onclick = () => {
          root.querySelectorAll("button").forEach((x) => (x.disabled = true));
          const hit = i === item.correct;
          if (hit) correct++;
          b.className = hit ? "right" : "wrong";
          if (!hit) opts.children[item.correct].className = "right";
          why.textContent = item.why;
          why.classList.add("show");
          const next = document.createElement("button");
          next.textContent = index + 1 < items.length ? "Next question" : "Finish";
          next.disabled = false;
          next.style.marginTop = "0.9rem";
          next.onclick = () => { index++; render(); };
          root.appendChild(next);
        };
        opts.appendChild(b);
      });
    }
    render();
  });
})();

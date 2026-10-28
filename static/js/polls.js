"use strict";

// Enhance normal HTML forms; all essential actions also work without JavaScript.
const summary = document.querySelector("[data-error-summary]");
if (summary) summary.focus();

for (const field of document.querySelectorAll(".form-field")) {
  const input = field.querySelector("input[maxlength]:not([type=password]), textarea[maxlength]");
  const counter = field.querySelector("[data-character-count]");
  if (!input || !counter) continue;
  const update = () => { counter.textContent = `${input.value.length} / ${input.maxLength} karakter`; };
  counter.hidden = false;
  input.addEventListener("input", update);
  window.addEventListener("pageshow", update);
  update();
}

const pollForm = document.querySelector("[data-poll-form]");
if (pollForm) {
  const rows = [...pollForm.querySelectorAll("[data-option-row]")];
  const add = pollForm.querySelector("[data-add-option]");
  const status = pollForm.querySelector("[data-option-status]");
  const update = () => {
    const count = rows.filter(row => !row.hidden).length;
    add.disabled = count === 5;
    status.textContent = `${count} seçenek alanı açık. ${count === 5 ? "En fazla 5 seçenek ekleyebilirsin." : "En az 2, en fazla 5 seçenek ekleyebilirsin."}`;
  };
  rows.forEach((row, i) => {
    row.hidden = i >= 2 && !row.querySelector("input").value && !row.querySelector(".errorlist");
    const remove = row.querySelector(".remove-option");
    if (remove) {
      remove.hidden = false;
      remove.setAttribute("aria-label", `${row.querySelector("label").textContent.replace(/:$/, "")} alanını kaldır`);
      remove.addEventListener("click", () => {
        const input = row.querySelector("input");
        input.value = "";
        input.dispatchEvent(new Event("input"));
        row.hidden = true;
        update();
        add.focus();
      });
    }
  });
  add.hidden = false;
  add.addEventListener("click", () => {
    const row = rows.find(row => row.hidden);
    if (row) { row.hidden = false; row.querySelector("input").focus(); }
    update();
  });
  update();
}

const voteForm = document.querySelector("[data-vote-form]");
const updateVote = () => {
  if (voteForm && voteForm.dataset.submitting !== "true") {
    voteForm.querySelector("button[type=submit]").disabled = !voteForm.querySelector("input[name=choice]:checked");
  }
};
if (voteForm) { voteForm.addEventListener("change", updateVote); updateVote(); }

for (const form of document.querySelectorAll('form[method="post"]')) {
  const button = form.querySelector('button[type="submit"]');
  if (!button) continue;
  const originalLabel = button.textContent;
  const status = document.createElement("p");
  status.className = "form-note submission-status";
  status.setAttribute("role", "status");
  button.after(status);
  form.addEventListener("submit", event => {
    if (event.defaultPrevented) return;
    if (form.dataset.submitting === "true") { event.preventDefault(); return; }
    form.dataset.submitting = "true";
    button.disabled = true;
    button.textContent = button.dataset.pendingLabel || "İşleniyor…";
    status.textContent = "İşlemin tamamlanması bekleniyor. Lütfen bu sayfayı kapatma.";
  });
  // Restore controls when the browser brings back a page from its history cache.
  window.addEventListener("pageshow", () => {
    delete form.dataset.submitting;
    button.disabled = false;
    button.textContent = originalLabel;
    status.textContent = "";
    updateVote();
  });
}

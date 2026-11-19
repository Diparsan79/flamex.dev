const root = document.documentElement;
const button = document.querySelector(".toggle")

root.dataset.theme = localStorage.getItem("theme") == "light" ? "light": "dark";

button.addEventListener("click", () => {
    const next = root.dataset.theme === "light" ? "dark" : "light";
    root.dataset.theme = next;
    localStorage.setItem("theme", next);
    button.setAttribute("aria-label", `Switch to ${next === "light" ? "dark" : "light"} theme `);
});
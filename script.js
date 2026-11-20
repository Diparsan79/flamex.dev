const root = document.documentElement;
const button = document.querySelector(".toggle")

root.dataset.theme = localStorage.getItem("theme") == "light" ? "light": "dark";

button.addEventListener("click", () => {
    const next = root.dataset.theme === "light" ? "dark" : "light";
    root.dataset.theme = next;
    localStorage.setItem("theme", next);
    button.setAttribute("aria-label", `Switch to ${next === "light" ? "dark" : "light"} theme `);
});

/* live data for homepage */
const lastfmTag = document.getElementById("lastfm-tag");
const lbTag = document.getElementById("lb-tag");

function stars(rating) {
    const n = parseFloat(rating);
    if (!n) return "";
    return " " + "*".repeat(Math.floor(n)) + (n % 1 ? "½" : "");
}

if (lastfmTag || lbTag) {
    fetch("data.json", { cache: "no-cache" })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(d => {
            if (lastfmTag && d.lastfm) {
                const { track, artist, nowplaying } = d.lastfm;
                lastfmTag.textContent = `${nowplaying ? "▶ Now playing" : "Last played"}: ${track} — ${artist}`;
            }
            if (lbTag && d.letterboxd) {
                const { title, year, rating } = d.letterboxd;
                lbTag.textContent = `Last watched: ${title}${year ? ` (${year})` : ""}`;
            }
        })
        .catch(() => {});
}
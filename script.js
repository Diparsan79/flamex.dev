const root = document.documentElement;
const button = document.querySelector(".toggle")

root.dataset.theme = localStorage.getItem("theme") == "light" ? "light": "dark";

button.addEventListener("click", () => {
    const next = root.dataset.theme === "light" ? "dark" : "light";
    root.dataset.theme = next;
    localStorage.setItem("theme", next);
    button.setAttribute("aria-label", `Switch to ${next === "light" ? "dark" : "light"} theme `);
});


/* live data for home page */
const lastfmTag = document.getElementById("lastfm-tag");
const lbTag = document.getElementById("lb-tag");

const LASTFM_USER = "flamex67";
const LASTFM_KEY = "90280740345f4d5e43bc95a2560826ed";/* its a read only key so idrc */
const POLL_MS = 30000;

function stars(rating) {
    const n = parseFloat(rating);
    if (!n) return "";
    return " " + "★".repeat(Math.floor(n)) + (n % 1 ? "½" : "");
}

function showTrack({ track, artist, nowplaying }) {
    lastfmTag.textContent = `${nowplaying ? "▶ Now playing" : "Last played"}: ${track} — ${artist}`;
}

async function pollLastfm() {
    try {
        const url = "https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
            + `&user=${encodeURIComponent(LASTFM_USER)}&api_key=${LASTFM_KEY}&format=json&limit=1`;
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) return;
        let t = (await r.json()).recenttracks.track;
        if (Array.isArray(t)) t = t[0];
        if (!t) return;
        showTrack({
            track: t.name,
            artist: t.artist["#text"],
            nowplaying: !!(t["@attr"] && t["@attr"].nowplaying === "true"),
        });
    } catch (e) {}
}

if (lastfmTag || lbTag) {
    fetch("data.json", { cache: "no-cache" })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(d => {
            if (lastfmTag && d.lastfm) showTrack(d.lastfm);
            if (lbTag && d.letterboxd) {
                const { title, year, rating } = d.letterboxd;
                lbTag.textContent = `Last watched: ${title}${year ? ` (${year})` : ""}`;
            }
        })
        .catch(() => {});

    if (lastfmTag) {
        let timer = null;
        const start = () => { if (!timer) { pollLastfm(); timer = setInterval(pollLastfm, POLL_MS); } };
        const stop = () => { clearInterval(timer); timer = null; };
        document.addEventListener("visibilitychange", () => document.hidden ? stop() : start());
        if (!document.hidden) start();
    }
}
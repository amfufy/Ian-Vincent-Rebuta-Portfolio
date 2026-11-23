/* Ian Vincent Rebuta portfolio: shared behaviour for every page.
   All content is plain HTML; this script only adds interaction. */
(() => {
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const root = document.documentElement;
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
};
const reduced = () => root.classList.contains("rm") || matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- theme toggle ---------- */
const isDark = () => root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
function paintTheme() { $$(".theme-btn").forEach(b => { b.classList.toggle("dark", isDark()); b.setAttribute("aria-pressed", isDark()); }); }
$$(".theme-btn").forEach(b => b.addEventListener("click", () => {
  root.dataset.theme = isDark() ? "light" : "dark";
  try { localStorage.setItem("theme", root.dataset.theme); } catch {}
  paintTheme();
}));
paintTheme();

/* ---------- accessibility panel ---------- */
const a11y = $("#a11y"), prefs = store.get("a11y", {});
function applyA11y() {
  root.classList.remove("fs-1", "fs-2"); if (prefs.fs) root.classList.add("fs-" + prefs.fs);
  ["hc", "rm", "ul"].forEach(k => root.classList.toggle(k, !!prefs[k]));
  $$("#a11y [data-fs]").forEach(b => b.setAttribute("aria-pressed", String((prefs.fs || 0) == b.dataset.fs)));
  $$("#a11y [data-opt]").forEach(c => c.checked = !!prefs[c.dataset.opt]);
  store.set("a11y", prefs);
  $$("video[autoplay]").forEach(v => reduced() ? v.pause() : v.play().catch(() => {}));
}
function openPanel(panel, opener) { panel.hidden = false; panel.classList.add("open"); panel._opener = opener; (panel.querySelector("input,button") || panel).focus(); }
function closePanel(panel) { panel.classList.remove("open"); panel.hidden = true; panel._opener && panel._opener.focus(); }
if (a11y) {
  $$(".a11y-btn").forEach(b => b.addEventListener("click", () => a11y.hidden ? openPanel(a11y, b) : closePanel(a11y)));
  a11y.querySelector(".a11y-x").addEventListener("click", () => closePanel(a11y));
  $$("#a11y [data-fs]").forEach(b => b.addEventListener("click", () => { prefs.fs = +b.dataset.fs; applyA11y(); }));
  $$("#a11y [data-opt]").forEach(c => c.addEventListener("change", () => { prefs[c.dataset.opt] = c.checked; applyA11y(); }));
  a11y.querySelector(".a11y-reset").addEventListener("click", () => { Object.keys(prefs).forEach(k => delete prefs[k]); applyA11y(); });
  applyA11y();
}

/* ---------- reveal on scroll ---------- */
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .08 });
$$(".rv").forEach(el => io.observe(el));

/* ---------- project filters (segmented control) ---------- */
const filters = $("#filters"), cases = $$(".case");
function moveThumb() {
  const b = $('#filters button[aria-pressed="true"]'), t = $("#filters .thumb");
  if (b && t) { t.style.width = b.offsetWidth + "px"; t.style.transform = `translateX(${b.offsetLeft}px)`; }
}
function applyFilter(cat, animate) {
  let n = 0;
  cases.forEach(el => {
    const show = cat === "all" || el.dataset.cats.split(" ").includes(cat);
    el.hidden = !show; el.classList.remove("pop");
    if (show) {
      el.querySelectorAll(".rv").forEach(r => r.classList.add("in"));
      if (animate) { void el.offsetWidth; el.style.animationDelay = Math.min(n, 4) * 60 + "ms"; el.classList.add("pop"); }
      n++;
    }
  });
  $$("#filters button").forEach(b => b.setAttribute("aria-pressed", b.dataset.cat === cat));
  moveThumb();
  const b = $('#filters button[aria-pressed="true"]');
  if (animate && b && filters.scrollWidth > filters.clientWidth) filters.scrollTo({ left: b.offsetLeft - (filters.clientWidth - b.offsetWidth) / 2, behavior: "smooth" });
}
if (filters) {
  filters.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b || b.getAttribute("aria-pressed") === "true") return;
    applyFilter(b.dataset.cat, true); history.replaceState(null, "", b.dataset.cat === "all" ? location.pathname : "#" + b.dataset.cat);
  });
  const fromHash = location.hash.slice(1), valid = $$("#filters button").map(b => b.dataset.cat);
  applyFilter(valid.includes(fromHash) ? fromHash : "money");
  addEventListener("resize", moveThumb); document.fonts && document.fonts.ready.then(moveThumb);
}

/* ---------- one video at a time ---------- */
document.addEventListener("play", e => $$("video").forEach(v => { if (v !== e.target && !v.muted) v.pause(); }), true);
$$("video[autoplay]").forEach(v => { if (reduced()) v.pause(); });

/* ---------- world clock + online status ---------- */
function tzParts(tz) {
  const f = new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "numeric", minute: "2-digit", second: "2-digit", hour12: false, weekday: "short" }).formatToParts(new Date());
  const g = t => f.find(p => p.type === t).value; return { h: +g("hour") % 24, m: +g("minute"), s: +g("second"), wd: g("weekday") };
}
function tick() {
  [["cb", "Asia/Manila"], ["cn", "America/New_York"]].forEach(([id, tz]) => {
    const t = tzParts(tz), set = (k, deg) => { const el = document.getElementById(id + k); if (el) el.style.transform = `rotate(${deg}deg)`; };
    set("h", (t.h % 12) * 30 + t.m / 2); set("m", t.m * 6 + t.s / 10); set("s", t.s * 6);
    const txt = document.getElementById(id + "t"); if (txt) txt.textContent = new Date().toLocaleTimeString("en-US", { timeZone: tz, hour: "numeric", minute: "2-digit" });
  });
  const ny = tzParts("America/New_York"), open = !["Sat", "Sun"].includes(ny.wd) && ny.h >= 8 && ny.h < 18;
  $$("#status").forEach(st => { st.classList.toggle("live", open); st.textContent = open ? "Online now" : "Back in US business hours"; });
}
if ($("#status") || $("#cbt")) { tick(); setInterval(tick, 1000); }

/* ---------- ID badge: swing in, tilt toward the pointer ---------- */
const badge = $("#badge");
if (badge && matchMedia("(hover: hover)").matches) {
  const wrap = badge.parentElement;
  wrap.addEventListener("pointermove", e => {
    if (reduced()) return;
    const r = badge.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
    badge.style.setProperty("--rx", (-y * 12).toFixed(2) + "deg"); badge.style.setProperty("--ry", (x * 14).toFixed(2) + "deg");
    badge.style.setProperty("--mx", (x + .5) * 100 + "%"); badge.style.setProperty("--my", (y + .5) * 100 + "%");
    badge.classList.add("tilt");
  });
  wrap.addEventListener("pointerleave", () => { badge.classList.remove("tilt"); badge.style.setProperty("--rx", "0deg"); badge.style.setProperty("--ry", "0deg"); });
}

/* ---------- sticky book bar (tablet widths) ---------- */
const bar = $("#ctabar");
if (bar) addEventListener("scroll", () => bar.classList.toggle("show", scrollY > 500 && innerHeight + scrollY < document.body.scrollHeight - 300), { passive: true });

/* ---------- Latte: FAQ assistant (runs in the browser, answers only from this site) ---------- */
const BOOK = "https://calendly.com/ianrebuta/30min";
const book = (t = "Book a free 30-min call") => `<a href="${BOOK}" target="_blank" rel="noopener">${t}</a>`;
const KB = [
  { k: ["who", "about", "ian", "yourself", "background", "introduce", "tell me"], a: `Ian Vincent Rebuta is a remote operations and QA specialist, social media manager, video editor and web & AI automation builder in Bohol, Philippines, with six years at US companies. He led 23 QA analysts at Ibex Global, did QA and machine learning work at Nooro, and runs Pvblicly. <a href="/about">More about Ian</a>`, f: ["What services does he offer?", "What hours does he work?"] },
  { k: ["service", "services", "offer", "do", "does", "help", "build", "what can", "specialize"], a: `Four kinds of work:<br>• <b>Operations &amp; QA</b>: call audits, SOPs, reports, CRM follow-up<br>• <b>Social media</b>: calendars, captions, scheduling and posting<br>• <b>Video &amp; animation</b>: reels, brand films, animated shorts<br>• <b>Web &amp; AI automation</b>: landing pages, web apps, AI concierges, Zapier<br><a href="/services">See services</a>`, f: ["How much does it cost?", "Show me his projects"] },
  { k: ["price", "pricing", "cost", "rate", "rates", "much", "budget", "fee", "charge", "salary", "pay"], a: `It depends on the scope and hours. Pvblicly's remote operations plans start from $1,000/month, and a full-time role is something Ian prefers to scope with you on a call. ${book("Book a free call to get a number")}`, f: ["How do I hire him?", "What's included?"] },
  { k: ["hour", "hours", "time", "timezone", "zone", "schedule", "shift", "night", "eastern", "est", "pst", "uk", "australia", "overlap"], a: `Ian works remotely from Bohol, Philippines (GMT+8) on US Eastern business hours, and he's comfortable with US, UK or Australian hours, including night shift.`, f: ["Is he available now?", "How do I hire him?"] },
  { k: ["available", "availability", "hire", "hiring", "full", "part", "role", "job", "position", "start", "freelance", "contract", "looking"], a: `Yes, he's available now for a full-time remote role or ongoing project work with a US team, in operations, social media, video or web. ${book()}`, f: ["What hours does he work?", "How much does it cost?"] },
  { k: ["contact", "email", "reach", "call", "book", "meeting", "talk", "calendly", "message", "phone"], a: `The fastest way is a free 30-minute call: ${book("calendly.com/ianrebuta/30min")}. You can also see <a href="/contact">FAQ &amp; contact</a>.`, f: ["What happens on the call?"] },
  { k: ["happens", "prep", "prepare", "agenda"], a: `The call covers what you need, how Ian would handle it and whether it's a fit. No prep needed. ${book()}`, f: [] },
  { k: ["social", "facebook", "instagram", "posts", "posting", "content", "pages", "calendar", "captions", "gokaizn", "smm"], a: `Ian manages ten Facebook and Instagram accounts (real estate, hobby retail, weddings, cabin rentals and more) from one GoKaizn planner: calendars, captions, research, reels, scheduling and a log of everything posted. <a href="/projects#social">See social work</a>`, f: ["Does he make videos?", "How much does it cost?"] },
  { k: ["video", "videos", "reel", "reels", "edit", "editing", "editor", "animation", "capcut", "film", "motion", "youtube", "tiktok"], a: `Yes: vertical reels, brand films, explainers and animated shorts, from script to finished MP4 with music and sound effects, sized for each platform. <a href="/projects#video">Watch his videos</a>`, f: ["Can he build websites?"] },
  { k: ["web", "website", "websites", "site", "landing", "page", "app", "html", "developer", "design", "funnel", "booking"], a: `He's built 7 live websites and a web app: lawn care sites in Tennessee, a wedding invitation, a cabin rental page, the Happy Hobby BHL marketplace on GoHighLevel and the Kusog fitness app. <a href="/projects#web">See the sites</a>`, f: ["Does he do AI automation?"] },
  { k: ["ai", "automation", "automate", "claude", "chatgpt", "gpt", "zapier", "ghl", "gohighlevel", "highlevel", "concierge", "bot", "workflow", "script"], a: `Ian built a 24/7 AI concierge in GoHighLevel and Google AI Studio that qualified leads for clients, writes his own Claude skills for daily work (social media, QA audits, animated shorts), and sets up Zapier and Google Apps Script automations.`, f: ["What tools does he use?"] },
  { k: ["qa", "quality", "audit", "audits", "scorecard", "csat", "calls", "coaching", "ibex", "nooro", "compliance"], a: `QA is his background: 23 QA analysts led across Jamaica, Honduras and the Philippines at Ibex Global, and at Nooro he rebuilt the knowledge base behind the AI call-audit pipeline. The CX team held a 97% CSAT afterwards.`, f: ["What else does he do?"] },
  { k: ["tool", "tools", "software", "stack", "apps", "use", "salesforce", "slack", "notion", "monday"], a: `Google Workspace, Slack, Notion, Monday.com, Salesforce, GoHighLevel, Real Geeks, Zendesk, GoKaizn, Meta Business Suite, Canva, CapCut, Photoshop, HTML/CSS/JS, GitHub, Vercel, Claude Code, Zapier and more. <a href="/about#toolkit">See the full toolkit</a>`, f: [] },
  { k: ["where", "based", "location", "country", "philippines", "bohol", "live", "from"], a: `He's based in Bohol, Philippines, and works remotely on US hours.`, f: ["What hours does he work?"] },
  { k: ["experience", "years", "worked", "companies", "resume", "cv", "career", "history", "employer"], a: `Six years with US companies: Ibex Global (customer service to QA supervisor, 2020–2024), Nooro (QA, machine learning & social media, 2024–2026), and now Pvblicly. <a href="/about#experience">See experience</a>`, f: ["Is he available now?"] },
  { k: ["english", "language", "languages", "speak", "communication"], a: `He works in English with US teams every day; his intro video on the <a href="/about#intro">About page</a> is a good sample.`, f: [] },
  { k: ["hi", "hello", "hey", "yo", "good morning", "good afternoon"], a: `Hi! Ask me anything about Ian's work, hours, rates or how to hire him.`, f: ["What does Ian do?", "How much does it cost?", "How do I hire him?"] },
  { k: ["thanks", "thank", "ty", "great", "cool", "awesome"], a: `You're welcome! When you're ready, ${book("grab a free call with Ian")}.`, f: [] },
];
const START = ["What does Ian do?", "How much does it cost?", "How do I hire him?", "What hours does he work?"];
function answer(q) {
  const words = q.toLowerCase().replace(/[^a-z0-9\s']/g, " ").split(/\s+/).filter(Boolean), text = " " + words.join(" ") + " ";
  let best = null, score = 0;
  KB.forEach(e => {
    let s = 0;
    e.k.forEach(k => { if (k.includes(" ") ? text.includes(" " + k + " ") : words.includes(k) || words.some(w => w.length > 4 && w.startsWith(k) && k.length > 3)) s += k.length > 3 ? 2 : 1; });
    if (s > score) { score = s; best = e; }
  });
  return score ? best : { a: `I'm not sure about that one, and I'd rather not guess. Ian can answer it on a quick call: ${book()}`, f: START.slice(0, 3) };
}
const chat = $("#chat");
if (chat) {
  const log = chat.querySelector(".chat-log"), sugg = chat.querySelector(".chat-sugg"), form = chat.querySelector(".chat-f"), input = $("#chat-in");
  const fab = $(".chat-fab");
  const say = (html, who) => { const m = document.createElement("div"); m.className = "msg " + who; m.innerHTML = html; log.appendChild(m); log.scrollTop = log.scrollHeight; return m; };
  const chips = list => { sugg.innerHTML = ""; list.forEach(t => { const b = document.createElement("button"); b.type = "button"; b.textContent = t; b.onclick = () => ask(t); sugg.appendChild(b); }); };
  function ask(q) {
    q = q.trim(); if (!q) return;
    const u = say("", "me"); u.textContent = q; chips([]);
    const typing = say('<span class="dots"><i></i><i></i><i></i></span>', "bot typing");
    const r = answer(q);
    setTimeout(() => { typing.remove(); say(r.a, "bot"); chips(r.f && r.f.length ? r.f : START.slice(0, 3)); }, reduced() ? 0 : 550 + Math.min(r.a.length, 400));
  }
  let greeted = false;
  function open(opener) {
    openPanel(chat, opener); fab.classList.add("on");
    if (!greeted) { greeted = true; say(`Hey! I'm <b>Latte</b>, Ian's assistant ☕ Ask me what he does, his hours, rates, or how to hire him.`, "bot"); chips(START); }
    input.focus();
  }
  fab.addEventListener("click", () => chat.hidden ? open(fab) : (closePanel(chat), fab.classList.remove("on")));
  $$(".open-chat").forEach(b => b.addEventListener("click", () => open(b)));
  chat.querySelector(".chat-x").addEventListener("click", () => { closePanel(chat); fab.classList.remove("on"); });
  form.addEventListener("submit", e => { e.preventDefault(); ask(input.value); input.value = ""; });
}
document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  [chat, a11y].forEach(p => { if (p && !p.hidden) { closePanel(p); $(".chat-fab") && $(".chat-fab").classList.remove("on"); } });
});
})();

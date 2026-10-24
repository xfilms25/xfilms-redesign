/* X Films — site search. A magnifier in the menu bar opens a panel that searches every project
   (title, Spanish title, director, cast, genre, year) and the main pages. Index: assets/search.json, written by build.py.
   Shortcuts: "/" or Ctrl/Cmd+K to open, arrows to move, Enter to open, Esc to close. */
(() => {
  const me = document.currentScript && document.currentScript.src;
  const BASE = me ? new URL("..", me).href : location.origin + "/";
  const CLD = "https://res.cloudinary.com/dsbe46noz/image/upload/f_auto,q_auto,c_fill,w_160,h_100/";
  let INDEX = null, loading = null, open = false, sel = -1, shown = [];
  const fold = s => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const T = s => (window.XF ? XF.t(s) : s);
  const ES = s => (window.XF && XF.es ? XF.es(s) : "");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function load() {
    if (INDEX || loading) return loading;
    loading = fetch(BASE + "assets/search.json").then(r => r.json()).then(d => {
      INDEX = d.map(it => {
        const words = [it.t, it.es, it.k, it.g, it.y, it.d, it.c, it.x].filter(Boolean).join(" ");
        const esWords = [it.k, it.g, it.sub].concat((it.x || "").split(" · ")).map(ES).join(" ");
        return Object.assign(it, { hay: fold(words + " " + esWords + " " + (it.sub || "")), tt: fold(it.t) + " " + fold(it.es) });
      });
    }).catch(() => { INDEX = []; });
    return loading;
  }

  function score(it, q, terms) {
    if (!terms.every(w => it.hay.indexOf(w) >= 0)) return -1;
    let s = 10;
    if (it.tt.startsWith(q) || fold(it.es).startsWith(q)) s += 100;
    else if (it.tt.indexOf(q) >= 0) s += 60;
    if (fold(it.d).indexOf(q) >= 0) s += 30;
    if (fold(it.c).indexOf(q) >= 0) s += 25;
    if (it.type === "page") s -= 5;
    return s;
  }

  function render(q) {
    const list = ui.querySelector(".xs-list"), head = ui.querySelector(".xs-head");
    q = fold(q.trim());
    if (!INDEX) { list.innerHTML = ""; return; }
    if (!q) {
      shown = INDEX.filter(it => it.quick);
      head.textContent = T("Quick links");
    } else {
      const terms = q.split(/\s+/);
      shown = INDEX.map(it => [it, score(it, q, terms)]).filter(a => a[1] >= 0).sort((a, b) => b[1] - a[1]).slice(0, 8).map(a => a[0]);
      head.textContent = T("Results");
    }
    sel = shown.length ? 0 : -1;
    if (!shown.length) { list.innerHTML = '<li class="xs-none">' + esc(T("No matches. Try a film title, a name or a service.")) + "</li>"; return; }
    list.innerHTML = shown.map((it, i) => {
      const meta = it.type === "page" ? T(it.sub || "Page") : [T(it.k), it.d ? T("Directed by") + " " + it.d : "", it.y].filter(Boolean).join(" · ");
      const img = it.img ? '<img src="' + (it.img.indexOf("img/") === 0 ? BASE + it.img : CLD + it.img) + '" alt="" loading="lazy">' : '<span class="xs-ico" aria-hidden="true">' + (it.icon || "›") + "</span>";
      return '<li><a href="' + BASE + it.u + '" class="' + (i === sel ? "on" : "") + '" data-i="' + i + '">' + img +
        '<span class="xs-t"><b>' + esc(T(it.t)) + "</b>" + (it.es && it.es !== it.t ? ' <i>' + esc(it.es) + "</i>" : "") + "<small>" + esc(meta) + "</small></span></a></li>";
    }).join("");
  }
  function move(d) {
    if (!shown.length) return;
    sel = (sel + d + shown.length) % shown.length;
    ui.querySelectorAll(".xs-list a").forEach((a, i) => a.classList.toggle("on", i === sel));
    const a = ui.querySelector('.xs-list a[data-i="' + sel + '"]'); if (a) a.scrollIntoView({ block: "nearest" });
  }

  let ui, input, btn;
  function build() {
    const st = document.createElement("style");
    st.textContent = `
.xs-btn{background:none;border:0;color:rgba(245,245,247,.8);width:34px;height:34px;display:grid;place-items:center;cursor:pointer;border-radius:50%;transition:color .2s,background .2s;margin-left:auto}
.xs-btn:hover{color:#fff;background:rgba(255,255,255,.08)}.xs-btn svg{width:16px;height:16px}
.nav .wrap > ul + .xs-btn{margin-left:0}.xs-btn + .lang{margin-left:0}
.xs{position:fixed;inset:0;z-index:80;display:none}
.xs.on{display:block}
.xs-back{position:absolute;inset:0;background:rgba(0,0,0,.55);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);animation:xsF .25s ease}
.xs-panel{position:relative;background:rgba(14,14,16,.97);border-bottom:1px solid rgba(255,255,255,.12);padding:calc(18px + env(safe-area-inset-top,0px)) max(22px,env(safe-area-inset-right,0px)) 26px max(22px,env(safe-area-inset-left,0px));animation:xsD .3s cubic-bezier(.2,.7,.2,1)}
.xs-in{max-width:760px;margin:0 auto}
.xs-row{display:flex;align-items:center;gap:14px;border-bottom:1px solid rgba(255,255,255,.18);padding-bottom:12px}
.xs-row svg{width:22px;height:22px;flex:none;color:#ffa045}
.xs-row input{flex:1;min-width:0;background:none;border:0;outline:none;color:#f5f5f7;font:400 clamp(22px,3vw,30px) "Cormorant Garamond",Georgia,serif;font-style:italic;padding:6px 0}
.xs-row input::-webkit-search-cancel-button,.xs-row input::-webkit-search-decoration{-webkit-appearance:none;appearance:none;display:none}
.xs-row input::placeholder{color:rgba(245,245,247,.38)}
.xs-x{background:none;border:0;color:rgba(245,245,247,.7);font-size:26px;line-height:1;cursor:pointer;width:36px;height:36px;border-radius:50%}
.xs-x:hover{color:#fff;background:rgba(255,255,255,.08)}
.xs-head{margin:18px 0 8px;font:500 10px var(--ui,system-ui);letter-spacing:.24em;text-transform:uppercase;color:rgba(245,245,247,.5)}
.xs-list{list-style:none;margin:0;padding:0;max-height:min(62vh,520px);overflow:auto}
.xs-list a{display:flex;align-items:center;gap:16px;padding:10px 12px;border-radius:10px;color:#f5f5f7;text-decoration:none}
.xs-list a.on,.xs-list a:hover{background:rgba(255,160,69,.1)}
.xs-list a.on b{color:#ffbe6b}
.xs-list img{width:80px;height:50px;object-fit:cover;border-radius:4px;flex:none;background:#1d1d1f}
.xs-ico{width:80px;height:50px;border-radius:4px;flex:none;display:grid;place-items:center;background:#1d1d1f;color:#ffa045;font-size:20px}
.xs-t{display:grid;gap:3px;min-width:0}
.xs-t b{font:500 16px var(--ui,system-ui);letter-spacing:.01em}
.xs-t i{font:italic 15px "Cormorant Garamond",Georgia,serif;color:rgba(245,245,247,.6)}
.xs-t small{font:400 12px var(--ui,system-ui);color:rgba(245,245,247,.55);letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.xs-none{padding:14px 12px;color:rgba(245,245,247,.6);font-size:15px}
.xs-keys{margin-top:14px;font:400 11px var(--ui,system-ui);color:rgba(245,245,247,.4);letter-spacing:.06em}
.xs-keys kbd{font:inherit;border:1px solid rgba(255,255,255,.2);border-radius:4px;padding:1px 5px;margin:0 2px}
@media (hover:none){.xs-keys{display:none}}
@keyframes xsF{from{opacity:0}}@keyframes xsD{from{transform:translateY(-14px);opacity:0}}
@media (prefers-reduced-motion:reduce){.xs-back,.xs-panel{animation:none}}`;
    document.head.appendChild(st);
    ui = document.createElement("div");
    ui.className = "xs"; ui.setAttribute("role", "dialog"); ui.setAttribute("aria-modal", "true"); ui.setAttribute("aria-label", "Search");
    ui.innerHTML = '<div class="xs-back"></div><div class="xs-panel"><div class="xs-in">' +
      '<div class="xs-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>' +
      '<input id="xs-q" type="search" autocomplete="off" spellcheck="false" placeholder="Search films, people, services…" aria-label="Search">' +
      '<button class="xs-x" type="button" aria-label="Close search">×</button></div>' +
      '<p class="xs-head">Quick links</p><ul class="xs-list" role="listbox"></ul>' +
      '<p class="xs-keys"><kbd>↑</kbd><kbd>↓</kbd> · <kbd>Enter</kbd> · <kbd>Esc</kbd></p></div></div>';
    document.body.appendChild(ui);
    input = ui.querySelector("input");
    input.addEventListener("input", () => render(input.value));
    input.addEventListener("keydown", e => {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { const a = ui.querySelector('.xs-list a[data-i="' + sel + '"]'); if (a) { e.preventDefault(); close(); location.href = a.href; } }
    });
    ui.querySelector(".xs-back").addEventListener("click", close);
    ui.querySelector(".xs-x").addEventListener("click", close);
    ui.addEventListener("click", e => { if (e.target.closest(".xs-list a")) close(); });
  }
  function openS() {
    if (open) return; open = true;
    if (!ui) build();
    ui.classList.add("on"); document.documentElement.style.overflow = "hidden";
    input.value = ""; render(""); load().then(() => { if (open) render(input.value); });
    setTimeout(() => input.focus(), 30);
  }
  function close() {
    if (!open) return; open = false;
    ui.classList.remove("on"); document.documentElement.style.overflow = "";
    if (btn) btn.focus({ preventScroll: true });
  }

  function mount() {
    const bar = document.querySelector(".nav .wrap");
    if (!bar || bar.querySelector(".xs-btn")) return;
    btn = document.createElement("button");
    btn.type = "button"; btn.className = "xs-btn"; btn.setAttribute("aria-label", "Search");
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>';
    btn.addEventListener("click", openS);
    btn.addEventListener("pointerenter", load, { once: true });
    const before = bar.querySelector(".lang") || bar.querySelector(".book");
    bar.insertBefore(btn, before || null);
    if (window.XF) XF.setLang(XF.lang);   /* translate the new button's label */
  }
  document.addEventListener("keydown", e => {
    const typing = /^(input|textarea|select)$/i.test((e.target && e.target.tagName) || "") || (e.target && e.target.isContentEditable);
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); open ? close() : openS(); }
    else if (e.key === "/" && !typing && !open) { e.preventDefault(); openS(); }
    else if (e.key === "Escape" && open) { e.preventDefault(); close(); }
  });
  document.addEventListener("xf:lang", () => { if (open) render(input.value); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
})();

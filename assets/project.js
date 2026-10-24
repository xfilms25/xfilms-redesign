// X Films — project pages: background trailer, trailer player, poster + stills viewer.
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // muted trailer behind the hero
  const yt = document.getElementById("yt");
  if (yt && !reduce) {
    // Show the video only once YouTube reports it is actually playing,
    // then fade the still out so nothing shows through.
    const reveal = () => { yt.classList.add("on"); yt.closest(".p-hero").classList.add("playing"); };
    addEventListener("message", e => {
      if (!/youtube/.test(e.origin) || e.source !== yt.contentWindow) return;
      let d; try { d = JSON.parse(e.data); } catch (_) { return; }
      if ((d.event === "onStateChange" && d.info === 1) || (d.event === "infoDelivery" && d.info && d.info.playerState === 1)) reveal();
    });
    yt.addEventListener("load", () => yt.contentWindow.postMessage(JSON.stringify({ event: "listening", id: "yt", channel: "widget" }), "*"), { once: true });
    yt.src = yt.dataset.src + "&enablejsapi=1&origin=" + encodeURIComponent(location.origin);
  }

  // trailer player with sound
  const player = document.getElementById("player");
  const pframe = player && player.querySelector("iframe");
  document.querySelectorAll("[data-trailer]").forEach(b => b.addEventListener("click", () => {
    if (!player) return;
    pframe.src = "https://www.youtube-nocookie.com/embed/" + b.dataset.trailer + "?autoplay=1&rel=0&modestbranding=1&playsinline=1";
    player.showModal();
  }));
  if (player) {
    player.addEventListener("close", () => { pframe.src = "about:blank"; });
    player.querySelector(".x").addEventListener("click", () => player.close());
    player.addEventListener("click", e => { if (e.target === player || e.target.classList.contains("box")) player.close(); });
  }

  // official game: ember title card, then load the game in place
  const screen = document.getElementById("gscreen");
  if (screen) {
    const coarse = matchMedia("(pointer: coarse)").matches;
    const exit = screen.querySelector(".gexit");
    const start = () => {
      if (coarse) { window.open(screen.dataset.url, "_blank", "noopener"); return; }   // phones: full screen tab
      if (screen.classList.contains("live")) return;
      const f = document.createElement("iframe");
      f.src = screen.dataset.url;
      f.title = "Game: " + document.title;
      f.allow = "autoplay; fullscreen; gamepad; pointer-lock";
      f.allowFullscreen = true;
      screen.appendChild(f);
      screen.classList.add("live");
      exit.hidden = false;
      screen.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
      setTimeout(() => f.focus(), 400);
    };
    document.querySelectorAll("[data-game]").forEach(b => b.addEventListener("click", start));
    exit.addEventListener("click", () => { screen.querySelector("iframe")?.remove(); screen.classList.remove("live"); exit.hidden = true; });

    const cv = screen.querySelector(".embers");
    if (cv && !reduce) {
      const ctx = cv.getContext("2d");
      let w, h, parts = [], run = false;
      const size = () => { const r = cv.getBoundingClientRect(); w = cv.width = r.width * devicePixelRatio; h = cv.height = r.height * devicePixelRatio; };
      const spawn = () => ({ x: Math.random() * w, y: h + Math.random() * h * .3, r: (Math.random() * 1.6 + .5) * devicePixelRatio, v: (Math.random() * .35 + .15) * devicePixelRatio, d: Math.random() * Math.PI * 2, a: Math.random() * .6 + .3 });
      const frame = () => {
        if (!run) return;
        ctx.clearRect(0, 0, w, h);
        for (const p of parts) {
          p.y -= p.v; p.d += .01; p.x += Math.sin(p.d) * .3 * devicePixelRatio;
          if (p.y < -10) Object.assign(p, spawn(), { y: h + 10 });
          ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(255," + (150 + Math.round(p.a * 60)) + ",70," + p.a + ")";
          ctx.shadowBlur = 8 * devicePixelRatio; ctx.shadowColor = "rgba(255,140,40,.9)";
          ctx.fill();
        }
        requestAnimationFrame(frame);
      };
      size(); parts = Array.from({ length: 70 }, () => Object.assign(spawn(), { y: Math.random() * h }));
      addEventListener("resize", size);
      new IntersectionObserver(es => es.forEach(en => { const was = run; run = en.isIntersecting && !screen.classList.contains("live"); if (run && !was) requestAnimationFrame(frame); })).observe(screen);
    }
  }

  // poster + stills viewer
  const viewer = document.getElementById("viewer");
  const shot = viewer && viewer.querySelector(".shot");
  const items = [...document.querySelectorAll("[data-full]")];
  let i = 0;
  const show = n => { i = (n + items.length) % items.length; shot.src = items[i].dataset.full; shot.alt = items[i].dataset.alt || ""; };
  items.forEach((el, n) => el.addEventListener("click", () => { show(n); viewer.showModal(); }));
  if (viewer) {
    viewer.querySelector(".x").addEventListener("click", () => viewer.close());
    viewer.querySelector(".arr.l").addEventListener("click", () => show(i - 1));
    viewer.querySelector(".arr.r").addEventListener("click", () => show(i + 1));
    viewer.addEventListener("click", e => { if (e.target === viewer || e.target.classList.contains("box")) viewer.close(); });
    viewer.addEventListener("keydown", e => { if (e.key === "ArrowLeft") show(i - 1); if (e.key === "ArrowRight") show(i + 1); });
    if (items.length < 2) viewer.querySelectorAll(".arr").forEach(a => a.hidden = true);
  }
})();

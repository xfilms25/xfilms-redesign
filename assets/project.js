// X Films — project pages: background trailer, trailer player, poster + stills viewer.
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // muted trailer behind the hero
  const yt = document.getElementById("yt");
  if (yt && !reduce) {
    const hero = yt.closest(".p-hero");
    // YouTube shows its title bar and controls for the first seconds of play (and again when it loops).
    // Keep the still on screen until the video has been playing steadily for a few seconds,
    // and cover it again whenever the player stops, buffers or restarts.
    let st = -1, revealT = 0;
    const show = () => { yt.style.transition = ""; yt.classList.add("on"); hero.classList.add("playing"); };
    const hide = () => { clearTimeout(revealT); revealT = 0; yt.style.transition = "none"; yt.classList.remove("on"); hero.classList.remove("playing"); };
    const onState = s => {
      if (s === st) return; st = s;
      if (s === 1) { clearTimeout(revealT); revealT = setTimeout(show, 3800); }
      else hide();
    };
    addEventListener("message", e => {
      if (!/youtube/.test(e.origin) || e.source !== yt.contentWindow) return;
      let d; try { d = JSON.parse(e.data); } catch (_) { return; }
      if (d.event === "onStateChange") onState(d.info);
      else if (d.event === "infoDelivery" && d.info && typeof d.info.playerState === "number") onState(d.info.playerState);
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
    const exit = screen.querySelector(".gexit");
    const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement;
    const stop = () => {
      screen.querySelector("iframe")?.remove();
      screen.classList.remove("live");
      exit.hidden = true;
      if (fsEl()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    };
    // Play opens the game full screen on every device. Where a browser can't go
    // full screen (iPhone Safari), it opens the game in its own tab instead.
    const start = () => {
      const req = screen.requestFullscreen || screen.webkitRequestFullscreen;
      if (!req) { window.open(screen.dataset.url, "_blank", "noopener"); return; }
      if (!screen.classList.contains("live")) {
        const f = document.createElement("iframe");
        f.src = screen.dataset.url;
        f.title = "Game: " + document.title;
        f.allow = "autoplay; fullscreen; gamepad; pointer-lock";
        f.allowFullscreen = true;
        screen.appendChild(f);
        screen.classList.add("live");
        exit.hidden = false;
      }
      Promise.resolve(req.call(screen, { navigationUI: "hide" }))
        .then(() => setTimeout(() => screen.querySelector("iframe")?.focus(), 300))
        .catch(() => { stop(); window.open(screen.dataset.url, "_blank", "noopener"); });
    };
    document.querySelectorAll("[data-game]").forEach(b => b.addEventListener("click", start));
    exit.addEventListener("click", stop);
    // leaving full screen (Esc, swipe, back) closes the game and shows the title card again
    const onFs = () => { if (!fsEl() && screen.classList.contains("live")) stop(); };
    document.addEventListener("fullscreenchange", onFs);
    document.addEventListener("webkitfullscreenchange", onFs);

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

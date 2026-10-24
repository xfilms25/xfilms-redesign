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

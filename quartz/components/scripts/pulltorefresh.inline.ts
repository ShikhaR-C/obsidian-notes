const TRIGGER_DISTANCE = 70 // px the finger must travel before a refresh fires
const MAX_PULL = 120
const RESISTANCE = 0.5

let startY = 0
let pulling = false
let refreshing = false

function indicator(): HTMLElement {
  let el = document.getElementById("pull-to-refresh")
  if (!el) {
    el = document.createElement("div")
    el.id = "pull-to-refresh"
    el.innerHTML = `<div class="ptr-spinner"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></div>`
    document.body.appendChild(el)
  }
  return el
}

function setOffset(distance: number) {
  const el = indicator()
  el.style.transform = `translate(-50%, ${distance}px)`
  el.style.opacity = `${Math.min(1, distance / TRIGGER_DISTANCE)}`
  el.classList.toggle("ready", distance >= TRIGGER_DISTANCE)
}

function reset() {
  const el = indicator()
  el.classList.add("settling")
  el.classList.remove("ready", "refreshing")
  el.style.transform = ""
  el.style.opacity = ""
  setTimeout(() => el.classList.remove("settling"), 250)
}

async function refresh() {
  refreshing = true
  const el = indicator()
  el.classList.add("refreshing")
  el.style.transform = `translate(-50%, ${TRIGGER_DISTANCE}px)`
  el.style.opacity = "1"

  // drop the service worker's cached copies so we really do get fresh content
  try {
    const keys = await caches.keys()
    await Promise.all(keys.filter((k) => k.startsWith("quartz-")).map((k) => caches.delete(k)))
  } catch {
    // caches unavailable (e.g. insecure context) — a plain reload is still fine
  }
  window.location.reload()
}

function onTouchStart(e: TouchEvent) {
  if (refreshing || e.touches.length !== 1) return
  // only start a pull when the page is already scrolled to the very top
  if (window.scrollY > 0) return
  startY = e.touches[0].clientY
  pulling = true
}

function onTouchMove(e: TouchEvent) {
  if (!pulling || refreshing) return
  const delta = e.touches[0].clientY - startY
  if (delta <= 0 || window.scrollY > 0) {
    pulling = false
    reset()
    return
  }
  const distance = Math.min(MAX_PULL, delta * RESISTANCE)
  if (e.cancelable) e.preventDefault()
  setOffset(distance)
}

function onTouchEnd(e: TouchEvent) {
  if (!pulling || refreshing) return
  pulling = false
  const delta = (e.changedTouches[0]?.clientY ?? startY) - startY
  if (delta * RESISTANCE >= TRIGGER_DISTANCE) {
    void refresh()
  } else {
    reset()
  }
}

document.addEventListener("nav", () => {
  indicator()
  refreshing = false

  // a visible button for desktop / anyone who prefers tapping over pulling
  const onClickRefresh = () => void refresh()
  for (const button of document.getElementsByClassName("refresh-button")) {
    button.addEventListener("click", onClickRefresh)
    window.addCleanup(() => button.removeEventListener("click", onClickRefresh))
  }

  document.addEventListener("touchstart", onTouchStart, { passive: true })
  document.addEventListener("touchmove", onTouchMove, { passive: false })
  document.addEventListener("touchend", onTouchEnd, { passive: true })
  document.addEventListener("touchcancel", onTouchEnd, { passive: true })
  window.addCleanup(() => {
    document.removeEventListener("touchstart", onTouchStart)
    document.removeEventListener("touchmove", onTouchMove)
    document.removeEventListener("touchend", onTouchEnd)
    document.removeEventListener("touchcancel", onTouchEnd)
  })
})

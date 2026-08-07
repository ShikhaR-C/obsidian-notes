const STORAGE_KEY = "sidebar-left-collapsed"

function apply(collapsed: boolean) {
  const root = document.getElementById("quartz-root")
  root?.classList.toggle("left-collapsed", collapsed)
  for (const button of document.getElementsByClassName("sidebar-toggle")) {
    button.setAttribute("aria-expanded", collapsed ? "false" : "true")
  }
}

document.addEventListener("nav", () => {
  let collapsed = localStorage.getItem(STORAGE_KEY) === "true"
  apply(collapsed)

  const toggle = () => {
    collapsed = !collapsed
    localStorage.setItem(STORAGE_KEY, `${collapsed}`)
    apply(collapsed)
  }

  for (const button of document.getElementsByClassName("sidebar-toggle")) {
    button.addEventListener("click", toggle)
    window.addCleanup(() => button.removeEventListener("click", toggle))
  }
})

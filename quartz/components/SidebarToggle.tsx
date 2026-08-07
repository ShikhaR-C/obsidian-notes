// @ts-ignore
import script from "./scripts/sidebartoggle.inline"
import styles from "./styles/sidebartoggle.scss"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

const SidebarToggle: QuartzComponent = ({ displayClass }: QuartzComponentProps) => {
  return (
    <div class={classNames(displayClass, "sidebar-rail")}>
      <button
        class="sidebar-toggle"
        type="button"
        aria-label="Toggle sidebar"
        aria-expanded="true"
        title="Toggle sidebar"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <line x1="9" y1="3" x2="9" y2="21" />
          <polyline points="15 9 12 12 15 15" />
        </svg>
      </button>
    </div>
  )
}

SidebarToggle.beforeDOMLoaded = script
SidebarToggle.css = styles

export default (() => SidebarToggle) satisfies QuartzComponentConstructor

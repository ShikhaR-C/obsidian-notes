// @ts-ignore
import script from "./scripts/pulltorefresh.inline"
import styles from "./styles/pulltorefresh.scss"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

// Renders the refresh button and installs the pull-to-refresh gesture.
// Both clear the service worker cache before reloading, so an installed PWA
// can always be forced back to the freshly deployed content.
const RefreshButton: QuartzComponent = ({ displayClass }: QuartzComponentProps) => {
  return (
    <button
      class={classNames(displayClass, "refresh-button")}
      type="button"
      aria-label="Refresh"
      title="Refresh (or pull down)"
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
        <polyline points="23 4 23 10 17 10" />
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
      </svg>
    </button>
  )
}

RefreshButton.afterDOMLoaded = script
RefreshButton.css = styles

export default (() => RefreshButton) satisfies QuartzComponentConstructor

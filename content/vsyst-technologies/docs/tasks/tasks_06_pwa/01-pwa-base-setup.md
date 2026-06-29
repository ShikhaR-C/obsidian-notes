# 01 — PWA Base Setup (Installable + Auto-Update)

> Phase 1 of the PWA initiative. Makes `dip-web` installable as a standalone app and registers a service worker with auto-update behavior.
> **No offline data caching yet** — that's Phase 2.

---

## TL;DR

Install `vite-plugin-pwa`, configure it in `vite.config.js`, replace the stale CRA `public/manifest.json`, clean up `index.html`, and decide on update-prompt UX. End state: the app passes Lighthouse PWA audit, can be installed on Android Chrome / Desktop Chrome / iOS Safari, and silently updates when a new version deploys.

Estimated effort: **1 day** including testing on real devices.

---

## 1. Current State

| Concern                     | File                                        | Notes                                                                       |
| --------------------------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| Build tool                  | `dip-web/vite.config.js`                    | Vite 6, `@vitejs/plugin-react ^4`. Output dir `build/`                      |
| Entry HTML                  | `dip-web/index.html`                        | References `/manifest.json` (the stale CRA file)                            |
| Manifest                    | `dip-web/public/manifest.json`              | **Stale CRA placeholder.** `name: "Create React App Sample"`, generic icons |
| Service worker registration | _none_                                      | `grep -rn "serviceWorker\|workbox\|VitePWA"` returns 0 hits                 |
| App entry                   | `dip-web/src/index.js`                      | Renders `<App />`. No SW registration.                                      |
| Icons                       | `dip-web/public/logo192.png`, `logo512.png` | Default CRA React-logo icons                                                |

`index.html` already has:

- `<link rel="icon" href="/favicon.ico" />`
- `<meta name="viewport" ...>`
- `<meta name="theme-color" content="#000000" />`
- `<link rel="apple-touch-icon" href="/logo192.png" />`
- `<link rel="manifest" href="/manifest.json" />`
- `<title>RO DIP-METER</title>`

Most of this is reusable. Only the `<link rel="manifest">` needs to go (the plugin auto-injects), and we'll add iOS-specific meta tags.

---

## 2. Why `vite-plugin-pwa`

| Option                             | Pros                                                                                       | Cons                                                                             |
| ---------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **Hand-rolled SW + manifest**      | No dep, full control                                                                       | Reimplements Workbox cache strategies, precache manifest generation, update flow |
| **Workbox CLI + custom Vite hook** | Closer to "real" Workbox                                                                   | More glue, no Vite HMR awareness, no `virtual:pwa-register` helper               |
| **`vite-plugin-pwa` (chosen)**     | Wraps Workbox, generates manifest, integrates with Vite build, exposes SW registration API | Adds a dev dep                                                                   |

Used by Vue, SvelteKit, Astro starters. Maintained. Generates a Workbox-based SW with sensible defaults.

---

## 3. Implementation

### 3.1 Install dependency

```bash
yarn add -D vite-plugin-pwa
```

Verify it lands in `package.json` under `devDependencies`. The plugin is build-time only — no runtime bundle impact except the generated SW itself.

### 3.2 Update `vite.config.js`

Add the plugin import and configuration. Keep all existing config (esbuild loader, optimizeDeps, server, build).

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate", // SW takes over → checks for new SW on every nav
      injectRegister: "auto", // plugin injects registration code into entry
      includeAssets: ["favicon.ico", "logo192.png", "logo512.png"],
      manifest: {
        name: "DIP Meter — Dzzlooms Inspection Platform",
        short_name: "DIP Meter",
        description: "Field inspection platform for RO/water systems",
        theme_color: "#000000", // TODO D3: replace with PALETTES.light primary
        background_color: "#ffffff",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        scope: "/",
        icons: [
          { src: "logo192.png", sizes: "192x192", type: "image/png" },
          { src: "logo512.png", sizes: "512x512", type: "image/png" },
          {
            src: "logo512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
        // Phase 1: precache app shell only. Phase 2 will add runtimeCaching.
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff,woff2}"],
        navigateFallback: "/index.html", // SPA fallback for BrowserRouter
        navigateFallbackDenylist: [/^\/api\//, /^\/_/],
        cleanupOutdatedCaches: true,
      },
      devOptions: {
        enabled: false, // do not register SW in `yarn start` (HMR clashes)
      },
    }),
  ],
  esbuild: { loader: "jsx", include: /\.js$/, exclude: [] },
  optimizeDeps: { esbuild: { loader: { ".js": "jsx" } } },
  server: { port: 3000, open: true },
  build: { outDir: "build" },
});
```

**Why these specific options:**

- `registerType: "autoUpdate"` — when a new SW is detected, it activates as soon as all tabs are closed (or immediately on user reload). Alternative `prompt` requires manual user confirmation.
- `injectRegister: "auto"` — plugin injects the registration call automatically; no manual code needed in `src/index.js` for the basic case.
- `navigateFallback: "/index.html"` — for `BrowserRouter`, any unknown route must serve `index.html`. Without this, `/dashboard` reload offline fails.
- `navigateFallbackDenylist` — don't fallback API or internal Vite paths to `index.html`.
- `devOptions.enabled: false` — service workers in dev cause "stale module" weirdness with HMR. Enable only when actively testing PWA features.

### 3.3 Delete `public/manifest.json`

The plugin generates `manifest.webmanifest` at build time from the config above. Keeping the old CRA placeholder around is a footgun — only one of them will be served depending on which `<link>` wins, and `name: "Create React App Sample"` showing up in production install dialogs would be embarrassing.

```bash
rm dip-web/public/manifest.json
```

### 3.4 Clean up `index.html`

Remove the manual manifest link (plugin auto-injects) and add iOS meta tags:

```html
<!-- REMOVE: -->
<!-- <link rel="manifest" href="/manifest.json" /> -->

<!-- ADD: -->
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<meta name="apple-mobile-web-app-title" content="DIP Meter" />
```

Why: iOS Safari ignores most of `manifest.webmanifest`. These three meta tags are how you tell iOS to treat the installed bookmark as a standalone app.

Update the existing `<meta name="theme-color">` if you change the value in the manifest config (D3) — keep them in sync.

### 3.5 Optional: custom update prompt (Decision D5)

Default is silent auto-update. If you want a "new version available — reload?" prompt, replace `injectRegister: "auto"` with `injectRegister: false` and add to `src/index.js`:

```js
import { registerSW } from "virtual:pwa-register";

const updateSW = registerSW({
  onNeedRefresh() {
    // TODO: replace with a real toast/modal in the design system
    if (
      window.confirm("A new version of DIP Meter is available. Reload now?")
    ) {
      updateSW(true);
    }
  },
  onOfflineReady() {
    console.log("[PWA] App is ready to work offline");
  },
});
```

**Recommendation:** start with `injectRegister: "auto"` (simplest, least UX surface). Add the prompt later if users complain about losing in-progress work to silent updates.

### 3.6 Optional: custom install button (Decision D6)

Browsers fire a `beforeinstallprompt` event when the app meets installability criteria. Capture it and trigger the install dialog from a custom button (e.g. in the user menu).

```jsx
// src/components/InstallPwaButton.js (new file)
import { useEffect, useState } from "react";

export function InstallPwaButton() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (!deferredPrompt) return null;

  const onClick = async () => {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") setDeferredPrompt(null);
  };

  return <button onClick={onClick}>Install App</button>;
}
```

iOS Safari does not fire `beforeinstallprompt`. For iOS users, show a static "Install via Share → Add to Home Screen" hint when `navigator.userAgent` includes iPhone/iPad and `window.matchMedia('(display-mode: standalone)').matches` is false.

---

## 4. Testing Checklist

Run after every change in this phase. Most items can be verified with Chrome DevTools.

### 4.1 Build verification

- [ ] `yarn build` completes without errors
- [ ] `build/` contains `manifest.webmanifest` (auto-generated)
- [ ] `build/` contains `sw.js` and `workbox-*.js`
- [ ] `build/` contains `registerSW.js` (only if `injectRegister: "auto"`)
- [ ] `build/index.html` has `<link rel="manifest" href="/manifest.webmanifest">` injected

### 4.2 Manifest validation

- [ ] DevTools → Application → Manifest shows correct name, short_name, icons
- [ ] No errors in the manifest panel
- [ ] Theme color matches design system (D3)

### 4.3 Service worker

- [ ] DevTools → Application → Service Workers shows `sw.js` activated
- [ ] DevTools → Application → Cache Storage shows `workbox-precache-*` populated
- [ ] On rebuild + redeploy, DevTools shows old SW going to "redundant" and new SW activated

### 4.4 Installability

- [ ] Desktop Chrome: install icon appears in address bar; clicking installs the app
- [ ] Installed app launches in its own window with no browser chrome
- [ ] Android Chrome (real device or remote debugging): "Install app" appears in menu
- [ ] iOS Safari: Share → "Add to Home Screen" produces standalone launch (no Safari chrome)
- [ ] Lighthouse → PWA audit passes all checks

### 4.5 Offline app shell

- [ ] DevTools → Network → Offline; reload page; **app shell loads** (UI renders, even if API calls fail)
- [ ] Hard reload offline: same — `index.html` served from precache

### 4.6 Update flow

- [ ] Build, serve, install. Then change a string in the UI, rebuild, redeploy.
- [ ] Reload installed app: new version appears (after one navigation cycle, per `autoUpdate` semantics)
- [ ] No console errors during update

---

## 5. Rollback Plan

PWA features are additive. To roll back:

1. Remove `VitePWA(...)` from `vite.config.js` plugins array
2. Remove the `import { VitePWA }` line
3. Re-add `public/manifest.json` from git history (or accept the broken-bookmark behavior)
4. Re-add `<link rel="manifest" href="/manifest.json" />` to `index.html`
5. Run `yarn build` → no `sw.js` will be emitted
6. **Existing installed users with an active SW need to be cleared.** Add a one-shot SW that calls `self.registration.unregister()` and ship that as the final SW build before removing the plugin entirely. Otherwise users stay on the cached app forever.

The `unregister-only SW` pattern is in the `vite-plugin-pwa` docs under "How to disable PWA features" — keep a copy if you anticipate needing this.

---

## 6. What This Phase Does **Not** Include

- API response caching (Phase 2)
- Stale-while-revalidate for any runtime requests (Phase 2)
- Logout cache clearing (Phase 2)
- Push notifications (Phase 3)
- Offline mutation queueing (Phase 4)
- Branded icon design (Decision D4 — designer task, not code)

---

## 7. Acceptance Criteria

- [ ] Lighthouse PWA audit: all checks pass
- [ ] App installs on at least one Android phone, one iPhone, and Desktop Chrome
- [ ] App shell loads offline (UI renders, even if no data)
- [ ] No regressions in normal online flow (login, dashboard, masters, transactions)
- [ ] No new console errors or warnings
- [ ] `yarn build` output size delta < 50 KB (the SW + Workbox runtime)

---

## 8. References

- `vite-plugin-pwa` docs: https://vite-pwa-org.netlify.app/
- Workbox docs: https://developer.chrome.com/docs/workbox/
- iOS PWA quirks: https://firt.dev/notes/pwa-ios/
- `dip-web/CLAUDE.md` — architecture invariants
- `00-overview.md` — phase context and decisions

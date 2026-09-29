# Store rating and review — StoreKit review prompt, Google Play In-App Review, and how DZZLO OMS should integrate them (research notes, verified 2026-09-30)

> Scope: native APIs, store rules, React Native libraries (New Architecture), when to ask, the "Rate DZZLO" link, test-first plan. All web sources fetched 2026-09-30 unless stated. App facts read read-only from `dzzlo_oms_app` @ `e29f0e5d` (branch `release/v1_79`, committed 2026-09-29).
> **Correction to the brief:** the App Store rule "use the provided API … we will disallow custom review prompts" is guideline **5.6.1 App Store Reviews**. Guideline **1.1.7** reads "Harmful concepts which capitalize or seek to profit on recent or current events, such as violent conflicts, terrorist attacks, and epidemics." — nothing to do with ratings. The course should cite 5.6.1 (plus 3.2.2(x), 5.6.3 and the Introduction). See §2.

## 1. The native APIs in 2026 — what exists, how each behaves in debug / beta / production, and what iOS 26–27 changed

### Takeaway
iOS has one current UIKit-side call, `AppStore.requestReview(in: UIWindowScene)` (StoreKit, iOS 16+, `@MainActor`), plus SwiftUI's `RequestReviewAction` (iOS 16+). `SKStoreReviewController.requestReview(in:)` (iOS 14+) has been deprecated since iOS 18, but it is the only option on iOS 15, which DZZLO still supports (deployment target 15.1). Android has one API, Play In-App Review: `com.google.android.play:review:2.0.2`, published 2024-10-18 and still the latest on 2026-09-30. You call `requestReviewFlow()` and then `launchReviewFlow()`. Neither platform tells the app whether the sheet appeared or what the user did. No new review API or policy came with iOS 26 or iOS 27. iOS 26.1 shipped a sheet whose "Not Now" button was disabled (reported fixed in 26.2). Dev builds on iOS 26.5 seeds stopped showing the sheet, and Apple's reply was "review requests are not allowed in seed".

### Cited Findings

**iOS — API surface (Apple DocC JSON, fetched 2026-09-30, i.e. with the iOS 27 SDK docs live)**
- `AppStore.requestReview(in:)` is declared as `@MainActor static func requestReview(in scene: UIWindowScene)`. Available on iOS / iPadOS / Mac Catalyst 16.0 and visionOS 1.0; not deprecated. A separate macOS 13.0 overload takes an `NSViewController`. — [AppStore.requestReview(in:) (UIWindowScene)](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs); [macOS overload](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-4r0y9)
- `RequestReviewAction` (SwiftUI): "Read the requestReview environment value to get an instance of this structure… You call the instance directly because it defines a callAsFunction() method". Available on iOS / iPadOS / Mac Catalyst 16.0, macOS 13.0, visionOS 1.0. — [RequestReviewAction](https://developer.apple.com/documentation/storekit/requestreviewaction)
- `SKStoreReviewController.requestReview(in:)`: available on iOS / iPadOS / Mac Catalyst from 14.0, **deprecated in 18.0** with the message "Use AppStore.requestReview(in:)." (visionOS 1.0, deprecated 2.0). — [SKStoreReviewController.requestReview(in:)](https://developer.apple.com/documentation/storekit/skstorereviewcontroller/requestreview(in:))
- The `SKStoreReviewController` class: iOS 10.3, deprecated 18.0. Its deprecation summary says "Use RequestReviewAction instead." — [SKStoreReviewController](https://developer.apple.com/documentation/storekit/skstorereviewcontroller)
- The old `SKStoreReviewController.requestReview()` (no scene argument): iOS 10.3, deprecated 14.0 ("Use +[SKStoreReviewController requestReviewInScene:]"). — [requestReview()](https://developer.apple.com/documentation/storekit/skstorereviewcontroller/requestreview())
- The `AppStore` enum's "Requesting reviews" topic lists only `RequestReviewAction` and the two `requestReview(in:)` overloads. Nothing newer exists. — [AppStore](https://developer.apple.com/documentation/storekit/appstore)
- Apple's StoreKit "Updates" page has no review-related entry. Its only dated section is June 2024. — [StoreKit updates](https://developer.apple.com/documentation/updates/storekit)

**iOS — display rules and behaviour by build type (verbatim; the same text appears on the AppStore, RequestReviewAction and SKStoreReviewController pages)**
- "When your app calls this API, StoreKit uses the following criteria: If the person hasn't rated or reviewed your app on this device, StoreKit displays the ratings and review request a maximum of three times within a 365-day period. If the person has rated or reviewed your app on this device, StoreKit displays the ratings and review request if the app version is new, and if more than 365 days have passed since the person's previous review." — [AppStore.requestReview(in:)](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs)
- "Because this method may not present an alert, don't call requestReview() or requestReview(in:) in response to a button tap or other user action. It's up to your app to decide on the best timing for requesting reviews." — [AppStore.requestReview(in:)](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs)
- "When your app calls this method while it's in development mode, StoreKit always displays the rating and review request view, so you can test the user interface and experience. However, this method has no effect in apps that you distribute for beta testing using TestFlight." (heading "Test review requests") — [AppStore.requestReview(in:)](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs); same wording on [RequestReviewAction](https://developer.apple.com/documentation/storekit/requestreviewaction)
- HIG: "the system checks for previous feedback and — if there isn't any — displays an in-app prompt that asks for a rating and an optional written review. People can supply feedback or dismiss the prompt with a single tap or click; they can also opt out of receiving these prompts for all apps they have installed. The system automatically limits the display of the prompt to three occurrences per app within a 365-day period." — [HIG: Ratings and reviews](https://developer.apple.com/design/human-interface-guidelines/ratings-and-reviews)
- The opt-out is a Settings switch on iOS and macOS, and prompts are on by default. — [Daring Fireball, 17 Apr 2026](https://daringfireball.net/linked/2026/04/17/apples-developer-guidelines-for-ratings-and-review-prompts). This post only links to the HIG and reports no rule change.
- Apple's sample "Requesting App Store reviews" (iOS 17 / Xcode 15) prompts only when three conditions hold:
  - "The app hasn't shown a review prompt for a version of the app bundle that matches the current bundle version."
  - The task has been completed "at least four times" ("This number is arbitrary").
  - The person "must pause on the Process Completed scene for a few seconds".

  The code does `try await Task.sleep(for: .seconds(2))` before `await requestReview()`. It keeps `processCompletedCount` and `lastVersionPromptedForReview` in `@AppStorage`, adding "In other apps, there might be more appropriate on-device storage options." It also states: "The conditions above exist purely to delay the call to requestReview, so days, weeks, or even months can elapse without the app prompting a user for a review." — [Requesting App Store reviews (sample)](https://developer.apple.com/documentation/storekit/requesting-app-store-reviews)
- The sample's best practices: "Make the request at a time that doesn't interrupt what someone is trying to achieve in your app, for example, at the end of a sequence of events that they successfully complete. Avoid showing a request for a review immediately when a user launches your app, even if it isn't the first time it launches. Avoid requesting a review as the result of a user action. Also, remember that people can disable requests for reviews from ever appearing on their device." — [Requesting App Store reviews (sample)](https://developer.apple.com/documentation/storekit/requesting-app-store-reviews)

**iOS 26.x / 27 — field reports (from the community; Apple has not documented any change)**
- **iOS 26.1, "Not Now" disabled.** The report: "When the Review Alert shows, the "Not Now" button is disabled for some reason!? … there is no way to opt out, unless the user taps on the stars first." Apple DTS (Nov 2025): "I wasn't able to reproduce the issue", and asked for a retest on iOS 26.2 beta 3. A developer reply marked Recommended (Dec 2025): "With iOS 26.2 it's fixed. "Not now" button is clickable". — [Apple Developer Forums thread 807408](https://developer.apple.com/forums/thread/807408)
- **The same report against expo-store-review on iOS 26.** Tapping outside does nothing, "Not Now" is greyed out, and the only way out is to pick a star and then tap Cancel. Opened 2025-11-19. An Expo maintainer replied (2025-11-28) "this is a change in iOS, not something we control"; the issue is closed. — [expo/expo#41116](https://github.com/expo/expo/issues/41116)
- **iOS 26.5, dev builds.** "[SKStoreReviewController requestReviewInScene:] no longer displays the review prompt in debug/development builds on iOS 26.5 beta (23F5043k and 23F5043g)… This worked correctly on previous iOS versions (26.4)" (Apr 2026, FB22445620). Follow-ups:
  - The original poster (May 2026): "fixed in the latest iOS 26.5 RC".
  - The same poster (Jun 2026): "I got a reply that review requests are not allowed in seed so that's not a bug."
  - Another developer (Jul 2026): "It does not appear when calling AppStore.requestReview(in: windowScene) even on iOS 26.5.1 GM. It does not appear on 26.5.2 either."

  — [Apple Developer Forums thread 821981](https://developer.apple.com/forums/thread/821981)
- **What the system sheet looks like.** On an iOS 26.2 simulator it reads "Enjoying <App>?" with stars and a "Not Now" button. For an iPhone-only app in an iPad compatibility window, the sheet is on screen but missing from the accessibility hierarchy, so UI automation cannot tap it. — [larchwave/flowbaton#43 (2026-09-28)](https://github.com/larchwave/flowbaton/issues/43)
- **Expo fixed a wrong-scene bug** in 57.0.2 (2026-08-14): "[iOS] Present the review prompt from the foregrounded scene." (#48318). In 56.0.0 (2026-05-05) Expo "Migrated requestReview to the new @MainActor async-function API" and "Bumped minimum iOS/tvOS version to 16.4". — [expo-store-review CHANGELOG](https://github.com/expo/expo/blob/main/packages/expo-store-review/CHANGELOG.md) (read from the 57.0.3 tarball)

**Android — Play In-App Review**
- `com.google.android.play:review` has versions 2.0.0, 2.0.1 and 2.0.2. Latest/release is 2.0.2, with Maven `lastUpdated` 20241018 (2024-10-18). `review-ktx` is identical (2.0.2, 2024-10-18). Nothing newer existed on 2026-09-30. — [review maven-metadata.xml](https://dl.google.com/android/maven2/com/google/android/play/review/maven-metadata.xml); [review-ktx maven-metadata.xml](https://dl.google.com/android/maven2/com/google/android/play/review-ktx/maven-metadata.xml)
- The integration page (last updated 2026-09-16) shows:
  - dependencies `implementation("com.google.android.play:review:2.0.2")` and `implementation("com.google.android.play:review-ktx:2.0.2")`
  - `ReviewManagerFactory.create(context)`
  - `manager.requestReviewFlow()`, which returns `Task<ReviewInfo>`; on failure, `(task.getException() as ReviewException).errorCode`, typed `@ReviewErrorCode`
  - `manager.launchReviewFlow(activity, reviewInfo)`, which returns `Task<Void>`

  — [Integrate in-app reviews (Kotlin or Java)](https://developer.android.com/guide/playcore/in-app-review/kotlin-java)
- "The ReviewInfo object is only valid for a limited amount of time. Pre-cache the ReviewInfo object ahead of time, but only once you are certain the in-app review flow will be launched." — [Integrate in-app reviews](https://developer.android.com/guide/playcore/in-app-review/kotlin-java)
- "The flow has finished. The API does not indicate whether the user reviewed or not, or even whether the review dialog was shown. Thus, no matter the result, we continue our app flow." Also: "If an error occurs, do not inform the user or change your app's normal flow." — [Integrate in-app reviews](https://developer.android.com/guide/playcore/in-app-review/kotlin-java)
- The `ReviewErrorCode` constants are `NO_ERROR`, `PLAY_STORE_NOT_FOUND`, `INVALID_REQUEST` and `INTERNAL_ERROR`. — [ReviewErrorCode](https://developer.android.com/reference/com/google/android/play/core/review/model/ReviewErrorCode)
- Supported devices: "Android devices (phones, tablets, and TVs with Google TV) running Android 5.0 (API level 21) or higher that have the Google Play Store installed" and "ChromeOS devices that have the Google Play Store installed". The overview (last updated 2026-01-30) still says "your app must use version 1.8.0 or higher of the Play Core library". That wording is left over from the old all-in-one Play Core library. — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review)

### Inferences
- **DZZLO needs both iOS branches** because of its iOS 15.1 floor: `if #available(iOS 16.0, *) { AppStore.requestReview(in: scene) } else { SKStoreReviewController.requestReview(in: scene) }`. This is exactly what every maintained library does (§3). The deprecated call sits only in the iOS < 16 branch, and the deployment target (15.1) is below 18.0, so no deprecation warning is expected _(unverified — check the Xcode 27 build log)_. When the floor rises to 16.0, the `else` branch goes away.
- **Use the scene-based call, not SwiftUI.** `RequestReviewAction` only works inside SwiftUI; DZZLO's screens are React Native views hosted in UIKit. So the module calls `AppStore.requestReview(in:)` with the foreground-active `UIWindowScene`, found with `UIApplication.shared.connectedScenes.first { $0.activationState == .foregroundActive } as? UIWindowScene`. On iPhone there is one scene (DZZLO's SceneDelegate lives inside `AppDelegate.swift`, per the course canon). On iPad with several windows, the "foreground active" filter matters; Expo's 57.0.2 fix shows what happens when it's wrong.
- **"Development mode" is about signing.** In Apple's wording it means a development-signed build run from Xcode, not React Native's `__DEV__`. A Release-configuration build run from Xcode should therefore still always show the sheet _(inference; Apple does not spell this out)_. Beta iOS seeds can suppress it, so test on a release iOS and treat the 26.5.x reports as unresolved.
- **iOS 26.1 users get a sheet they must star to dismiss.** That is one more reason to ask only at a happy moment.
- **Firebase App Distribution builds won't show the Android card.** DZZLO's minSdk 24 is above 21, so every Play-installed device qualifies. But App Distribution builds are sideloaded and aren't in the tester's Play library (inferred from Google's troubleshooting table in §6).
- **Use core `review:2.0.2` only.** `review-ktx` adds coroutine helpers that a promise-based Turbo Module doesn't need.
- **The module can only report "we asked" or "we could not ask".** Since neither API reports whether the sheet appeared, the promise can say "asked" or "could not ask" (no scene / no activity / a flow error code). That is still worth logging (§4).

### Gaps
- **iOS 27:** no Apple documentation or developer report on any change to the review sheet (searched 2026-09-30). Apple has not publicly confirmed the 26.1 bug or the 26.5.x dev-build reports; the status of FB22445620 is unknown.
- **iOS Ad Hoc builds:** Apple does not document the behaviour for Ad Hoc–signed builds.
- **Play review 2.0.2 changelog:** could not be retrieved (Google's release-notes URL returned 404). Only the Maven date is confirmed.
- **`ReviewErrorCode` values:** the numeric values were not captured.
- **iOS 26 visual redesign:** whether the iOS 26 sheet was visually redesigned (Liquid Glass) is not documented.

## 2. The exact 2026 rules and limits on both stores (quoted)

### Takeaway
**Apple.** Guideline 5.6.1 requires the system API and disallows custom review prompts. 3.2.2(x) forbids making a rating or review a condition for using the app. 5.6.3 and the Introduction forbid manipulated, incentivised or "filtered" feedback. The system shows the sheet at most three times per 365 days. The guidelines page reads "Updated: June 8, 2026", and neither the 13 Nov 2025 nor the 8 Jun 2026 revision touched ratings.

**Google.** The Play policy "User Ratings, Reviews, and Installs" bans incentivised ratings. The In-App Review guidelines forbid:
- asking any question before or during the card, naming "Do you like the app?" as an example;
- triggering the API from a button;
- modifying the card or covering it with anything.

The quota is time-based, the exact value isn't published, and Google can change it without notice.

### Cited Findings

**Apple App Review Guidelines (page marked "Updated: June 8, 2026")** — all from [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- **1.1.7** (not about ratings): "Harmful concepts which capitalize or seek to profit on recent or current events, such as violent conflicts, terrorist attacks, and epidemics."
- **5.6.1 App Store Reviews** (both paragraphs, verbatim):
  - "App Store customer reviews can be an integral part of the app experience, so you should treat customers with respect when responding to their comments. Keep your responses targeted to the user's comments and do not include personal information, spam, or marketing in your response."
  - "Use the provided API to prompt users to review your app; this functionality allows customers to provide an App Store rating and review without the inconvenience of leaving your app, and we will disallow custom review prompts."
- **3.2.2(x)**: "Apps must not force users to rate the app, review the app, download other apps, or other store-related actions in order to access functionality, content, or use of the app. Apps may otherwise incentivize users to take specific actions within apps (e.g. completing a level, watching an ad)."
- **5.6.3 Discovery Fraud**: "Participating in the App Store requires integrity and a commitment to building and maintaining customer trust. Manipulating any element of the App Store customer experience such as charts, search, reviews, or referrals to your app erodes customer trust and is not permitted."
- **5.6.4 App Quality**: "…Indications that this expectation is not being met include excessive customer reports about concerns with your app, such as negative customer reviews, and excessive refund requests. Inability to maintain high quality may be a factor in deciding whether a developer is abiding by the Developer Code of Conduct."
- **Introduction**: "If we find that you have attempted to manipulate reviews, inflate your chart rankings with paid, incentivized, filtered, or fake feedback, or engage with third-party services to do so on your behalf, we will take steps to preserve the integrity of the App Store, which may include expelling you from the Apple Developer Program."
- **5.6 Developer Code of Conduct**: "Repeated manipulative or misleading behavior or other fraudulent conduct will lead to your removal from the Apple Developer Program."

**Apple guideline revision history**
- The **8 Jun 2026** revision changed only: the Introduction (kid and teen safety), 1.2, 4.3(a), 4.3(b) and 4.5.3 (Live Activities may not be used to spam). Nothing on ratings. — [Apple Developer News, 8 Jun 2026](https://developer.apple.com/news/?id=a233fmpw)
- The **13 Nov 2025** revision changed 1.2.1(a), 2.5.10, 3.2.2(ix) (loan APR), 4.1(c), 4.7, 4.7.2, 4.7.5, 5.1.1(ix) and 5.1.2(i). Nothing on ratings. — [Apple Developer News, 13 Nov 2025](https://developer.apple.com/news/?id=ey6d8onl)
- **The "forcing users" rule is long-standing.** The 1 Feb 2021 revision "Removed duplicative section regarding forcing users to perform actions; renumbered former 3.2.2(x)". — [Apple Developer News, 1 Feb 2021](https://developer.apple.com/news/?id=3ozbk628)

**Apple design and product guidance**
- **HIG best practices** (verbatim excerpts):
  - "Ask for a rating only after people have demonstrated engagement with your app or game… Avoid asking for a rating on first launch or during onboarding… People may even be more likely to leave negative feedback if they feel an app is asking for a rating before they get a chance to use it."
  - "Avoid interrupting people while they're performing a task or playing a game… Look for natural breaks or stopping points in your app or game where a rating request is less likely to be bothersome."
  - "Avoid pestering people. Repeated rating requests can be irritating, and may even negatively influence people's opinion of your app. Consider allowing at least a week or two between requests, prompting again after people demonstrate additional engagement with your experience."
  - "Prefer the system-provided prompt."
  - "Weigh the benefits of resetting your summary rating against the potential disadvantage of showing fewer ratings."

  The page's latest change-log entry is 12 Sep 2023 ("Added artwork"). — [HIG: Ratings and reviews](https://developer.apple.com/design/human-interface-guidelines/ratings-and-reviews)
- **Apple's App Store ratings page:**
  - "Make the request when users are most likely to feel satisfaction with your app, such as when they've completed an action, level, or task. Make sure not to interrupt their activity."
  - "You can prompt for ratings up to three times in a 365-day period."
  - "Ensure that your support contact information is easy to find in your app and on your App Store product page."

  — [Apple: Ratings, reviews, and responses](https://developer.apple.com/app-store/ratings-and-reviews/)
- **A persistent link is explicitly allowed:** "you may include a persistent link to your App Store product page in your app's settings or configuration screens. Append the query parameter action=write-review to your product page URL to automatically open the App Store page where users can write a review." — [AppStore.requestReview(in:)](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs)

**Google Play**
- **Policy "User Ratings, Reviews, and Installs":** "Developers must not attempt to manipulate the placement of any apps on Google Play. This includes, but is not limited to, inflating product ratings, reviews, or install counts by illegitimate means, such as fraudulent or incentivized reviews and ratings, or incentivizing users to install other apps as the app's main functionality." Listed violations include:
  - "Asking users to rate your app while offering an incentive" (illustrated with a notification offering a discount for a high rating);
  - "Repeatedly submitting ratings posing as users to influence an app's placement on Google Play";
  - "Submitting or encouraging users to submit reviews containing inappropriate content, including affiliates, coupons, game codes, email addresses, or links to websites or other apps."

  Guidance on replies: "Keep your reply focused on the issues raised in the user's comments and don't ask for a higher rating." — [Play Console Help: User Ratings, Reviews, and Installs](https://support.google.com/googleplay/android-developer/answer/9898684)
- **When to request** (verbatim):
  - "Trigger the in-app review flow after a user has experienced enough of your app or game to provide useful feedback."
  - "Don't prompt the user excessively for a review…"
  - "Your app shouldn't ask the user any questions before or while presenting the rating button or card, including questions about their opinion (such as "Do you like the app?") or predictive questions (such as "Would you rate this app 5 stars")."

  — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review)
- **Design** (verbatim):
  - "Surface the card as-is, without tampering or modifying the existing design in any way, including size, opacity, shape, or other properties."
  - "Don't add any overlay on top of the card or around the card."
  - "The card and the card's background should be on the topmost layer. Once the card has surfaced, don't programmatically remove the card…"

  — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review)
- **Quotas** (verbatim):
  - "Google Play enforces a time-bound quota on how often a user can be shown the review dialog. Because of this quota, calling the launchReviewFlow method more than once during a short period of time (for example, less than a month) might not always display a dialog."
  - "The specific value of the quota is an implementation detail, and it can be changed by Google Play without any notice."
  - "…you should not have a call-to-action option (such as a button) to trigger the API, as a user might have already hit their quota and the flow won't be shown, presenting a broken experience to the user. For this use case, redirect the user to the Play Store instead."

  — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review)
- "The quota limits are not enforced if the app is downloaded from the internal test track." — [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test)

### Inferences
- **What the course cites.** In the review/policy map, cite **5.6.1** (not 1.1.7), with 3.2.2(x), 5.6.3 and the Introduction. For Play, cite the "User Ratings, Reviews, and Installs" policy plus the In-App Review "when to request", "design" and "quotas" sections.
- **Pre-prompts ("Enjoying DZZLO?").** Android forbids them outright. Apple's text says nothing about a pre-question either way, and no current Apple text "permits a pre-question that does not gate the API". The brief's premise is developer lore, not policy. Two further problems:
  - A Yes/No question that sends "No" to a feedback form and only "Yes" to the sheet is the "filtered … feedback" the Introduction names.
  - A custom question in front of Apple's sheet repeats the sheet's own "Enjoying <App>?" heading.

  Under the house parity rule, DZZLO ships **no pre-prompt on either platform**. Unhappy users reach the team through Help → Contact Us, which Apple itself says should be easy to find.
- **Incentives.** Never tie a rating to a discount, a trial extension or any subscription benefit. This is covered by the Play example, Apple's Introduction ("incentivized") and 3.2.2(x).
- **Buttons.** Both stores say not to trigger the API from a tap, and both endorse a store link instead. Apple: a persistent link with `action=write-review`. Google: "redirect the user to the Play Store instead". That is exactly the "Rate DZZLO" row (§5).
- **Replies.** Replies in App Store Connect and Play Console must not ask for a higher rating (Play), or include marketing or personal information (5.6.1).

### Gaps
- **9 Jun 2025 revision:** not checked on its own. The verbatim text above is the current page (updated 8 Jun 2026), so the wording in force in 2026 is covered.
- **Play incentive example:** the bullet about a notification offering a discount was summarised by the fetch tool, not captured verbatim. Re-read the page before quoting that bullet word for word.

## 3. React Native libraries on the New Architecture — and whether a small in-house Turbo Module is the better call

### Takeaway
Two libraries are healthy Turbo Modules:
- **react-native-store-review 0.5.0** (2026-04-15): minimal, with a `void` API.
- **react-native-rate-app 2.1.3** (2026-09-07): New Architecture only, with a promise API and store-link helpers.

The rest are weaker:
- **react-native-in-app-review 4.4.2** (2025-09-03), the most-downloaded bare-RN package, is a legacy bridge module with 31 open issues and 26 open PRs.
- **react-native-rate** is unmaintained.
- **expo-store-review** needs Expo modules and iOS 16.4.

Every one of them wraps the same two OS calls in 20–40 lines of native logic. Recommendation: **BUILD** a house `NativeStoreReview` Turbo Module (≈40 lines of logic, ≈100 lines with boilerplate _(est.)_). If the team doesn't want native code for this, **USE react-native-store-review 0.5.0** as the fallback.

### Cited Findings

**Sources for the table:**
- npm registry JSON, `https://registry.npmjs.org/<pkg>`, e.g. [react-native-in-app-review](https://registry.npmjs.org/react-native-in-app-review)
- npm downloads API, `https://api.npmjs.org/downloads/point/last-week/<pkg>`, e.g. [react-native-store-review](https://api.npmjs.org/downloads/point/last-week/react-native-store-review)
- GitHub REST API, `https://api.github.com/repos/<owner>/<repo>`, e.g. [oblador/react-native-store-review](https://api.github.com/repos/oblador/react-native-store-review)
- reactnative.directory API, `https://reactnative.directory/api/libraries?search=<pkg>`, e.g. [react-native-rate-app](https://reactnative.directory/api/libraries?search=react-native-rate-app)
- The published tarballs themselves (native source read directly), e.g. [react-native-store-review-0.5.0.tgz](https://registry.npmjs.org/react-native-store-review/-/react-native-store-review-0.5.0.tgz)

| Package | Latest (date) | Weekly downloads (21–27 Sep 2026) | Repo health (2026-09-30) | Architecture | Android dependency |
| --- | --- | --- | --- | --- | --- |
| react-native-in-app-review | 4.4.2 (2025-09-03) | 237,509 | 728★, 31 open issues + 26 open PRs, last push 2026-01-28, last commit 2025-09-03 | Legacy bridge: `RCT_EXTERN_MODULE` Swift class + `ReactContextBaseJavaModule`/`@ReactMethod`, no `codegenConfig`. Directory: `github.newArchitecture` false, "Not updated recently" | `play:review:2.0.1` + `play-services-base:17.5.0` |
| react-native-store-review | 0.5.0 (2026-04-15; previous 0.4.3, 2023-10-26) | 57,067 | 780★, 2 open issues, 0 open PRs, last push 2026-04-15 | Turbo Module with codegen (`RNStoreReviewSpec`) plus an old-arch fallback. Directory: `github.newArchitecture` true | `play:review` default 2.0.1 (can be overridden via `playCoreReviewVersion`) |
| react-native-rate-app | 2.1.3 (2026-09-07; 2.0.0 was 2026-03-07) | 7,171 | 258★, 2 open issues + 3 open PRs, last push 2026-09-28 | New-Architecture-only Turbo Module (`RateAppSpec`), Kotlin. Directory: `newArchitecture` true, "Recently updated" | `play:review:2.0.2` |
| expo-store-review | 57.0.3 (2026-09-11, SDK 57); `next` 58.0.1 (2026-09-29) | 1,120,167 | expo/expo monorepo | Expo module (peer dependencies `expo: *`, `react-native: *`). Directory: `newArchitecture` true | `play:review:2.0.1` + `review-ktx:2.0.0` |
| react-native-rate | 1.2.12 (2023-01-23) | 35,162 | 678★, 18 open issues + 6 open PRs, last push 2024-08-09 | Legacy. Directory: **unmaintained** | — |
| react-native-app-review | 1.1.0 (2020-08-16) | 47 | — | Legacy | — |

**react-native-in-app-review 4.4.2 (read from the tarball)**
- **iOS:** calls `AppStore.requestReview(in:)` (via `Task { await MainActor.run { … } }`) on iOS 16+ and `SKStoreReviewController.requestReview(in:)` on 14–15. It resolves `"true"` right after calling, so it cannot know whether the sheet showed. Without a foreground scene it rejects with code `"25"`, `SCENE_DOESN'T_EXIST`.
- **Android:** first checks `GoogleApiAvailability`; if Play services are missing it rejects with `"22"` (`GOOGLE_SERVICES_NOT_AVAILABLE`). Otherwise it resolves with `reviewFlow.isSuccessful()`. It also exposes Huawei AppGallery "in-app comment".
- **Build files:** the podspec says `:ios, "9.0"`; the buildscript uses AGP 7.3.1 and Java 1.8; `gradle.properties` holds `playReviewVersion=2.0.1` and `playServicesVersion=17.5.0`.

— [tarball 4.4.2](https://registry.npmjs.org/react-native-in-app-review/-/react-native-in-app-review-4.4.2.tgz)

**react-native-store-review 0.5.0**
- **Spec:** `requestReview(): void` via `TurboModuleRegistry.get<Spec>('RNStoreReview')`.
- **iOS:** a Swift `@MainActor static` method picks the foreground-active scene, then calls `AppStore.requestReview` (16+) or `SKStoreReviewController` (14–15). If no scene is found it does nothing, silently. Podspec minimum iOS 14.0 with `install_modules_dependencies`.
- **Android:** Java. Failures are only written to `Log.w`. The buildscript pins AGP 7.0.4.
- **Recent history:** 2026-04-15 commits "refactor: add AppStore requestReview method, replace deprecated SKStoreReviewController (#95)" and "Update React Native to 0.85 (#97)".

— [tarball 0.5.0](https://registry.npmjs.org/react-native-store-review/-/react-native-store-review-0.5.0.tgz); [GitHub commits](https://api.github.com/repos/oblador/react-native-store-review/commits)
- **README advice:**
  - "Since it's not possible to know if a dialog will be shown or not you should not call it as a result of tapping a button"
  - For a button, open `itms-apps://apps.apple.com/app/id${IOS_APP_ID}?action=write-review` / `market://details?id=${ANDROID_APP_ID}` with `Linking` instead.
  - "The strings in the dialog comes from the OS, if your translations are purely in JavaScript land you need to add meta data so iOS understand which languages you support"
  - "The dialog is not showing while testing with TestFlight"

  — [react-native-store-review README](https://github.com/oblador/react-native-store-review)

**react-native-rate-app 2.1.3**
- **Spec:** `requestReview(): Promise<boolean>`, `requestReviewAppGallery()` and `requestReviewGalaxyStore(androidPackageName)`, via `getEnforcing`.
- **iOS:** `AppStore.requestReview` inside `Task { @MainActor in … }` on 16+, `SKStoreReviewController` otherwise. It rejects with `no_active_scene` when there is no foreground scene.
- **Android:** Kotlin. It rejects with `REQUEST_REVIEW_FLOW_FAILED`, `ACTIVITY_NULL` and similar codes. The Gradle file guards against AGP 9's built-in Kotlin ("AGP 9 ships built-in Kotlin support…"). Defaults: minSdk 24, compileSdk 36.
- **Store-link helper:** `openStoreForReview` builds `itms-apps://apps.apple.com/app/id<ID>?action=write-review` on iOS and Google / Amazon / Samsung / Huawei market URLs on Android, and calls `Linking.canOpenURL`.
- **Extras:** ships an Expo config plugin.
- **README statements:** "Version 2 supports **only the New Architecture**. Versions older than v2 are **no longer maintained**."; "Supports Android 5+ (API level 21+) and iOS 14+"; requires `LSApplicationQueriesSchemes` containing `itms-apps`.

— [tarball 2.1.3](https://registry.npmjs.org/react-native-rate-app/-/react-native-rate-app-2.1.3.tgz); [README](https://github.com/huextrat/react-native-rate-app)

**expo-store-review 57.0.3**
- `isAvailableAsync()` returns false on TestFlight builds. It detects TestFlight as an App Store receipt named `sandboxReceipt` with no `embedded.mobileprovision`.
- `requestReview()` falls back to opening `ios.appStoreUrl` / `android.playStoreUrl` from the Expo app config.
- The iOS minimum has been 16.4 since 56.0.0.

— [tarball 57.0.3](https://registry.npmjs.org/expo-store-review/-/expo-store-review-57.0.3.tgz)

**DZZLO today**
- No review library is installed: none of these packages appears in `dzzlo_oms_app/package.json` dependencies (read 2026-09-30).
- React Native 0.84.1, iOS deployment target 15.1; the planned 0.87 upgrade brings AGP 9 (course canon, `style-and-outline.md`).

### Inferences

| Option | Verdict | Why |
| --- | --- | --- |
| House `NativeStoreReview` Turbo Module (`specs/` + Swift behind an Objective-C++ adapter + Kotlin/`BaseReactPackage`) | **BUILD (recommended)** | See the reasons listed after this table. |
| react-native-store-review 0.5.0 | **USE (fallback)** | Healthy (2 issues / 0 PRs), Turbo Module, correct iOS calls. Its `void` return and log-only failures give analytics nothing. Its AGP 7.0.4 buildscript is an untested risk under AGP 9. |
| react-native-rate-app 2.1.3 | Acceptable, not chosen | Active and New-Architecture-only. Its extras (Galaxy Store, AppGallery, Amazon) don't matter for DZZLO. It has one maintainer and 7k weekly downloads. `openStoreForReview` uses `canOpenURL`, which forces `LSApplicationQueriesSchemes` plus Android `<queries>`. |
| react-native-in-app-review 4.4.2 | **SKIP** | Legacy bridge module on the interop layer. No release in 12+ months, 57 open issues and PRs, drags in `play-services-base` 17.5.0 and Huawei code. |
| expo-store-review 57.x / 58.x | Optional Expo track only | Needs expo-modules-core and iOS 16.4 (DZZLO is on 15.1). Pair it only with an Expo-paired RN version, per the course decision. |
| react-native-rate 1.2.12 | **SKIP** | Unmaintained (reactnative.directory), last release January 2023. |

**Why BUILD the house module:**
1. **The surface is tiny and stable.** It is two OS calls, unchanged since iOS 16 (2022) and Play `review` 2.0.x (2.0.2, October 2024).
2. **It fits the course's module doctrine.** Official Turbo Modules, TypeScript spec only in `specs/`. It is an ideal second module after `NativeAppInfo`.
3. **It can be tested.** Inject the `ReviewManager` factory so `FakeReviewManager` can stand in (§6), and return an outcome string for analytics.
4. **It is safe through the 0.87 upgrade.** The code builds under the app's own Gradle and CocoaPods settings, not a third-party buildscript pinned to AGP 7.
5. **One new dependency only:** `com.google.android.play:review:2.0.2`.

Size: ≈10 lines of spec + ≈20 Swift + ≈20 Objective-C++ + ≈30 Kotlin + ≈15 package ≈ 95 lines, of which ≈40 are logic _(est.)_.

**Sketch — adapt names to the Phase 1 module conventions; not compiled here.**

```ts
// specs/NativeStoreReview.ts
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  /** Asks the OS for its review sheet. Resolves with what the app can observe:
   *  'requested' | 'no_scene' | 'no_activity' | 'error:<ReviewErrorCode>'.
   *  It never says whether the sheet was shown — neither store reports that. */
  requestReview(): Promise<string>;
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeStoreReview');
```

```swift
// ios/StoreReview/StoreReview.swift  (SWIFT_VERSION 5.0 in the app targets)
import StoreKit
import UIKit

@objc public final class StoreReview: NSObject {
  @objc public static func requestReview(_ done: @escaping (String) -> Void) {
    Task { @MainActor in
      guard let scene = UIApplication.shared.connectedScenes
        .first(where: { $0.activationState == .foregroundActive }) as? UIWindowScene
      else { done("no_scene"); return }
      if #available(iOS 16.0, *) {
        AppStore.requestReview(in: scene)            // iOS 16+, @MainActor
      } else {
        SKStoreReviewController.requestReview(in: scene)   // iOS 14–15 only (deprecated 18.0)
      }
      done("requested")
    }
  }
}
```

```objc
// ios/StoreReview/NativeStoreReview.mm  (codegen header name follows codegenConfig.name)
#import <React/RCTBridgeModule.h>
#import "<CodegenName>/<CodegenName>.h"
#import "dzzlo_oms_app-Swift.h"

@interface NativeStoreReview : NSObject <NativeStoreReviewSpec>
@end

@implementation NativeStoreReview
RCT_EXPORT_MODULE(NativeStoreReview)

- (void)requestReview:(RCTPromiseResolveBlock)resolve reject:(RCTPromiseRejectBlock)reject {
  [StoreReview requestReview:^(NSString *outcome) { resolve(outcome); }];
}

- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:
    (const facebook::react::ObjCTurboModule::InitParams &)params {
  return std::make_shared<facebook::react::NativeStoreReviewSpecJSI>(params);
}
@end
```

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/storereview/NativeStoreReviewModule.kt
package `in`.vsyst.dzzlooms.storereview   // `in` is a Kotlin hard keyword — backticks, exactly as MainActivity.kt:1 does

import android.content.Context
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.google.android.play.core.review.ReviewException
import com.google.android.play.core.review.ReviewManager
import com.google.android.play.core.review.ReviewManagerFactory
// import the codegen-generated NativeStoreReviewSpec from codegenConfig.android.javaPackageName
// (Java accepts `in` as a package segment; Kotlin imports of it need the same backticks)

class NativeStoreReviewModule(
  context: ReactApplicationContext,
  private val managerFor: (Context) -> ReviewManager = ReviewManagerFactory::create, // test seam → FakeReviewManager
) : NativeStoreReviewSpec(context) {

  override fun getName() = NAME

  override fun requestReview(promise: Promise) {
    val activity = reactApplicationContext.currentActivity ?: return promise.resolve("no_activity")
    val manager = managerFor(reactApplicationContext)
    manager.requestReviewFlow().addOnCompleteListener { request ->
      if (!request.isSuccessful) {
        promise.resolve("error:${(request.exception as? ReviewException)?.errorCode}")
        return@addOnCompleteListener
      }
      manager.launchReviewFlow(activity, request.result)
        .addOnCompleteListener { promise.resolve("requested") }   // Google: result says nothing about display
    }
  }

  companion object { const val NAME = "NativeStoreReview" }
}
```

Also needed: a `BaseReactPackage` that returns the module for `NAME` with `isTurboModule = true` in its `ReactModuleInfo`, and `implementation("com.google.android.play:review:2.0.2")` in `android/app/build.gradle`.

**App facts behind the sketch:**
- `android/app/src/main/java/in/vsyst/dzzlooms/MainActivity.kt:1` and `MainApplication.kt:1` both declare ``package `in`.vsyst.dzzlooms``.
- `android/app/build.gradle:84` sets `namespace "in.vsyst.dzzlooms"`.

### Gaps
- **Not built or run here.** The codegen header names, the `ReactModuleInfo` constructor arity in RN 0.84 and the Swift bridging-header name must follow the course's Phase 1 conventions (`rn-native-module-tech.md`).
- **Upgrade risks not tested:** how react-native-in-app-review's legacy module behaves on the 0.84 / 0.87 interop layer, and whether react-native-store-review's AGP 7.0.4 buildscript works under AGP 9.

## 4. Recommended trigger logic (data-backed) for a B2B order/invoice app, the state to persist, pre-prompts, and measurement

### Takeaway
**When to ask.** Only at the end of a completed, successful task: an invoice shared, an order delivered, or an order placed. And only after the person has seen value: at least 3 successes and at least 7 days since first launch.

**When never to ask:** at launch, during onboarding or login, mid-task, or after an error.

**How often:**
- at most once per app version;
- at least 30 days apart (above the HIG's "week or two" minimum, and in line with Play's "less than a month" quota example);
- no more than 3 times per rolling 365 days (Apple's display cap);
- never within 7 days of a crash or visible error;
- 2 seconds after the success screen appears.

**No pre-prompt** on either platform.

**Storage and measurement.** Keep one per-install JSON value in AsyncStorage. Measure with Firebase events plus App Store Connect and Play Console, because the APIs themselves report nothing.

### Cited Findings

**Case studies (all single-app and self-reported)**
- **Keepsafe Photo Vault** (Phiture, 25 Jun 2019, Tim Jones). Among people shown the prompt:
  - "Users converted at 13.5% to a submitted rating", average 4.7 stars;
  - "only 0.07% to a review";
  - people who gave 1 star went on to write a review 12.2% of the time, versus 0.05% for 5 stars;
  - "Negative app reviews from the iOS Ratings Prompt have 3x the character count as positive reviews";
  - suppressing prompts for 7 days after a crash gave "a small but significant increase in avg. rating".

  The article also cites Apptentive research: 32× daily ratings and a 20% average-star improvement (second-hand). Method caveat: the study used a "Fake Prompt" copying Apple's UI to track events. — [Phiture: Unlocking the data behind the iOS Rating Prompt](https://phiture.com/asostack/unlocking-the-data-behind-the-ios-rating-prompt-8e942bfe9134/)
- **Appbot, 17 Nov 2023** (Stuart Hall). Prompting much sooner — after 1 completed workout (7 Minute Workout) or 1 key action (WordBoard) — raised WordBoard's rating volume by more than 400% per month, while the average stayed around 4.84. Conclusion: "We should all be prompting more often, if it's a good app, then your star rating will hold up." — [Appbot: You aren't prompting for app ratings and reviews often enough](https://appbot.co/blog/app-ratings-reviews-strategy-experiment/)
- **Appbot, 20 Feb 2025.** Moving the prompt to the end of onboarding caused "a big drop in the velocity of ratings". Waiting for the "aha moment" produced more ratings. Caveat from the article: "There's No One-Size-Fits-All Solution". — [Appbot: When to Ask for App Ratings](https://appbot.co/blog/prompting-for-ratings-prompt-early-or-wait/)
- **Seatfrog, Android** (Jake Lee, 26 Dec 2024). Triggers after "Bid made", "Bun purchased" and "Ticket purchased"; "I only want to prompt for the same trigger once per session"; each trigger switchable from Firebase config. Results:
  - rating went from 2.2 (Nov 2024) to 4.7 (25 Dec 2024) within 2 weeks of full rollout;
  - hundreds of 4–5★ reviews, against a usual 2–5 a week;
  - "once you've seen one prompt, you might not see any others for a few weeks".

  — [Jake Lee: Rapidly improving Play Store rating with an Android in-app review prompt](https://blog.jakelee.co.uk/play-store-rating-prompt/)
- **Platform guidance** (quoted in full in §1–§2). Apple: ask "at the end of a sequence of events that they successfully complete", once per bundle version, after the task is done "at least four times", with a 2-second delay ([sample](https://developer.apple.com/documentation/storekit/requesting-app-store-reviews)). HIG: "at least a week or two between requests" ([HIG](https://developer.apple.com/design/human-interface-guidelines/ratings-and-reviews)). Google: "after a user has experienced enough of your app", with a quota example of "less than a month" ([overview](https://developer.android.com/guide/playcore/in-app-review)).

**Measurement tools**
- Neither API reports display or submission. Google: "The API does not indicate whether the user reviewed or not, or even whether the review dialog was shown" ([Google](https://developer.android.com/guide/playcore/in-app-review/kotlin-java)). Apple: "this method may not present an alert", and the call returns nothing ([Apple](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs)).
- GA4 limits for app streams: 500 distinctly named events per app user; event names up to 40 characters; 25 parameters per event; parameter names up to 40 characters; parameter values up to 100 characters; 25 user properties. — [GA4 collection limits](https://support.google.com/analytics/answer/9267744)
- App Store Connect: ratings and reviews filter by country or region, "All Versions: View reviews for a specific app version", "All Ratings", and edited/responded reviews; you can reply to reviews. — [App Store Connect Help: View ratings and reviews](https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/view-ratings-and-reviews)
- Play Console: the public rating "is weighted towards more recent ratings to reflect changes and updates that you make to your app". Ratings can be broken down by country/region, language, app version, Android version, device type, device model and operator. "You can write one public reply for each user review of your app." — [Play Console Help: View and analyze your app's ratings and reviews](https://support.google.com/googleplay/android-developer/answer/138230)

**DZZLO facts** (read-only, 2026-09-30)
- **Baseline rating.** App Store India storefront: version 1.78 (released 2026-06-24), 1 rating, average 5.0. The SG and US storefronts: 0 ratings. Minimum OS 15.1. — [iTunes lookup, IN storefront](https://itunes.apple.com/lookup?id=1553062924&country=in) (SG/US via `country=sg` / `country=us`). The Play listing shows "Updated on 23 Jun 2026", category Business; no aggregate rating was present in the fetched HTML. — [Play listing](https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms&hl=en_IN&gl=IN)
- **Storage.** `@react-native-async-storage/async-storage` 3.0.2 is installed. 33 files use the default import. v3 also exports `createAsyncStorage(databaseName)`, and marks `getLegacyStorage()` "Usage is discouraged". Jest already mocks it: `jest.setup.js:50-53` requires `@react-native-async-storage/async-storage/jest`.
- **Analytics.** A safe wrapper, `logEvent(name, params)`, lives at `src/utils/firebase.js:21`. `tagEnv` sets `proj_env` from `PROJ_ENV` (`src/utils/firebase.js:8-18`), and API calls already log `api_call` (`src/store/middleware/rtkQueryPerfLogger.js:41-42`). `@react-native-firebase/analytics` is 24.0.0.
- **Invoice sharing is commented out today** (`src/components/Download/invoiceHTML/ShowInvoice.js:284-338`, `Share.share`), and no share library is installed. React Native's core `Share.share()` behaves differently per platform. On iOS it resolves `sharedAction` or `dismissedAction`. On Android it "returns a Promise which will always be resolved with action being `Share.sharedAction`". — [React Native docs: Share](https://reactnative.dev/docs/share)
- **Roles.** Help reads the user's role through `selectUserRole` (`src/screens/Common/Help/index.js:7`).

### Inferences
**Rules for DZZLO.** All values are starting points to tune _(est.)_; each rule gets a red test first (§6).

| # | Rule | Starting value | Basis |
| --- | --- | --- | --- |
| R1 | Ask only right after a success event | Dealer: order marked delivered; invoice shared (capstone A); payment recorded. Customer: order placed; order delivered | Apple "end of a sequence of events that they successfully complete"; Seatfrog's purchase triggers |
| R2 | The person must have seen value | ≥ 3 success events since the last request **and** ≥ 7 days since first seen | HIG "demonstrated engagement"; Apple sample ≥ 4 ("arbitrary"); Appbot shows asking earlier can work, so start at 3 and tune |
| R3 | Never ask here | First launch, onboarding, login/OTP, mid order entry, any error screen, offline | HIG; Apple sample; Google |
| R4 | Quiet period after a problem | 7 days after a user-visible API error or a crash in the previous session | Keepsafe's 7-day crash suppression → "small but significant" average-rating gain |
| R5 | Once per app version | `lastRequestVersion !== currentVersion` | Apple sample |
| R6 | Spacing | ≥ 30 days between requests | HIG's "a week or two" is the floor; Play's quota example is "less than a month" |
| R7 | Rolling cap | ≤ 3 requests in the last 365 days | Apple's display cap (calls beyond it are wasted moments) |
| R8 | After the store link | If "Rate DZZLO" was opened in the last 365 days → no automatic request | The person already chose to go to the store _(inference)_ |
| R9 | Delay and focus | Wait 2 s after the success UI; ask only if the screen is still focused, `AppState` is `active`, and no Paper `Modal`/`Portal` is open | Apple sample's 2 s pause; Google "topmost layer… no overlay" |
| R10 | Environment | Production `PROJ_ENV` only, plus an explicit dev override for device tests | Keeps TestFlight, App Distribution and dev noise out of analytics |
| R11 | Kill switch | Server-side or feature-flag toggle | Seatfrog switched triggers from Firebase config |

- **Android share caveat.** An "invoice shared" event is reliable on iOS (`sharedAction`) but not on Android, where the promise always resolves `sharedAction`. On Android, count a share as a success only together with another success, or weight delivered orders instead.
- **What to store.** One key, e.g. `dzzlo.storeReview.v1`, per install rather than per user or company (both OS quotas are per device/account):

```json
{ "firstSeenAt": 1759190400000, "successCount": 2, "requests": [1756598400000],
  "lastRequestVersion": "1.79", "lastProblemAt": null, "storeLinkOpenedAt": null }
```

  Keep `requests` trimmed to the last 365 days. On corrupt JSON, fall back to a fresh state with `firstSeenAt = now`. Use the app's existing default AsyncStorage import (33 files already do); a separate `createAsyncStorage('store-review')` database is an option, not a need.
- **"Don't ask again".** There is no user-facing control, because custom prompts are disallowed on iOS and questions are forbidden on Android. The app stops asking through R5–R8. The OS covers the rest: the iOS Settings switch and the Play quota.
- **No pre-prompt** (see §2). Don't copy Keepsafe's 2019 "Fake Prompt" method either: a lookalike sheet is a custom review prompt under 5.6.1.
- **Analytics events** (via `logEvent`, `src/utils/firebase.js:21`; names ≤ 40 characters):
  - `review_eligible` {trigger}
  - `review_requested` {trigger, outcome: 'requested' | 'no_scene' | 'no_activity' | 'error:<code>', app_version}
  - `review_link_opened` {source: 'help'}
  - optionally `review_skipped` {reason: 'R4' | 'R6' | …}, sampled
- **Measure per release.** Divide new ratings in App Store Connect (IN storefront) and Play Console (filtered by app version) by `review_requested` counts per platform. Track the per-version average and the share of 1–2★ reviews that mention bugs. Starting from one iOS rating, the rating count is the first number to move. Resetting the summary rating (HIG) makes no sense at this volume.

### Gaps
- **No B2B or India-specific data** on prompt timing was found.
- **No public evidence of how Khatabook, Vyapar, myBillBook, OkCredit or Zoho trigger their prompts.** Searches returned only comparison pages and Play listings. The review counts in those snippets (Khatabook "5.91 lakh reviews", OkCredit "4.32 lakh reviews") come from third-party comparison sites and are unverified. The only way to learn their behaviour is to observe the apps directly.
- **Case-study quality.** The numbers come from single apps and are self-reported (Keepsafe 2019, WordBoard / 7 Minute Workout, Seatfrog); none is peer-reviewed. Apptentive's "32×" is second-hand.
- **DZZLO's Play rating count** could not be read from the fetched listing.

## 5. What the "Rate DZZLO" row in Help/Settings links to on each platform

### Takeaway
- **iOS:** `https://apps.apple.com/app/id1553062924?action=write-review`. This is Apple's documented form, and it opens the App Store's write-a-review page.
- **Android:** the Play listing, via `market://details?id=in.vsyst.dzzlooms` with a fallback to `https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms`. Google's own documented method is the https URL in an Intent with `setPackage("com.android.vending")`. There is no documented Play deep link straight to the review form.

The row must never call the in-app review API. The app already hard-codes store URLs in three files with inconsistent storefronts; the new row should come from one shared helper.

### Cited Findings
- **Apple sample:** `let url = "https://apps.apple.com/app/idYOURAPPSTOREID?action=write-review"` followed by `openURL(writeReviewURL)`, described as "To enable a person to initiate a review as a result of an action in the UI". — [Requesting App Store reviews](https://developer.apple.com/documentation/storekit/requesting-app-store-reviews)
- **Google:** "you should not have a call-to-action option (such as a button) to trigger the API… For this use case, redirect the user to the Play Store instead." — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review)
- **Google's linking page** (last updated 2026-08-07) documents `https://play.google.com/store/apps/details?id=<package_name>` and an in-app Intent example with `setPackage("com.android.vending")`, so the Play Store app opens instead of a chooser. The page mentions `market://` only as `market://launch?id=<package_name>`; `market://details` no longer appears. — [Linking to Google Play](https://developer.android.com/distribute/marketing-tools/linking-to-google-play)
- **Library conventions** for the same button: `itms-apps://apps.apple.com/app/id<ID>?action=write-review` and `market://details?id=<pkg>`. — [react-native-store-review README](https://github.com/oblador/react-native-store-review); [react-native-rate-app constants (tarball)](https://registry.npmjs.org/react-native-rate-app/-/react-native-rate-app-2.1.3.tgz)
- **React Native `Linking.canOpenURL`:** "The Promise will reject on Android if it was impossible to check if the URL can be opened or when targeting Android 11 (SDK 30) if you didn't specify the relevant intent queries in AndroidManifest.xml. Similarly on iOS, the promise will reject if you didn't add the specific scheme in the LSApplicationQueriesSchemes key inside Info.plist". It also notes that from iOS 9 "your app also needs to provide the LSApplicationQueriesSchemes key inside Info.plist or canOpenURL() will always resolve to false". — [React Native docs: Linking](https://reactnative.dev/docs/linking)

**DZZLO facts** (read-only, 2026-09-30)
- **Store URLs are duplicated in three files:**
  - `src/components/Error/ErrorMessage.js:21-26` — the update-app flow; `:36` awaits `Linking.canOpenURL(updateURL)` (https) and `:37` calls `Linking.openURL(updateLinkingURL)`;
  - `src/components/Error/index.js:22-31` — `STORE_URLS`;
  - `src/helpers/OneSignal/index.js:7-12`.
- **The iOS URLs are inconsistent.** The "open" URL is `itms-apps://itunes.apple.com/us/app/apple-store/id1553062924?mt=8/`: an old host, the US storefront, a wrong slug and a trailing slash. The "check" URL is `https://apps.apple.com/sg/app/dzzlo-oms/id1553062924` (Singapore storefront). Meanwhile the app's only rating is in the IN storefront.
- **The Android URLs** are `market://details?id=in.vsyst.dzzlooms` plus the https listing.
- **No query declarations exist.** There is no `LSApplicationQueriesSchemes` key in `ios/dzzlo_oms_app/Info.plist` and no `<queries>` in `android/app/src/main/AndroidManifest.xml` (grep, no matches).
- **The Help screen** is `src/screens/Common/Help/index.js` (246 lines). Its rows use `ItemSetting`, imported from Settings (`:10`). Current rows:
  - an `ItemSetting` with `onPress={() => {}}` (`:104-111`);
  - "Customer Manual" / "Dealer Manual" by role, opening WebView modals of `https://www.manual.vsyst.in` / `https://dealer.manual.vsyst.in` (`:12-13`, `:122`, `:146`);
  - "Contact Us" (`:162-170`).

  Labels are hard-coded English strings.
- **The row component.** `ItemSetting` is exported at `src/screens/Common/Settings/index.js:219` with props `leftText, RightComponent, onPress, leftTextColor, marginTop, paddingHorizontal`. It picks colours from `useTheme()`.
- **iOS localisations.** `ios/dzzlo_oms_app/Info.plist:7-8` sets `CFBundleDevelopmentRegion` to `en`. There is no `CFBundleLocalizations` key, and `project.pbxproj:237-240` lists `knownRegions` as `en, Base`. Per the react-native-store-review README, the iOS sheet's strings come from the OS and follow the languages the app declares.

### Inferences
**One helper, used by the new row now and by the three old copies in a separate test-first refactor later:**

```js
// src/helpers/StoreLinks/index.js
import { Linking, Platform } from 'react-native';

export const IOS_APP_ID = '1553062924';
export const ANDROID_PACKAGE = 'in.vsyst.dzzlooms';

export const STORE_LINKS = {
  iosWriteReview: `https://apps.apple.com/app/id${IOS_APP_ID}?action=write-review`,
  androidPlayApp: `market://details?id=${ANDROID_PACKAGE}`,
  androidWeb: `https://play.google.com/store/apps/details?id=${ANDROID_PACKAGE}`,
};

// No canOpenURL → no LSApplicationQueriesSchemes, no <queries> needed.
export async function openStoreForReview() {
  if (Platform.OS === 'ios') {
    await Linking.openURL(STORE_LINKS.iosWriteReview);
    return 'ios_write_review';
  }
  try {
    await Linking.openURL(STORE_LINKS.androidPlayApp);
    return 'android_play_app';
  } catch {
    await Linking.openURL(STORE_LINKS.androidWeb);
    return 'android_web';
  }
}
```

- **The row.** Place it in Help next to "Contact Us" (and optionally in Settings): `<ItemSetting leftText={strings.help.rateApp} onPress={onRate} />`. `onRate` calls `openStoreForReview()`, logs `review_link_opened` {source: 'help'} and records `storeLinkOpenedAt` (rule R8). House rules apply: label in en + hi, laid out at 320 dp × fontScale 1, colours via theme tokens (the component already uses `useTheme()`).
- **Optional Android upgrade.** If `market://` ever fails on some device, add an `openStoreListing()` method to the native module that builds Google's documented Intent (https URL plus `setPackage("com.android.vending")`) before falling back to the browser.
- **Hindi on iOS.** Because DZZLO's Hindi is JavaScript-side only (no `hi` in `knownRegions`), the iOS system sheet will likely stay in English for a Hindi-first user _(inference from the README; check on a device)_. Declaring `hi` in `CFBundleLocalizations` / `knownRegions` is a one-line fix to test. Android's card follows the Play Store's language _(unverified)_.

### Gaps
- **Storefront handling.** Not verified whether the App Store app respects the storefront in the URL (`/sg/`, `/us/`) or uses the account's storefront. The country-less `apps.apple.com/app/id…` form avoids the question.
- **No Play review deep link.** Google documents no link to the Play "write a review" form, only to the listing.
- **Devices without Play.** `market://` handling was not tested on Indian OEM devices without Google Play; the https fallback covers them.

## 6. How to test it test-first in this app (Jest, native unit tests, device checklist)

### Takeaway
Work red → green in this order:
1. **Jest, pure policy function:** table-driven tests of R1–R11.
2. **Jest, trigger hook:** a mocked Turbo Module spec, fake timers and the existing AsyncStorage v3 mock.
3. **Jest, Help row:** assert which URL `Linking.openURL` receives on each platform, and that the review API is never called from the tap.
4. **Android native test:** JUnit with `FakeReviewManager` injected (it shows no UI and always succeeds).
5. **iOS native test:** XCTest against an injected protocol spy, because the StoreKit call itself can't be observed.

Then run the device checklist:
- an Xcode dev build on a release iOS always shows the sheet (not on iOS seeds);
- TestFlight shows nothing;
- the Play internal test track shows it with no quota;
- internal app sharing shows it with Submit disabled.

### Cited Findings
- **`FakeReviewManager`:** "completely self-contained and does not interact with the Play Store. No UI is shown and no review is performed". It is "intended for unit-tests and early development iterations only, not for full stack integration tests". Constructor: `public FakeReviewManager(Context context)`. — [FakeReviewManager reference](https://developer.android.com/reference/com/google/android/play/core/review/testing/FakeReviewManager). The test guide adds: "It only fakes the API method result by always providing a fake ReviewInfo object and returning a success status when the in-app review flow is launched." — [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test) (last updated 2025-07-21)
- **Internal test track** conditions (verbatim):
  1. "The user account is part of the Internal Test Track."
  2. "The user account is the primary account and it's selected in the Play Store."
  3. "The user account has downloaded the app from the Play Store (the app is listed in the user's Google Play library)."
  4. "The user account does not currently have a review for the app."

  Also: "After the account on the device has downloaded the app at least once from the internal test track and is part of the testers list, you can deploy new versions of the app locally to that device (for example, using Android Studio)." And: "The quota limits are not enforced if the app is downloaded from the internal test track." — [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test)
- **Internal app sharing:** "When using an app installed with internal app sharing, reviews can't be submitted. To emphasize this difference, the button is disabled in the UI." — [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test)
- **Google's troubleshooting table:**
  - the app needn't be published, but its `applicationID` must at least be on the internal testing track;
  - the app must be in the user's Play library;
  - the primary account must be the one selected in the Play Store;
  - "The user account is protected (for example, with enterprise accounts)" → "Use a Gmail account instead";
  - already reviewed → "Delete the review directly from Play Store";
  - quota reached → use the internal test track or internal app sharing;
  - Play Store sideloaded onto the device → use a different device.

  — [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test)
- **iOS:** "StoreKit always displays" the sheet in development mode and it has "no effect" in TestFlight — [Apple](https://developer.apple.com/documentation/storekit/appstore/requestreview(in:)-1q8qs). On iOS seeds, "review requests are not allowed in seed" (per the forum poster's reply from Apple); unconfirmed reports say it doesn't show on 26.5.1 / 26.5.2 either — [thread 821981](https://developer.apple.com/forums/thread/821981).
- **Detecting TestFlight** (from expo-store-review's source): a receipt named `sandboxReceipt` and no `embedded.mobileprovision` means TestFlight. — [expo-store-review 57.0.3 tarball](https://registry.npmjs.org/expo-store-review/-/expo-store-review-57.0.3.tgz)
- **The app's test setup** (read-only):
  - `jest.config.js` plus `jest.setup.js` and `jest.setup.after-env.js`;
  - Jest ^30.3.0 and @testing-library/react-native ^13;
  - the AsyncStorage v3 mock at `jest.setup.js:50-53`;
  - `src/screens/Common/Settings/__tests__/` exists; `src/screens/Common/Help/` has no tests yet.

  Per the course canon (`style-and-outline.md`), there are no XCTest or JUnit targets and CI runs Jest only.

### Inferences

**Jest tests (write each red first)**
1. **`src/helpers/StoreReview/__tests__/policy.test.js`** — a pure `shouldRequestReview(state, { now, appVersion })`, tested table-driven with one row per rule R1–R10. Include the boundary cases: exactly 30 days, the 3rd vs the 4th request inside 365 days, a new version resetting R5, day 6 vs day 7 after a problem. A mutation smoke (for example `>=` → `>` in R6) must turn a test red.
2. **`…/__tests__/storage.test.js`** — load/save round-trip against the v3 mock. Corrupt JSON falls back to a fresh state. `requests` is trimmed to 365 days.
3. **`…/__tests__/useStoreReview.test.js`**:
   - Setup: `jest.mock('<path>/specs/NativeStoreReview', () => ({ __esModule: true, default: { requestReview: jest.fn(() => Promise.resolve('requested')) } }))` and `jest.useFakeTimers()`.
   - After 3 `recordSuccess('invoice_shared')` calls and 7 simulated days, the hook waits 2 s, calls `requestReview` exactly once, and logs `review_requested` with its outcome.
   - Blurring the screen, a non-`active` `AppState` or an open Paper `Portal` within those 2 s means no call.
   - A problem recorded 3 days earlier means no call.
   - A native outcome of `'error:-1'` is logged and never shown to the user (Google: "do not inform the user").
4. **`src/screens/Common/Help/__tests__/Help.test.js`**:
   - Pressing "Rate DZZLO" calls `Linking.openURL('https://apps.apple.com/app/id1553062924?action=write-review')` when `Platform.OS` is `'ios'`.
   - On Android it calls `market://details?id=in.vsyst.dzzlooms` and then the https fallback when the first call rejects.
   - The mocked `requestReview` is **never** called.
   - `review_link_opened` is logged.
   - The label renders in en and hi at the `PHONE_NARROW` 320-dp preset.

**Android native test**
- Put a JUnit + Robolectric test in `android/app/src/test/…`. Construct the module with `managerFor = { FakeReviewManager(it) }` and a mocked `Promise`. Assert `resolve("requested")`; with no current activity, assert `resolve("no_activity")`.
- `Task` listeners may need the main looper idled (`shadowOf(Looper.getMainLooper()).idle()`) _(unverified)_.
- This would be the app's first JVM test target, so it needs test dependencies: JUnit, Robolectric, a mocking library.

**iOS native test**
- Put the scene lookup and the StoreKit call behind an injectable closure or protocol (for example `var request: (UIWindowScene) -> Void`). Test the `"no_scene"` path and that the injected requester is called exactly once.
- StoreKit's own sheet can't be asserted. This would be the app's first XCTest target.

**Device checklist.** Record results in the phase's Lab Notes, dated.

| # | Setup | Expected | Evidence |
| --- | --- | --- | --- |
| D1 | iOS, Xcode Debug build on iPhone 17e (release iOS 26.x/27), trigger R1–R2 met through the dev clock override | Sheet shows every time (development mode) | Screenshot + iOS build number |
| D2 | D1 at AX-L (fontScale 2.143) and with the device language set to Hindi | Sheet readable; language probably English unless `hi` is declared | Screenshot |
| D3 | iOS, TestFlight build | Nothing shows, no crash; `review_requested` logged with outcome `requested` | Firebase DebugView |
| D4 | iPad, two windows | Sheet appears on the active scene | Screenshot |
| D5 | Android, Play internal test track, Gmail tester (not Workspace), app installed from Play once | Card shows (quota not enforced) | Screenshot |
| D6 | Android, internal app sharing | Card shows, Submit disabled | Screenshot |
| D7 | Android, Firebase App Distribution APK, or the Fold AVD without a Play image | Nothing shows; outcome `requested` or `error:<code>` | logcat + DebugView |
| D8 | Both: Help → Rate DZZLO | iOS opens the App Store write-review page; Android opens the Play listing (no chooser) | Screenshot |
| D9 | Both: trigger an API error, then a success event | No request for 7 days (dev clock) | Log |

### Gaps
- **Robolectric.** Whether `FakeReviewManager` tasks complete under Robolectric without idling the looper was not verified; the app has no JVM test harness yet.
- **Resetting iOS for repeat testing.** Apple documents no way to reset the 3-per-365 counter. Development mode bypasses it, and it doesn't apply to TestFlight, so production behaviour can only be observed after release.
- **iOS 27 dev builds.** Whether iOS 27 (released 2026-09-14) always shows the sheet for development builds hasn't been observed; record it in Lab Notes.
- **The Fold AVD.** It isn't known whether the Pixel 10 Pro Fold AVD used for DZZLO has a Google Play system image. Without one, expect `PLAY_STORE_NOT_FOUND`.

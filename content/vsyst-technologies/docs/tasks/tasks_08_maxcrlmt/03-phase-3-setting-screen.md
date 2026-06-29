# Phase 3 — App: the `CustSettings` credit-limit control

**Repo:** `dzzlo_oms_app`
**File:** `src/screens/Dealer/Customers/CustSettings.js`
**Goal:** Replace the bare numeric `TextInput` (`:788`) with two chips (**Unlimited** / **Block credit**) + an amount input revealed under Block. Writes the new contract: Unlimited → `null`, Blocked → `0`, Capped → the number.

Reuses `RadioChip` (already imported at `:35` and used for Credit Bill Period). Chip taps never open the keyboard; the keyboard appears only when the dealer taps the revealed amount field to type a cap.

> ⚠️ **Release-version gotcha (must do):** the backend write-gate (Phase 1 §2/§3) treats any client reporting `version <= 1.77` as **legacy** and rewrites its `0` → `null`. So this new control only works end-to-end once the app reports **`1.78`**. Bump `android/app/build.gradle` `versionName` and iOS `MARKETING_VERSION` from `1.77` → `1.78` as part of this phase. For on-device testing before the bump, the API honors the magic test version `"1.510"` as "newest" (see `meta` idiom) — or just test against the `1.78` build.

---

## 1. Add the currency import

`formatCurrency` is not yet imported here. Add near the other `utils` imports (after `:33`):

```js
import { formatCurrency } from "../../../utils/Currency";
```

> **Label note:** the chip label string lives in `CR_MODE.BLOCK` below. To rename "Block credit" → "Set limit", change it in that one place.

---

## 2. Module-scope constants + helpers

Add near the top of the file (e.g. just below `confirmAndUpdate`, ~`:76`):

```js
const CR_MODE = { UNLIMITED: "Unlimited", BLOCK: "Block credit" };

// digits + a single dot, rounded to 2dp; NaN-safe
const sanitizeAmount = (txt) => {
  const cleaned = String(txt ?? "").replace(/[^0-9.]/g, "");
  const [intPart, ...rest] = cleaned.split(".");
  const norm = rest.length ? `${intPart}.${rest.join("")}` : intPart;
  const n = Number(norm);
  return Number.isFinite(n) ? Math.round(n * 100) / 100 : NaN;
};

// stored value -> committed numeric form: '' / null / undefined -> null (unlimited)
const toCommitted = (v) =>
  v === "" || v === null || v === undefined ? null : Number(v);
```

---

## 3. State — replace `maxCrLmt`

**Remove** (`:289`):

```js
const [maxCrLmt, setmaxCrLmt] = useState("");
```

**Add:**

```js
// committed server value: null = unlimited, 0 = blocked, >0 = capped
const [crLmtValue, setCrLmtValue] = useState(null);
// editable text in the amount field; doubles as the "restore" hint when blocked
const [crLmtAmt, setCrLmtAmt] = useState("");
```

`maxcrlmtInput` ref (`:330`) stays.

---

## 4. Init effect — replace the `maxCrLmt` branch

Inside the existing effect (`:293-323`), **replace** (`:300-302`):

```js
if (!!CUSTmax_cr_lmt) {
  setmaxCrLmt(CUSTmax_cr_lmt);
}
```

**with:**

```js
setCrLmtValue(toCommitted(CUSTmax_cr_lmt));
// only (re)load the field for a real cap (>0); leave it alone for unlimited/blocked
// so a just-entered amount stays visible as a restore hint until we navigate away
if (Number(CUSTmax_cr_lmt) > 0) {
  setCrLmtAmt(`${CUSTmax_cr_lmt}`);
}
```

Effect deps already include `CUSTmax_cr_lmt` (`:317`) — no change. (After a Block write the row refetches as `0`; `Number(0) > 0` is false, so the typed cap stays in `crLmtAmt` as the restore hint. ✅)

---

## 5. Handlers — replace `handleMaxCreditLimit`

**Remove** `handleMaxCreditLimit` (`:420-429`). **Add:**

```js
const isUnlimited = crLmtValue === null;
const isBlocked = crLmtValue === 0;
const isCapped = typeof crLmtValue === "number" && crLmtValue > 0;

const submitCreditLimit = ({ value, title, subtitle = "", onOk }) => {
  confirmAndUpdate({
    title,
    subtitle,
    updateFn: update_dealer_custs,
    dealer_cust,
    updatePayload: { max_cr_lmt: value, allow: "permit" },
    onSuccess: () => onOk && onOk(),
    setErrorMsg,
  });
};

const onSelectUnlimited = () => {
  if (isUnlimited) return; // no-op re-tap
  submitCreditLimit({
    value: null, // MUST be null (not undefined) — JSON drops undefined
    title: `Set ${customerName} to Unlimited credit?`,
    subtitle: "No credit limit will be enforced.",
    onOk: () => setCrLmtValue(null),
  });
};

const onSelectBlock = () => {
  if (isBlocked) return; // already fully blocked
  submitCreditLimit({
    value: 0, // 0 = blocked
    title: `Block credit for ${customerName}?`,
    subtitle: isCapped
      ? `Current limit ${formatCurrency(Number(crLmtValue))} will be overridden.`
      : "This customer cannot place credit orders (advance deposit still usable).",
    onOk: () => setCrLmtValue(0), // keep crLmtAmt as the greyed restore hint
  });
};

// commit a cap from the amount field (on blur)
const handleSetAmount = () => {
  const n = sanitizeAmount(crLmtAmt);
  if (!Number.isFinite(n) || n <= 0) {
    // junk / empty / 0 while in Block mode -> remain fully blocked
    if (crLmtAmt !== "") setCrLmtAmt("");
    return;
  }
  if (n === Number(crLmtValue)) return; // unchanged cap -> no confirm
  submitCreditLimit({
    value: n,
    title: `Update Credit Limit to ${formatCurrency(n)}?`,
    onOk: () => {
      setCrLmtValue(n);
      setCrLmtAmt(`${n}`);
    },
  });
};
```

**Behavior recap**
| Dealer action | Confirm | Stored | Keyboard? |
| ------------- | ------- | ------ | --------- |
| Tap **Unlimited** | "Set … Unlimited?" | `null` | no |
| Tap **Block credit** (from Unlimited/Capped) | "Block credit?" (+ cites old cap) | `0` | no |
| Type amount in revealed field, blur | "Update to ₹X?" | `X` | yes (typing) |
| Clear field, blur (while Blocked) | — | stays `0` | — |

---

## 6. JSX — replace the credit-limit `Pressable`

**Replace** the whole `Pressable` containing the old `maxcrlmt` `TextInput` (`:774-799`) with:

```jsx
<View style={styles.settingsItem}>
  <Text>Credit Limit</Text>

  <View
    style={{
      flexDirection: "row",
      flexWrap: "wrap",
      justifyContent: "flex-end",
      alignItems: "center",
    }}
  >
    <RadioChip
      selectedRadio={CR_MODE.UNLIMITED}
      radio={isUnlimited ? CR_MODE.UNLIMITED : CR_MODE.BLOCK}
      setRadio={onSelectUnlimited}
    />
    <RadioChip
      selectedRadio={CR_MODE.BLOCK}
      radio={isUnlimited ? CR_MODE.UNLIMITED : CR_MODE.BLOCK}
      setRadio={onSelectBlock}
    />
  </View>
</View>;

{
  !isUnlimited && (
    <Pressable
      onPress={() => {
        if (maxcrlmtInput.current && !maxcrlmtInput.current.isFocused()) {
          maxcrlmtInput.current.focus();
        }
      }}
      style={({ pressed }) => [
        styles.settingsItem,
        stateStyles.enabledSetting(pressed),
      ]}
    >
      <Text>Set amount</Text>

      <TextInput
        value={crLmtAmt}
        onChangeText={(t) => setCrLmtAmt(t.replace(/[^0-9.]/g, ""))}
        placeholder={isBlocked ? "Blocked — tap to set a limit" : "0"}
        placeholderTextColor={colors.placeholder}
        ref={maxcrlmtInput}
        style={[
          styles.textInputItem,
          stateStyles.textInputItem,
          isBlocked && { color: colors.placeholder }, // greyed restore hint
        ]}
        keyboardType={"numeric"}
        onBlur={handleSetAmount}
        returnKeyType={"done"}
      />
    </Pressable>
  );
}

<Text
  style={{
    paddingHorizontal: 16,
    paddingBottom: 8,
    fontSize: 12,
    color: colors.placeholder,
  }}
>
  Unlimited = no cap. Block credit = no credit unless you set an amount. Advance
  deposit is still usable when blocked.
</Text>;
```

Notes:

- `RadioChip` highlights when `radio === selectedRadio`. Passing `radio = isUnlimited ? 'Unlimited' : 'Block credit'` lights exactly one chip; `setRadio` is wired to our handlers (the label arg it passes is ignored).
- When **blocked**, `crLmtAmt` may still hold the previous cap (e.g. `"50000"`), rendered greyed via `colors.placeholder` = the "restore" hint. Tapping the row focuses the field; typing + blur re-commits it as a cap (decision locked earlier).
- The keyboard-dismiss `Pressable` wrapper that previously blurred `maxcrlmtInput` (`:774-780`) is replaced; nothing else references it for this field.

---

## 7. Phase 3 acceptance (simulator)

- [ ] New/blocked customer → opens with **Block credit** selected, field shows "Blocked — tap to set a limit". No keyboard on load.
- [ ] Tap **Unlimited** → confirm → reopen shows Unlimited, amount field hidden.
- [ ] Tap **Block credit** → confirm "Block credit?" (no keyboard) → blocked.
- [ ] Under Block, type `50000`, blur → confirm "Update Credit Limit to ₹50,000?" → reopen shows Block + `50,000`.
- [ ] With `50,000` set, tap **Block credit** → confirm cites "Current limit ₹50,000 will be overridden" → field shows `50,000` greyed; navigate back & return → field empty (server is `0`).
- [ ] Re-tap the already-selected chip → no dialog.
- [ ] Clear the amount while blocked, blur → stays blocked, no dialog.

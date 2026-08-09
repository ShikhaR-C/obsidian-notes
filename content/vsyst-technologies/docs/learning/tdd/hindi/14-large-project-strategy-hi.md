# 14. बड़े प्रोजेक्ट में TDD

अब तक सब कुछ छोटे पैमाने का TDD था: एक function, एक फ़ाइल, एक kata। यह हिस्सा दूसरी समस्या पर है — **सिस्टम बड़ा होने पर चक्र को तेज़ बनाए रखना**।

दस्तावेज़ 14–18 का चलता हुआ उदाहरण एक असली जैसा stack है:

```
                      ┌──────────────────────┐
   React web app ────▶│                      │
   Vanilla JS/HTML ──▶│   Node/Express API   │──▶ MongoDB (Mongoose)
   React Native app ─▶│                      │──▶ 3rd-party APIs
                      └──────────────────────┘
```

चार deployables, जिनमें तीन clients, एक database, और कुछ बाहर जाने वाला network। इस आकार पर TDD को टेस्ट लिखना कभी नहीं मारता — मारते हैं **feedback में देरी और अस्थिरता**। दोनों की जड़ एक ही है: ऐसे टेस्ट जो उन सीमाओं तक पहुँच जाते हैं जिनकी ज़रूरत नहीं थी।

---

## वह एक नियम जो बाक़ी सब मुमकिन बनाता है

> **Business नियम बिना server, बिना database, बिना browser, और बिना network के चलने चाहिए।**

अगर pricing, पात्रता, sync-conflict का निपटारा और validation, Express handlers, Mongoose models और React components के अंदर रहते हैं, तो किसी भी business नियम के हर टेस्ट को चलता हुआ सिस्टम चाहिए — और आप फिर उसी 12-मिनट वाली suite पर पहुँच जाते हैं जिसे कोई नहीं चलाता।

इसलिए ढाँचा उबाऊ और जान-बूझकर ऐसा है:

```
packages/
├── domain/         शुद्ध business नियम। शून्य dependencies। शून्य I/O।
├── contracts/      साझा request/response schemas (Zod)। कोई logic नहीं।
├── api/            Express + use cases + Mongoose adapters
├── web/            React ऐप
├── admin/          vanilla JS + HTML पेज
├── mobile/         React Native ऐप
└── test-support/   builders, fakes, fixtures, MSW handlers
```

`domain` और `contracts` को सब import करते हैं और ये ख़ुद कुछ import नहीं करते। हर धीमी चीज़ किनारों पर रहती है, उस interface के पीछे जिसे domain तय करता है। यही एक बंदिश आपके 80% टेस्टों को milliseconds में चलने देती है।

---

## परतें (tiers)

"unit बनाम integration" नहीं — इन शब्दों का मतलब हर किसी के लिए अलग है। परतें इस आधार पर तय कीजिए कि **वे किसे छू सकती हैं**, और हर एक को एक runtime बजट में बाँधिए।

| परत                   | किसे छूती है                                         | आम संख्या                   | बजट           | कब चलती है           |
| --------------------- | ---------------------------------------------------- | --------------------------- | ------------- | -------------------- |
| **T0 — domain**       | कुछ नहीं। शुद्ध functions और in-memory fakes।        | हज़ारों                     | **< कुल 5 s** | हर save पर           |
| **T1 — module**       | असली Mongo (in-memory), असली Mongoose, कोई HTTP नहीं | सैकड़ों                     | < 60 s        | push से पहले         |
| **T2 — API contract** | supertest + असली DB के ज़रिए पूरी API process        | ~हर endpoint पर 1 × मामले   | < 2 मिनट      | हर PR पर             |
| **T3 — client**       | jsdom / RN test renderer + MSW। असली network नहीं।   | सैकड़ों                     | < 90 s        | हर PR पर             |
| **T4 — E2E smoke**    | असली browser / device, असली deployed stack           | **5–15, इससे ज़्यादा नहीं** | < 10 मिनट     | main में merge पर    |
| **T5 — canary**       | तीसरे पक्ष की APIs, staging, असली network            | गिनती के कुछ                | बिना समय-सीमा | रात में, gating नहीं |

संख्याएँ भी उतनी ही अहम हैं जितने runtimes। **T4 एक बजट है, लक्ष्य नहीं।** जो भी टीम end-to-end टेस्टों को बेलगाम बढ़ने देती है, उसकी suite 40 मिनट लेती है और 15% बार ऐसे कारणों से फेल होती है जिनकी कोई जाँच नहीं करता।

```
        /\          T4  E2E smoke        5–15      धीमे, अस्थिर, ऊँचा भरोसा
       /  \         T3  client           ~300      तेज़, jsdom + MSW
      /    \        T2  API contract     ~150      एक process, असली DB
     /      \       T1  module           ~400      असली Mongo, कोई HTTP नहीं
    /________\      T0  domain          ~1500      milliseconds
```

---

## हर परत _किसलिए_ है

परतें "एक ही टेस्ट के अलग-अलग आकार" नहीं हैं। हर परत बग की उस श्रेणी को पकड़ने के लिए है जिसे नीचे वाली परत पकड़ **नहीं सकती**:

- **T0** — क्या नियम सही है? (`3 महीने में रद्द हुआ 12-महीने का plan, सालाना क़ीमत का 9/12 वापस करे, ग्राहक के पक्ष में गोल किया हुआ`)
- **T1** — क्या यह persistence में टिकता है? Unique indexes, query की सटीकता, schema validation, transactions।
- **T2** — क्या HTTP सतह सही है? Status codes, error envelopes, auth, pagination, वह response आकार जिस पर तीन clients निर्भर हैं।
- **T3** — क्या UI उस response के साथ सही काम करता है? Loading, ख़ाली, error, success। Optimistic updates। Form validation।
- **T4** — क्या यह सचमुच जुड़ा और deploy हुआ है? Config, CORS, auth cookies, build output।
- **T5** — क्या रातों-रात किसी तीसरे पक्ष ने कुछ बदल दिया?

अगर आप बता नहीं सकते कि नया टेस्ट किस परत का है, तो यह डिज़ाइन की बदबू है: व्यवहार शायद अलग-थलग नहीं है।

**हर टेस्ट उस सबसे निचली परत पर लिखिए जो उस कारण से फेल हो सकती है जिसकी आपको परवाह है।** Browser के ज़रिए टेस्ट किया गया rounding नियम ऐसा नियम है जिसे बदलने से आप डरेंगे।

---

## Test-support: वह package जो तय करता है कि यह टिकेगा या नहीं

छोटे पैमाने पर हर कोई टेस्ट डेटा हाथ से बनाता है। बड़े पैमाने पर suites इसी वजह से सड़ती हैं — 400 टेस्ट, हर एक अपना `User` literal बनाता हुआ, और एक ज़रूरी field जोड़ते ही सब टूट जाते हैं।

एक package बनाइए और उसे ढंग से संभालिए:

```js
// packages/test-support/builders/user.js
const base = () => ({
  email: "ada@example.com",
  name: "Ada Lovelace",
  plan: "free",
  createdAt: new Date("2026-01-01T00:00:00Z"),
  verified: true,
})

export const aUser = (overrides = {}) => ({ ...base(), ...overrides })

export const anAdmin = (overrides = {}) =>
  aUser({ role: "admin", permissions: ["billing:write"], ...overrides })
```

```js
// टेस्ट सिर्फ़ वही बताता है जो उसके लिए मायने रखता है
const user = aUser({ plan: "pro" })
```

इसे काम का बनाए रखने वाले नियम:

1. **Builder की defaults मान्य होनी चाहिए।** जो टेस्ट किसी field की परवाह नहीं करता, उसे मुफ़्त में चलता हुआ मान मिल जाता है।
2. **टेस्ट सिर्फ़ वे fields बताएँ जिन पर वे निर्भर हैं।** अगर कोई टेस्ट `verified: true` सेट करता है और assertion का verification से कोई लेना-देना नहीं, तो वह लाइन हटा दीजिए — यह शोर है जो असली input को छिपाता है।
3. **कोई ज़रूरी field जोड़िए → एक फ़ाइल बदलिए।** निवेश का पूरा रिटर्न यही है।
4. साथ में यह भी दीजिए: एक `fixedClock()`, एक `InMemoryEventBus`, seed किए हुए ID generators, और [18. API और network टेस्ट](18-tdd-api-network-hi.md) वाले साझा MSW handlers।

---

## Isolation, यानी: आपकी suite अस्थिर क्यों है

बड़ी suite की लगभग सारी अस्थिरता इन चार में से एक है। इन्हें retries से नहीं, ढाँचे से ठीक कीजिए।

| कारण                          | लक्षण                                            | इलाज                                                                                     |
| ----------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **टेस्टों के बीच साझा state** | अकेले पास, suite में फेल; क्रम पर निर्भर         | हर worker के लिए एक DB, टेस्टों के बीच truncate। देखिए [16](16-tdd-mongodb-mongoose-hi.md)। |
| **असली समय**                  | आधी रात, महीने के अंत, या CI के timezone में फेल | घड़ी inject कीजिए। Domain कोड में `new Date()` कभी मत बुलाइए।                            |
| **असली network**              | दफ़्तर का wifi हिचकोला ले तो फेल                 | `onUnhandledRequest: 'error'` के साथ MSW। असली network सिर्फ़ T5 में।                    |
| **sleep करके इंतज़ार**        | Local पर पास, व्यस्त CI मशीन पर फेल              | किसी शर्त पर `waitFor` / `findBy`। कभी `setTimeout(500)` नहीं।                           |

Isolation को जान-बूझकर साबित कीजिए: दिन में एक बार CI में suite को random क्रम (`vitest --sequence.shuffle`) में चलाइए। अगर फेरबदल से टूटती है, तो साझा state है — यह आपके टेस्टों में बग है, और यही वह चीज़ है जो आख़िरकार किसी असली फ़ेल्योर को छिपा देगी।

> **Retries इलाज नहीं हैं।** जो टेस्ट दूसरी कोशिश में पास होता है, वह कुछ बता रहा था और नज़रअंदाज़ कर दिया गया। उसी दिन उसे gating suite से quarantine कीजिए, एक मालिक और तारीख़ के साथ, फिर दो हफ़्ते में ठीक कीजिए या हटा दीजिए।

---

## कब क्या चलता है

```
फ़ाइल save          → watch mode में T0                       < 1 s
pre-push hook       → बदले packages के लिए T0 + T1            < 60 s
pull request        → T0 T1 T2 T3, sharded, समानांतर          < 5 मिनट कुल
main में merge      → ऊपर वाला + staging पर T4 smoke          < 15 मिनट
रात में             → T5 canaries, फेरबदल क्रम, पूरा E2E       बिना समय-सीमा, gating नहीं
```

दो चीज़ों पर समझौता नहीं, दोनों [11, चरण 6](11-tutorial-first-feature-hi.md) से:

- **जल्दी फेल हो।** T0, T1 का द्वार है; T1, T2 का। किसी domain unit test के लाल होने का पता लगाने के लिए आठ मिनट E2E पर मत लगाइए।
- **Gating suite में auto-retry नहीं।** ऊपर देखिए।

Shard परत के हिसाब से कीजिए, फ़ाइलों की संख्या के हिसाब से नहीं — परतों की setup लागत बिल्कुल अलग होती है, और जो shard Mongo चालू करता है उसे शुद्ध functions चलाने का कोई काम नहीं।

---

## सीमा-पार drift: इसी आकार की ख़ास चूक

एक API पर तीन clients होने पर जो बग आपको सचमुच चोट पहुँचाएगा वह local स्तर पर किसी की ग़लती नहीं होती: API `total_cents` का नाम बदलकर `totalCents` कर देती है, हर API टेस्ट पास होता है, हर React टेस्ट अपने हाथ से लिखे mock के ख़िलाफ़ पास होता है, और React Native ऐप production में टूट जाता है।

इसका इलाज यह है कि **mock और server एक ही स्रोत से आएँ**:

1. Response का आकार एक ही बार, `packages/contracts` में, Zod schema के रूप में तय कीजिए।
2. API के T2 टेस्ट assert करें कि असली responses उस schema से **parse** होते हैं।
3. हर client के T3 टेस्ट अपने MSW handlers उसी schema **से** बनाएँ।

अब कोई नाम बदले तो API टेस्ट _और_ हर client टेस्ट एक साथ, commit के समय ही फेल हो जाएँगे। ब्योरा और कोड [18. API और network टेस्ट](18-tdd-api-network-hi.md) में।

---

## बड़े मौजूदा codebase पर शुरुआत

आप retrofit नहीं करते। [13, चरण 4](13-adoption-phases-hi.md) ज्यों का त्यों लागू होता है, बस बड़े प्रोजेक्ट के लिए दो चीज़ें और:

- **टेस्ट लिखने से पहले परतें तय कीजिए।** वरना सब कुछ T2 या T4 में जा गिरेगा, जहाँ यह धीमा है, और साल भर में suite बचाने लायक़ नहीं रहेगी।
- **`domain` को धीरे-धीरे निकालिए।** जब भी आप किसी नियम का test-drive करें, उसे handler या component से निकालकर शुद्ध package में ले जाइए। छह महीने बाद क़ीमती logic एक ऐसे package में होगा जो 4 सेकंड में चलता है।

---

## 🛠 मिनी-प्रोजेक्ट — ढाँचा

_उसमें कुछ डालने लायक़ होने से पहले ढाँचा खड़ा कीजिए। एक दिन।_

1. ऊपर वाला monorepo ढाँचा बनाइए — `domain`, `contracts`, `test-support` — ख़ाली पर जुड़े हुए, हर एक में एक पास होता टेस्ट।
2. `domain` में एक असली नियम जोड़िए, test-first। कहीं से कोई import नहीं।
3. परत-वार scripts जोड़िए: `test:t0`, `test:t1`, `test:t2`, `test:t3`। हर एक अलग से चलने लायक़, हर एक अपना runtime छापता हुआ।
4. `test-support` में पहला builder लिखिए और उसे किसी `domain` टेस्ट से इस्तेमाल कीजिए।
5. हर परत के लिए एक CI job जोड़िए जिसमें तालिका वाला बजट **फ़ेल्योर के रूप में लागू** हो, चेतावनी के रूप में नहीं।
6. रात वाला फेरबदल run जोड़िए।
7. परतों की तालिका repo के README में डालिए, हर परत की मौजूदा संख्या और runtime के साथ।

**नतीजा:** ऐसा repo जहाँ ख़ाली प्रोजेक्ट पर `npm run test:t0` 5 सेकंड से कम में चले, और कोई भी परत बजट पार करे तो CI फेल हो।

**क्या साबित होता है:** दबाव आने से पहले बंदिश जगह पर है। 2,000 मौजूदा टेस्टों पर परतें बाद में चढ़ाना एक तिमाही का काम है; पहले दिन इन्हें बनाना एक दिन का।

---

आगे: [15. Node backend →](15-tdd-node-backend-hi.md) · संबंधित: [13. अपनाने के चरण](13-adoption-phases-hi.md) · [3. अच्छे टेस्ट लिखना](03-writing-good-tests-hi.md)

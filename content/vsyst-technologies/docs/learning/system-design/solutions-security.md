# Solutions: Security Hardening

> Actionable fixes for every security problem identified in `docs/strategy/system-design.md` Section 13.4.
> Priority-ordered. Cost and effort estimated. Code snippets reference actual DZZLO-OMS files.

---

## Priority Summary

| #   | Problem                          | Effort    | Cost/month       | Priority            |
| --- | -------------------------------- | --------- | ---------------- | ------------------- |
| 1   | SSH open to 0.0.0.0/0            | 1 hour    | $0               | **P0 — do now**     |
| 2   | MongoDB Atlas open to all IPs    | 2 hours   | $0 (VPC Peering) | **P0 — do now**     |
| 3   | Rate limiting commented out      | 15 min    | $0               | **P0 — do now**     |
| 4   | API key `==` comparison          | 15 min    | $0               | **P0 — do now**     |
| 5   | OTP stored in plaintext          | 30 min    | $0               | **P0 — do now**     |
| 6   | Server starts before DB connects | 15 min    | $0               | **P0 — do now**     |
| 7   | No WAF on ALB                    | 1 hour    | ~$12             | **P1 — this month** |
| 8   | No request validation            | 2-4 hours | $0               | **P1 — this month** |
| 9   | JWT 30-day expiry, no revocation | 4-6 hours | $0               | **P1 — this month** |
| 10  | .env plaintext on disk           | 2 hours   | $0               | **P1 — this month** |
| 11  | Bus factor = 1                   | 2 hours   | $0               | **P1 — this month** |

> P0 items can all be done in a single afternoon. Total infrastructure cost increase: ~$12/month (WAF only). Everything else is free.

---

## Solution 1: Replace SSH with AWS SSM Session Manager

**Problem:** Port 22 open to 0.0.0.0/0 — anyone can attempt brute-force.
**Solution:** AWS SSM Session Manager. Shell access through AWS API. No inbound ports. Free. Full audit trail.

### Step 1: Attach IAM role to EC2

AWS Console: EC2 > Instances > Select instance > Actions > Security > Modify IAM Role

Attach managed policy: `AmazonSSMManagedInstanceCore`

### Step 2: Verify SSM Agent is running

```bash
sudo systemctl status amazon-ssm-agent
# If not running:
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
```

### Step 3: Remove SSH rule from Security Group

AWS Console: EC2 > Security Groups > Select SG > Inbound Rules > Edit > **Delete** the Port 22 / 0.0.0.0/0 rule

### Step 4: Connect from your laptop

```bash
# Install Session Manager plugin (macOS)
brew install --cask session-manager-plugin

# Connect
aws ssm start-session --target i-0abc123def456 --region ap-south-1
```

### Step 5: Enable session logging

AWS Console: Systems Manager > Session Manager > Preferences > Edit:

- CloudWatch logging: log group `/aws/ssm/sessions`
- S3 logging: bucket `dzzlo-ssm-logs`

**Cost:** $0 (SSM is free). CloudWatch logs ~$0.50/GB.
**Docs:** https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html

---

## Solution 2: VPC Peering for MongoDB Atlas

**Problem:** Atlas IP whitelist is 0.0.0.0/0 because ASG gives dynamic IPs.
**Solution:** VPC Peering whitelists the entire VPC CIDR range, not individual IPs. Dynamic IPs no longer matter.

### Option A: VPC Peering (Recommended — Free)

**Step 1: In MongoDB Atlas**

- Atlas Console > Network Access > Peering > Add Peering Connection
- Select AWS, your region (ap-south-1)
- Enter: AWS Account ID, VPC ID, VPC CIDR (e.g., `10.0.0.0/16`)
- Atlas generates a Peering Connection ID

**Step 2: In AWS Console**

- VPC > Peering Connections > Accept the pending request from Atlas
- Route Tables > Edit routes for your EC2 subnets:
  - Destination: Atlas CIDR (Atlas tells you, e.g., `192.168.248.0/21`)
  - Target: Peering Connection ID

**Step 3: Update Atlas IP Access List**

- Network Access > IP Access List > **Remove 0.0.0.0/0**
- Add your VPC CIDR: `10.0.0.0/16`

**Step 4: Update connection string**
Use the private endpoint connection string from Atlas:

```
DATABASE_URI=mongodb+srv://cluster0-pri.abcde.mongodb.net/dzzlo_oms
```

### Option B: AWS PrivateLink (More isolated, costs money)

- Atlas > Network Access > Private Endpoint > Create > AWS > Select region
- AWS > VPC > Endpoints > Create with the Atlas service name
- ~$7.50/month per AZ

**Cost:** VPC Peering is **free**. PrivateLink ~$7.50/month per AZ.
**Docs:** https://www.mongodb.com/docs/atlas/security-vpc-peering/

---

## Solution 3: Enable Rate Limiting

**Problem:** `express-rate-limit` v7.2.0 is installed but commented out at `dzzlo_oms.js:81-86`.
**Solution:** Uncomment and configure with per-endpoint limits.

### Code: `dzzlo_oms.js`

Add after `const app = express();`:

```javascript
// Trust ALB proxy so req.ip is real client IP, not ALB IP
app.set("trust proxy", 1);
```

Replace the commented-out rate limiter block:

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 100,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: "Too many requests, please try again later." },
});
app.use(limiter);
```

### Auth-specific stricter limiter

```javascript
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 10, // Only 10 login attempts per 15 min per IP
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: "Too many authentication attempts, try again later." },
});
```

Apply in `api_v/api2.js`:

```javascript
router.use("/auth", authLimiter, require("./../api_v2/routes/auth"));
```

**Cost:** $0 — already installed.
**Docs:** https://www.npmjs.com/package/express-rate-limit

---

## Solution 4: Timing-Safe API Key Comparison

**Problem:** `helpers/middlewares.js` uses `==` for API key comparison — vulnerable to timing attacks.
**Solution:** Use `crypto.timingSafeEqual`.

### Code: `helpers/middlewares.js`

Add at top:

```javascript
const crypto = require("crypto");

function timingSafeCompare(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) {
    crypto.timingSafeEqual(Buffer.from(b), Buffer.from(b));
    return false;
  }
  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
```

Replace all `==` comparisons:

```javascript
// BEFORE:
const match = API_KEY_HEADER == process.env.X_API_KEY;

// AFTER:
const match = timingSafeCompare(API_KEY_HEADER, process.env.X_API_KEY || "");
```

Apply to all three functions: `api_key_v1`, `api_key`, `api_key_v3`.

**Cost:** $0 — built into Node.js `crypto` module.
**Docs:** https://nodejs.org/api/crypto.html#cryptotimingsafeequala-b

---

## Solution 5: Hash OTP Before Storage

**Problem:** `models/users.js:203` stores OTP as plaintext. Anyone with DB read access can bypass OTP.
**Solution:** Hash with SHA-256 (same pattern as `resetPasswordToken`).

### Code: `models/users.js`

Replace `getOTPToken` method:

```javascript
UserSchema.methods.getOTPToken = function () {
  const otpPlaintext = generateOTP();
  this.OTP_Value = crypto
    .createHash("sha256")
    .update(otpPlaintext)
    .digest("hex");
  this.OTP_Expire = Date.now() + 10 * 60 * 1000;
  return otpPlaintext; // Return plaintext to send via SMS
};
```

Replace `matchOTP` method:

```javascript
UserSchema.methods.matchOTP = function (enteredOTP) {
  const hashedEntry = crypto
    .createHash("sha256")
    .update(enteredOTP)
    .digest("hex");
  return hashedEntry === this.OTP_Value;
};
```

Do the same for `order_msts.js` order OTP.

**Cost:** $0.

---

## Solution 6: Wait for DB Before Accepting Requests

**Problem:** `app.listen()` runs immediately; `mongoose.connect()` is fire-and-forget. Server accepts requests before DB is ready.
**Solution:** Export the connection promise, await it before listening.

### Code: `helpers/db_conn.js`

```javascript
const defaultConnectionPromise = mongoose
  .connect(databaseURI)
  .then(() => {
    console.log("DATABASE CONNECTED!!");
    return mongoose.connection;
  })
  .catch((err) => {
    console.error("Database connection failed:", err.message);
    throw err;
  });

module.exports = { dbDefault, db_dip, defaultConnectionPromise };
```

### Code: `dzzlo_oms.js`

```javascript
const { defaultConnectionPromise } = require("./helpers/db_conn");

// ... all middleware and route setup ...

defaultConnectionPromise
  .then(() => {
    app.listen(port, () => {
      console.log(`Server running on http://${SYSIPAddress}:${port}`);
    });
  })
  .catch((err) => {
    console.error("Failed to connect to database. Exiting.", err);
    process.exit(1);
  });
```

**Cost:** $0.

---

## Solution 7: AWS WAF on ALB

**Problem:** No protection against OWASP attacks at the edge.
**Solution:** AWS WAF with managed rule groups.

### Setup

AWS Console: WAF & Shield > Web ACLs > Create:

- Region: ap-south-1
- Resource: select your ALB

Add these managed rule groups:

| Rule Group                              | Purpose               | Cost   |
| --------------------------------------- | --------------------- | ------ |
| `AWSManagedRulesCommonRuleSet`          | OWASP Top 10          | Free\* |
| `AWSManagedRulesKnownBadInputsRuleSet`  | Log4j, known exploits | Free\* |
| `AWSManagedRulesSQLiRuleSet`            | SQL injection         | Free\* |
| `AWSManagedRulesAmazonIpReputationList` | Block known bad IPs   | Free\* |

\*Free beyond base WAF pricing.

Add a rate-based rule: 2000 requests per 5 minutes per IP → Block.

**Cost:** ~$5/month base + $1/rule + $0.60/million requests = **~$12/month total**.
**Docs:** https://docs.aws.amazon.com/waf/latest/developerguide/getting-started.html

---

## Solution 8: Input Validation with express-validator

**Problem:** express-validator installed but unused. No input validation on any endpoint.
**Solution:** Create a shared validators file, apply to routes incrementally.

### Create: `helpers/validators.js`

```javascript
const { body, param, validationResult } = require("express-validator");
const ErrorResponse = require("./ErrorResponse");

const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const messages = errors.array().map((e) => e.msg);
    return next(new ErrorResponse(messages.join(". "), 400));
  }
  next();
};

const mongoIdParam = (paramName = "id") => [
  param(paramName).isMongoId().withMessage(`Invalid ${paramName} format`),
];

const loginRules = [
  body("email").trim().notEmpty().isEmail().normalizeEmail(),
  body("password").notEmpty().isLength({ min: 6 }),
];

module.exports = { validate, mongoIdParam, loginRules };
```

### Apply to routes

```javascript
const { loginRules, validate } = require("../../helpers/validators");
router.post("/login", loginRules, validate, controller.login);
```

Start with auth routes, then expand to order creation, user creation, vouchers.

**Cost:** $0 — already installed.
**Docs:** https://express-validator.github.io/docs/guides/getting-started/

---

## Solution 9: JWT Token Revocation (Short-lived + Refresh Tokens)

**Problem:** JWT expires in 30 days with no way to revoke (fired employee keeps access).
**Solution:** Short-lived access tokens (15 min) + server-side refresh tokens with revocation.

### Step 1: Reduce JWT expiry

`.env`: `JWT_EXPIRE=15m`

### Step 2: Create refresh token model

```javascript
// models/refresh_tokens.js
const RefreshTokenSchema = new mongoose.Schema({
  user: { type: ObjectId, ref: "users", required: true },
  token: { type: String, required: true, unique: true },
  expiresAt: { type: Date, required: true, index: { expireAfterSeconds: 0 } },
  revoked: { type: Boolean, default: false },
});
```

TTL index auto-deletes expired tokens. Revoke immediately by setting `revoked: true`.

### Step 3: Issue both tokens on login

- Access token: JWT, 15-min expiry, stateless
- Refresh token: random 40-byte hex, hashed with SHA-256, stored in DB, 30-day expiry

### Step 4: Refresh endpoint

`POST /auth/refresh` — validate refresh token, rotate (revoke old, issue new pair)

### Step 5: Revoke on logout / fire employee

```javascript
await RefreshToken.updateMany({ user: userId }, { revoked: true });
```

**Cost:** $0.

---

## Solution 10: Secrets Management with AWS Parameter Store

**Problem:** `.env` files copied manually, plaintext on disk.
**Solution:** AWS Systems Manager Parameter Store (free tier).

### Store secrets

```bash
aws ssm put-parameter \
  --name "/dzzlo-oms/production/DATABASE_URI" \
  --value "mongodb+srv://..." \
  --type SecureString \
  --region ap-south-1
```

### Load at startup

```javascript
// helpers/loadSecrets.js
const {
  SSMClient,
  GetParametersByPathCommand,
} = require("@aws-sdk/client-ssm");

async function loadSecrets() {
  if (process.env.NODE_ENV === "development") return;
  const client = new SSMClient({ region: "ap-south-1" });
  const path = `/dzzlo-oms/${process.env.NODE_ENV}/`;
  const { Parameters } = await client.send(
    new GetParametersByPathCommand({ Path: path, WithDecryption: true }),
  );
  for (const param of Parameters) {
    process.env[param.Name.replace(path, "")] = param.Value;
  }
}
module.exports = loadSecrets;
```

Keep only non-secret config in `.env` files (PORT, NODE_ENV, IP_ADDRESS).

**Cost:** $0 (Standard tier free for up to 10,000 parameters).
**Docs:** https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html

---

## Solution 11: Bus Factor Reduction

**Problem:** 1 person holds all production access. Complete paralysis if unavailable.

### Immediate actions

1. **Enable MFA** on AWS root account
2. **Create IAM Identity Center** — add a second trusted person with DeveloperAccess
3. **Enable CloudTrail** — audit trail of all AWS API calls (first trail is free)
4. **Invite second person to MongoDB Atlas** org with Project Data Access Admin role
5. **Write an emergency runbook** — store in private repo:
   - AWS account ID
   - SSM connection commands
   - PM2 commands
   - MongoDB Atlas login
   - DNS provider access
   - Rollback procedure
6. **Set up billing alerts** — 120% of typical spend → email both people

**Cost:** $0.
**Docs:** https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html

---

## Files That Need Changes

| File                                | Problems Solved                           |
| ----------------------------------- | ----------------------------------------- |
| `dzzlo_oms.js`                      | #3 (rate limiting), #6 (DB before listen) |
| `helpers/middlewares.js`            | #4 (timing-safe compare)                  |
| `models/users.js`                   | #5 (OTP hashing)                          |
| `models/order_msts.js`              | #5 (order OTP hashing)                    |
| `helpers/db_conn.js`                | #6 (export connection promise)            |
| **New:** `helpers/validators.js`    | #8 (input validation)                     |
| **New:** `helpers/loadSecrets.js`   | #10 (secrets management)                  |
| **New:** `models/refresh_tokens.js` | #9 (token revocation)                     |

---

_All P0 items can be completed in one afternoon. Total ongoing cost increase: ~$12/month (WAF only)._

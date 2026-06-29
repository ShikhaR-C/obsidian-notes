# Session 4: Auth & Security

> Phase 2 — API & Security | 2 hours | Review: 15 min

## What You'll Learn

- How JWTs work, what the OWASP recommendations are, and why your 30-day non-revocable tokens are a risk
- Rate limiting patterns — from single-server to multi-server with Redis — and how to enable the rate limiter that's already installed in your codebase
- AWS security primitives that eliminate entire attack surfaces: SSM Session Manager to replace SSH, VPC Peering/PrivateLink to lock down MongoDB Atlas

## Why This Matters for DZZLO-OMS

Your security posture has several gaps that would be found in the first five minutes of a real penetration test:

1. **JWT tokens last 30 days and cannot be revoked.** If an employee is fired, their token works for up to 30 days. The only defense is the `check_user_company_status` middleware, which catches INACTIVE/REMOVED users — but that requires the admin to actually update the user's status, and it still does a MongoDB lookup on every request for every user.
2. `**api_key_v1()` allows requests with no API key at all.** It only rejects *invalid* keys — a request with no `x-api-key` header passes straight through. This was an intentional relaxation (the strict check is commented out on line 9 of `helpers/middlewares.js`), but it means any of your v1 endpoints are effectively public.
3. **API key comparison uses `==` instead of a timing-safe comparison.** All three key-check functions (`api_key`, `api_key_v1`, `api_key_v3`) compare with `==`, which is vulnerable to timing attacks. Node.js provides `crypto.timingSafeEqual()` for exactly this purpose.
4. **Rate limiting is commented out.** In `dzzlo_oms.js` (lines 81-86), the rate limiter is imported but the actual middleware is commented out. The `express-rate-limit` package (v7.2.0) is already installed. There is nothing stopping a brute-force attack on your login endpoints right now.
5. **OTP codes are stored in plaintext in MongoDB.** Both user login OTPs and order verification OTPs sit in the database as plain strings. Anyone with DB read access (or a MongoDB injection) gets every active OTP.
6. **SSH port 22 is open to 0.0.0.0/0 on EC2.** Every instance is reachable over SSH from any IP on the internet. AWS SSM Session Manager eliminates the need for SSH entirely — no open ports, no key management, full audit trail — and it's free.
7. **MongoDB Atlas is whitelisted to 0.0.0.0/0.** This was done because ASG instances get dynamic IPs, which is understandable — but VPC Peering or AWS PrivateLink solves this properly by routing traffic over a private connection.
8. **No AWS WAF on the ALB, no firewall on EC2 instances.** There is no layer filtering malicious requests before they hit your Express app.

By the end of this session, you'll understand how to fix every one of these, and you'll have actually enabled rate limiting and set up SSM Session Manager.

## Hour 1 — Concepts (60 min)

### Step 1: JWT Best Practices (20 min)

**Read:** [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

Despite the "Java" in the title, this is the OWASP reference for JWT security in any language. **Focus on these sections:**

- Token storage (where to keep JWTs on the client)
- Token expiration and revocation
- Algorithm selection and `none` algorithm attacks
- Payload content (what should and shouldn't be in the payload)

**While reading, audit your own JWT implementation in `models/users.js` (line 143):**

```js
UserSchema.methods.getSignedJwtToken = function () {
  return jwt.sign(
    {
      id: this._id,
      email: this.email,
      username: this.username,
      co_id: this.co_id,
      role: this.role,
    },
    process.env.JWT_SECRET,
    {
      expiresIn: process.env.JWT_EXPIRE,
    }
  );
};
```

**Questions to answer as you read:**

1. **Payload size:** Your JWT includes `email`, `username`, `co_id`, and `role`. Is all of this necessary in every token? What happens if a user's role changes — the old token still carries the old role for up to 30 days.
2. **Expiration:** `JWT_EXPIRE` is set to 30 days. OWASP recommends short-lived access tokens (15 min to 1 hour) plus refresh tokens. Why?
3. **Revocation:** What happens when you fire an employee today? Their token works until it expires. What are the strategies for revoking tokens?

**Token revocation strategies to understand:**


| Strategy                           | How it works                                                                                          | Tradeoff                                                                     |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Short-lived access + refresh token | Access token expires in 15 min; refresh token gets a new one. Revoke the refresh token to cut access. | More complexity, but standard practice.                                      |
| Token blocklist (Redis)            | On logout/revoke, add the token's `jti` to a Redis set. Check on every request.                       | Extra Redis lookup per request, but simple.                                  |
| Token version in DB                | Store a `tokenVersion` on the user. Increment on revoke. Reject tokens with old version.              | DB lookup per request (you already do this via `check_user_company_status`). |
| Short expiry + no revocation       | Set tokens to 15-30 min. If someone is fired, their token dies quickly on its own.                    | Simplest. Acceptable for your scale.                                         |


**For DZZLO-OMS, the pragmatic fix is:** Reduce `JWT_EXPIRE` to 1-2 hours and implement a refresh token endpoint. Alternatively, since `check_user_company_status` already queries the DB on every request, you could add a `tokenVersion` check there with near-zero additional cost.

**Also read:** [Node.js Security Best Practices](https://nodejs.org/learn/getting-started/security-best-practices) — skim the sections on authentication and secret management.

### Step 2: Rate Limiting Patterns (20 min)

**Read:** [MDN: Securing APIs with express-rate-limit](https://developer.mozilla.org/en-US/blog/securing-apis-express-rate-limit-and-slow-down/)

This walks through exactly the library you already have installed. **Focus on:**

- Window-based rate limiting (fixed window vs. sliding window)
- Per-endpoint vs. global rate limits
- Custom key generators (rate limit by IP, by user, by API key)
- Response headers (`RateLimit-`*)

**Then read the docs:** [express-rate-limit npm](https://www.npmjs.com/package/express-rate-limit)

Pay attention to the `store` option. By default, `express-rate-limit` uses an in-memory store. This means:

- If you have 2 EC2 instances behind your ALB, each has its own counter. A client can make 100 requests to instance A *and* 100 to instance B.
- If the process restarts (PM2 restart, deploy), all counters reset to zero.

For multi-server deployments, you need a shared store. The standard choice is `rate-limit-redis` with ElastiCache. But at your current scale (1-2 instances), in-memory is fine to start.

**Your existing commented-out code in `dzzlo_oms.js` (line 81):**

```js
// // Rate limiting
// const limiter = rateLimit({
//   windowMs: 10 * 60 * 1000, // 10 minutes
//   max: 100,
// });
// app.use(limiter);
```

This applies a blanket 100-requests-per-10-minutes limit globally. That's a reasonable starting point, but you should also have stricter per-endpoint limits:


| Endpoint                      | Suggested limit       | Why                             |
| ----------------------------- | --------------------- | ------------------------------- |
| `/auth/loginrx`               | 5 per 15 min per IP   | Brute-force password protection |
| `/auth/loginCredentialVerify` | 5 per 15 min per IP   | Same — OTP request              |
| `/auth/loginOTP`              | 5 per 15 min per IP   | OTP verification                |
| Global (all routes)           | 100 per 10 min per IP | General abuse prevention        |


**Also read:** [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html) — the rate limiting section and the general recommendations.

### Step 3: AWS Security (20 min)

**Read:** [AWS SSM Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) — read the overview and "How it works" sections.

**Then read:** [Session Manager: Replacing SSH](https://cloudkiln.com/blog/session-manager-guide) — a practical guide to setting it up.

**Key insight:** SSM Session Manager gives you shell access to EC2 instances *without opening port 22*. Instead:

- The SSM Agent (pre-installed on Amazon Linux 2/2023) creates an outbound connection to the SSM service
- You connect through the AWS Console or CLI (`aws ssm start-session --target i-xxx`)
- All sessions are logged in CloudTrail
- No SSH keys to manage, rotate, or lose
- No security group rule for port 22 needed at all

**This directly solves your "SSH port 22 open to 0.0.0.0/0" problem** and is strictly better in every dimension: more secure, easier to manage, full audit trail, and free.

**For MongoDB Atlas network access, read:**

- [MongoDB Atlas VPC Peering](https://www.mongodb.com/docs/atlas/security-vpc-peering/)
- [MongoDB Atlas Private Endpoints](https://www.mongodb.com/docs/atlas/security-private-endpoint/)

These solve the "0.0.0.0/0 whitelist" problem:


| Approach        | How it works                                                                                               | Cost                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| VPC Peering     | Creates a private network link between your AWS VPC and Atlas's VPC. Traffic never touches the internet.   | Free (standard AWS data transfer charges apply) |
| AWS PrivateLink | Creates an endpoint in your VPC that routes to Atlas over AWS's backbone. Even more isolated than peering. | ~$7.50/month per endpoint + data transfer       |


With either approach, you remove the 0.0.0.0/0 whitelist from Atlas and only allow connections from your VPC. ASG instances get dynamic IPs, but that doesn't matter — the peering/endpoint works at the VPC level, not the IP level.

**Also read:** [AWS WAF Getting Started](https://docs.aws.amazon.com/waf/latest/developerguide/getting-started.html) — understand what WAF can block (SQL injection patterns, rate limiting at the edge, geo-blocking, bot detection) and what it costs (~$5/month base + $1/rule + $0.60 per million requests). For your traffic volume, this is under $10/month.

## Hour 2 — Hands-On (60 min)

### Step 4: Penetration Test Your Own API (20 min)

Run these tests against your local dev server or a staging environment. **Never run these against production without authorization.**

Start your local server, then test each vulnerability:

**Test 1: Brute-force login (no rate limiting)**

```bash
# Try 20 rapid login attempts — all should succeed (no 429 response)
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5000/api/v3/auth/loginrx \
    -H "Content-Type: application/json" \
    -H "x-api-key: YOUR_DEV_KEY" \
    -d '{"email":"wrong@test.com","password":"wrongpassword"}' &
done
wait
echo ""
# Expected: all 20 return 401 (unauthorized), none return 429 (rate limited)
# This proves: no rate limiting is active
```

**Test 2: Request with no API key (api_key_v1 bypass)**

```bash
# Send a request with NO x-api-key header to a v1-protected endpoint
curl -v http://localhost:5000/api/v1/some-endpoint \
  -H "Content-Type: application/json"
# Expected: request goes through (not blocked)
# This proves: api_key_v1() allows keyless requests
```

**Test 3: Expired/tampered JWT**

```bash
# Take a valid JWT and modify one character in the payload
# (change a letter in the middle section between the two dots)
TAMPERED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.TAMPERED.signature"
curl -v http://localhost:5000/api/v3/some-protected-route \
  -H "Authorization: Bearer $TAMPERED_TOKEN" \
  -H "x-api-key: YOUR_DEV_KEY"
# Expected: 401 — this SHOULD fail (and it does, jwt.verify catches it)
# Good: your JWT verification is sound
```

**Test 4: Valid JWT, wrong co_id in request body**

```bash
# Log in as user in company A, then try to access company B's data
# by sending co_id of company B in the request
curl -v http://localhost:5000/api/v3/orders \
  -H "Authorization: Bearer $TOKEN_FOR_COMPANY_A" \
  -H "x-api-key: YOUR_DEV_KEY" \
  -H "Content-Type: application/json" \
  -d '{"co_id":"COMPANY_B_ID"}'
# Check: does the API use co_id from the JWT or from the request body?
# If it uses the body value, that's an authorization bypass (BOLA/IDOR)
```

**Write down what you found.** Which tests passed (vulnerability confirmed)? Which failed (protection exists)?

### Step 5: Enable Rate Limiting on /auth/login (20 min)

This is the highest-impact, lowest-effort security fix you can make. The package is installed, the import exists — you just need to uncomment and configure.

**Step 5a: Uncomment the global rate limiter**

In `dzzlo_oms.js`, uncomment lines 81-86:

```js
// Rate limiting
const limiter = rateLimit({
  windowMs: 10 * 60 * 1000, // 10 minutes
  max: 100,
});
app.use(limiter);
```

**Step 5b: Add a strict limiter for auth endpoints**

In your auth route files (e.g., `api_v3/routes/auth/index.js` or wherever the login routes are defined), add a per-endpoint limiter:

```js
const rateLimit = require("express-rate-limit");

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: "Too many login attempts. Please try again after 15 minutes.",
  },
});

// Apply to login routes
router.post("/loginrx", authLimiter, loginrx);
router.post("/loginCredentialVerify", authLimiter, loginCredentialVerify);
router.post("/loginOTP", authLimiter, loginOTP);
```

**Step 5c: Test it**

```bash
# After enabling, try the brute-force test again
for i in $(seq 1 10); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    http://localhost:5000/api/v3/auth/loginrx \
    -H "Content-Type: application/json" \
    -H "x-api-key: YOUR_DEV_KEY" \
    -d '{"email":"wrong@test.com","password":"wrongpassword"}')
  echo "Attempt $i: $STATUS"
done
# Expected: first 5 return 401, attempts 6-10 return 429
```

**Step 5d: Verify the contact_email limiter still works**

Your `api_v2/routes/open_apis/contact_email.js` and `api_v3/routes/open_apis/contact_email.js` already have rate limiting applied correctly. Check that they're using the same pattern you just implemented.

**Reference:** [express-rate-limit npm](https://www.npmjs.com/package/express-rate-limit) for additional configuration options (custom key generators, skip functions, etc.).

### Step 6: Set Up AWS SSM Session Manager (20 min)

Follow these steps to replace SSH access entirely. There is no additional AWS cost for Session Manager.

**Reference:** [SSM Session Manager Docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) and [Session Manager Replacing SSH](https://cloudkiln.com/blog/session-manager-guide)

**Step 6a: Verify the SSM Agent is running on your EC2 instances**

```bash
# SSH into your instance one last time
ssh ec2-user@your-instance

# Check SSM Agent status
sudo systemctl status amazon-ssm-agent
# Expected: active (running)
# If not running:
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
```

On Amazon Linux 2 and Amazon Linux 2023, the SSM Agent comes pre-installed. If you're on Ubuntu, you may need to install it.

**Step 6b: Create an IAM role with SSM permissions**

Your EC2 instances need an instance profile with the `AmazonSSMManagedInstanceCore` policy. If your instances already have an IAM role, add this managed policy to it:

```bash
aws iam attach-role-policy \
  --role-name YourEC2Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
```

If your instances don't have an IAM role, create one:

```bash
# Create the role
aws iam create-role \
  --role-name DZZLO-EC2-SSM \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach SSM policy
aws iam attach-role-policy \
  --role-name DZZLO-EC2-SSM \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create instance profile and attach role
aws iam create-instance-profile --instance-profile-name DZZLO-EC2-SSM
aws iam add-role-to-instance-profile \
  --instance-profile-name DZZLO-EC2-SSM \
  --role-name DZZLO-EC2-SSM

# Associate with your instance (replace instance ID)
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --iam-instance-profile Name=DZZLO-EC2-SSM
```

**Step 6c: Install the Session Manager plugin locally**

```bash
# macOS
brew install --cask session-manager-plugin

# Verify
session-manager-plugin --version
```

**Step 6d: Connect without SSH**

```bash
# Find your instance ID
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*dzzlo*" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text

# Start a session
aws ssm start-session --target i-xxxxxxxxxxxxxxxxx
```

You now have shell access without SSH. The session is logged in CloudTrail.

**Step 6e: Remove SSH access from security groups**

Once you've confirmed SSM works:

```bash
# Remove the SSH rule (replace sg-xxx with your security group ID)
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxxxxxxxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

Port 22 is now closed. No more SSH keys to manage. No more attack surface.

## 15-Minute Review

### What You Should Now Understand

- Why 30-day non-revocable JWTs are a risk and what the alternatives are
- How `api_key_v1()` allows keyless requests and why `==` comparison is insecure
- How rate limiting works (fixed window, per-endpoint, shared store for multi-server)
- How SSM Session Manager replaces SSH entirely
- How VPC Peering / PrivateLink eliminates the MongoDB Atlas 0.0.0.0/0 whitelist

### Prioritized Security Fixes for DZZLO-OMS

Ranked by risk severity and implementation effort:


| Priority | Fix                                                                | Risk Eliminated                               | Effort  | Do This             |
| -------- | ------------------------------------------------------------------ | --------------------------------------------- | ------- | ------------------- |
| **P0**   | Enable rate limiting (uncomment + per-endpoint)                    | Brute-force login, API abuse                  | 30 min  | This session        |
| **P0**   | Set up SSM Session Manager, close port 22                          | SSH-based attacks on all instances            | 1 hour  | This session        |
| **P1**   | Replace `==` with `crypto.timingSafeEqual()` in all API key checks | Timing attack on API keys                     | 15 min  | This week           |
| **P1**   | Fix `api_key_v1()` to reject empty API keys                        | Unauthenticated access to v1 endpoints        | 10 min  | This week           |
| **P1**   | Reduce JWT expiry to 2 hours, add refresh token endpoint           | Fired employee access, stolen token window    | 4 hours | This week           |
| **P2**   | Hash OTPs before storing in DB (`crypto.createHash('sha256')`)     | OTP exposure via DB access                    | 1 hour  | Next week           |
| **P2**   | Set up VPC Peering for MongoDB Atlas                               | DB accessible from entire internet            | 2 hours | Next week           |
| **P2**   | Add AWS WAF to ALB                                                 | SQL injection, bot traffic, geo-based attacks | 1 hour  | Next week           |
| **P3**   | Add firewall rules (UFW or iptables) on EC2 instances              | Defense-in-depth for instance-level access    | 30 min  | Next sprint         |
| **P3**   | Implement token blocklist in Redis for immediate revocation        | Instant token revocation on user deactivation | 3 hours | When Redis is added |


### Key Takeaway

The two highest-impact fixes — rate limiting and SSM Session Manager — are both effectively free and can be done today. Rate limiting is literally uncommenting code. SSM is a 15-minute setup that eliminates an entire attack vector. Do these before moving to the next session.

## Resources


| Resource                                                                                                                               | Section                            |
| -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)                       | JWT security best practices        |
| [OWASP Node.js Security](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)                              | Node.js-specific security guidance |
| [Node.js Security Best Practices](https://nodejs.org/learn/getting-started/security-best-practices)                                    | Official Node.js security docs     |
| [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)                                       | Express-specific hardening         |
| [express-rate-limit npm](https://www.npmjs.com/package/express-rate-limit)                                                             | Rate limiting library docs         |
| [MDN: Securing APIs with express-rate-limit](https://developer.mozilla.org/en-US/blog/securing-apis-express-rate-limit-and-slow-down/) | Practical rate limiting guide      |
| [AWS SSM Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)                           | Official SSM docs                  |
| [Session Manager: Replacing SSH](https://cloudkiln.com/blog/session-manager-guide)                                                     | Practical SSM setup guide          |
| [MongoDB Atlas VPC Peering](https://www.mongodb.com/docs/atlas/security-vpc-peering/)                                                  | Private network for Atlas          |
| [MongoDB Atlas Private Endpoints](https://www.mongodb.com/docs/atlas/security-private-endpoint/)                                       | AWS PrivateLink for Atlas          |
| [AWS WAF Getting Started](https://docs.aws.amazon.com/waf/latest/developerguide/getting-started.html)                                  | WAF setup and rule creation        |


---

*Next session: [05-caching.md](./05-caching.md) — Cache patterns, Redis/ElastiCache, when caching is worth it*
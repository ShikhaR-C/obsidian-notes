# Session 12: VPC & Network Architecture

> Phase 6 — Deep Dives | 2 hours | Review: 15 min

## What You'll Learn

- What a VPC is and why it matters (explained for a developer, not a network engineer)
- Your current network setup and why everything is "open"
- How to secure MongoDB Atlas with VPC Peering (solves the 0.0.0.0/0 problem)
- The ideal DZZLO-OMS network architecture
- AWS SSM Session Manager as SSH replacement

## Why This Matters for DZZLO-OMS

Your MongoDB Atlas is whitelisted to **all IPs** (0.0.0.0/0). Your SSH is open to **all IPs**. If your database credentials leak, anyone on the internet can connect. VPC Peering solves this by creating a private tunnel between your EC2s and Atlas — no public internet involved.

---

## Hour 1 — Concepts (60 min)

### Step 1: What is a VPC? (15 min)

**Analogy:** A VPC is your own private floor in AWS's building.

- The building (AWS region, e.g., ap-south-1 Mumbai) has many floors
- Your floor (VPC) has its own rooms (subnets), doors (security groups), and hallways (route tables)
- You control who enters each room, which rooms connect to each other, and which rooms have windows to the outside (internet access)

**Your EC2 instances are already in a VPC** — the default VPC that AWS created when you first launched EC2. You just never customized it.

**Key VPC components:**

```
VPC (10.0.0.0/16 = your private floor, 65,536 IP addresses)
│
├── Public Subnet (10.0.1.0/24 = room with a window to the internet)
│   └── Your EC2s live here currently (default setup)
│   └── Internet Gateway attached (door to the internet)
│
├── Private Subnet (10.0.2.0/24 = room with NO window)
│   └── Where your EC2s SHOULD live
│   └── No direct internet access
│   └── Uses NAT Gateway for outbound-only internet
│
├── Security Groups (door guards for each room)
│   └── Currently: ports 22, 80, 443, 465 open to 0.0.0.0/0
│
├── Route Tables (hallway signs saying "this way to the internet")
│   └── Public subnet → Internet Gateway
│   └── Private subnet → NAT Gateway
│
└── Internet Gateway (the building's front door)
```

### Step 2: Your Current Setup — Why Everything is Open (15 min)

**What AWS created by default:**

```
                    INTERNET
                       │
                       ▼
              Internet Gateway
                       │
                       ▼
        ┌──────────────────────────────┐
        │     DEFAULT VPC (public)      │
        │                               │
        │  ┌─────────┐  ┌─────────┐    │
        │  │ EC2      │  │ EC2      │   │
        │  │ t3.small │  │ t3.micro │   │
        │  │ Public IP│  │ Public IP│   │
        │  └────┬─────┘  └────┬─────┘  │
        │       │              │        │
        │  Security Group:              │
        │  Port 22  → 0.0.0.0/0  ⚠️    │
        │  Port 80  → 0.0.0.0/0        │
        │  Port 443 → 0.0.0.0/0        │
        │  Port 465 → 0.0.0.0/0        │
        └──────────────────────────────┘
                       │
                       │ PUBLIC INTERNET
                       ▼
              MongoDB Atlas (0.0.0.0/0 whitelisted) ⚠️
```

**Problems:**

1. EC2s have public IPs — directly reachable from internet
2. SSH open to all — anyone can try to brute-force
3. MongoDB Atlas open to all — if credentials leak, game over
4. No network-level isolation — everything in one flat network

### Step 3: The Ideal Architecture (15 min)

```
                    INTERNET
                       │
                       ▼
              ┌─────────────────┐
              │  AWS CloudFront  │  (CDN, DDoS protection)
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │    AWS ALB       │  ← Public subnet
              │  (HTTPS only)   │
              └────────┬────────┘
                       │ (port 8030 only)
        ┌──────────────▼───────────────┐
        │       PRIVATE SUBNET          │
        │                               │
        │  ┌─────────┐  ┌─────────┐    │
        │  │ EC2      │  │ EC2      │   │
        │  │ t3.small │  │ t3.micro │   │
        │  │ NO public│  │ NO public│   │
        │  │ IP       │  │ IP       │   │
        │  └─────────┘  └─────────┘    │
        │                               │
        │  Security Group:              │
        │  Port 8030 → ALB SG only      │
        │  Port 443  → SSM VPC endpoint │
        │  No SSH (port 22 closed)      │
        │                               │
        │  ┌─────────────────────┐      │
        │  │ NAT Gateway         │      │ ← For outbound internet
        │  │ (npm, 2Factor, etc) │      │   (EC2s can call APIs but
        │  └─────────────────────┘      │    can't be reached from internet)
        │                               │
        │  ┌─────────────────────┐      │
        │  │ SSM VPC Endpoints   │      │ ← Shell access without SSH
        │  └─────────────────────┘      │
        └──────────────┬───────────────┘
                       │
                  VPC Peering  ← Private tunnel, no internet
                       │
              ┌────────▼────────┐
              │ MongoDB Atlas    │
              │ IP whitelist:    │
              │ 10.0.0.0/16     │  ← Only your VPC, not 0.0.0.0/0
              │ (your VPC CIDR)  │
              └─────────────────┘
```

### Step 4: VPC Peering with MongoDB Atlas (15 min)

**Why VPC Peering solves the dynamic IP problem:**

- ASG launches new EC2 → gets IP from your VPC subnet (e.g., 10.0.2.47)
- Atlas whitelist allows entire VPC CIDR (10.0.0.0/16)
- Any IP within your VPC is automatically allowed
- No need to whitelist individual IPs

**Step-by-step:**

1. **Atlas Console** → Network Access → Peering → Add Peering Connection
   - Cloud Provider: AWS
   - Region: ap-south-1
   - Your AWS Account ID, VPC ID, VPC CIDR

2. **AWS Console** → VPC → Peering Connections → Accept request from Atlas

3. **AWS Console** → Route Tables → Edit routes for your subnets:
   - Destination: Atlas CIDR (Atlas tells you, e.g., `192.168.248.0/21`)
   - Target: Peering Connection ID

4. **Atlas Console** → Network Access → IP Access List:
   - **Remove** 0.0.0.0/0
   - **Add** your VPC CIDR (e.g., 10.0.0.0/16)

5. **Update connection string** to private endpoint URL from Atlas

**Cost:** VPC Peering is **free** (same region). Cross-region: ~$0.01/GB.

---

## Hour 2 — Hands-On (60 min)

### Step 5: Set Up VPC Peering (30 min)

Follow the step-by-step above in your AWS Console + Atlas Console. This is the single highest-impact security improvement you can make.

### Step 6: Set Up SSM Session Manager (15 min)

Replace SSH entirely:

1. **Attach IAM role** to EC2 with policy `AmazonSSMManagedInstanceCore`
2. **Verify SSM agent**: `sudo systemctl status amazon-ssm-agent`
3. **Install plugin locally**: `brew install --cask session-manager-plugin`
4. **Connect**: `aws ssm start-session --target i-XXXXX --region ap-south-1`
5. **Remove port 22** from Security Group

**Cost:** $0.

### Step 7: Security Group Lockdown (15 min)

**Current (too open):**

| Port | Source    | Status                     |
| ---- | --------- | -------------------------- |
| 22   | 0.0.0.0/0 | Remove entirely (use SSM)  |
| 80   | 0.0.0.0/0 | Remove (ALB handles HTTP)  |
| 443  | 0.0.0.0/0 | Remove (ALB handles HTTPS) |
| 465  | 0.0.0.0/0 | Keep (outbound SMTP)       |

**Target (locked down):**

| Port | Source                 | Purpose                                |
| ---- | ---------------------- | -------------------------------------- |
| 8030 | ALB Security Group     | App traffic from ALB only              |
| 443  | VPC CIDR (10.0.0.0/16) | SSM VPC endpoints                      |
| 465  | 0.0.0.0/0              | Outbound SMTP (or restrict to SES IPs) |

---

## 15-Minute Review

1. Is VPC Peering set up? Can you remove 0.0.0.0/0 from Atlas?
2. Is SSM working? Can you close port 22?
3. Are Security Groups locked down to ALB-only for app traffic?
4. **Cost check:** VPC Peering = $0. SSM = $0. NAT Gateway = ~$32/month (needed only if moving to private subnet). Decision: is private subnet worth $32/month now?

## Resources

| Resource                      | URL                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| AWS VPC User Guide            | https://docs.aws.amazon.com/vpc/latest/userguide/                                    |
| MongoDB Atlas VPC Peering     | https://www.mongodb.com/docs/atlas/security-vpc-peering/                             |
| MongoDB Atlas PrivateLink     | https://www.mongodb.com/docs/atlas/security-private-endpoint/                        |
| AWS SSM Session Manager       | https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html    |
| SSM replacing SSH             | https://cloudkiln.com/blog/session-manager-guide                                     |
| VPC Peering Guide (community) | https://dev.to/techprane/secure-your-mongodb-atlas-cluster-with-aws-vpc-peering-5ejn |

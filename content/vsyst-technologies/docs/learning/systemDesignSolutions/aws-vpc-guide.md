# AWS VPC Deep Dive for DZZLO-OMS

> Written for a Node.js developer who has never configured networking.
> Uses DZZLO-OMS (EC2 + ALB + MongoDB Atlas) as the running example throughout.

---

## Table of Contents

1. [What is a VPC](#1-what-is-a-vpc)
2. [VPC Components Explained](#2-vpc-components-explained)
3. [Your Current VPC Setup](#3-your-current-vpc-setup-what-aws-gave-you-by-default)
4. [Security Groups Deep Dive](#4-security-groups-deep-dive)
5. [Private Subnets for EC2](#5-private-subnets-for-ec2)
6. [VPC Peering with MongoDB Atlas](#6-vpc-peering-with-mongodb-atlas)
7. [AWS PrivateLink for MongoDB Atlas](#7-aws-privatelink-for-mongodb-atlas)
8. [VPC for ASG (Auto Scaling Group)](#8-vpc-for-asg--auto-scaling-group)
9. [VPC Flow Logs](#9-vpc-flow-logs)
10. [Target Network Architecture](#10-target-network-architecture)
11. [Cost of VPC Improvements](#11-cost-of-vpc-improvements)
12. [Step-by-Step Migration Plan](#12-step-by-step-migration-plan)

---

## 1. What is a VPC

### The Analogy

Think of AWS as a massive office complex with millions of rooms. When you launched your EC2 instances, you rented two rooms in this complex. But you did not build any walls, doors, locks, or hallways. You just said "give me two rooms" and AWS said "sure, here you go" and put them in a shared open-plan floor.

A **VPC (Virtual Private Cloud)** is like getting your own private floor in that office building. You decide:

- How many rooms (subnets) to create
- Which rooms face the street (public subnets) and which are internal-only (private subnets)
- Who can enter through the front door (Internet Gateway)
- What security badge is needed to enter each room (Security Groups)
- What the hallway layout looks like between rooms (Route Tables)

**The key insight: Your EC2 instances ARE already in a VPC.** AWS created one for you automatically --- the "default VPC." The problem is that this default VPC is configured for convenience, not security. It is like a floor plan where every door is unlocked and every window faces the street.

### What Problem Does It Solve?

Without a VPC, your servers sit on the raw internet like a house with no fence, no walls, and no locks. Anyone who knows the address can walk up and try every door.

With a properly configured VPC:

- Your EC2 instances are invisible from the internet (private subnet)
- Only the ALB is exposed (public subnet)
- MongoDB Atlas traffic never touches the public internet (VPC Peering)
- SSH is not needed because you manage instances through AWS SSM (Systems Manager)
- Every packet in and out is logged (VPC Flow Logs)

### Your Current Situation

```
CURRENT (insecure):

    Internet ──────────► ALB ──────────► EC2 (public subnet)
       │                                    │
       │ SSH (port 22) from ANYWHERE        │ MongoDB connection
       └────────────────────────────────────┘ over PUBLIC INTERNET
                                              (Atlas allows 0.0.0.0/0)

WHAT IT SHOULD LOOK LIKE:

    Internet ──► ALB (public subnet) ──► EC2 (PRIVATE subnet)
                                           │
                                           │ VPC Peering (private network)
                                           │
                                        MongoDB Atlas
                                        (only allows YOUR VPC CIDR)
```

### Worth Doing Now vs Later?

**NOW.** The 0.0.0.0/0 MongoDB Atlas whitelist and open SSH are critical security risks. If someone compromises your MongoDB connection string (from leaked `.env`, logs, or a dependency vulnerability), they can connect to your database from anywhere on Earth.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html

---

## 2. VPC Components Explained

Every VPC component explained using your DZZLO-OMS setup as the example.

### 2.1 VPC Itself

The VPC is a virtual network. When you create one, you pick a CIDR block --- a range of private IP addresses.

```
Your VPC CIDR: 10.0.0.0/16
This means:  10.0.0.0 → 10.0.255.255
That's:      65,536 IP addresses for your stuff
```

Think of the CIDR as the square footage of your private floor. `/16` gives you a huge floor. `/24` gives you a small one (256 IPs). For most setups, `/16` is the right choice.

### 2.2 Subnets (Public vs Private)

Subnets are rooms on your floor. You divide your VPC into subnets, each with a slice of the IP range.

```
VPC: 10.0.0.0/16
│
├── Public Subnet A:   10.0.1.0/24  (256 IPs) ← AZ us-east-1a
│   └── ALB lives here
│   └── NAT Gateway lives here
│
├── Public Subnet B:   10.0.2.0/24  (256 IPs) ← AZ us-east-1b
│   └── ALB lives here too (ALB needs 2+ AZs)
│
├── Private Subnet A:  10.0.10.0/24 (256 IPs) ← AZ us-east-1a
│   └── EC2 instance 1 lives here
│
└── Private Subnet B:  10.0.20.0/24 (256 IPs) ← AZ us-east-1b
    └── EC2 instance 2 lives here
```

**What makes a subnet "public" or "private"?**

It is NOT a setting you toggle. A subnet is public if its route table has a route to an Internet Gateway. A subnet is private if it does NOT.

|                                    | Public Subnet                   | Private Subnet                       |
| ---------------------------------- | ------------------------------- | ------------------------------------ |
| Can receive traffic from internet? | Yes                             | No                                   |
| Can initiate traffic to internet?  | Yes                             | Yes (via NAT Gateway)                |
| Gets public IP on instance launch? | Optional (usually yes)          | No                                   |
| Use case                           | ALB, NAT Gateway, bastion hosts | Application servers (EC2), databases |

### 2.3 Internet Gateway (IGW)

The front door of your building. Exactly one per VPC. It allows traffic to flow between your VPC and the public internet.

```
Internet ◄──── IGW ────► Public Subnets
                              │
                         (no direct path to private subnets)
```

Without an IGW, nothing in your VPC can reach the internet and nothing from the internet can reach your VPC.

### 2.4 NAT Gateway

A one-way mirror door. It lets instances in private subnets initiate outbound connections to the internet (to download npm packages, call external APIs, send emails via port 465, etc.) but it does NOT allow inbound connections from the internet.

```
Private Subnet EC2 ──► NAT Gateway (in public subnet) ──► IGW ──► Internet
                                                                  (npm, Atlas*, SMTP)
             ✗ Internet CANNOT initiate a connection back through the NAT
```

\*Atlas traffic goes over the internet only if you do not set up VPC Peering. With peering, Atlas traffic stays on the private network.

**Cost:** ~$0.045/hour (~$32/month) + $0.045/GB data processed. This is the most expensive component of a proper VPC setup.

### 2.5 Route Tables

Route tables are the hallway signs telling traffic where to go. Every subnet is associated with one route table.

**Public Subnet Route Table:**

```
Destination         Target
10.0.0.0/16         local            (traffic within VPC stays in VPC)
0.0.0.0/0           igw-xxxxxxx      (everything else → Internet Gateway)
```

**Private Subnet Route Table:**

```
Destination         Target
10.0.0.0/16         local            (traffic within VPC stays in VPC)
0.0.0.0/0           nat-xxxxxxx      (everything else → NAT Gateway)
192.168.248.0/21    pcx-xxxxxxx      (Atlas CIDR → VPC Peering connection)
```

The Atlas line is added when you set up VPC Peering (covered in Section 6).

### 2.6 Security Groups vs NACLs

Two layers of firewall. Think of it like this:

|              | Security Group                                                                        | NACL (Network ACL)                                                    |
| ------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Analogy      | Lock on a room door                                                                   | Security guard at the hallway entrance                                |
| Level        | Instance-level (attached to EC2, ALB, etc.)                                           | Subnet-level (applies to everything in the subnet)                    |
| Rules        | Allow only (implicit deny)                                                            | Allow AND Deny explicitly                                             |
| Statefulness | **Stateful** --- if you allow inbound, the response is automatically allowed outbound | **Stateless** --- you must explicitly allow both inbound AND outbound |
| Typical use  | Primary firewall (you use this 95% of the time)                                       | Defense-in-depth (secondary layer, or to block specific IPs)          |

**For DZZLO-OMS, you will primarily work with Security Groups.** NACLs are useful as an extra layer, but security groups are the main tool.

### Component Interaction Diagram

```
┌─────────────────── YOUR VPC (10.0.0.0/16) ───────────────────┐
│                                                                │
│   ┌─── Public Subnet A (10.0.1.0/24) ──────────────────┐     │
│   │                                                      │     │
│   │   ┌─────────┐         ┌──────────────┐              │     │
│   │   │   ALB   │         │ NAT Gateway  │              │     │
│   │   │ (SG-alb)│         │              │              │     │
│   │   └────┬────┘         └──────┬───────┘              │     │
│   │        │                     │                       │     │
│   │   Route Table: 0.0.0.0/0 → igw-xxx                  │     │
│   └────────┼─────────────────────┼───────────────────────┘     │
│            │                     ▲                              │
│            │ port 8030           │ outbound internet            │
│            ▼                     │                              │
│   ┌─── Private Subnet A (10.0.10.0/24) ─────────────────┐    │
│   │                                                       │    │
│   │   ┌──────────┐                                        │    │
│   │   │   EC2    │ ──── outbound to NAT ─────────────────┼───►│
│   │   │(SG-app)  │                                        │    │
│   │   └──────────┘                                        │    │
│   │                                                       │    │
│   │   Route Table: 0.0.0.0/0 → nat-xxx                   │    │
│   │                192.168.248.0/21 → pcx-xxx (Atlas)     │    │
│   └───────────────────────────────────────────────────────┘    │
│                                                                │
│   Internet Gateway (igw-xxx) ◄──────────► Internet             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                          │
                    VPC Peering (pcx-xxx)
                          │
                          ▼
              ┌─────────────────────┐
              │   MongoDB Atlas VPC  │
              │   192.168.248.0/21   │
              └─────────────────────┘
```

### Worth Doing Now vs Later?

Understanding these components is necessary NOW because every section that follows builds on them. There is no action item here --- this is the vocabulary.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-subnets-commands.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html

---

## 3. Your Current VPC Setup (What AWS Gave You by Default)

When you created your AWS account, AWS automatically created a "default VPC" in every region. When you launched your EC2 instances, they went into this default VPC because you did not specify otherwise.

### What the Default VPC Looks Like

```
Default VPC: 172.31.0.0/16
│
├── Default Subnet in AZ-a:  172.31.0.0/20   (4,096 IPs)  ← PUBLIC
├── Default Subnet in AZ-b:  172.31.16.0/20  (4,096 IPs)  ← PUBLIC
├── Default Subnet in AZ-c:  172.31.32.0/20  (4,096 IPs)  ← PUBLIC
│
├── Internet Gateway: attached automatically
├── Route Table: 0.0.0.0/0 → igw (everything is routed to internet)
└── Default Security Group: allows all outbound, allows all inbound FROM ITSELF
```

**Key problem: Every subnet in the default VPC is public.** Every EC2 instance gets a public IP by default. There are no private subnets.

### What This Means for DZZLO-OMS Right Now

```
┌─── Default VPC (172.31.0.0/16) ───────────────────────────────┐
│                                                                 │
│   EVERYTHING is in public subnets:                              │
│                                                                 │
│   ┌──────┐   ┌──────┐   ┌──────┐                              │
│   │ EC2  │   │ EC2  │   │ ALB  │    All have public IPs        │
│   │ :22  │   │ :22  │   │:80/443│   All reachable from internet│
│   │ :8030│   │ :8030│   │      │                               │
│   └──┬───┘   └──┬───┘   └──────┘                              │
│      │          │                                               │
│   Security Group:                                               │
│     Inbound: 22 (0.0.0.0/0) ← SSH from ANYWHERE               │
│     Inbound: 80 (0.0.0.0/0) ← HTTP from ANYWHERE              │
│     Inbound: 443 (0.0.0.0/0) ← HTTPS from ANYWHERE            │
│     Inbound: 465 (0.0.0.0/0) ← SMTP from ANYWHERE             │
│     Inbound: 8030 (0.0.0.0/0) ← Node.js from ANYWHERE         │
│     Outbound: ALL (0.0.0.0/0)                                  │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    PUBLIC INTERNET
                         │
                         ▼
              ┌─────────────────────┐
              │   MongoDB Atlas      │
              │   Whitelist: 0.0.0.0/0 ← ANYONE CAN CONNECT  │
              └─────────────────────┘
```

### How to See Your Current Setup

**AWS Console steps:**

1. Go to **VPC Dashboard** (https://console.aws.amazon.com/vpc/)
2. Click **Your VPCs** --- you will see one VPC with "Default VPC: Yes"
3. Click **Subnets** --- you will see 2-3 subnets, all with "Auto-assign public IP: Yes"
4. Click **Route Tables** --- you will see one route table with `0.0.0.0/0 → igw-xxx`
5. Click **Internet Gateways** --- you will see one, attached to your default VPC

**AWS CLI:**

```bash
# See your default VPC
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"

# See subnets in default VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-YOUR_ID"

# See route tables
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-YOUR_ID"

# See security groups
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=vpc-YOUR_ID"
```

### The Specific Security Problems

| Problem                             | Risk Level   | What Could Happen                                                                                                 |
| ----------------------------------- | ------------ | ----------------------------------------------------------------------------------------------------------------- |
| SSH open to 0.0.0.0/0               | **CRITICAL** | Anyone can try to brute-force SSH. Bots scan for this constantly. One leaked key = full server access.            |
| EC2 in public subnet with public IP | **HIGH**     | Direct attack surface. Port scanners find your EC2 and try every open port.                                       |
| MongoDB Atlas allows 0.0.0.0/0      | **CRITICAL** | If your connection string leaks (logs, .env in git, dependency hack), anyone can read/write your entire database. |
| Port 8030 open to 0.0.0.0/0         | **HIGH**     | Someone could bypass ALB and hit your Node.js server directly.                                                    |
| Port 465 open to 0.0.0.0/0          | **MEDIUM**   | SMTP port should be outbound only, not inbound.                                                                   |

### Worth Doing Now vs Later?

**You should fix the security group rules (Section 4) this week.** It takes 10 minutes and costs nothing.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html

---

## 4. Security Groups Deep Dive

Security Groups are virtual firewalls attached to each AWS resource (EC2, ALB, etc.). They control what traffic is allowed in and out.

### Key Concepts

1. **Security Groups are STATEFUL.** If you allow inbound traffic on port 443, the response is automatically allowed outbound. You do NOT need to create a matching outbound rule.

2. **Security Groups are ALLOW only.** You cannot create a "deny" rule. If a port is not explicitly allowed, it is denied. This is called "implicit deny."

3. **You can reference OTHER security groups.** Instead of whitelisting IP addresses, you can say "allow traffic from any resource that has security group SG-alb." This is extremely powerful.

### Your Current Security Group (Estimated)

```
INBOUND RULES (what you probably have):
┌──────────┬──────────────┬──────────────────────────┐
│  Port    │  Protocol    │  Source                   │
├──────────┼──────────────┼──────────────────────────┤
│  22      │  TCP         │  0.0.0.0/0  ← DANGEROUS │
│  80      │  TCP         │  0.0.0.0/0               │
│  443     │  TCP         │  0.0.0.0/0               │
│  465     │  TCP         │  0.0.0.0/0  ← WHY?      │
│  8030    │  TCP         │  0.0.0.0/0  ← DANGEROUS │
└──────────┴──────────────┴──────────────────────────┘

OUTBOUND RULES:
┌──────────┬──────────────┬──────────────────────────┐
│  All     │  All         │  0.0.0.0/0               │
└──────────┴──────────────┴──────────────────────────┘
```

### What It SHOULD Look Like (Three Security Groups)

You need three separate security groups:

#### SG-alb (for the ALB)

```
INBOUND:
┌──────────┬──────────────┬───────────────────────────────────┐
│  Port    │  Protocol    │  Source                            │
├──────────┼──────────────┼───────────────────────────────────┤
│  443     │  TCP         │  0.0.0.0/0  (HTTPS from internet) │
│  80      │  TCP         │  0.0.0.0/0  (HTTP → redirect 443) │
└──────────┴──────────────┴───────────────────────────────────┘

OUTBOUND:
┌──────────┬──────────────┬───────────────────────────────────┐
│  8030    │  TCP         │  SG-app  (only to your EC2s)      │
└──────────┴──────────────┴───────────────────────────────────┘
```

#### SG-app (for EC2 instances)

```
INBOUND:
┌──────────┬──────────────┬────────────────────────────────────────┐
│  Port    │  Protocol    │  Source                                 │
├──────────┼──────────────┼────────────────────────────────────────┤
│  8030    │  TCP         │  SG-alb  (ONLY from ALB, not internet) │
│  443     │  TCP         │  SG-ssm-endpoints (for SSM agent)      │
└──────────┴──────────────┴────────────────────────────────────────┘

  NO PORT 22. SSH IS GONE.

OUTBOUND:
┌──────────┬──────────────┬─────────────────────────────────────────────┐
│  443     │  TCP         │  0.0.0.0/0  (HTTPS: npm, Atlas*, AWS APIs) │
│  27017   │  TCP         │  SG-atlas or Atlas CIDR  (MongoDB)         │
│  465     │  TCP         │  0.0.0.0/0  (SMTP for email sending)       │
└──────────┴──────────────┴─────────────────────────────────────────────┘
```

\*Port 27017 outbound to Atlas CIDR only applies after VPC Peering is set up. Without peering, Atlas traffic goes over 443 (mongodb+srv uses TLS).

#### SG-ssm (for VPC Endpoints, if using SSM)

```
INBOUND:
┌──────────┬──────────────┬──────────────────────────────────────┐
│  443     │  TCP         │  SG-app  (EC2 instances talk to SSM) │
└──────────┴──────────────┴──────────────────────────────────────┘
```

### How to Reference a Security Group Instead of an IP

This is the most important concept. Instead of saying "allow port 8030 from 0.0.0.0/0," you say "allow port 8030 from SG-alb." Now ONLY resources that have the SG-alb security group attached can reach port 8030 on your EC2.

```
BEFORE (wrong):
  EC2 Security Group: Allow 8030 from 0.0.0.0/0
  Result: ANYONE on the internet can hit your Node.js app directly

AFTER (correct):
  EC2 Security Group: Allow 8030 from sg-0abc123def (SG-alb)
  Result: ONLY the ALB can reach your Node.js app
```

### AWS Console Steps to Fix Security Groups Right Now

**Step 1: Create SG-alb**

1. Go to EC2 Dashboard > Security Groups > Create Security Group
2. Name: `dzzlo-alb-sg`
3. VPC: Select your VPC
4. Inbound: Add `HTTPS (443) from 0.0.0.0/0` and `HTTP (80) from 0.0.0.0/0`
5. Outbound: Add `Custom TCP (8030) to SG-app` (you will create SG-app next, come back to set this)
6. Click Create

**Step 2: Create SG-app**

1. Create Security Group
2. Name: `dzzlo-app-sg`
3. Inbound: Add `Custom TCP (8030) from dzzlo-alb-sg`
4. Outbound: Add `HTTPS (443) to 0.0.0.0/0` and `Custom TCP (465) to 0.0.0.0/0`
5. Click Create

**Step 3: Assign SG-alb to the ALB**

1. Go to EC2 > Load Balancers > Select your ALB
2. Actions > Edit Security Groups
3. Remove the old security group, add `dzzlo-alb-sg`

**Step 4: Assign SG-app to EC2 instances**

1. Go to EC2 > Instances > Select instance
2. Actions > Security > Change Security Groups
3. Remove the old security group, add `dzzlo-app-sg`

**Step 5: Remove SSH (port 22) immediately**

- In the old security group, remove the port 22 rule
- Or better: once you have moved EC2 to SG-app (which has no port 22), the old SG is no longer attached

### AWS CLI Commands

```bash
# Create ALB security group
aws ec2 create-security-group \
  --group-name dzzlo-alb-sg \
  --description "ALB security group for DZZLO-OMS" \
  --vpc-id vpc-YOUR_VPC_ID

# Create App security group
aws ec2 create-security-group \
  --group-name dzzlo-app-sg \
  --description "EC2 app security group for DZZLO-OMS" \
  --vpc-id vpc-YOUR_VPC_ID

# Add inbound HTTPS to ALB SG
aws ec2 authorize-security-group-ingress \
  --group-id sg-ALB_SG_ID \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Add inbound HTTP to ALB SG (for redirect)
aws ec2 authorize-security-group-ingress \
  --group-id sg-ALB_SG_ID \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# Add inbound 8030 to App SG FROM ALB SG (security group reference!)
aws ec2 authorize-security-group-ingress \
  --group-id sg-APP_SG_ID \
  --protocol tcp --port 8030 \
  --source-group sg-ALB_SG_ID

# Revoke the dangerous SSH rule from old security group
aws ec2 revoke-security-group-ingress \
  --group-id sg-OLD_SG_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0
```

### What About SSH? Use AWS SSM Instead

**AWS Systems Manager Session Manager (SSM)** lets you open a shell on your EC2 instance through the AWS Console or CLI, without SSH, without port 22, without a key pair.

**How it works:**

1. An SSM Agent runs on your EC2 (it is pre-installed on Amazon Linux 2 AMIs)
2. The agent connects OUTBOUND to AWS SSM service over HTTPS (port 443)
3. You start a session from the AWS Console or CLI
4. AWS brokers the connection through its service --- your EC2 never opens an inbound port

```
YOU (browser/CLI)
    │
    ▼
AWS SSM Service (managed by AWS)
    │
    ▼ (agent-initiated outbound HTTPS)
EC2 Instance (SSM Agent)
```

**Setup steps:**

1. Attach the IAM role `AmazonSSMManagedInstanceCore` to your EC2 instances
2. Ensure outbound HTTPS (443) is allowed in your security group (it should be)
3. Go to AWS Systems Manager > Session Manager > Start Session
4. Select your instance and click "Start session" --- you get a terminal in your browser

**CLI alternative:**

```bash
# Install the Session Manager plugin for AWS CLI
# Then:
aws ssm start-session --target i-YOUR_INSTANCE_ID
```

**This is why you do not need port 22.** SSM is more secure (IAM-authenticated, logged to CloudTrail, no key management) and more convenient.

### Cost Implications

- **Security Groups:** Free. No cost whatsoever.
- **SSM Session Manager:** Free. No additional cost (IAM + SSM Agent are included).
- **SSM VPC Endpoints (optional):** ~$7.20/month per endpoint if EC2 is in a private subnet with no internet access. You need 3 endpoints (ssm, ssmmessages, ec2messages). Total: ~$21.60/month. But if you have a NAT Gateway, SSM traffic can go through it and you do not need the VPC endpoints.

### Worth Doing Now vs Later?

**DO THIS TODAY. Zero cost. Fifteen minutes of work. Massive security improvement.**

1. Create the two security groups (10 min)
2. Attach them to ALB and EC2 (3 min)
3. Test that the API still works through the ALB (2 min)
4. Remove port 22 from the old SG (1 min)
5. Set up SSM for shell access (15 min, but can do later)

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html

---

## 5. Private Subnets for EC2

### The Concept

Right now, your EC2 instances have public IP addresses and sit in public subnets. This means anyone can try to connect to them directly. The ALB is just one path to your EC2 --- but it is not the ONLY path if the security group allows direct access.

The fix: put EC2 instances in a **private subnet** that has no route to the Internet Gateway. Now EC2 instances are completely unreachable from the internet. The ONLY way to reach them is through the ALB (which IS in a public subnet).

### How Traffic Flows

```
BEFORE (current --- EC2 in public subnet):

    User → Internet → ALB → EC2  (intended path)
    Hacker → Internet → EC2      (also possible! direct access)

AFTER (EC2 in private subnet):

    User → Internet → ALB → EC2  (intended path --- works!)
    Hacker → Internet → ✗        (cannot reach private subnet)
```

### But Wait, EC2 Needs Outbound Internet Access

Your Node.js app needs to:

- Connect to MongoDB Atlas (if not using VPC Peering)
- Send emails via SMTP (port 465)
- Download npm packages during deployment
- Call external APIs (if any)

This is where the **NAT Gateway** comes in. It sits in the public subnet and lets private subnet instances make outbound connections, but blocks all inbound connections from the internet.

```
┌─── Public Subnet ───────────────┐    ┌─── Private Subnet ──────────────┐
│                                  │    │                                   │
│   ┌─────────┐   ┌────────────┐  │    │   ┌──────────┐                   │
│   │   ALB   │   │ NAT Gateway│◄─┼────┼───│   EC2    │                   │
│   │         │   │            │  │    │   │ (Node.js) │                   │
│   └────┬────┘   └─────┬──────┘  │    │   └──────────┘                   │
│        │              │         │    │                                   │
└────────┼──────────────┼─────────┘    └───────────────────────────────────┘
         │              │
         ▼              ▼
    Internet Gateway (igw)
         │
         ▼
      Internet
```

### Step-by-Step: Create Private Subnets

**AWS Console:**

1. Go to VPC > Subnets > Create Subnet
2. Create **Private Subnet A**:
   - VPC: your VPC
   - Availability Zone: same AZ as your first EC2 (e.g., us-east-1a)
   - CIDR: `10.0.10.0/24` (or if using default VPC: `172.31.48.0/20`)
   - Name: `dzzlo-private-a`
3. Create **Private Subnet B**:
   - Availability Zone: different AZ (e.g., us-east-1b)
   - CIDR: `10.0.20.0/24` (or `172.31.64.0/20`)
   - Name: `dzzlo-private-b`

4. Go to VPC > NAT Gateways > Create NAT Gateway
   - Subnet: one of your PUBLIC subnets
   - Allocate an Elastic IP
   - Name: `dzzlo-nat`

5. Go to VPC > Route Tables > Create Route Table
   - Name: `dzzlo-private-rt`
   - VPC: your VPC
   - Add route: `0.0.0.0/0` → `nat-xxx` (your NAT Gateway)
   - Associate with your two private subnets

**AWS CLI:**

```bash
# Create private subnet
aws ec2 create-subnet \
  --vpc-id vpc-YOUR_ID \
  --cidr-block 172.31.48.0/20 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=dzzlo-private-a}]'

# Allocate Elastic IP for NAT Gateway
aws ec2 allocate-address --domain vpc

# Create NAT Gateway in a public subnet
aws ec2 create-nat-gateway \
  --subnet-id subnet-PUBLIC_SUBNET_ID \
  --allocation-id eipalloc-YOUR_EIP_ID

# Create route table for private subnets
aws ec2 create-route-table --vpc-id vpc-YOUR_ID

# Add route: all outbound traffic → NAT Gateway
aws ec2 create-route \
  --route-table-id rtb-YOUR_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-YOUR_NAT_ID

# Associate private subnets with the route table
aws ec2 associate-route-table \
  --route-table-id rtb-YOUR_RT_ID \
  --subnet-id subnet-PRIVATE_SUBNET_A_ID
```

### Moving EC2 to Private Subnets

You cannot just "move" a running EC2 instance to a different subnet. You have two options:

**Option A: Launch new instances in the private subnet (recommended)**

1. Create an AMI from your current EC2 instance
2. Launch a new instance from that AMI into the private subnet
3. Update the ALB target group to point to the new instance
4. Verify everything works
5. Terminate the old instance

**Option B: Use ASG (better long-term)**

1. Create a Launch Template from your current instance config
2. Set the Launch Template to use the private subnets
3. Create an ASG with the Launch Template
4. ASG will launch instances in the private subnets
5. Register them with the ALB target group

### Cost Implications

| Component            | Cost                                         |
| -------------------- | -------------------------------------------- |
| Private Subnets      | Free                                         |
| Route Tables         | Free                                         |
| NAT Gateway          | ~$32/month + $0.045/GB data processed        |
| Elastic IP (for NAT) | Free while in use, $3.65/month if unattached |

The NAT Gateway is the only real cost here. At your current scale, outbound data processing is likely minimal (a few GB/month), so budget approximately **$35/month**.

### Worth Doing Now vs Later?

**Later (Phase 2).** The security group fixes in Section 4 give you 80% of the security benefit for zero cost. Moving to private subnets is the right architectural choice but involves downtime risk and the ~$35/month NAT Gateway cost. Do it when you are ready for the migration (Section 12).

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html

---

## 6. VPC Peering with MongoDB Atlas

This is the most impactful networking change you can make. It eliminates the `0.0.0.0/0` Atlas whitelist, which is your single biggest security vulnerability.

### What is VPC Peering?

VPC Peering creates a private network connection between two VPCs. Traffic between them never touches the public internet. It is like building a private hallway between two floors of the office building.

```
BEFORE (current):
  EC2 ──► public internet ──► MongoDB Atlas
  (Atlas must allow 0.0.0.0/0 because EC2 IPs are dynamic)

AFTER (VPC Peering):
  EC2 ──► VPC Peering connection (private) ──► MongoDB Atlas VPC
  (Atlas only allows your VPC CIDR, e.g., 172.31.0.0/16)
```

### Why This Solves the 0.0.0.0/0 Problem

MongoDB Atlas runs in its own VPC in AWS. When you create a VPC Peering connection, you connect YOUR VPC to Atlas's VPC. Then in Atlas, instead of whitelisting `0.0.0.0/0` (all IPs), you whitelist only your VPC CIDR (e.g., `172.31.0.0/16`). Now ONLY instances in your VPC can reach the database.

Even if someone steals your MongoDB connection string, they cannot connect because they are not in your VPC.

### Prerequisites

- MongoDB Atlas on **M10 or higher** tier (dedicated cluster). You mentioned you are on a dedicated plan, so this is met.
- Your VPC and Atlas must be in the **same AWS region**.
- The CIDR blocks must NOT overlap (your default VPC is `172.31.0.0/16`; Atlas typically uses `192.168.248.0/21` --- no overlap, so you are fine).

### Step-by-Step Setup

#### Step 1: Initiate Peering in MongoDB Atlas

1. Log in to **MongoDB Atlas** (https://cloud.mongodb.com)
2. Go to **Network Access** > **Peering** > **Add Peering Connection**
3. Select **AWS**
4. Fill in:
   - **AWS Account ID:** Your 12-digit AWS account number (find in AWS Console top-right dropdown)
   - **VPC ID:** Your VPC ID (e.g., `vpc-0abc123`)
   - **VPC CIDR:** `172.31.0.0/16` (your default VPC)
   - **AWS Region:** Must match your EC2 region (e.g., `ap-south-1` for Mumbai)
5. Click **Initiate Peering**
6. Atlas will give you:
   - A **Peering Connection ID** (e.g., `pcx-0abc123`)
   - Atlas's **VPC CIDR** (e.g., `192.168.248.0/21`)
   - The status will show "Waiting for Approval"

#### Step 2: Accept the Peering Request in AWS

1. Go to AWS Console > **VPC** > **Peering Connections**
2. You will see a pending peering request from Atlas
3. Select it > **Actions** > **Accept Request**
4. Click **Yes, Accept**
5. Status changes to "Active"

**AWS CLI alternative:**

```bash
# List pending peering connections
aws ec2 describe-vpc-peering-connections \
  --filters "Name=status-code,Values=pending-acceptance"

# Accept it
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-YOUR_PEERING_ID
```

#### Step 3: Update Route Tables

You must tell your VPC where to send traffic destined for Atlas's CIDR.

1. Go to **VPC** > **Route Tables**
2. Select the route table associated with your EC2 subnets
3. **Edit Routes** > **Add Route**:
   - **Destination:** `192.168.248.0/21` (Atlas's VPC CIDR --- Atlas tells you this)
   - **Target:** `pcx-YOUR_PEERING_ID`
4. **Save**

If you have separate route tables for public and private subnets, add this route to the one(s) where your EC2 instances live.

**AWS CLI:**

```bash
aws ec2 create-route \
  --route-table-id rtb-YOUR_RT_ID \
  --destination-cidr-block 192.168.248.0/21 \
  --vpc-peering-connection-id pcx-YOUR_PEERING_ID
```

#### Step 4: Update Security Groups

Add an outbound rule to your EC2 security group allowing traffic to Atlas's CIDR on port 27017 (MongoDB).

```bash
aws ec2 authorize-security-group-egress \
  --group-id sg-APP_SG_ID \
  --protocol tcp --port 27017 \
  --cidr 192.168.248.0/21
```

(If your outbound rules already allow all traffic to 0.0.0.0/0, this step is technically not needed, but it is best practice to be explicit.)

#### Step 5: Update MongoDB Atlas Network Access

1. In Atlas, go to **Network Access** > **IP Access List**
2. **Add** your VPC CIDR: `172.31.0.0/16`
3. **Test** your connection (deploy and verify your app connects)
4. **REMOVE** the `0.0.0.0/0` entry

**Do NOT remove 0.0.0.0/0 until you have verified the peered connection works.**

#### Step 6: Update Your Connection String (Maybe)

If you are using the `mongodb+srv://` connection string format, Atlas will automatically resolve DNS to the private IPs over the peering connection. You likely do NOT need to change your connection string.

However, verify by checking the DNS resolution from your EC2 instance:

```bash
# SSH (or SSM) into your EC2 and run:
nslookup your-cluster.xxxxx.mongodb.net
# It should resolve to private IPs (192.168.x.x), not public IPs
```

### Troubleshooting Common Issues

| Issue                            | Cause                          | Fix                                                  |
| -------------------------------- | ------------------------------ | ---------------------------------------------------- |
| Peering stuck in "Pending"       | You did not accept it in AWS   | Go to VPC > Peering Connections > Accept             |
| Connection timeout after peering | Route table not updated        | Add Atlas CIDR route to route table                  |
| DNS resolves to public IPs       | DNS not configured for peering | In Atlas, ensure "Private IP for Peering" is enabled |
| CIDR overlap error               | VPC CIDRs overlap              | You would need a new VPC with a different CIDR range |

### Cost

**VPC Peering is FREE.** There is no charge for the peering connection itself. You only pay for data transfer across the peering connection, which is $0.01/GB (same-region). For your data volumes, this is effectively free.

### Worth Doing Now vs Later?

**Do this within the next 2 weeks. This is priority #2 after fixing security groups.** It is free, it eliminates your biggest security vulnerability, and it is a one-time setup that takes about 30 minutes.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html
- https://www.mongodb.com/docs/atlas/security-vpc-peering/

---

## 7. AWS PrivateLink for MongoDB Atlas

### What is PrivateLink?

PrivateLink is an alternative to VPC Peering. Instead of connecting two entire VPCs, PrivateLink creates a **one-way private endpoint** in YOUR VPC that connects to a specific service (in this case, MongoDB Atlas).

```
VPC Peering:
  Your VPC ◄════════════════════► Atlas VPC    (bidirectional, full network)

PrivateLink:
  Your VPC ──► VPC Endpoint ──► Atlas Service  (one-way, specific service)
```

### How It Works

1. Atlas creates an **Endpoint Service** on their side
2. You create a **VPC Endpoint** (type: Interface) in YOUR VPC
3. AWS creates an Elastic Network Interface (ENI) in your subnet with a private IP
4. Your app connects to that private IP (or a private DNS name) instead of the public Atlas URL
5. Traffic flows privately through AWS's backbone, never touching the internet

```
┌─── Your VPC ──────────────────────────────────────────────┐
│                                                            │
│   ┌──────────┐      ┌───────────────────────┐             │
│   │   EC2    │─────►│  VPC Endpoint (ENI)    │             │
│   │ (Node.js)│      │  10.0.10.55            │             │
│   └──────────┘      └───────────┬────────────┘             │
│                                 │ (private)                │
└─────────────────────────────────┼──────────────────────────┘
                                  │
                          AWS PrivateLink fabric
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  MongoDB Atlas   │
                        │  Endpoint Service│
                        └─────────────────┘
```

### VPC Peering vs PrivateLink: When to Use Which

| Feature                 | VPC Peering                           | PrivateLink                         |
| ----------------------- | ------------------------------------- | ----------------------------------- |
| Connection type         | Bidirectional, full VPC-to-VPC        | Unidirectional, your VPC → service  |
| Setup complexity        | Moderate (route tables, CIDRs)        | Simpler (no route table changes)    |
| CIDR overlap allowed?   | No (CIDRs must not overlap)           | Yes (no CIDR dependency)            |
| Security                | Both VPCs can initiate traffic        | Only YOUR side can initiate         |
| Cost                    | Free (only data transfer at $0.01/GB) | ~$7.20/month per AZ + $0.01/GB      |
| Cross-region            | No (same region only)                 | Yes (with Inter-Region PrivateLink) |
| Scales to multiple VPCs | Need one peering per VPC pair         | Each VPC creates its own endpoint   |
| Atlas tier required     | M10+ (Dedicated)                      | M10+ (Dedicated)                    |

### Recommendation for DZZLO-OMS

**Use VPC Peering, not PrivateLink.** Here is why:

1. **Cost:** VPC Peering is free. PrivateLink costs ~$7.20/month minimum.
2. **Your setup is simple:** One VPC, one Atlas cluster, same region. No CIDR overlap. VPC Peering is the straightforward choice.
3. **PrivateLink is better when:** You have many VPCs, or CIDRs overlap, or you need cross-region connectivity. None of these apply to you now.

### If You DO Want PrivateLink (For Reference)

#### Step 1: Create PrivateLink in Atlas

1. Atlas > Network Access > Private Endpoint > Add Private Endpoint
2. Select AWS and your region
3. Atlas gives you a **Service Name** (e.g., `com.amazonaws.vpce.us-east-1.vpce-svc-xxx`)

#### Step 2: Create VPC Endpoint in AWS

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-YOUR_ID \
  --service-name com.amazonaws.vpce.us-east-1.vpce-svc-xxx \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-YOUR_PRIVATE_SUBNET \
  --security-group-ids sg-YOUR_SG
```

#### Step 3: Complete in Atlas

1. Paste the VPC Endpoint ID back into Atlas
2. Atlas verifies and activates the connection
3. Atlas gives you a new connection string (with `-pl-0` suffix)
4. Update your `.env` `DATABASE_URI` with the new string

### Cost

| Component             | Monthly Cost             |
| --------------------- | ------------------------ |
| VPC Endpoint (per AZ) | ~$7.20/month ($0.01/hr)  |
| Data processed        | $0.01/GB                 |
| **Total (2 AZs)**     | **~$14.40/month + data** |

### Worth Doing Now vs Later?

**Later, and only if VPC Peering does not work for your setup.** VPC Peering is free and simpler. Use that.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html
- https://www.mongodb.com/docs/atlas/security-private-endpoint/

---

## 8. VPC for ASG (Auto Scaling Group)

### The Problem You Had

You mentioned that ASG gives dynamic IPs, so you cannot whitelist static EC2 IPs in MongoDB Atlas. This is exactly right --- and it is exactly what VPC Peering solves.

### How ASG Works With VPC

When ASG launches a new EC2 instance, it places it in one of the subnets you configured in the Launch Template or ASG settings. The instance gets a **private IP** from that subnet's CIDR range.

```
ASG Configuration:
  Subnets: [dzzlo-private-a (10.0.10.0/24), dzzlo-private-b (10.0.20.0/24)]
  Min: 2, Max: 4, Desired: 2

What happens on scale-out:
  New EC2 instance → placed in dzzlo-private-a → gets IP 10.0.10.47
  Another EC2 instance → placed in dzzlo-private-b → gets IP 10.0.20.12

These IPs are DIFFERENT every time. You never know what IP a new instance will get.
```

### Why VPC Peering Solves This

With VPC Peering, you do NOT whitelist individual IPs in Atlas. You whitelist your **entire VPC CIDR block.**

```
Atlas IP Access List:
  BEFORE: 0.0.0.0/0              ← anyone on Earth
  AFTER:  10.0.0.0/16            ← only IPs in your VPC (or 172.31.0.0/16 for default VPC)

Any instance ASG launches in your VPC will have an IP within 10.0.0.0/16.
Atlas allows that entire range. Problem solved.
```

### Practical Setup

```
┌─── Your VPC (10.0.0.0/16) ─────────────────────────────────────┐
│                                                                   │
│   ASG launches EC2s in private subnets:                           │
│                                                                   │
│   ┌─ Private Subnet A ──┐    ┌─ Private Subnet B ──┐            │
│   │  EC2: 10.0.10.5     │    │  EC2: 10.0.20.8     │            │
│   │  EC2: 10.0.10.47    │    │  EC2: 10.0.20.12    │            │
│   │  (new from ASG)     │    │  (new from ASG)     │            │
│   └──────────────────────┘    └──────────────────────┘            │
│                                                                   │
│   ALL of these IPs fall within 10.0.0.0/16                       │
│                                                                   │
└───────────────┬───────────────────────────────────────────────────┘
                │
          VPC Peering
                │
                ▼
      ┌─────────────────┐
      │  MongoDB Atlas   │
      │  Whitelist:      │
      │  10.0.0.0/16 ✓  │  ← All your EC2 IPs are allowed
      └─────────────────┘
```

### What About Elastic IPs? (Common Misconception)

Some people try to solve this by assigning Elastic IPs (static IPs) to EC2 instances. This does NOT work with ASG because:

1. Elastic IPs must be manually assigned
2. ASG launches and terminates instances automatically
3. You would run out of Elastic IPs quickly (AWS limit: 5 per region by default)
4. Elastic IPs cost $3.65/month each when unattached

**VPC Peering is the correct solution. Elastic IPs are a band-aid.**

### What About NAT Gateway? (Another Approach)

If you do NOT set up VPC Peering, there is another way to get a stable outbound IP: all instances in a private subnet go through the NAT Gateway, which has one Elastic IP. So from Atlas's perspective, all your traffic comes from one IP (the NAT Gateway's Elastic IP).

```
EC2 (10.0.10.5)   ──┐
EC2 (10.0.10.47)  ──┼──► NAT Gateway (52.1.2.3) ──► Internet ──► Atlas
EC2 (10.0.20.8)   ──┘
                    All appear as 52.1.2.3 to Atlas
```

You could whitelist just the NAT Gateway's Elastic IP in Atlas. But this is still traffic over the public internet, just with a predictable source IP. **VPC Peering is better because traffic stays private.**

### ASG Launch Template Subnet Configuration

When you create your ASG, specify the private subnets:

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name dzzlo-oms-asg \
  --launch-template LaunchTemplateId=lt-YOUR_ID,Version='$Latest' \
  --min-size 2 \
  --max-size 4 \
  --desired-capacity 2 \
  --vpc-zone-identifier "subnet-PRIVATE_A_ID,subnet-PRIVATE_B_ID" \
  --target-group-arns arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/YOUR_TG
```

The `--vpc-zone-identifier` parameter is where you specify the subnets. ASG will distribute instances across these subnets.

### Worth Doing Now vs Later?

**The VPC Peering part: do now (it is free and solves the whitelist problem). The ASG-in-private-subnets part: do as part of the migration (Section 12).**

---

## 9. VPC Flow Logs

### What They Are

VPC Flow Logs capture information about IP traffic flowing through your VPC's network interfaces. Think of them as CCTV cameras for your network --- they record who talked to whom, on what port, and whether the traffic was accepted or rejected.

### What a Flow Log Entry Looks Like

```
2 123456789012 eni-abc123 10.0.10.5 52.94.133.150 8030 443 6 10 840 1616729292 1616729349 ACCEPT OK
```

Breaking that down:

```
version:       2
account-id:    123456789012
interface-id:  eni-abc123        (which network interface)
src-addr:      10.0.10.5         (source IP --- your EC2)
dst-addr:      52.94.133.150     (destination IP --- Atlas)
src-port:      8030              (source port)
dst-port:      443               (destination port)
protocol:      6                 (TCP)
packets:       10
bytes:         840
start:         1616729292        (Unix timestamp)
end:           1616729349
action:        ACCEPT            (or REJECT)
log-status:    OK
```

### Why You Need Them

1. **Security auditing:** See if anyone is trying to access your instances on blocked ports (the REJECT entries)
2. **Debugging:** "Why can my EC2 not connect to Atlas?" --- check flow logs to see if traffic is being rejected
3. **Compliance:** Many standards (SOC2, ISO 27001) require network traffic logging
4. **Anomaly detection:** Spot unusual traffic patterns (e.g., your EC2 suddenly talking to unknown IPs)

### How to Enable Them

**Option A: Send to CloudWatch Logs (easier to search)**

AWS Console:

1. Go to **VPC** > **Your VPCs** > Select your VPC
2. **Flow Logs** tab > **Create Flow Log**
3. Settings:
   - Filter: **All** (captures both ACCEPT and REJECT)
   - Maximum aggregation interval: **1 minute** (for debugging) or **10 minutes** (for cost saving)
   - Destination: **Send to CloudWatch Logs**
   - Destination log group: Create one called `/vpc/dzzlo-flow-logs`
   - IAM Role: Create a new role (AWS will guide you)
4. Click **Create**

**Option B: Send to S3 (cheaper for long-term storage)**

```bash
# Create an S3 bucket for flow logs
aws s3 mb s3://dzzlo-vpc-flow-logs-YOUR_ACCOUNT_ID

# Create the flow log
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-YOUR_VPC_ID \
  --traffic-type ALL \
  --log-destination-type s3 \
  --log-destination arn:aws:s3:::dzzlo-vpc-flow-logs-YOUR_ACCOUNT_ID \
  --max-aggregation-interval 600
```

### Useful Queries (CloudWatch Logs Insights)

Once flow logs are in CloudWatch, you can query them:

```sql
-- Find all REJECTED traffic (potential attacks or misconfigurations)
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| sort @timestamp desc
| limit 50

-- Find who is trying to access port 22 (SSH)
fields @timestamp, srcAddr, dstPort, action
| filter dstPort = 22
| sort @timestamp desc

-- Find all traffic to MongoDB Atlas CIDR
fields @timestamp, srcAddr, dstAddr, dstPort, bytes
| filter dstAddr like /192\.168\.248/
| sort @timestamp desc

-- Find top talkers (which source IPs send the most data)
stats sum(bytes) as totalBytes by srcAddr
| sort totalBytes desc
| limit 10
```

### Cost

| Destination     | Ingestion Cost    | Storage Cost                  | Notes                                             |
| --------------- | ----------------- | ----------------------------- | ------------------------------------------------- |
| CloudWatch Logs | $0.50/GB ingested | $0.03/GB/month stored         | More expensive but easier to query                |
| S3              | Free ingestion    | $0.023/GB/month (S3 Standard) | Cheaper, but need Athena to query ($5/TB scanned) |

For a small setup like DZZLO-OMS, flow logs will generate maybe 1-5 GB/month. Cost: **$0.50-$2.50/month to CloudWatch**, or **nearly free to S3**.

### Worth Doing Now vs Later?

**Do it when you set up VPC Peering (Phase 2).** It is cheap, easy, and incredibly useful for debugging network issues during migration. Send to S3 for cost efficiency. If you need to debug something, use CloudWatch Logs Insights temporarily.

**AWS docs:**

- https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html

---

## 10. Target Network Architecture

### The Ideal DZZLO-OMS Network Diagram

```
                            ┌──────────────┐
                            │   INTERNET    │
                            └──────┬───────┘
                                   │
                            ┌──────▼───────┐
                            │ Internet      │
                            │ Gateway (IGW) │
                            └──────┬───────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────┐
│                           YOUR VPC (10.0.0.0/16)                        │
│                                  │                                      │
│  ┌───────────────────────────────┼─────────────────────────────────┐   │
│  │          PUBLIC SUBNETS                                          │   │
│  │                               │                                  │   │
│  │   ┌─ AZ-a (10.0.1.0/24) ─────┼── AZ-b (10.0.2.0/24) ──┐      │   │
│  │   │                           │                           │      │   │
│  │   │  ┌──────────────┐         │    ┌──────────────┐       │      │   │
│  │   │  │     ALB      │◄────────┘    │     ALB      │       │      │   │
│  │   │  │  [SG-alb]    │              │  (2nd AZ)    │       │      │   │
│  │   │  │ :80 → :443   │              │              │       │      │   │
│  │   │  │   redirect   │              │              │       │      │   │
│  │   │  └──────┬───────┘              └──────┬───────┘       │      │   │
│  │   │         │                             │               │      │   │
│  │   │  ┌──────▼───────┐                     │               │      │   │
│  │   │  │ NAT Gateway  │                     │               │      │   │
│  │   │  │ (EIP: x.x.x)│                     │               │      │   │
│  │   │  └──────┬───────┘                     │               │      │   │
│  │   │         │                             │               │      │   │
│  │   └─────────┼─────────────────────────────┼───────────────┘      │   │
│  └─────────────┼─────────────────────────────┼──────────────────────┘   │
│                │                             │                          │
│  ┌─────────────┼─────────────────────────────┼──────────────────────┐   │
│  │          PRIVATE SUBNETS                                          │   │
│  │             │                             │                       │   │
│  │   ┌─ AZ-a (10.0.10.0/24) ────── AZ-b (10.0.20.0/24) ──┐       │   │
│  │   │         │                             │               │       │   │
│  │   │  ┌──────▼───────┐              ┌──────▼───────┐       │       │   │
│  │   │  │    EC2 #1    │              │    EC2 #2    │       │       │   │
│  │   │  │  [SG-app]   │              │  [SG-app]   │       │       │   │
│  │   │  │  Node.js    │              │  Node.js    │       │       │   │
│  │   │  │  :8030      │              │  :8030      │       │       │   │
│  │   │  │  PM2        │              │  PM2        │       │       │   │
│  │   │  │  SSM Agent  │              │  SSM Agent  │       │       │   │
│  │   │  └──────┬───────┘              └──────┬───────┘       │       │   │
│  │   │         │                             │               │       │   │
│  │   └─────────┼─────────────────────────────┼───────────────┘       │   │
│  └─────────────┼─────────────────────────────┼───────────────────────┘   │
│                │                             │                          │
│                └──────────┬──────────────────┘                          │
│                           │                                             │
│  ┌────────────────────────┼─────────────────────────────────────────┐   │
│  │  VPC ENDPOINTS (for SSM when no NAT route is desired)            │   │
│  │                        │                                          │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │   │
│  │  │ ssm             │  │ ssmmessages     │  │ ec2messages     │  │   │
│  │  │ [SG-ssm]        │  │ [SG-ssm]        │  │ [SG-ssm]        │  │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  VPC Flow Logs → S3 / CloudWatch                                        │
│                                                                          │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                        VPC Peering (pcx-xxx)
                    Route: 192.168.248.0/21 → pcx
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │      MongoDB Atlas VPC       │
                  │      192.168.248.0/21        │
                  │                              │
                  │   ┌────────────────────┐     │
                  │   │  Atlas Cluster     │     │
                  │   │  (Dedicated M10+)  │     │
                  │   │                    │     │
                  │   │  IP Access List:   │     │
                  │   │  10.0.0.0/16 ONLY  │     │
                  │   └────────────────────┘     │
                  │                              │
                  └──────────────────────────────┘
```

### Traffic Flows in the Ideal Architecture

```
1. USER REQUEST:
   User → Internet → ALB (public subnet, SG-alb allows :443)
   → ALB → EC2 (private subnet, SG-app allows :8030 from SG-alb)
   → EC2 runs Node.js, processes request

2. DATABASE QUERY:
   EC2 → VPC Peering → Atlas (private, never touches internet)
   Atlas IP Access List only allows 10.0.0.0/16

3. OUTBOUND INTERNET (npm, SMTP, external APIs):
   EC2 → NAT Gateway (public subnet) → IGW → Internet
   (one-way: internet cannot reach EC2 through NAT)

4. ADMIN ACCESS (replacing SSH):
   Admin → AWS Console/CLI → SSM Service → SSM Agent on EC2
   (no inbound ports needed, IAM-authenticated, logged in CloudTrail)

5. ASG SCALE-OUT:
   ASG launches EC2 in private subnet → gets IP 10.0.10.x
   → ALB health check passes → instance receives traffic
   → Atlas accepts connection (10.0.10.x is within 10.0.0.0/16)
```

### Security Groups Summary

```
┌────────────────────────────────────────────────────────────────────┐
│ SG-alb (attached to ALB)                                          │
├────────────┬──────────────┬───────────────────────────────────────┤
│ Direction  │ Port         │ Source/Dest                            │
├────────────┼──────────────┼───────────────────────────────────────┤
│ Inbound    │ 443 (HTTPS)  │ 0.0.0.0/0                            │
│ Inbound    │ 80 (HTTP)    │ 0.0.0.0/0 (redirect to 443)          │
│ Outbound   │ 8030         │ SG-app                                │
└────────────┴──────────────┴───────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ SG-app (attached to EC2 instances)                                │
├────────────┬──────────────┬───────────────────────────────────────┤
│ Direction  │ Port         │ Source/Dest                            │
├────────────┼──────────────┼───────────────────────────────────────┤
│ Inbound    │ 8030         │ SG-alb (only from ALB)                │
│ Outbound   │ 443 (HTTPS)  │ 0.0.0.0/0 (npm, AWS APIs, etc.)     │
│ Outbound   │ 27017        │ 192.168.248.0/21 (Atlas via peering) │
│ Outbound   │ 465 (SMTP)   │ 0.0.0.0/0                            │
└────────────┴──────────────┴───────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ SG-ssm (attached to VPC Endpoints — only if NOT using NAT)        │
├────────────┬──────────────┬───────────────────────────────────────┤
│ Direction  │ Port         │ Source/Dest                            │
├────────────┼──────────────┼───────────────────────────────────────┤
│ Inbound    │ 443          │ SG-app (EC2 SSM Agent → Endpoint)     │
└────────────┴──────────────┴───────────────────────────────────────┘
```

---

## 11. Cost of VPC Improvements

### Cost Breakdown

| Component                         | Monthly Cost | One-Time | Notes                                                      |
| --------------------------------- | ------------ | -------- | ---------------------------------------------------------- |
| **Security Groups** (restructure) | $0           | 0        | Free. Do today.                                            |
| **VPC Peering** (Atlas)           | ~$0          | 0        | Free. Data transfer ~$0.01/GB. Your DB traffic is tiny.    |
| **NAT Gateway**                   | ~$32         | 0        | $0.045/hr + $0.045/GB. The biggest ongoing cost.           |
| **Elastic IP** (for NAT)          | $0           | 0        | Free while attached to NAT Gateway.                        |
| **Private Subnets**               | $0           | 0        | Free.                                                      |
| **SSM Session Manager**           | $0           | 0        | Free (uses existing SSM agent).                            |
| **SSM VPC Endpoints** (3x)        | ~$22         | 0        | Only needed if EC2 has no NAT route. Skip if you have NAT. |
| **VPC Flow Logs** (to S3)         | ~$1-3        | 0        | Depends on traffic volume. Minimal at your scale.          |
| **New VPC** (if creating custom)  | $0           | 0        | VPCs are free.                                             |

### Total Monthly Cost by Phase

| Phase                                  | What                          | Added Monthly Cost                                         |
| -------------------------------------- | ----------------------------- | ---------------------------------------------------------- |
| Phase 1: Security Groups + VPC Peering | Fix SGs, set up Atlas peering | **$0/month**                                               |
| Phase 2: Private Subnets + NAT         | Move EC2 to private subnets   | **+$33/month**                                             |
| Phase 3: SSM + Flow Logs               | Replace SSH, add logging      | **+$1-3/month** (flow logs to S3; SSM through NAT is free) |

**Total additional monthly cost for the full setup: ~$35/month.**

### Is It Worth It?

**Yes.** For context:

- A single data breach investigation costs $10,000+ in professional services
- MongoDB Atlas dedicated cluster alone costs $57+/month (M10)
- Two EC2 instances cost $15-150+/month depending on size
- $35/month for NAT Gateway is a rounding error on your infrastructure bill

**Phase 1 costs literally $0 and eliminates 80% of your security risk.** There is no reason not to do it.

### Cost-Saving Tips

1. **NAT Gateway cost reduction:** If your outbound traffic is low, consider using a NAT Instance (a tiny EC2 running NAT) instead of a managed NAT Gateway. A t3.nano costs ~$3.80/month. However, NAT Gateway is more reliable and AWS-managed.

2. **Single NAT Gateway (acceptable at your scale):** The architecture diagram shows one NAT Gateway. For high availability, you would want one per AZ (~$64/month). At your current scale, one is fine --- if it goes down, outbound internet breaks but your app still serves traffic through the ALB.

3. **SSM through NAT:** If you have a NAT Gateway, SSM Agent traffic flows through it. You do NOT need the three SSM VPC Endpoints ($22/month saved).

---

## 12. Step-by-Step Migration Plan

### Overview

```
CURRENT STATE                          TARGET STATE
─────────────                          ────────────
Default VPC (172.31.0.0/16)            Custom or Default VPC with proper config
All public subnets                     Public + Private subnets
EC2 in public subnet                   EC2 in private subnet
ALB in public subnet                   ALB in public subnet (stays)
SSH open (port 22, 0.0.0.0/0)         No SSH. SSM instead.
One mega security group                Three purpose-specific SGs
Atlas whitelist: 0.0.0.0/0            Atlas whitelist: VPC CIDR only
No VPC Peering                         VPC Peering to Atlas
No Flow Logs                           Flow Logs to S3
```

### Phase 1: Immediate Security Fixes (Day 1 --- 30 minutes, $0/month)

**Goal: Fix the worst problems with zero cost and near-zero risk.**

```
Step 1.1: Create new Security Groups
─────────────────────────────────────
  - Create SG-alb  (inbound: 80,443 from 0.0.0.0/0)
  - Create SG-app  (inbound: 8030 from SG-alb ONLY)
  - See Section 4 for exact rules and CLI commands

Step 1.2: Assign SG-alb to ALB
──────────────────────────────
  - EC2 > Load Balancers > Your ALB > Edit Security Groups
  - Add SG-alb, remove old SG

Step 1.3: Assign SG-app to EC2 instances
────────────────────────────────────────
  - EC2 > Instances > Select each > Actions > Security > Change Security Groups
  - Add SG-app, remove old SG
  - TEST: Verify API works through ALB
  - TEST: Verify direct EC2 IP on :8030 is BLOCKED

Step 1.4: Remove SSH rule
─────────────────────────
  - SG-app has no port 22 rule, so once old SG is detached, SSH is gone
  - WARNING: Before doing this, set up SSM (Step 1.5) or accept
    that you'll temporarily lose shell access

Step 1.5: Set up SSM (replaces SSH)
────────────────────────────────────
  - Attach IAM role AmazonSSMManagedInstanceCore to EC2 instances
    (EC2 > Instance > Actions > Security > Modify IAM role)
  - Ensure SG-app allows outbound HTTPS (443) — it should
  - Wait 5 minutes for SSM Agent to register
  - Test: AWS Console > Systems Manager > Session Manager > Start Session
  - If it works: you now have shell access without SSH
```

**Verification checklist after Phase 1:**

- [ ] API responds normally through ALB URL
- [ ] Direct EC2 public IP on :8030 returns timeout/connection refused
- [ ] SSH to EC2 public IP times out (port 22 blocked)
- [ ] SSM Session Manager can open a shell on both instances
- [ ] MongoDB Atlas still works (connection string unchanged)

### Phase 2: VPC Peering with Atlas (Day 2-3 --- 1 hour, $0/month)

**Goal: Remove 0.0.0.0/0 from Atlas and route DB traffic privately.**

```
Step 2.1: Set up VPC Peering
─────────────────────────────
  - Follow Section 6 step-by-step
  - Atlas > Network Access > Peering > Add Peering Connection
  - AWS > VPC > Peering Connections > Accept
  - AWS > Route Tables > Add route for Atlas CIDR

Step 2.2: Update Atlas IP Access List
──────────────────────────────────────
  - ADD your VPC CIDR (e.g., 172.31.0.0/16) to Atlas IP Access List
  - TEST: Verify your app still connects to MongoDB
  - Wait 24 hours and monitor for any issues

Step 2.3: Remove 0.0.0.0/0 from Atlas
───────────────────────────────────────
  - ONLY after you've confirmed peering works for 24+ hours
  - Atlas > Network Access > IP Access List > Delete 0.0.0.0/0
  - TEST: Verify your app still works
  - TEST: Try connecting from your laptop (should FAIL — that's the point)
```

**Verification checklist after Phase 2:**

- [ ] VPC Peering status is "Active" in both Atlas and AWS
- [ ] Route table has Atlas CIDR → peering connection route
- [ ] App connects to MongoDB normally
- [ ] Atlas IP Access List only shows your VPC CIDR
- [ ] Connection from outside your VPC (e.g., your laptop) is refused by Atlas
  - Note: Add your office/home IP to Atlas Access List if you need to use MongoDB Compass from your laptop

### Phase 3: Private Subnets + NAT (Week 2 --- 2 hours, +$33/month)

**Goal: Move EC2 instances from public to private subnets.**

**This phase involves instance replacement. Plan for a maintenance window or do it with zero-downtime using the ALB.**

```
Step 3.1: Create private subnets
─────────────────────────────────
  - Create 2 private subnets (one per AZ)
  - See Section 5 for details

Step 3.2: Create NAT Gateway
─────────────────────────────
  - Allocate Elastic IP
  - Create NAT Gateway in one of your public subnets
  - Wait 5 minutes for it to become "Available"

Step 3.3: Create private route table
─────────────────────────────────────
  - Create route table
  - Add route: 0.0.0.0/0 → NAT Gateway
  - Add route: 192.168.248.0/21 → VPC Peering connection
  - Associate with both private subnets

Step 3.4: Create AMI from current EC2
──────────────────────────────────────
  - EC2 > Instance > Actions > Image and Templates > Create Image
  - Name: dzzlo-oms-migration-YYYYMMDD
  - Wait for AMI to become "Available" (5-15 minutes)

Step 3.5: Launch new EC2 in private subnet
──────────────────────────────────────────
  - Launch instance from your AMI
  - Select a private subnet
  - Assign SG-app security group
  - Assign the SSM IAM role
  - Do NOT assign a public IP (private subnet, not needed)

Step 3.6: Register new EC2 with ALB Target Group
──────────────────────────────────────────────────
  - EC2 > Target Groups > Your target group > Register targets
  - Add the new EC2 instance
  - Wait for health check to pass (instance shows "healthy")

Step 3.7: Deregister old EC2 from ALB Target Group
────────────────────────────────────────────────────
  - Select old instance > Deregister
  - ALB will drain connections (default: 300 seconds)
  - During this time, new requests go to new instance, existing connections finish on old

Step 3.8: Verify and repeat for second instance
─────────────────────────────────────────────────
  - Verify new instance handles traffic correctly
  - Repeat steps 3.5-3.7 for second instance
  - When both new instances are healthy, terminate old instances

Step 3.9: Enable VPC Flow Logs
──────────────────────────────
  - See Section 9
  - Send to S3 for cost efficiency
```

**Zero-downtime approach:** Because the ALB distributes traffic, you can migrate one instance at a time. The ALB always has at least one healthy instance serving traffic.

**Verification checklist after Phase 3:**

- [ ] Both EC2 instances are in private subnets
- [ ] EC2 instances have NO public IP addresses
- [ ] ALB target group shows both instances as "healthy"
- [ ] API responds normally
- [ ] SSM Session Manager works on both instances (traffic goes through NAT)
- [ ] MongoDB Atlas connection works (traffic goes through VPC Peering)
- [ ] Outbound internet works from EC2 (test: `curl https://api.github.com` from SSM session)
- [ ] Old EC2 instances are terminated
- [ ] VPC Flow Logs are active

### Phase 4: ASG Setup (Week 3 --- 1 hour, $0 additional)

**Goal: Replace manually managed EC2 instances with Auto Scaling Group.**

```
Step 4.1: Create Launch Template
─────────────────────────────────
  - EC2 > Launch Templates > Create
  - Use your AMI
  - Instance type: same as current
  - Security group: SG-app
  - IAM role: SSM role
  - User data: your deployment script (git pull, npm install, pm2 start)
  - No public IP

Step 4.2: Create ASG
────────────────────
  - EC2 > Auto Scaling Groups > Create
  - Launch Template: from step 4.1
  - VPC: your VPC
  - Subnets: both private subnets
  - Attach to ALB target group
  - Min: 2, Max: 4, Desired: 2
  - Health check: ELB (uses ALB health check)
  - Health check grace period: 300 seconds

Step 4.3: Verify ASG launches healthy instances
────────────────────────────────────────────────
  - Wait for ASG to launch 2 instances
  - Check ALB target group — both should be "healthy"
  - Test API

Step 4.4: Terminate old manually-launched instances
────────────────────────────────────────────────────
  - Deregister from target group (if still registered)
  - Terminate
```

### Timeline Summary

```
Week 1, Day 1:  Phase 1 — Security Groups + SSM        (30 min, $0)
Week 1, Day 2:  Phase 2 — VPC Peering + Atlas lockdown  (1 hr,  $0)
Week 2:         Phase 3 — Private Subnets + NAT          (2 hrs, +$33/mo)
Week 3:         Phase 4 — ASG setup                      (1 hr,  $0)
                                                    ─────────────────
                                              Total:  ~5 hours, +$33/month
```

### Rollback Plan

At every phase, you can roll back:

- **Phase 1 rollback:** Re-attach the old security group to EC2 and ALB. Takes 2 minutes.
- **Phase 2 rollback:** Re-add 0.0.0.0/0 to Atlas IP Access List. Takes 1 minute.
- **Phase 3 rollback:** Old instances are not terminated until new ones are verified. Just deregister new instances and re-register old ones.
- **Phase 4 rollback:** Delete ASG (it terminates its instances), re-launch manual instances.

---

## Quick Reference: Decision Matrix

| Question                          | Answer                                                                                             |
| --------------------------------- | -------------------------------------------------------------------------------------------------- |
| Should I fix Security Groups?     | **YES, today.** Free, 15 min, massive impact.                                                      |
| Should I set up VPC Peering?      | **YES, this week.** Free, 30 min, eliminates biggest vulnerability.                                |
| Should I set up SSM?              | **YES, this week.** Free, 15 min, replaces SSH.                                                    |
| Should I move to private subnets? | **Yes, within 2 weeks.** $33/month, proper architecture.                                           |
| Should I set up PrivateLink?      | **No.** VPC Peering is free and sufficient.                                                        |
| Should I set up VPC Flow Logs?    | **Yes, during Phase 3.** $1-3/month, useful for debugging.                                         |
| Should I create a new VPC?        | **Optional.** You can add private subnets to your default VPC. A new VPC is cleaner but more work. |
| Should I set up NACLs?            | **Later.** Security Groups are sufficient for now. NACLs add defense-in-depth but complexity.      |

---

## Glossary

| Term                 | Simple Definition                                                                       |
| -------------------- | --------------------------------------------------------------------------------------- |
| **VPC**              | Your private network in AWS. An isolated section of the cloud.                          |
| **Subnet**           | A subdivision of your VPC with its own IP range and routing rules.                      |
| **CIDR**             | An IP range notation. `10.0.0.0/16` = all IPs from 10.0.0.0 to 10.0.255.255.            |
| **Internet Gateway** | The door between your VPC and the internet.                                             |
| **NAT Gateway**      | A one-way door that lets private instances reach the internet (outbound only).          |
| **Route Table**      | The map that tells traffic where to go in your VPC.                                     |
| **Security Group**   | A stateful firewall attached to a resource (EC2, ALB, etc.). Allow-only rules.          |
| **NACL**             | A stateless firewall at the subnet level. Allow and deny rules.                         |
| **VPC Peering**      | A free, private connection between two VPCs (yours and Atlas's).                        |
| **PrivateLink**      | A paid, one-way private endpoint from your VPC to a service.                            |
| **SSM**              | AWS Systems Manager. Session Manager lets you get a shell without SSH.                  |
| **ASG**              | Auto Scaling Group. Automatically launches/terminates EC2 instances based on rules.     |
| **Flow Logs**        | Network traffic logs for your VPC. Who talked to whom, what port, accepted or rejected. |
| **ENI**              | Elastic Network Interface. A virtual network card attached to an instance.              |
| **EIP**              | Elastic IP. A static public IP you can assign to resources.                             |

---

## AWS Documentation Links

| Topic                   | URL                                                                               |
| ----------------------- | --------------------------------------------------------------------------------- |
| VPC Overview            | https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html          |
| Default VPC             | https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html                 |
| Subnets                 | https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html           |
| Security Groups         | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html         |
| NAT Gateway             | https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html             |
| VPC Peering             | https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html           |
| PrivateLink             | https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html       |
| VPC Flow Logs           | https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html                   |
| SSM Session Manager     | https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html |
| Atlas VPC Peering       | https://www.mongodb.com/docs/atlas/security-vpc-peering/                          |
| Atlas Private Endpoints | https://www.mongodb.com/docs/atlas/security-private-endpoint/                     |

# DZZLO OMS API — AWS Backend Deployment Runbook

Manual blue/green deployment of `dzzlo_oms_api` on EC2: update the standalone **live** server in place, verify it, bake a new AMI from it, roll the auto-scale fleet onto that AMI, then restore normal traffic weights.

**Conventions:** **bold** = AWS console section · _italics_ = button/UI control · `code` = terminal command.

## Glossary

| Abbr. | Meaning                                                       |
| ----- | ------------------------------------------------------------- |
| LB    | Load Balancer (ALB `dzzlo-load-balancer`)                     |
| TG    | Target Group                                                  |
| ASG   | Auto Scaling Group                                            |
| LT    | Launch Template (replaces legacy Launch Configurations, "LC") |
| AMI   | Amazon Machine Image                                          |
| pm2   | Node.js process manager running `dzzlo_oms.js` on each server |

## Architecture at a glance

```
                         weight 1   ┌─ DzzloOMS-TG ──→ "live" t3.micro  (standalone, SSH-managed)
Internet ─ HTTPS:443 ─→ ALB ────────┤
                         weight 5   └─ ASG-TG ───────→ ASG fleet, t3.small (launched from LT + AMI)
```

- **Steady state:** listener forwards weighted `DzzloOMS-TG : ASG-TG = 1 : 5`.
- **Deploy model:** the live server is both a canary and the bake source — update it first, image it, then refresh the ASG from the new image.

## Prerequisites

- AWS console access (EC2: Instances, Load Balancers, AMIs, Launch Templates, Auto Scaling Groups).
- Key file `dzzlooms.pem` on the Mac.
- Git credentials (username + token) for the `dzzlo_oms_api` repo.
- DB migration queries ready, if this release changes the schema (Phase 8).

---

## Phase 1 — Take the live server out of rotation

1. Log in to **AWS** → **EC2** → **Instances**. You will see two kinds of instances: the standalone **live** server (t3.micro) and the ASG-launched server(s).
2. Go to **Load Balancers** → select `dzzlo-load-balancer` → **Listeners** → _HTTPS : 443_ → _Actions_ → _Edit listener_.
3. Set **DzzloOMS-TG** (live server) weight to **0** → _Save changes_. All traffic now goes to the ASG fleet.

## Phase 2 — SSH into the live server

1. **Instances** → select the _t3 micro live_ server (the non-ASG instance) → _Connect_ → **SSH client** tab → copy the example SSH command.
2. In a local terminal, go to the key folder and run the command, replacing `root` with `ubuntu`:

```bash
cd ~/Documents/KIT/AWS/DzzloOMS
ssh -i "dzzlooms.pem" ubuntu@ec2-65-1-134-226.ap-south-1.compute.amazonaws.com
```

> [!note]
> The hostname/IP changes if the instance was stopped and started — always copy a fresh command from the console's **SSH client** tab. (Dragging the `.pem` file from Finder into the terminal also pastes its path.)

## Phase 3 — Update code and restart pm2

On the server:

```bash
cd dzzlo_oms_api/
git pull            # enter git username & password/token when prompted
```

Re-register the app with pm2 and restart:

```bash
pm2 unstartup       # copy the command line it prints and run it
pm2 startup         # copy the command line it prints and run it
pm2 start ecosystem.config.js --env production
pm2 logs            # confirm a clean start, then Ctrl+C to exit
pm2 save
exit
```

## Phase 4 — Health check

1. **Instances** → select the live server → **Details** → copy the **Public IPv4 address** using the _copy_ icon. Do **not** use _open address_ — that opens `https://`, and the instance itself serves plain `http`.
2. In a browser open `http://<Public-IPv4>/healthcheck` and confirm the API responds.

## Phase 5 — Bake a new AMI from the live server

1. **Instances** → select the _live_ (non-ASG) instance → _Actions_ → _Image and templates_ → _Create image_.
2. Name the image with the server name + today's date → _Create image_.
3. Go to the **AMIs** tab and wait until the new AMI's status is **Available**. Note its exact name — you will search for it in the next phase.

> Image creation may briefly reboot the instance; that is fine, it is out of rotation.

## Phase 6 — New Launch Template version

1. **Launch Templates** → select the template → _Actions_ → _Modify template (Create new version)_.
2. **Launch template name and version description** → describe like `ASG-LTemplate-T3smallInst-latest-<date>` (e.g. `…-20march2023`).
3. **Application and OS Images (Amazon Machine Image)** → **My AMIs** tab → select the newly created AMI (latest date).
4. _Create template version_, then set the **default version** to this latest version (_Actions_ → _Set default version_).

## Phase 7 — Shift all traffic to the updated live server

**Load Balancers** → _Listeners_ → _Edit listener_ → **DzzloOMS-TG** weight **1**, **ASG-TG** weight **0** → _Save changes_.

The updated live server now serves all requests while the ASG is rolled.

## Phase 8 — DB migration window _(only if this release changes the schema)_

1. **Load Balancers** → **Network mapping** (_description_ → _edit subnets_ in the old console) → change subnets to **1a & 1c**. The LB stays alive but stops receiving traffic — this is the maintenance window.
2. Run the release's database update queries on the DB server.
3. Change the subnets back to **1a & 1b** to resume traffic.

> [!warning]
> This subnet swap is a deliberate hard-downtime hack; existing connections drop while LB nodes move. See [Recommended improvements](#recommended-improvements) for a cleaner maintenance mode.

## Phase 9 — Roll the ASG onto the new template

1. **Auto Scaling Groups** → select the group → _Edit_ → set **Launch template version** to the new version → _Update_. Confirm the ASG's template version is correct.
2. (Optional, before refreshing) SSH into the **current** ASG instance and note `pm2 logs` / `git log` — this is the old code you are replacing.
3. Start an **Instance refresh** (_Instance refresh_ tab → _Start instance refresh_) so the ASG replaces its instances with ones from the new AMI.
4. When the new ASG instance is running, verify it the same way as [Phase 4](#phase-4--health-check) (its Public IPv4 + `/healthcheck`), and/or SSH in and check `pm2 logs` / `git log` show the new code. The ASG is receiving no traffic at this point (weight 0), so verification is safe.

## Phase 10 — Restore steady-state weights

**Load Balancers** → _Listeners_ → _Edit listener_ → **DzzloOMS-TG** weight **1**, **ASG-TG** weight **5** → _Save changes_.

Deployment complete — both target groups serve at the normal 1 : 5 ratio.

## Rollback

| Situation                              | Action                                                                                                                          |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Live server bad, ASG not yet refreshed | ASG still runs the old code: set listener weights **DzzloOMS-TG 0 / ASG-TG 1** and fix the live server off-line.                |
| ASG refreshed onto a bad AMI           | **Launch Templates** → _Set default version_ back to the previous version → run another **Instance refresh** → restore weights. |
| DB migration went wrong                | Re-open the maintenance window (Phase 8) and apply the reverse queries. Prefer backward-compatible migrations (see below).      |

---

## Recommended improvements

### Quick wins (no architecture change)

1. **Simplify the pm2 step.** `pm2 unstartup` / `pm2 startup` configure boot persistence and are only needed **once per new instance**. A routine deploy only needs:

   ```bash
   git pull && pm2 restart dzzlo_oms && pm2 save
   ```

2. **Replace the subnet-swap hack with a listener rule.** Add a fixed-response rule on the HTTPS:443 listener (priority 1, respond `503 – under maintenance`) and enable/disable it for the migration window. Instant, reversible, no LB node churn, nothing to forget to restore.
3. **Health-check via the target group, not the public IP.** After deploying, watch **Target Groups → Targets** until the instance is _healthy_ against `/healthcheck`. Then the instances' security group can drop public HTTP entirely (see security below).
4. **Point the ASG at the `Latest` launch template version** (or rely on `Default` since Phase 6 already sets it). Phase 9 step 1 then disappears — a deploy becomes: bake AMI → new LT version → instance refresh.

### Security

1. **Use SSM Session Manager instead of SSH.** _Connect → Session Manager_ gives shell access with no open port 22, no `.pem` file sitting in `~/Documents` to protect or rotate, and every session logged in CloudTrail. Attach the `AmazonSSMManagedInstanceCore` policy to the instance role, then remove inbound 22 from the security group.
2. **Stop typing git credentials on the server.** Use a fine-grained, read-only deploy token (or SSH deploy key) stored once in the server's git credential store — or better, stop pulling source on production at all (see pipeline below).
3. **Tighten security groups.** App instances should accept HTTP only **from the ALB's security group**, not `0.0.0.0/0` (the public-IP health check currently requires open HTTP). The DB should accept connections only from the app security group and never be publicly reachable.
4. **Keep secrets out of AMIs.** Every baked AMI snapshots whatever `.env`/config is on disk. Move runtime secrets to SSM Parameter Store (free) or Secrets Manager and fetch them at boot via the instance role.
5. **Patch drift.** Each AMI freezes an aging Ubuntu. Run `sudo apt update && sudo apt upgrade` before baking, or enable SSM Patch Manager for the fleet.
6. **Ship pm2 logs to CloudWatch.** ASG instances take their logs with them when they scale in; the CloudWatch agent (or `pm2-cloudwatch` style forwarding) preserves them for incident review.
7. **Console hygiene.** Deploy with an IAM user/Identity Center role with MFA — never the root account.

### Ease of deployment — a phased path

| Phase | Change                                                                                                                                                                                                                                | What it removes                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1     | **Artifact-based launches:** launch-template user-data pulls a versioned build (S3 object or git tag) and starts pm2 on boot.                                                                                                         | AMI baking and LT versioning per release — a deploy becomes _upload artifact → instance refresh_.         |
| 2     | **AWS CodeDeploy + CodePipeline** (CodeDeploy is free on EC2): push to the release branch → build → deploy to the live server → approval gate → rolling/blue-green deploy to the ASG with automatic rollback on failed health checks. | All console clicking, SSH sessions, and manual weight juggling.                                           |
| 3     | _(Optional, longer term)_ **Containerize** the API and run on ECS Fargate or App Runner.                                                                                                                                              | AMIs, pm2, SSH, and instance management entirely; rolling deploys and health-gated cutovers are built in. |

### One architectural observation

At steady state the 1 : 5 weighting sends ~17% of production traffic to the hand-managed t3.micro while the fleet runs t3.small — mixed capacity, and a single un-autoscaled "pet" in the production path. Consider either keeping **DzzloOMS-TG at weight 0** in steady state (making the live box purely a staging/bake server) or matching its instance type to the fleet.

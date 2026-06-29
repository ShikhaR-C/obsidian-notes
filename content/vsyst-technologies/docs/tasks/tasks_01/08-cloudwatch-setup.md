# CloudWatch Agent Setup — Centralized Logging & Monitoring

> Stream all server logs (PM2, Nginx, system) and server stats (CPU, memory, disk) to AWS CloudWatch.
> One-time setup on EC2. No code changes needed.

---

## Prerequisites

- EC2 instance with IAM role attached (not access keys — roles are more secure and auto-rotate)
- AWS CLI installed on the server
- PM2 and Nginx already running

---

## Step 1: Create IAM Role for CloudWatch

**Where:** AWS Console → IAM → Roles

1. Create a new role for EC2
2. Attach these managed policies:
   - `CloudWatchAgentServerPolicy` — allows writing logs and metrics
   - `AmazonSSMManagedInstanceCore` — allows SSM parameter store (agent stores its config there)
3. Name it: `EC2-CloudWatch-Role`
4. Attach the role to your EC2 instance:
   - EC2 Console → select instance → Actions → Security → Modify IAM Role → select `EC2-CloudWatch-Role`

**Why IAM role instead of access keys:** Roles auto-rotate credentials. Access keys sitting in a config file are a security risk — if the server is compromised, the keys are exposed. With roles, there are no keys on disk.

---

## Step 2: Install CloudWatch Agent

SSH into your EC2 instance:

```bash
# Amazon Linux 2 / AL2023
sudo yum install -y amazon-cloudwatch-agent

# Ubuntu
sudo apt-get update && sudo apt-get install -y amazon-cloudwatch-agent
```

Verify installation:

```bash
amazon-cloudwatch-agent-ctl -a status
```

---

## Step 3: Create Agent Configuration

Create the config file:

```bash
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

Paste this configuration (adjust paths if your setup differs):

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root",
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/.pm2/logs/*-out.log",
            "log_group_name": "/dzzlo/pm2/stdout",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30,
            "timestamp_format": "%Y-%m-%dT%H:%M:%S"
          },
          {
            "file_path": "/home/ec2-user/.pm2/logs/*-error.log",
            "log_group_name": "/dzzlo/pm2/stderr",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30,
            "timestamp_format": "%Y-%m-%dT%H:%M:%S"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/dzzlo/nginx/access",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/dzzlo/nginx/error",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/dzzlo/system/messages",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/secure",
            "log_group_name": "/dzzlo/system/secure",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 14,
            "timestamp_format": "%b %d %H:%M:%S"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "Dzzlo/Server",
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
        "totalcpu": true
      },
      "mem": {
        "measurement": ["mem_used_percent", "mem_used", "mem_available"]
      },
      "disk": {
        "measurement": ["disk_used_percent", "disk_free"],
        "resources": ["/"]
      },
      "net": {
        "measurement": ["bytes_sent", "bytes_recv"],
        "resources": ["eth0"]
      },
      "processes": {
        "measurement": ["total", "running", "sleeping", "zombies"]
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}"
    }
  }
}
```

### What this config collects

**Logs:**

| Log Group                | Source           | What it captures                                                        |
| ------------------------ | ---------------- | ----------------------------------------------------------------------- |
| `/dzzlo/pm2/stdout`      | PM2 stdout logs  | All `console.log` output — request logs, startup messages, DB connected |
| `/dzzlo/pm2/stderr`      | PM2 stderr logs  | All `console.error` output — unhandled errors, crashes, stack traces    |
| `/dzzlo/nginx/access`    | Nginx access log | Every HTTP request — IP, method, URL, status, response time             |
| `/dzzlo/nginx/error`     | Nginx error log  | Nginx errors — upstream failures, connection timeouts, config errors    |
| `/dzzlo/system/messages` | System log       | OS-level events — service starts/stops, kernel messages, cron output    |
| `/dzzlo/system/secure`   | Auth log         | SSH logins, sudo commands — security audit trail                        |

**Metrics (every 60 seconds):**

| Metric        | Why                                                     |
| ------------- | ------------------------------------------------------- |
| CPU usage     | Detect high load, size your instance correctly          |
| Memory used % | Catch memory leaks before OOM kills your process        |
| Disk used %   | Prevent disk-full crashes                               |
| Network bytes | Spot unusual traffic patterns (DDoS, data exfiltration) |
| Process count | Zombies = something is broken                           |

---

## Step 4: Start the Agent

```bash
# Load the config and start
sudo amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Verify it's running
sudo amazon-cloudwatch-agent-ctl -a status
```

Expected output should show `"status": "running"`.

**Enable on boot (so it survives restarts):**

```bash
sudo systemctl enable amazon-cloudwatch-agent
```

---

## Step 5: Verify in AWS Console

1. Go to **CloudWatch → Log groups** — you should see the `/dzzlo/*` groups appearing within 1-2 minutes
2. Go to **CloudWatch → Metrics → Custom Namespaces → Dzzlo/Server** — server stats should appear within 2-3 minutes
3. Click into any log group → check that log entries are flowing

---

## Step 6: Set Up Log Metric Filters & Alarms

**Where:** CloudWatch → Log groups → select group → Metric filters

### Filter 1: PM2 Error Count

- Log group: `/dzzlo/pm2/stderr`
- Filter pattern: `ERROR` (or leave blank to count all stderr lines)
- Metric name: `PM2ErrorCount`
- Alarm: > 20 errors in 5 minutes → SNS notification

### Filter 2: Nginx 5xx Errors

- Log group: `/dzzlo/nginx/access`
- Filter pattern: `[ip, dash, user, timestamp, request, status=5*, size, ...]`
- Metric name: `Nginx5xxCount`
- Alarm: > 10 in 5 minutes → SNS notification

### Filter 3: Nginx Upstream Timeout

- Log group: `/dzzlo/nginx/error`
- Filter pattern: `upstream timed out`
- Metric name: `NginxUpstreamTimeout`
- Alarm: > 5 in 5 minutes → SNS notification

### Filter 4: Server Disk Full Warning

- Metric: `Dzzlo/Server → disk_used_percent`
- Alarm: > 80% for 5 minutes → SNS notification

### Filter 5: Memory High

- Metric: `Dzzlo/Server → mem_used_percent`
- Alarm: > 85% for 5 minutes → SNS notification

---

## Step 7: (Optional) Export Old Logs to S3

For long-term archival at low cost:

1. Create an S3 bucket: `dzzlo-logs-archive`
2. CloudWatch → Log groups → Actions → Export to S3
3. Or set up automatic export with a Lambda on a schedule

Cost comparison:

- CloudWatch: ~$0.50/GB ingestion + $0.03/GB storage/month
- S3: ~$0.023/GB storage/month (Standard), $0.004/GB (Glacier)

Keep 30 days in CloudWatch for active search, archive older logs to S3.

---

## Troubleshooting

| Problem                        | Check                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| No logs appearing              | `sudo cat /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log` for errors |
| Permission denied on log files | Agent runs as root by default — check file permissions on PM2 logs                      |
| No metrics appearing           | Verify IAM role has `CloudWatchAgentServerPolicy`                                       |
| Wrong log file paths           | Check actual PM2 log path: `pm2 logs --lines 0` shows the file paths                    |
| Agent not starting on boot     | `sudo systemctl enable amazon-cloudwatch-agent`                                         |

---

## Adjustments for Your Setup

- **PM2 log path:** If you run PM2 as a different user, adjust `/home/ec2-user/.pm2/logs/` to the correct path. Run `pm2 logs --lines 0` to see the actual paths.
- **Nginx paths:** If Nginx logs are elsewhere, check with `nginx -t` or look at your Nginx config.
- **Ubuntu vs Amazon Linux:** System log is `/var/log/syslog` on Ubuntu instead of `/var/log/messages`. Auth log is `/var/log/auth.log` instead of `/var/log/secure`.
- **retention_in_days:** Set per log group. Stderr (errors) at 30 days, system/secure at 14 days. Adjust based on your needs and cost tolerance.

---

## Cost Estimate (t3.small, ~650 req/day)

| Item                             | Estimate                           |
| -------------------------------- | ---------------------------------- |
| Log ingestion (~100MB/month)     | ~$0.05/month                       |
| Log storage (30 day retention)   | ~$0.003/month                      |
| Custom metrics (6 metrics × 60s) | Free tier covers 10 custom metrics |
| **Total**                        | **< $1/month**                     |

At your scale, this is essentially free.

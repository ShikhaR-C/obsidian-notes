# DZZLO-OMS Maximum Automation Strategy

> Complete automation playbook for a solo developer running Node.js/Express/MongoDB on AWS.
> Prioritized by impact-to-effort ratio. Each section is standalone and implementable.

---

## Priority Matrix (Implement in This Order)


| #   | Topic                         | Priority          | Effort   | Monthly Cost   | Impact                                |
| --- | ----------------------------- | ----------------- | -------- | -------------- | ------------------------------------- |
| 6   | PM2 cluster mode              | P0 - Do Now       | 1 hour   | $0             | Zero-downtime deploys, full CPU usage |
| 7   | Automated SSL/TLS (ACM)       | P0 - Do Now       | 2 hours  | $0             | Eliminate manual cert renewal         |
| 1   | GitHub Actions CI/CD          | P0 - Do Now       | 4 hours  | $0 (free tier) | Automated testing + deploy on merge   |
| 8   | Log rotation & cleanup        | P1 - This Week    | 1 hour   | $0             | Prevent disk-full crashes             |
| 10  | Self-healing                  | P1 - This Week    | 2 hours  | $0             | Auto-restart on crash                 |
| 11  | Automated security patching   | P2 - This Month   | 3 hours  | $0             | OS patches without SSH                |
| 5   | Automated AMI creation        | P2 - This Month   | 4 hours  | ~$1/mo         | Reproducible server images            |
| 9   | Scheduled tasks (EventBridge) | P2 - This Month   | 4 hours  | ~$1/mo         | Cron without server dependency        |
| 12  | Database automation (Atlas)   | P2 - This Month   | 2 hours  | $0 (included)  | Auto-scaling, alerts                  |
| 2   | AWS CodeDeploy                | P3 - Next Quarter | 1 day    | $0             | Rolling deploys to ASG                |
| 3   | AWS CodePipeline              | P3 - Next Quarter | 1-2 days | ~$1/mo         | Full AWS-native pipeline              |
| 4   | Infrastructure as Code        | P3 - Next Quarter | 2-3 days | $0             | Reproducible infra                    |


---

## 1. GitHub Actions CI/CD

**What:** Run Jest tests on every PR, auto-deploy to EC2 on merge to master via SSH.

**Why first:** Prevents deploying broken code. Replaces `ssh → git pull → pm2 restart`. Free for public repos, 2000 min/mo for private repos.

### Complete Workflow: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  pull_request:
    branches: [master]
  push:
    branches: [master]

env:
  NODE_VERSION: '18'

jobs:
  # ─── TEST ────────────────────────────────────────────────
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Create test env file
        run: cp .env.example .env.development

      - name: Run tests
        run: yarn test --forceExit --detectOpenHandles
        env:
          NODE_ENV: development
          # mongodb-memory-server downloads mongod binary automatically
          # No external MongoDB needed — tests use MongoMemoryServer

      # Optional: upload coverage
      # - name: Upload coverage
      #   uses: actions/upload-artifact@v4
      #   with:
      #     name: coverage
      #     path: coverage/

  # ─── DEPLOY (only on push to master) ─────────────────────
  deploy:
    name: Deploy to EC2
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          port: 22
          script_stop: true
          script: |
            cd /home/${{ secrets.EC2_USER }}/dzzlo_oms_api
            git fetch origin master
            git reset --hard origin/master
            yarn install --frozen-lockfile --production
            pm2 reload ecosystem.config.js --env production
            pm2 save
            echo "Deploy complete at $(date)"

      - name: Health check
        run: |
          sleep 10
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://${{ secrets.EC2_HOST }}/healthcheck)
          if [ "$STATUS" != "200" ]; then
            echo "Health check failed with status $STATUS"
            exit 1
          fi
          echo "Health check passed"
```

### Required GitHub Secrets

Go to **Repository > Settings > Secrets and variables > Actions** and add:


| Secret        | Value                                                     |
| ------------- | --------------------------------------------------------- |
| `EC2_HOST`    | Your EC2 public IP or domain (e.g., `test.doms.vsyst.in`) |
| `EC2_USER`    | `ubuntu` or `ec2-user`                                    |
| `EC2_SSH_KEY` | Contents of your `.pem` private key file                  |


### Multi-Server Deploy (testing + production)

```yaml
  deploy-testing:
    name: Deploy to Testing
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.TESTING_EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd ~/dzzlo_oms_api
            git pull origin master
            yarn install --frozen-lockfile
            pm2 reload ecosystem.config.js --env testing
            pm2 save

  deploy-production:
    name: Deploy to Production
    needs: deploy-testing
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval in GitHub UI
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.PROD_EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.PROD_EC2_SSH_KEY }}
          script: |
            cd ~/dzzlo_oms_api
            git pull origin master
            yarn install --frozen-lockfile --production
            pm2 reload ecosystem.config.js --env production
            pm2 save
```

### Cost

- **Free tier:** 2,000 minutes/month for private repos (enough for ~200 deploys)
- **Public repos:** Unlimited
- **Overages:** $0.008/min for Linux runners

### Effort: 4 hours

- 2 hours: Create workflow, configure secrets
- 1 hour: Test with a PR
- 1 hour: Add health check, notifications

### Documentation

- [https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-nodejs](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-nodejs)
- [https://github.com/appleboy/ssh-action](https://github.com/appleboy/ssh-action)
- [https://docs.github.com/en/actions/security-guides/encrypted-secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 2. AWS CodeDeploy

**What:** Blue/green or rolling deploys to an Auto Scaling Group with automatic rollback on health check failure.

**Why:** Eliminates SSH-based deploys entirely. Automatically rolls back if the new version fails health checks. Required when you move to multiple EC2 instances behind an ASG.

### `appspec.yml` (project root)

```yaml
version: 0.0
os: linux

files:
  - source: /
    destination: /home/ubuntu/dzzlo_oms_api
    overwrite: true

file_exists_behavior: OVERWRITE

permissions:
  - object: /home/ubuntu/dzzlo_oms_api
    owner: ubuntu
    group: ubuntu
    mode: 755
    type:
      - directory
      - file

hooks:
  BeforeInstall:
    - location: scripts/codedeploy/before_install.sh
      timeout: 300
      runas: ubuntu

  AfterInstall:
    - location: scripts/codedeploy/after_install.sh
      timeout: 300
      runas: ubuntu

  ApplicationStart:
    - location: scripts/codedeploy/application_start.sh
      timeout: 300
      runas: ubuntu

  ValidateService:
    - location: scripts/codedeploy/validate_service.sh
      timeout: 120
      runas: ubuntu
```

### `scripts/codedeploy/before_install.sh`

```bash
#!/bin/bash
set -e

echo "[CodeDeploy] BeforeInstall — stopping PM2 processes"
cd /home/ubuntu/dzzlo_oms_api

# Stop PM2 gracefully if running
if pm2 list 2>/dev/null | grep -q "dzzlo-oms"; then
  pm2 stop dzzlo-oms || true
fi

# Clean up old node_modules (optional — speeds up fresh installs)
# rm -rf node_modules
```

### `scripts/codedeploy/after_install.sh`

```bash
#!/bin/bash
set -e

echo "[CodeDeploy] AfterInstall — installing dependencies"
cd /home/ubuntu/dzzlo_oms_api

# Install production dependencies only
yarn install --frozen-lockfile --production

# Ensure correct ownership
chown -R ubuntu:ubuntu /home/ubuntu/dzzlo_oms_api
```

### `scripts/codedeploy/application_start.sh`

```bash
#!/bin/bash
set -e

echo "[CodeDeploy] ApplicationStart — starting PM2"
cd /home/ubuntu/dzzlo_oms_api

# Reload (zero-downtime) or start fresh
if pm2 list 2>/dev/null | grep -q "dzzlo-oms"; then
  pm2 reload ecosystem.config.js --env production
else
  pm2 start ecosystem.config.js --env production
fi

pm2 save

echo "[CodeDeploy] Application started successfully"
```

### `scripts/codedeploy/validate_service.sh`

```bash
#!/bin/bash
set -e

echo "[CodeDeploy] ValidateService — running health check"

RETRIES=10
DELAY=3
PORT=${PORT:-8030}

for i in $(seq 1 $RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/healthcheck || echo "000")
  if [ "$STATUS" = "200" ]; then
    echo "[CodeDeploy] Health check passed on attempt $i"
    exit 0
  fi
  echo "[CodeDeploy] Health check attempt $i/$RETRIES — status $STATUS, retrying in ${DELAY}s..."
  sleep $DELAY
done

echo "[CodeDeploy] Health check FAILED after $RETRIES attempts"
exit 1
```

### Deployment Group Configuration (AWS CLI)

```bash
# Create CodeDeploy application
aws deploy create-application \
  --application-name dzzlo-oms \
  --compute-platform Server

# Create deployment group with auto-rollback
aws deploy create-deployment-group \
  --application-name dzzlo-oms \
  --deployment-group-name dzzlo-oms-production \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --auto-scaling-groups dzzlo-oms-asg \
  --service-role-arn arn:aws:iam::ACCOUNT_ID:role/CodeDeployServiceRole \
  --auto-rollback-configuration "enabled=true,events=DEPLOYMENT_FAILURE,DEPLOYMENT_STOP_ON_ALARM" \
  --alarm-configuration "enabled=true,alarms=[{name=dzzlo-oms-5xx-alarm}]" \
  --ec2-tag-filters "Key=Name,Value=dzzlo-oms,Type=KEY_AND_VALUE"
```

### Deployment Configurations Explained


| Config                          | Behavior                               | Best For             |
| ------------------------------- | -------------------------------------- | -------------------- |
| `CodeDeployDefault.OneAtATime`  | Deploy to 1 instance at a time         | Maximum safety       |
| `CodeDeployDefault.HalfAtATime` | Deploy to 50% of instances at a time   | Balance speed/safety |
| `CodeDeployDefault.AllAtOnce`   | Deploy to all instances simultaneously | Dev/testing          |


### Automatic Rollback

CodeDeploy automatically rolls back when:

- **Deployment fails** — any lifecycle hook script exits non-zero
- **CloudWatch alarm triggers** — e.g., 5xx error rate spike
- **Health check fails** — ValidateService hook returns non-zero

Rollback redeploys the last known good revision automatically.

### EC2 Instance Prerequisites

```bash
# Install CodeDeploy agent on Amazon Linux 2 / Ubuntu
sudo yum install -y ruby wget  # Amazon Linux
# sudo apt install -y ruby-full wget  # Ubuntu

cd /tmp
wget https://aws-codedeploy-ap-south-1.s3.ap-south-1.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto
sudo systemctl start codedeploy-agent
sudo systemctl enable codedeploy-agent
```

### Cost

- **CodeDeploy to EC2:** Free (no charge for EC2/on-premises deployments)
- **Only charged for:** ECS/Lambda deployments

### Effort: 1 day

- 2 hours: Install CodeDeploy agent on EC2, create IAM roles
- 2 hours: Write appspec.yml and lifecycle scripts
- 2 hours: Test deployment, configure rollback
- 2 hours: Integrate with GitHub Actions or CodePipeline

### Documentation

- [https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html)
- [https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-rollback-and-redeploy.html](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-rollback-and-redeploy.html)
- [https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html)

---

## 3. AWS CodePipeline

**What:** Full AWS-native pipeline: GitHub (source) -> CodeBuild (test) -> CodeDeploy (deploy). Fully managed, no server needed.

**Why:** If you want everything inside AWS instead of GitHub Actions. Better if you eventually want approval gates, multiple environments, and integration with other AWS services.

### Pipeline Architecture

```
GitHub (push to master)
    │
    ▼
CodePipeline (orchestrator)
    │
    ├── Stage 1: Source
    │   └── GitHub v2 connection → downloads code
    │
    ├── Stage 2: Build + Test (CodeBuild)
    │   └── buildspec.yml → npm install, npm test
    │
    └── Stage 3: Deploy (CodeDeploy)
        └── appspec.yml → deploy to EC2/ASG
```

### `buildspec.yml` (project root)

```yaml
version: 0.2

env:
  variables:
    NODE_ENV: "development"

phases:
  install:
    runtime-versions:
      nodejs: 18
    commands:
      - echo "Installing dependencies..."
      - yarn install --frozen-lockfile

  pre_build:
    commands:
      - echo "Creating test environment file..."
      - cp .env.example .env.development

  build:
    commands:
      - echo "Running tests on $(date)"
      - yarn test --forceExit --detectOpenHandles
    finally:
      - echo "Test phase completed"

  post_build:
    commands:
      - echo "Tests passed. Preparing deployment artifact..."
      - rm -rf node_modules
      - yarn install --frozen-lockfile --production

artifacts:
  files:
    - '**/*'
  exclude-paths:
    - 'node_modules/.cache/**/*'
    - '.git/**/*'
    - 'coverage/**/*'
    - 'test/**/*'
    - '.env.development'
    - '.env.testing'

cache:
  paths:
    - 'node_modules/**/*'
```

### Pipeline Setup (AWS CLI)

```bash
# 1. Create GitHub connection (do this in Console — requires OAuth)
#    Console > Developer Tools > Connections > Create connection > GitHub

# 2. Create CodeBuild project
aws codebuild create-project \
  --name dzzlo-oms-build \
  --source "type=CODEPIPELINE" \
  --artifacts "type=CODEPIPELINE" \
  --environment "type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_SMALL,image=aws/codebuild/amazonlinux2-x86_64-standard:5.0" \
  --service-role arn:aws:iam::ACCOUNT_ID:role/CodeBuildServiceRole

# 3. Create pipeline (JSON config)
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

### `pipeline.json`

```json
{
  "pipeline": {
    "name": "dzzlo-oms-pipeline",
    "roleArn": "arn:aws:iam::ACCOUNT_ID:role/CodePipelineServiceRole",
    "stages": [
      {
        "name": "Source",
        "actions": [
          {
            "name": "GitHub",
            "actionTypeId": {
              "category": "Source",
              "owner": "AWS",
              "provider": "CodeStarSourceConnection",
              "version": "1"
            },
            "configuration": {
              "ConnectionArn": "arn:aws:codestar-connections:ap-south-1:ACCOUNT_ID:connection/CONNECTION_ID",
              "FullRepositoryId": "YOUR_GITHUB_USER/dzzlo_oms_api",
              "BranchName": "master",
              "OutputArtifactFormat": "CODE_ZIP"
            },
            "outputArtifacts": [{ "name": "SourceOutput" }]
          }
        ]
      },
      {
        "name": "Build",
        "actions": [
          {
            "name": "CodeBuild",
            "actionTypeId": {
              "category": "Build",
              "owner": "AWS",
              "provider": "CodeBuild",
              "version": "1"
            },
            "configuration": {
              "ProjectName": "dzzlo-oms-build"
            },
            "inputArtifacts": [{ "name": "SourceOutput" }],
            "outputArtifacts": [{ "name": "BuildOutput" }]
          }
        ]
      },
      {
        "name": "Deploy",
        "actions": [
          {
            "name": "CodeDeploy",
            "actionTypeId": {
              "category": "Deploy",
              "owner": "AWS",
              "provider": "CodeDeploy",
              "version": "1"
            },
            "configuration": {
              "ApplicationName": "dzzlo-oms",
              "DeploymentGroupName": "dzzlo-oms-production"
            },
            "inputArtifacts": [{ "name": "BuildOutput" }]
          }
        ]
      }
    ]
  }
}
```

### GitHub Actions vs CodePipeline — Decision Guide


| Factor                | GitHub Actions                    | CodePipeline                   |
| --------------------- | --------------------------------- | ------------------------------ |
| **Setup effort**      | 1 file, 30 min                    | 3 services, 4+ hours           |
| **Cost**              | Free (2000 min/mo)                | ~$1/mo pipeline + CodeBuild    |
| **Flexibility**       | Thousands of marketplace actions  | AWS services only              |
| **SSH deploy**        | Built-in with appleboy/ssh-action | Requires CodeDeploy agent      |
| **Multi-environment** | Manual approval via environments  | Built-in approval actions      |
| **Recommendation**    | **Start here**                    | Move to this when you have ASG |


### Cost

- **CodePipeline:** $1/month per active pipeline
- **CodeBuild:** $0.005/min (build.general1.small) — ~$0.50/mo for 100 builds
- **CodeDeploy to EC2:** Free

### Effort: 1-2 days

- 4 hours: Create IAM roles (CodePipeline, CodeBuild, CodeDeploy)
- 2 hours: Create GitHub connection, CodeBuild project
- 2 hours: Create and configure pipeline
- 4 hours: Test, debug, refine

### Documentation

- [https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html)
- [https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
- [https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html](https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html)

---

## 4. Infrastructure as Code (Terraform)

**What:** Define all AWS resources (EC2, ALB, ASG, Security Groups, IAM roles) in `.tf` files. Run `terraform apply` to create/update everything.

**Why:** Your entire infrastructure becomes reproducible. If an EC2 instance dies, you run one command instead of clicking through the Console for 2 hours. Critical for bus factor = 1.

### Project Structure

```
infra/
├── main.tf              # Provider, backend
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── vpc.tf               # VPC, subnets
├── security_groups.tf   # SG rules
├── alb.tf               # ALB, target group, listener
├── asg.tf               # Launch template, ASG
├── iam.tf               # IAM roles
└── terraform.tfvars     # Variable values (DO NOT COMMIT)
```

### `infra/main.tf`

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state in S3 (recommended)
  backend "s3" {
    bucket         = "dzzlo-terraform-state"
    key            = "oms/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "dzzlo-oms"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

### `infra/variables.tf`

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "min_size" {
  description = "Minimum ASG size"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum ASG size"
  type        = number
  default     = 2
}

variable "desired_capacity" {
  description = "Desired ASG capacity"
  type        = number
  default     = 1
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "test.doms.vsyst.in"
}
```

### `infra/security_groups.tf`

```hcl
resource "aws_security_group" "alb" {
  name_prefix = "dzzlo-alb-"
  vpc_id      = aws_vpc.main.id
  description = "ALB security group"

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP (redirect to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "ec2" {
  name_prefix = "dzzlo-ec2-"
  vpc_id      = aws_vpc.main.id
  description = "EC2 instance security group"

  ingress {
    description     = "App port from ALB"
    from_port       = 8030
    to_port         = 8030
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["YOUR_IP/32"]  # Restrict to your IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

### `infra/alb.tf`

```hcl
resource "aws_lb" "main" {
  name               = "dzzlo-oms-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true
}

resource "aws_lb_target_group" "app" {
  name     = "dzzlo-oms-tg"
  port     = 8030
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/healthcheck"
    matcher             = "200"
  }

  deregistration_delay = 30
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

### `infra/asg.tf`

```hcl
resource "aws_launch_template" "app" {
  name_prefix   = "dzzlo-oms-"
  image_id      = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.ec2.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2.name
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e

    # Install/update CodeDeploy agent
    sudo yum update -y
    sudo yum install -y ruby wget
    cd /tmp
    wget https://aws-codedeploy-${var.aws_region}.s3.${var.aws_region}.amazonaws.com/latest/install
    chmod +x ./install
    sudo ./install auto

    # Start application (if pre-baked AMI has the code)
    cd /home/ubuntu/dzzlo_oms_api
    pm2 start ecosystem.config.js --env production
    pm2 save
    pm2 startup | tail -1 | bash
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "dzzlo-oms-${var.environment}"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "app" {
  name                = "dzzlo-oms-asg"
  min_size            = var.min_size
  max_size            = var.max_size
  desired_capacity    = var.desired_capacity
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }

  tag {
    key                 = "Name"
    value               = "dzzlo-oms-${var.environment}"
    propagate_at_launch = true
  }
}
```

### `infra/outputs.tf`

```hcl
output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "asg_name" {
  description = "Auto Scaling Group name"
  value       = aws_autoscaling_group.app.name
}
```

### Workflow

```bash
cd infra/
terraform init          # Download providers, init backend
terraform plan          # Preview changes (ALWAYS review)
terraform apply         # Apply changes (type 'yes')
terraform destroy       # Tear down everything (careful!)
```

### Cost

- **Terraform:** Free and open source
- **S3 state backend:** ~$0.02/mo
- **DynamoDB lock table:** Free tier covers it

### Effort: 2-3 days

- Day 1: VPC, security groups, ALB
- Day 2: ASG, launch template, IAM roles
- Day 3: Test, import existing resources, refine

### Documentation

- [https://developer.hashicorp.com/terraform/tutorials/aws-get-started](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- [https://registry.terraform.io/providers/hashicorp/aws/latest/docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [https://developer.hashicorp.com/terraform/language/import](https://developer.hashicorp.com/terraform/language/import) (import existing resources)

---

## 5. Automated AMI Creation

**What:** Build pre-configured AMIs automatically so new EC2 instances launch ready with Node.js, PM2, CodeDeploy agent, and your application pre-installed.

**Why:** Without this, every new EC2 instance requires manual setup. With AMIs, ASG launches fully configured instances automatically.

### Option A: AWS EC2 Image Builder (Recommended for Solo Dev)

**Console Setup:**

1. Go to **EC2 Image Builder** > Create image pipeline
2. Name: `dzzlo-oms-ami-pipeline`
3. Schedule: Monthly (or on-demand)
4. Base image: Amazon Linux 2023 or Ubuntu 22.04
5. Add components:
  - Install Node.js 18
  - Install PM2 globally
  - Install CodeDeploy agent
  - Install yarn
  - Clone repository
  - Install dependencies

**Component Document (YAML):**

```yaml
# image-builder-component.yml
name: DzzloOmsSetup
description: Install Node.js, PM2, and application dependencies
schemaVersion: 1.0

phases:
  - name: build
    steps:
      - name: InstallNodejs
        action: ExecuteBash
        inputs:
          commands:
            - curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            - sudo yum install -y nodejs git
            - sudo npm install -g pm2 yarn

      - name: InstallCodeDeployAgent
        action: ExecuteBash
        inputs:
          commands:
            - sudo yum install -y ruby wget
            - cd /tmp
            - wget https://aws-codedeploy-ap-south-1.s3.ap-south-1.amazonaws.com/latest/install
            - chmod +x ./install
            - sudo ./install auto
            - sudo systemctl enable codedeploy-agent

      - name: SetupApplication
        action: ExecuteBash
        inputs:
          commands:
            - sudo mkdir -p /home/ubuntu/dzzlo_oms_api
            - sudo chown ubuntu:ubuntu /home/ubuntu/dzzlo_oms_api

  - name: test
    steps:
      - name: VerifyNodejs
        action: ExecuteBash
        inputs:
          commands:
            - node --version
            - pm2 --version
            - yarn --version

      - name: VerifyCodeDeploy
        action: ExecuteBash
        inputs:
          commands:
            - sudo systemctl status codedeploy-agent
```

### Option B: HashiCorp Packer (More Portable)

`**packer/dzzlo-oms.pkr.hcl`:**

```hcl
packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

source "amazon-ebs" "dzzlo-oms" {
  ami_name      = "dzzlo-oms-{{timestamp}}"
  instance_type = "t3.micro"
  region        = var.aws_region
  source_ami_filter {
    filters = {
      name                = "amzn2-ami-hvm-*-x86_64-gp2"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["amazon"]
  }
  ssh_username = "ec2-user"

  tags = {
    Name        = "dzzlo-oms-ami"
    Environment = "production"
    BuildTime   = "{{timestamp}}"
  }
}

build {
  sources = ["source.amazon-ebs.dzzlo-oms"]

  provisioner "shell" {
    inline = [
      "sudo yum update -y",
      "curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -",
      "sudo yum install -y nodejs git ruby wget",
      "sudo npm install -g pm2 yarn",

      "# Install CodeDeploy agent",
      "cd /tmp",
      "wget https://aws-codedeploy-${var.aws_region}.s3.${var.aws_region}.amazonaws.com/latest/install",
      "chmod +x ./install",
      "sudo ./install auto",
      "sudo systemctl enable codedeploy-agent",

      "# Prepare application directory",
      "sudo mkdir -p /home/ec2-user/dzzlo_oms_api",
      "sudo chown ec2-user:ec2-user /home/ec2-user/dzzlo_oms_api"
    ]
  }
}
```

**Build command:**

```bash
cd packer/
packer init .
packer build dzzlo-oms.pkr.hcl
```

**Automate with GitHub Actions:**

```yaml
# .github/workflows/build-ami.yml
name: Build AMI
on:
  schedule:
    - cron: '0 2 1 * *'  # First of every month at 2 AM
  workflow_dispatch:       # Manual trigger

jobs:
  build-ami:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-packer@main
      - name: Build AMI
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          cd packer
          packer init .
          packer build dzzlo-oms.pkr.hcl
```

### Cost

- **Image Builder:** Free (you pay for the temporary EC2 instance ~$0.01 per build)
- **AMI storage:** ~$0.05/GB/month for EBS snapshots
- **Packer:** Free and open source

### Effort: 4 hours

- 2 hours: Write component/template
- 1 hour: Test build
- 1 hour: Schedule automation

### Documentation

- [https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html)
- [https://developer.hashicorp.com/packer/docs/builders/amazon/ebs](https://developer.hashicorp.com/packer/docs/builders/amazon/ebs)

---

## 6. PM2 Cluster Mode

**What:** Run your Node.js app on ALL available CPU cores with zero-downtime reloads. Currently you run a single process, wasting all but one core.

**Why:** Immediate performance improvement with a 1-line config change. Zero-downtime `pm2 reload` means users never see downtime during deploys.

### Updated `ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      cwd: __dirname,

      // ── Cluster Mode ──────────────────────────────────────
      instances: "max",        // Use all available vCPUs (or set to specific number like 2)
      exec_mode: "cluster",    // Enable cluster mode (required for multi-instance)

      // ── Zero-downtime ─────────────────────────────────────
      wait_ready: true,        // Wait for process.send('ready') before considering online
      listen_timeout: 10000,   // Max time (ms) to wait for ready signal
      kill_timeout: 5000,      // Graceful shutdown timeout (ms)

      // ── Reliability ───────────────────────────────────────
      max_memory_restart: "512M",  // Restart if memory exceeds 512MB
      max_restarts: 10,            // Max restarts within restart_delay window
      min_uptime: "5s",            // Min uptime to consider successfully started
      autorestart: true,           // Auto-restart on crash (default: true)

      // ── Logging ───────────────────────────────────────────
      time: true,                           // Timestamp in logs
      merge_logs: true,                     // Merge logs from all cluster instances
      error_file: "/home/ubuntu/.pm2/logs/dzzlo-oms-error.log",
      out_file: "/home/ubuntu/.pm2/logs/dzzlo-oms-out.log",

      // ── Environment ───────────────────────────────────────
      env: {
        NODE_ENV: "testing",
      },
      env_testing: {
        NODE_ENV: "testing",
      },
      env_production: {
        NODE_ENV: "production",
      },
    },
  ],
};
```

### Application Code Change (Optional but Recommended)

Add graceful shutdown and ready signal to `dzzlo_oms.js`:

```javascript
// At the end of dzzlo_oms.js, replace app.listen with:
const server = app.listen(port, () => {
  console.log(
    `Server is running in ${process.env.NODE_ENV} mode on- http://${SYSIPAddress}:${port}`
  );
  // Tell PM2 this process is ready to receive traffic
  if (process.send) {
    process.send('ready');
  }
});

// Graceful shutdown for zero-downtime reload
process.on('SIGINT', async () => {
  console.log('Received SIGINT. Graceful shutdown...');
  server.close(async () => {
    await mongoose.disconnect();
    console.log('Server closed. MongoDB disconnected.');
    process.exit(0);
  });
  // Force close after 5 seconds
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 5000);
});
```

### Commands

```bash
# Start in cluster mode
pm2 start ecosystem.config.js --env production

# Zero-downtime reload (one instance at a time)
pm2 reload dzzlo-oms

# Scale up/down
pm2 scale dzzlo-oms +2    # Add 2 more instances
pm2 scale dzzlo-oms 4     # Set to exactly 4 instances

# Monitor
pm2 monit                  # Real-time dashboard

# Check cluster status
pm2 list                   # Shows all instances with IDs
```

### Important Notes for Cluster Mode

1. **Socket.IO compatibility:** Your app uses `socket.io@2.4.1`. In cluster mode, you need sticky sessions or a Redis adapter:
  ```bash
   yarn add @socket.io/sticky @socket.io/cluster-adapter
  ```
   Or keep socket.io on a separate single-instance process.
2. **In-memory state:** Any in-memory variables (caches, counters) are NOT shared between cluster instances. Use Redis or MongoDB for shared state.
3. **Instance count for t3.micro:** t3.micro has 2 vCPUs, so `instances: "max"` creates 2 processes. For t3.small (2 vCPUs), same thing. For t3.medium (2 vCPUs), still 2.

### Cost

- $0 — This is a PM2 configuration change

### Effort: 1 hour

- 15 minutes: Update ecosystem.config.js
- 15 minutes: Add graceful shutdown code
- 30 minutes: Test reload behavior, verify Socket.IO works

### Documentation

- [https://pm2.keymetrics.io/docs/usage/cluster-mode/](https://pm2.keymetrics.io/docs/usage/cluster-mode/)
- [https://pm2.keymetrics.io/docs/usage/signals-clean-restart/](https://pm2.keymetrics.io/docs/usage/signals-clean-restart/)

---

## 7. Automated SSL/TLS Renewal

**What:** Use AWS Certificate Manager (ACM) for free, auto-renewing SSL certificates on your ALB. Never manually renew certs again.

**Why:** ACM certificates are free, auto-renew indefinitely, and require zero maintenance. If you are using Let's Encrypt + Certbot on Nginx, this eliminates that entire operational burden.

### Option A: ACM on ALB (Recommended)

**Setup Steps:**

```bash
# 1. Request a certificate
aws acm request-certificate \
  --domain-name "test.doms.vsyst.in" \
  --subject-alternative-names "*.doms.vsyst.in" \
  --validation-method DNS \
  --region ap-south-1

# 2. Get the CNAME record for DNS validation
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:ap-south-1:ACCOUNT_ID:certificate/CERT_ID \
  --query 'Certificate.DomainValidationOptions'

# 3. Add the CNAME record to your DNS provider
# (This proves you own the domain — one-time step)

# 4. Attach to ALB listener
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:listener/app/dzzlo-oms-alb/LB_ID/LISTENER_ID \
  --certificates CertificateArn=arn:aws:acm:ap-south-1:ACCOUNT_ID:certificate/CERT_ID \
  --protocol HTTPS \
  --port 443
```

**Key Facts:**

- ACM certificates are **completely free**
- Auto-renew before expiry (no cron, no certbot)
- **Cannot be exported** — only works with AWS services (ALB, CloudFront, API Gateway)
- **Regional** — must create one per region
- Wildcard certs (`*.doms.vsyst.in`) supported

### Option B: Let's Encrypt + Certbot (If No ALB)

If running Nginx directly on EC2 without ALB:

```bash
# Install certbot
sudo yum install -y certbot python3-certbot-nginx  # Amazon Linux
# sudo apt install -y certbot python3-certbot-nginx  # Ubuntu

# Get certificate
sudo certbot --nginx -d test.doms.vsyst.in --non-interactive --agree-tos -m your@email.com

# Auto-renewal cron (certbot installs this automatically)
# Verify:
sudo systemctl list-timers | grep certbot

# Manual test:
sudo certbot renew --dry-run
```

**Certbot auto-renewal:** Installed automatically as a systemd timer. Runs twice daily, renews if within 30 days of expiry.

### Recommendation

Use **ACM on ALB** (Option A). It is zero-maintenance and free. Let's Encrypt requires an EC2 process, can fail silently, and adds operational burden.

### Cost

- **ACM:** Free
- **Let's Encrypt:** Free (but requires compute time)

### Effort: 2 hours

- 30 minutes: Request ACM certificate
- 30 minutes: Add DNS validation CNAME record
- 30 minutes: Attach to ALB listener
- 30 minutes: Test HTTPS, redirect HTTP to HTTPS

### Documentation

- [https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)
- [https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html)
- [https://certbot.eff.org/instructions](https://certbot.eff.org/instructions)

---

## 8. Log Rotation & Cleanup

**What:** Prevent PM2 logs from filling the disk. Auto-rotate, compress, and delete old logs. Add MongoDB TTL indexes for automatic document cleanup.

**Why:** Unchecked PM2 logs will eventually fill your disk and crash the server. This is a silent time bomb.

### PM2 Log Rotation Module

```bash
# Install the module (runs as a PM2-managed process)
pm2 install pm2-logrotate

# Configure (persistent across restarts)
pm2 set pm2-logrotate:max_size 50M        # Rotate when file hits 50MB
pm2 set pm2-logrotate:retain 7            # Keep 7 rotated files
pm2 set pm2-logrotate:compress true       # Gzip old logs
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss
pm2 set pm2-logrotate:rotateModule true   # Also rotate pm2-logrotate's own logs
pm2 set pm2-logrotate:workerInterval 60   # Check every 60 seconds
pm2 set pm2-logrotate:rotateInterval '0 0 * * *'  # Force rotate at midnight daily

# Verify configuration
pm2 conf pm2-logrotate
```

### System-Level Logrotate (Belt and Suspenders)

Create `/etc/logrotate.d/pm2`:

```
/home/ubuntu/.pm2/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su ubuntu ubuntu
    maxsize 100M
}
```

Test it:

```bash
sudo logrotate -d /etc/logrotate.d/pm2    # Dry run
sudo logrotate -f /etc/logrotate.d/pm2    # Force run
```

### PM2 Log Cleanup Script

```bash
# scripts/cleanup-logs.sh
#!/bin/bash
# Delete PM2 logs older than 14 days
find /home/ubuntu/.pm2/logs/ -name "*.log" -mtime +14 -delete
find /home/ubuntu/.pm2/logs/ -name "*.gz" -mtime +30 -delete

# Flush current logs (if they are too large)
pm2 flush

echo "Log cleanup complete at $(date)"
```

Add to crontab:

```bash
crontab -e
# Add:
0 3 * * 0 /home/ubuntu/scripts/cleanup-logs.sh  # Weekly at 3 AM Sunday
```

### MongoDB TTL Indexes (Automatic Document Expiry)

For your `logging` middleware that stores request logs:

```javascript
// In your logging model schema:
const logSchema = new mongoose.Schema({
  // ... your fields ...
  createdAt: {
    type: Date,
    default: Date.now,
    expires: 2592000  // 30 days in seconds — MongoDB auto-deletes after 30 days
  }
});

// Or add TTL index directly:
// db.request_logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 })
```

```bash
# In MongoDB shell or Atlas:
db.request_logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 })  // 30 days
db.otp_verifications.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 600 })  // 10 minutes
db.sessions.createIndex({ "lastAccess": 1 }, { expireAfterSeconds: 86400 })  // 24 hours
```

### Cost

- $0 — All free

### Effort: 1 hour

- 20 minutes: Install and configure pm2-logrotate
- 20 minutes: Create logrotate config
- 20 minutes: Add MongoDB TTL indexes

### Documentation

- [https://github.com/keymetrics/pm2-logrotate](https://github.com/keymetrics/pm2-logrotate)
- [https://www.mongodb.com/docs/manual/tutorial/expire-data/](https://www.mongodb.com/docs/manual/tutorial/expire-data/)
- [https://linux.die.net/man/8/logrotate](https://linux.die.net/man/8/logrotate)

---

## 9. Scheduled Tasks

**What:** Replace cron jobs that depend on your EC2 instance being alive with managed AWS services (EventBridge + Lambda, or BullMQ for application-level jobs).

**Why:** If your EC2 instance goes down, cron jobs stop. EventBridge + Lambda runs independently. For a solo developer, managed services reduce operational burden.

### Option A: AWS EventBridge + Lambda (Recommended for Independent Tasks)

**Example: Daily billing reconciliation**

```javascript
// lambda/billing-reconciliation/index.mjs
import { MongoClient } from 'mongodb';

let client;

async function getClient() {
  if (!client) {
    client = new MongoClient(process.env.DATABASE_URI);
    await client.connect();
  }
  return client;
}

export const handler = async (event) => {
  const db = (await getClient()).db();

  // Example: Mark overdue invoices
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const result = await db.collection('invs').updateMany(
    { status: 'pending', createdAt: { $lt: thirtyDaysAgo } },
    { $set: { status: 'overdue', updatedAt: new Date() } }
  );

  console.log(`Marked ${result.modifiedCount} invoices as overdue`);
  return { statusCode: 200, body: `Processed ${result.modifiedCount} invoices` };
};
```

**EventBridge Rule (Terraform):**

```hcl
resource "aws_cloudwatch_event_rule" "daily_billing" {
  name                = "dzzlo-daily-billing"
  description         = "Run billing reconciliation daily at 1 AM IST"
  schedule_expression = "cron(30 19 * * ? *)"  # 19:30 UTC = 1:00 AM IST
}

resource "aws_cloudwatch_event_target" "billing_lambda" {
  rule = aws_cloudwatch_event_rule.daily_billing.name
  arn  = aws_lambda_function.billing_reconciliation.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.billing_reconciliation.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_billing.arn
}
```

**Common cron expressions (EventBridge uses UTC):**


| Schedule          | Cron Expression        | Notes        |
| ----------------- | ---------------------- | ------------ |
| Daily at 1 AM IST | `cron(30 19 * * ? *)`  | 19:30 UTC    |
| Every 6 hours     | `rate(6 hours)`        |              |
| Monday 9 AM IST   | `cron(30 3 ? * MON *)` | 3:30 UTC     |
| First of month    | `cron(0 0 1 * ? *)`    | Midnight UTC |


### Option B: BullMQ (Application-Level Scheduled Jobs)

Best for jobs that need access to your Express app context:

```bash
yarn add bullmq ioredis
```

```javascript
// helpers/scheduler.js
const { Queue, Worker } = require('bullmq');
const IORedis = require('ioredis');

const connection = new IORedis(process.env.REDIS_URL || 'redis://localhost:6379');

// Define queue
const scheduledQueue = new Queue('scheduled-tasks', { connection });

// Add recurring jobs
async function initScheduler() {
  // Clean up expired OTPs every hour
  await scheduledQueue.upsertJobScheduler('cleanup-otps', {
    every: 3600000,  // 1 hour in ms
  }, {
    name: 'cleanup-otps',
  });

  // Daily balance reconciliation at 1 AM
  await scheduledQueue.upsertJobScheduler('reconcile-balances', {
    pattern: '0 1 * * *',  // Cron: 1 AM daily
  }, {
    name: 'reconcile-balances',
  });
}

// Process jobs
const worker = new Worker('scheduled-tasks', async (job) => {
  switch (job.name) {
    case 'cleanup-otps':
      // Your cleanup logic
      break;
    case 'reconcile-balances':
      // Your reconciliation logic
      break;
  }
}, { connection });

worker.on('failed', (job, err) => {
  console.error(`Job ${job.name} failed:`, err);
});

module.exports = { initScheduler };
```

### Decision Guide


| Factor             | EventBridge + Lambda                 | BullMQ                                           |
| ------------------ | ------------------------------------ | ------------------------------------------------ |
| **Requires**       | AWS Lambda, no extra infra           | Redis server                                     |
| **Best for**       | Independent tasks, DB cleanup        | App-context tasks, retries                       |
| **Reliability**    | Fully managed, survives EC2 death    | Dies if EC2 dies                                 |
| **Cost**           | ~$0 (Lambda free tier: 1M reqs/mo)   | Redis: ~$15/mo (ElastiCache) or free (EC2 local) |
| **Recommendation** | **Use for critical scheduled tasks** | Use for app-level job queues                     |


### Cost

- **EventBridge rules:** Free (up to 14M/month invocations)
- **Lambda:** Free tier covers 1M requests/month
- **BullMQ + Redis:** $0 if Redis on same EC2, ~$15/mo for ElastiCache

### Effort: 4 hours

- 2 hours: Create Lambda functions
- 1 hour: Configure EventBridge rules
- 1 hour: Test and monitor

### Documentation

- [https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
- [https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)
- [https://docs.bullmq.io/guide/jobs/repeatable](https://docs.bullmq.io/guide/jobs/repeatable)

---

## 10. Self-Healing

**What:** Ensure your application automatically recovers from crashes without human intervention. Multiple layers: PM2 auto-restart, ASG instance replacement, ALB health checks.

### Layer 1: PM2 Auto-Restart (Already Partially Configured)

Your `ecosystem.config.js` update (from section 6) handles this:

```javascript
// These settings in ecosystem.config.js enable self-healing:
{
  autorestart: true,           // Restart on crash (PM2 default)
  max_memory_restart: "512M",  // Restart if memory leak
  max_restarts: 10,            // Prevent restart loops
  min_uptime: "5s",            // Must run 5s to count as "started"
  exp_backoff_restart_delay: 100,  // Exponential backoff on repeated crashes
}
```

### Layer 2: PM2 Startup Script (Survive Reboots)

```bash
# Generate startup script (run as the user that runs PM2)
pm2 startup
# Copy and run the command PM2 outputs, e.g.:
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu

# Save current process list
pm2 save

# Test: reboot the server
sudo reboot
# After reboot, PM2 should auto-start your app
```

### Layer 3: ASG Health Checks (Instance-Level Self-Healing)

```hcl
# In your Terraform ASG configuration:
resource "aws_autoscaling_group" "app" {
  # ...
  health_check_type         = "ELB"   # Use ALB health checks (not just EC2)
  health_check_grace_period = 300      # 5 minutes grace after launch

  # ASG behavior:
  # 1. ALB checks /healthcheck every 30 seconds
  # 2. If 3 consecutive checks fail (unhealthy_threshold: 3)
  # 3. ALB marks instance unhealthy
  # 4. ASG terminates unhealthy instance
  # 5. ASG launches new instance to maintain desired_capacity
  # 6. New instance auto-configures via launch template user_data
}
```

### Layer 4: CloudWatch Alarm + SNS Notification

```bash
# Create SNS topic for alerts
aws sns create-topic --name dzzlo-oms-alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:dzzlo-oms-alerts \
  --protocol email \
  --notification-endpoint your@email.com

# Alarm: Notify if ALB returns 5xx errors
aws cloudwatch put-metric-alarm \
  --alarm-name dzzlo-oms-5xx-errors \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:ap-south-1:ACCOUNT_ID:dzzlo-oms-alerts \
  --dimensions Name=LoadBalancer,Value=app/dzzlo-oms-alb/LB_ID

# Alarm: Notify if unhealthy host count > 0
aws cloudwatch put-metric-alarm \
  --alarm-name dzzlo-oms-unhealthy-hosts \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Maximum \
  --period 60 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --alarm-actions arn:aws:sns:ap-south-1:ACCOUNT_ID:dzzlo-oms-alerts \
  --dimensions Name=TargetGroup,Value=targetgroup/dzzlo-oms-tg/TG_ID \
               Name=LoadBalancer,Value=app/dzzlo-oms-alb/LB_ID

# Alarm: High CPU usage
aws cloudwatch put-metric-alarm \
  --alarm-name dzzlo-oms-high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --alarm-actions arn:aws:sns:ap-south-1:ACCOUNT_ID:dzzlo-oms-alerts \
  --dimensions Name=AutoScalingGroupName,Value=dzzlo-oms-asg
```

### Layer 5: Healthcheck Enhancement

Improve your existing `/healthcheck` endpoint to check more than just DB connectivity:

```javascript
// helpers/healthcheck.js — enhanced version
const express = require("express");
const mongoose = require("mongoose");
const router = express.Router({});

router.get("/", async (_req, res, _next) => {
  const healthcheck = {
    status: "ok",
    uptime: process.uptime(),
    timestamp: Date.now(),
    memory: process.memoryUsage(),
    db: {
      state: mongoose.connection.readyState,
      stateMessage: mongoose.STATES[mongoose.connection.readyState],
    },
  };

  try {
    // Actually ping the database
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.db.admin().ping();
      healthcheck.db.ping = "ok";
    } else {
      healthcheck.status = "degraded";
      healthcheck.db.ping = "failed";
    }

    const statusCode = healthcheck.status === "ok" ? 200 : 503;
    res.status(statusCode).json(healthcheck);
  } catch (e) {
    healthcheck.status = "error";
    healthcheck.error = e.message;
    res.status(503).json(healthcheck);
  }
});

module.exports = router;
```

### Self-Healing Summary


| Layer             | What             | Recovers From              | Automatic? |
| ----------------- | ---------------- | -------------------------- | ---------- |
| PM2 autorestart   | Process crash    | App crash, memory leak     | Yes        |
| PM2 startup       | Server reboot    | EC2 restart, patching      | Yes        |
| ASG + ELB health  | Instance failure | Hardware failure, hangs    | Yes        |
| CloudWatch alarms | Degradation      | High error rate, CPU spike | Alert only |


### Cost

- **PM2:** $0
- **CloudWatch alarms:** $0.10/alarm/month (3 alarms = $0.30/mo)
- **SNS email:** Free

### Effort: 2 hours

- 30 minutes: Configure PM2 settings + startup script
- 30 minutes: Create CloudWatch alarms
- 30 minutes: Enhance healthcheck endpoint
- 30 minutes: Test failure scenarios

### Documentation

- [https://pm2.keymetrics.io/docs/usage/restart-strategies/](https://pm2.keymetrics.io/docs/usage/restart-strategies/)
- [https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html)
- [https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)

---

## 11. Automated Security Patching

**What:** Use AWS Systems Manager (SSM) Patch Manager to automatically apply OS security patches to your EC2 instances without SSH.

**Why:** Unpatched servers are the #1 attack vector. Manual patching means it never happens. SSM Patch Manager automates this with configurable schedules and compliance reporting.

### Prerequisites

```bash
# 1. SSM Agent (pre-installed on Amazon Linux 2/2023 and Ubuntu 20.04+)
sudo systemctl status amazon-ssm-agent

# 2. IAM Instance Profile must include:
#    - AmazonSSMManagedInstanceCore (managed policy)
```

### IAM Role (Terraform)

```hcl
resource "aws_iam_role" "ec2_ssm" {
  name = "dzzlo-oms-ec2-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "codedeploy" {
  role       = aws_iam_role.ec2_ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2RoleforAWSCodeDeploy"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "dzzlo-oms-ec2-profile"
  role = aws_iam_role.ec2_ssm.name
}
```

### Quick Setup (Console — Recommended for Solo Dev)

1. Go to **AWS Systems Manager** > **Quick Setup**
2. Choose **Patch Manager**
3. Configure:
  - **Targets:** All managed instances (or specific tag: `PatchGroup=dzzlo-oms`)
  - **Patch operation:** Scan and install
  - **Schedule:** Weekly, Sunday 3:00 AM UTC (8:30 AM IST)
  - **Reboot option:** Reboot if needed
  - **Patch baseline:** AWS-DefaultPatchBaseline (security patches only)
4. Create

### Custom Patch Baseline (AWS CLI)

```bash
# Create a baseline that only auto-approves Critical and Important security patches
aws ssm create-patch-baseline \
  --name "dzzlo-oms-security-patches" \
  --operating-system "AMAZON_LINUX_2" \
  --approval-rules '{
    "PatchRules": [
      {
        "PatchFilterGroup": {
          "PatchFilters": [
            { "Key": "CLASSIFICATION", "Values": ["Security"] },
            { "Key": "SEVERITY", "Values": ["Critical", "Important"] }
          ]
        },
        "ApproveAfterDays": 3,
        "ComplianceLevel": "CRITICAL",
        "EnableNonSecurity": false
      }
    ]
  }' \
  --description "Auto-approve critical security patches after 3 days"
```

### Maintenance Window (AWS CLI)

```bash
# Create maintenance window: Sunday 3 AM UTC, 2 hour window
aws ssm create-maintenance-window \
  --name "dzzlo-oms-patching" \
  --schedule "cron(0 3 ? * SUN *)" \
  --duration 2 \
  --cutoff 1 \
  --allow-unassociated-targets

# Register targets
aws ssm register-target-with-maintenance-window \
  --window-id mw-XXXXXXXXX \
  --resource-type INSTANCE \
  --targets "Key=tag:PatchGroup,Values=dzzlo-oms"

# Register patching task
aws ssm register-task-with-maintenance-window \
  --window-id mw-XXXXXXXXX \
  --task-type RUN_COMMAND \
  --task-arn "AWS-RunPatchBaseline" \
  --targets "Key=WindowTargetIds,Values=TARGET_ID" \
  --task-invocation-parameters '{
    "RunCommand": {
      "Parameters": {
        "Operation": ["Install"],
        "RebootOption": ["RebootIfNeeded"]
      }
    }
  }' \
  --max-concurrency "1" \
  --max-errors "0" \
  --priority 1
```

### Pre-Patch Script (Stop App Before Patching)

```bash
# scripts/pre-patch.sh — drain traffic before patching
#!/bin/bash
echo "Pre-patch: stopping application"
pm2 stop dzzlo-oms || true
# Deregister from ALB target group (if not using ASG)
```

### Cost

- **SSM Patch Manager:** Free (no additional charge for on-demand patching)
- **Maintenance windows:** Free
- **SSM Agent:** Pre-installed, free

### Effort: 3 hours

- 1 hour: Verify SSM agent, attach IAM role
- 1 hour: Configure patch baseline and maintenance window
- 1 hour: Test with scan-only first, then scan-and-install

### Documentation

- [https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-patch.html](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-patch.html)
- [https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-policies-quick-setup.html](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-policies-quick-setup.html)

---

## 12. Database Automation (MongoDB Atlas)

**What:** Enable Atlas auto-scaling, set up alerts, configure scheduled backups to S3, and use Performance Advisor for auto-indexing.

**Why:** Atlas already hosts your database. These features are built-in but likely not configured. They prevent outages and reduce manual DBA work.

### Auto-Scaling (Atlas UI or API)

**In Atlas Console:**

1. Go to **Database** > **Your Cluster** > **...** (ellipsis) > **Edit Configuration**
2. Under **Cluster Tier:**
  - Enable **Auto-scale cluster tier**
  - Set minimum tier: M10 (or your current tier)
  - Set maximum tier: M30 (or your budget limit)
3. Under **Storage:**
  - Enable **Auto-expand storage** (enabled by default on M10+)
4. Click **Apply Changes**

**Atlas API:**

```bash
# Enable cluster auto-scaling via API
curl -X PATCH \
  "https://cloud.mongodb.com/api/atlas/v2/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}" \
  --header "Content-Type: application/json" \
  --header "Accept: application/vnd.atlas.2024-08-05+json" \
  --digest --user "{PUBLIC_KEY}:{PRIVATE_KEY}" \
  --data '{
    "autoScaling": {
      "compute": {
        "enabled": true,
        "scaleDownEnabled": true,
        "minInstanceSize": "M10",
        "maxInstanceSize": "M30"
      },
      "diskGBEnabled": true
    }
  }'
```

### Alerts (Atlas Console)

Go to **Project** > **Alerts** > **Add Alert:**


| Alert               | Condition                     | Notification                     |
| ------------------- | ----------------------------- | -------------------------------- |
| **Connections**     | > 80% of max connections      | Email / Slack                    |
| **CPU**             | > 75% for 10 minutes          | Email                            |
| **Disk**            | > 80% utilization             | Email                            |
| **Replication Lag** | > 10 seconds                  | Email                            |
| **Query Targeting** | Scanned/returned ratio > 1000 | Email                            |
| **Oplog Window**    | < 12 hours                    | Email (critical for replication) |


### Performance Advisor (Auto-Indexing)

**In Atlas Console:**

1. Go to **Database** > **Your Cluster** > **Performance Advisor**
2. Review suggested indexes (Atlas analyzes slow queries)
3. Click **Create Index** for recommended ones

**For M10+ clusters, enable auto-indexing:**

```bash
# Atlas API — enable auto-indexing
curl -X PATCH \
  "https://cloud.mongodb.com/api/atlas/v2/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}" \
  --header "Content-Type: application/json" \
  --digest --user "{PUBLIC_KEY}:{PRIVATE_KEY}" \
  --data '{
    "autoScaling": {
      "autoIndexingEnabled": true
    }
  }'
```

### Scheduled Backups

Atlas provides automated backups on M10+ clusters:

**In Atlas Console:**

1. Go to **Database** > **Your Cluster** > **Backup** > **Edit Policy**
2. Configure:
  - **Snapshot frequency:** Every 6 hours
  - **Snapshot retention:** 7 days
  - **Daily snapshot retention:** 7 days
  - **Weekly snapshot retention:** 4 weeks
  - **Monthly snapshot retention:** 12 months
3. **Point-in-time restore:** Enable continuous backup (M10+)

**Export to S3 (for long-term archival):**

```bash
# Set up Atlas Data Federation to export to S3
# Atlas Console > Database > Your Cluster > Backup > Scheduled Backup Export

# Or use mongodump on a schedule (from Lambda or EC2):
mongodump \
  --uri="mongodb+srv://user:pass@cluster.mongodb.net/dzzlo_oms" \
  --archive \
  --gzip \
  | aws s3 cp - s3://dzzlo-backups/$(date +%Y-%m-%d)/dzzlo_oms.gz
```

### MongoDB TTL Indexes (Automatic Data Cleanup)

```javascript
// Add to your application startup or a migration script:

// Clean up request logs after 30 days
db.request_logs.createIndex(
  { "createdAt": 1 },
  { expireAfterSeconds: 30 * 24 * 60 * 60 }  // 30 days
);

// Clean up OTP records after 10 minutes
db.otp_records.createIndex(
  { "createdAt": 1 },
  { expireAfterSeconds: 600 }  // 10 minutes
);

// Clean up notification logs after 90 days
db.notification_logs.createIndex(
  { "createdAt": 1 },
  { expireAfterSeconds: 90 * 24 * 60 * 60 }  // 90 days
);
```

### Cost

- **Atlas auto-scaling:** No extra charge (you pay for the tier you scale to)
- **Atlas alerts:** Free (included in all tiers)
- **Atlas backups:** Included in M10+ tier pricing
- **Atlas Performance Advisor:** Free on M10+
- **S3 backup storage:** ~$0.023/GB/month

### Effort: 2 hours

- 30 minutes: Enable auto-scaling
- 30 minutes: Configure alerts
- 30 minutes: Review and apply Performance Advisor suggestions
- 30 minutes: Configure backup policy, add TTL indexes

### Documentation

- [https://www.mongodb.com/docs/atlas/cluster-autoscaling/](https://www.mongodb.com/docs/atlas/cluster-autoscaling/)
- [https://www.mongodb.com/docs/atlas/configure-alerts/](https://www.mongodb.com/docs/atlas/configure-alerts/)
- [https://www.mongodb.com/docs/atlas/performance-advisor/](https://www.mongodb.com/docs/atlas/performance-advisor/)
- [https://www.mongodb.com/docs/atlas/backup/cloud-backup/overview/](https://www.mongodb.com/docs/atlas/backup/cloud-backup/overview/)
- [https://www.mongodb.com/docs/manual/tutorial/expire-data/](https://www.mongodb.com/docs/manual/tutorial/expire-data/)

---

## Implementation Roadmap

### Week 1: Foundation (8 hours)

```
Day 1 (4h):
  [x] PM2 cluster mode (ecosystem.config.js update)
  [x] PM2 log rotation (pm2-logrotate)
  [x] PM2 startup script (survive reboots)

Day 2 (4h):
  [x] GitHub Actions CI/CD workflow
  [x] ACM certificate on ALB (if not already)
  [x] CloudWatch alarms (3 basic alarms)
```

### Week 2: Monitoring & Database (4 hours)

```
Day 3 (2h):
  [x] Atlas alerts configuration
  [x] Atlas auto-scaling (if M10+)
  [x] MongoDB TTL indexes

Day 4 (2h):
  [x] Enhanced healthcheck endpoint
  [x] PM2 graceful shutdown in dzzlo_oms.js
  [x] SSM Patch Manager Quick Setup
```

### Month 2: Advanced Automation (16 hours)

```
Week 3-4:
  [ ] Automated AMI creation (Packer or Image Builder)
  [ ] EventBridge scheduled tasks for billing/cleanup
  [ ] CodeDeploy appspec.yml + lifecycle scripts
```

### Month 3: Infrastructure as Code (16 hours)

```
Week 5-8:
  [ ] Terraform project: VPC, SG, ALB, ASG
  [ ] Import existing resources into Terraform
  [ ] CodePipeline (optional — only if outgrowing GitHub Actions)
```

---

## Quick Reference: All New Files to Create

```
dzzlo_oms_api/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml              # GitHub Actions CI/CD
│       └── build-ami.yml          # Monthly AMI build (optional)
├── appspec.yml                    # CodeDeploy lifecycle
├── buildspec.yml                  # CodeBuild test spec
├── scripts/
│   └── codedeploy/
│       ├── before_install.sh
│       ├── after_install.sh
│       ├── application_start.sh
│       └── validate_service.sh
├── infra/                         # Terraform (optional)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── vpc.tf
│   ├── security_groups.tf
│   ├── alb.tf
│   ├── asg.tf
│   └── iam.tf
└── packer/                        # AMI build (optional)
    └── dzzlo-oms.pkr.hcl
```

---

## Total Cost Summary (Low Traffic)


| Service            | Monthly Cost      |
| ------------------ | ----------------- |
| GitHub Actions     | $0 (free tier)    |
| CodeDeploy         | $0 (free for EC2) |
| CodePipeline       | $1/pipeline       |
| CodeBuild          | ~$0.50/mo         |
| ACM certificates   | $0                |
| CloudWatch alarms  | ~$0.30/mo         |
| SNS notifications  | $0                |
| SSM Patch Manager  | $0                |
| EC2 Image Builder  | ~$0.10/build      |
| EventBridge        | $0                |
| Lambda             | $0 (free tier)    |
| S3 (state/backups) | ~$0.50/mo         |
| **Total**          | **~$2.50/month**  |


Everything above can be implemented for under $3/month of additional AWS costs.
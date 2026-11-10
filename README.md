# AWS Container Service

A containerized web application deployed on **Amazon ECS Fargate**, with
infrastructure provisioned using **Terraform**. The application combines
a React + TypeScript frontend with a FastAPI backend and provides a chat
interface for changing the desired task count of an ECS service using
plain-text requests.

## Features

-   FastAPI backend with health, runtime information, status, and chat
    endpoints.
-   React + TypeScript + Vite chat interface.
-   Multi-stage Docker build that compiles the frontend and packages it
    with the backend.
-   Amazon ECR for container image storage.
-   Amazon ECS Fargate for running and maintaining containers.
-   Application Load Balancer (ALB) for public HTTP access and health
    checks.
-   Terraform for infrastructure provisioning.
-   Boto3 integration for ECS service updates.
-   Rule-based request parsing and validation.

## Architecture

``` text
                         User Browser
                              |
                              v
                   Application Load Balancer
                         HTTP :80
                              |
                              v
                     ECS Fargate Service
                         (ECS tasks)
                              |
                              v
                    FastAPI Application :8000
                       /             \
                      /               \
             React Frontend         Chat API
                                         |
                                   Request Parser
                                         |
                                     Validator
                                         |
                                    ECS Manager
                                         |
                                    Boto3 / ECS API
                                         |
                                UpdateService API
```

The React frontend is built into static files and served by FastAPI.
Both run in the same Docker container, so the deployed application does
not require a separate frontend service.

## Technology Stack

  Component                 Technology
  ------------------------- -------------------------------
  Frontend                  React, TypeScript, Vite
  Backend                   Python, FastAPI
  AWS SDK                   Boto3
  Dependency management     `uv`, npm
  Containerization          Docker
  Container registry        Amazon ECR
  Container orchestration   Amazon ECS Fargate
  Load balancing            AWS Application Load Balancer
  Infrastructure as Code    Terraform

## Project Structure

``` text
aws-container-service/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── chat.py
│   ├── schemas/
│   │   └── chat.py
│   ├── services/
│   │   ├── parser.py
│   │   ├── validator.py
│   │   └── ecs_manager.py
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── ...
│   ├── package.json
│   └── package-lock.json
├── terraform/
│   ├── provider.tf
│   ├── main.tf
│   ├── networking.tf
│   ├── security.tf
│   ├── ecs.tf
│   └── alb.tf
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Prerequisites

Install the following tools:

-   Python 3.11 or later
-   [`uv`](https://docs.astral.sh/uv/)
-   Node.js and npm
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   [AWS
    CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
-   [Terraform](https://developer.hashicorp.com/terraform/install)

For AWS deployment, configure the AWS CLI with an IAM identity that has
the permissions required to push to ECR and manage the Terraform
resources. The identity used by Terraform also needs permission to pass
the ECS task and task-execution roles to ECS.

Check the configured AWS identity and region:

``` bash
aws sts get-caller-identity
aws configure get region
```

The project uses the AWS region `ap-southeast-2`.

## Local Development

### 1. Clone the repository

``` bash
git clone <repository-url>
cd aws-container-service
```

Replace `<repository-url>` with the URL of your Git repository.

### 2. Install backend dependencies

From the project root:

``` bash
uv sync
```

### 3. Start the FastAPI backend

``` bash
uv run uvicorn app.main:app --reload --port 8000
```

The backend is available at:

-   Application: <http://localhost:8000>
-   Health check: <http://localhost:8000/health>
-   API documentation: <http://localhost:8000/docs>

### 4. Start the frontend

Open a second terminal:

``` bash
cd frontend
npm install
npm run dev
```

The Vite development server is available at <http://localhost:5173>.

During local development, Vite proxies `/chat` requests to the FastAPI
backend. Keep the backend running while using the frontend.

## Docker

The project uses a multi-stage Docker build:

1.  The first stage installs frontend dependencies and builds the React
    application.
2.  The second stage installs Python dependencies and prepares the
    FastAPI application.
3.  The generated frontend files are copied into the final backend
    image.

### Build the image

Run this from the project root:

``` bash
docker build -t aws-container-service:v3 .
```

### Run locally

``` bash
docker run --rm -p 8000:8000 aws-container-service:v3
```

Open <http://localhost:8000> to access the application. The health
endpoint is available at <http://localhost:8000/health>.

## AWS Deployment

The deployed resources use **`ap-southeast-2` (Sydney)**. The ECR
repository and Terraform configuration are already part of this project
setup. The following steps describe how to publish a new image and apply
the infrastructure configuration.

### 1. Confirm the ECR repository

The repository used by this project is:

``` text
201909943484.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service
```

Check that it exists:

``` bash
aws ecr describe-repositories \
  --repository-names aws-container-service \
  --region ap-southeast-2
```

If deploying into a different AWS account, replace the account ID and
ensure the repository exists in that account and region.

### 2. Build the image

From the project root:

``` bash
docker build -t aws-container-service:v3 .
```

Use a new tag when publishing a new version (for example, `v4`) rather
than silently overwriting a tag used by an existing deployment.

### 3. Authenticate Docker with ECR

PowerShell:

``` powershell
$token = (aws ecr get-login-password --region ap-southeast-2).Trim()
docker login --username AWS --password $token 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com
```

The token is a password. Do not commit it, print it in logs, or share
it. Docker may warn that using `--password` exposes it to local
process/history mechanisms; use a secure credential helper or the
standard `--password-stdin` flow where your shell and Docker setup
support it.

### 4. Tag and push the image

PowerShell:

``` powershell
docker tag aws-container-service:v3 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service:v3

docker push 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service:v3
```

If you use a new tag, update the image reference in `terraform/ecs.tf`
to match that tag before applying Terraform.

### 5. Provision or update infrastructure with Terraform

``` bash
cd terraform
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

Review the plan before applying it. Terraform provisions or manages the
VPC, subnets, internet gateway, route table, security groups, ECS
cluster, task definition, ECS service, and Application Load Balancer.

If the infrastructure has already been created, Terraform will normally
plan updates rather than create a completely new stack. The exact
actions depend on the current Terraform state and AWS resources.

### 6. Open the deployed application

The project ALB DNS name recorded during deployment was:

``` text
http://aws-container-service-alb-928030712.ap-southeast-2.elb.amazonaws.com
```

Open the current ALB DNS name from the Terraform output or AWS console
if it has changed. The ALB listener exposes HTTP on port 80 and forwards
requests to healthy ECS task targets on port 8000.

Verify the health endpoint:

``` text
http://<ALB-DNS-NAME>/health
```

It should return HTTP 200 when the application is healthy.

### Deployment notes

-   The ECS task definition uses Fargate with `awsvpc` networking.
-   The ALB target group uses IP targets because Fargate tasks have
    their own network interfaces and IP addresses.
-   The ALB health check uses `GET /health`.
-   The ECS security group allows application traffic on port 8000 from
    the ALB security group.
-   ECS uses a task execution role to pull the image from ECR. The
    application uses its task role for AWS API calls through Boto3.
-   Terraform state should be preserved. Do not delete or manually edit
    state files to resolve a deployment issue.
-   AWS resources can incur charges while running. Use
    `terraform destroy` only when you intentionally want to remove the
    infrastructure and have checked what will be deleted.

## Chat Interface

The application accepts plain-text requests through the chat interface.
The backend parses the request, validates the requested value, and
invokes the ECS manager for supported operations.

### Example requests

The following requests express the currently supported
operation---changing the ECS service desired task count:

``` text
Scale the service to 2 tasks
Run 3 containers
Set the desired count to 1
```

The wording accepted depends on the rule-based patterns in the parser.
If a request is ambiguous or does not match a supported pattern, the
application may report that it could not interpret the request.

### What happens to a request?

1.  The frontend sends the message to the chat API.
2.  The parser identifies the requested operation and value.
3.  The validator checks the value against the configured constraints.
4.  For a supported operation, the ECS manager calls the AWS ECS API
    using Boto3.
5.  The backend returns a result message to the frontend.

### Implemented vs. recognized operations

  -----------------------------------------------------------------------
  Request type                        Current behaviour
  ----------------------------------- -----------------------------------
  Change desired task count           Parsed, validated and executed
                                      through ECS `UpdateService`

  Change CPU                          Recognized and validated; ECS
                                      task-definition update is not
                                      implemented

  Change memory                       Recognized and validated; ECS
                                      task-definition update is not
                                      implemented

  Change image version                Recognized and validated; image
                                      deployment logic is not implemented

  Other / unclear request             Reported as unsupported or unclear
  -----------------------------------------------------------------------

The desired task count is validated against the application's configured
minimum and maximum. The current project validator uses a range of 1--5
tasks.

**Important:** A response indicating that CPU, memory, or image intent
was understood does not mean the corresponding AWS resource was changed.
Only desired-count updates are implemented end to end.

## API Endpoints

  Method   Endpoint        Description
  -------- --------------- ------------------------------------------------
  GET      `/`             Application information / frontend entry point
  GET      `/health`       Health-check endpoint
  GET      `/info`         ECS task and runtime information
  GET      `/api/status`   Application status
  POST     `/chat/`        Submit a plain-text management request
  GET      `/docs`         FastAPI Swagger documentation

### Example chat API request

``` bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Scale the service to 2 tasks"}'
```

Example request body:

``` json
{
  "message": "Scale the service to 2 tasks"
}
```

The response indicates whether the request was understood, rejected by
validation, successfully submitted to ECS, or failed. The actual
response text depends on the AWS API result.

## Security

-   AWS access keys are not stored in the Docker image.
-   The ECS task execution role is used for task startup operations such
    as pulling the image.
-   The ECS task role supplies AWS permissions to application code
    running inside the container.
-   IAM permissions should be scoped to the intended ECS cluster and
    service wherever the AWS action supports resource-level permissions.
-   Do not commit credentials, `.env` files, Terraform state, local
    virtual environments, or dependency directories.
-   The baseline deployment uses HTTP. Add HTTPS and
    authentication/authorization before exposing a management interface
    for production use.

## Known Limitations and Future Improvements

-   CPU and memory changes are parsed and validated but are not applied
    through a new ECS task definition revision.
-   Image version requests are parsed and validated but do not trigger a
    deployment.
-   The chat parser is rule-based and supports a limited set of
    phrasings.
-   The management interface does not currently provide a full
    authentication and authorization workflow.
-   The baseline ALB listener uses HTTP; HTTPS/TLS is not configured.
-   CloudWatch logging, metrics and alarms were not configured as part
    of the baseline.
-   The ECS tasks were configured in public subnets with public IP
    assignment. A more locked-down deployment could use private subnets
    with suitable NAT Gateway or VPC endpoint connectivity.
-   Terraform and the chat application can both change the ECS desired
    count. If Terraform declares a different count from the live
    service, a later `terraform apply` may change it back. Decide which
    system should own that setting.

Possible improvements include implementing task-definition updates for
CPU, memory and image versions; adding authentication, authorization and
audit logging; adding CloudWatch observability; enabling HTTPS; and
moving tasks to private subnets.

## Notes

-   AWS region: `ap-southeast-2`
-   ECR repository: `aws-container-service`
-   ECS cluster: `aws-container-service-cluster`
-   ECS service: `aws-container-service`
-   Container name: `health-api`
-   Container port: `8000`
-   Health check: `GET /health` (HTTP 200)

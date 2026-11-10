# AWS Container Service

A containerized web application deployed on **AWS ECS Fargate**, with infrastructure provisioned using **Terraform**. It provides a React-based chat interface that allows users to manage an ECS service using plain-text commands.

## Features

- FastAPI backend with health and service information endpoints.
- React + TypeScript chat interface.
- Docker multi-stage build combining frontend and backend.
- Amazon ECR for container image storage.
- AWS ECS Fargate for container orchestration.
- Application Load Balancer for public access.
- Terraform for infrastructure provisioning.
- Boto3 integration for ECS service management.
- Input parsing and validation for infrastructure requests.

## Architecture

```text
                 User Browser
                      |
                      v
             Application Load Balancer
                      |
                      v
                ECS Fargate
                 (3 Tasks)
                      |
               FastAPI Application
                 /          \
                /            \
        React Frontend     Chat API
                               |
                        Request Parser
                               |
                           Validator
                               |
                         ECS Manager
                               |
                         AWS ECS API
```

The React frontend is built into static files and served by FastAPI. Both applications run in the same Docker container, avoiding the need for a separate frontend service.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| AWS SDK | Boto3 |
| Containerization | Docker |
| Container Registry | Amazon ECR |
| Orchestration | AWS ECS Fargate |
| Load Balancing | AWS Application Load Balancer |
| Infrastructure as Code | Terraform |
| Dependency Management | uv, npm |

## Project Structure

```text
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
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── ...
│   ├── package.json
│   └── package-lock.json
│
├── terraform/
│   ├── provider.tf
│   ├── main.tf
│   ├── networking.tf
│   ├── security.tf
│   ├── ecs.tf
│   └── alb.tf
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Prerequisites

Install the following tools:

- Python 3.11 or later
- uv
- Node.js and npm
- Docker Desktop
- AWS CLI
- Terraform

Configure AWS CLI credentials with an IAM identity that has the required permissions.

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd aws-container-service
```

### 2. Install backend dependencies

```bash
uv sync
```

### 3. Start FastAPI

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The backend is available at:

- Application: http://localhost:8000
- Health: http://localhost:8000/health
- API documentation: http://localhost:8000/docs

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at:

http://localhost:5173

During local development, Vite proxies `/chat` requests to the FastAPI backend.

## Docker

The project uses a multi-stage Docker build.

- The first stage builds the React frontend.
- The second stage installs Python dependencies and prepares FastAPI.
- The frontend production build is copied into the backend image.

### Build the image

```bash
docker build -t aws-container-service:v3 .
```

### Run locally

```bash
docker run --rm -p 8000:8000 aws-container-service:v3
```

Open http://localhost:8000 to access the application.

## AWS Deployment

The application is deployed in the `ap-southeast-2` region.

### 1. Create the ECR repository

The ECR repository used by this project is:

```text
aws-container-service
```

### 2. Authenticate Docker with ECR

```powershell
$token = (aws ecr get-login-password --region ap-southeast-2).Trim()

docker login --username AWS --password $token 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com
```

### 3. Tag and push the image

```powershell
docker tag aws-container-service:v3 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service:v3

docker push 201909943484.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service:v3
```

### 4. Provision infrastructure using Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Review the Terraform plan before applying changes.

Terraform provisions the VPC, networking, security groups, ECS cluster, task definition, ECS service, and Application Load Balancer.

## Chat Interface

The application accepts plain-text requests through its chat interface.

Example:

```text
Run 3 containers
Scale the service to 2 tasks
```

The backend processes requests through the following stages:

1. Parse the user's message.
2. Identify the requested ECS operation.
3. Validate the requested value.
4. Execute supported operations through Boto3.
5. Return a response to the frontend.

**Currently implemented ECS operation:** Changing the desired task count.

CPU, memory, and image version requests are recognized and validated, but their ECS execution logic is not yet implemented.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information or frontend |
| GET | `/health` | Health check |
| GET | `/info` | ECS task and runtime information |
| GET | `/api/status` | Service status |
| POST | `/chat/` | Submit a plain-text management request |
| GET | `/docs` | FastAPI Swagger documentation |

Example chat request:

```json
{
  "message": "Scale the service to 2 tasks"
}
```

## Security

- AWS credentials are not stored in the Docker image.
- ECS uses a task execution role to pull images and an application task role to manage the ECS service.
- ECS management permissions should be restricted to the intended service.
- Terraform state, environment files, and local dependencies are excluded from Git.

## Notes

- The deployed application uses AWS ECS Fargate.
- The Application Load Balancer exposes the application through HTTP.
- The desired ECS task count can be modified through the chat interface.
- AWS resources may incur charges while running. Destroy resources when they are no longer required.

## Future Improvements

- Implement CPU and memory configuration updates.
- Implement controlled image version deployments.
- Add authentication and authorization to the management interface.
- Add deployment progress and service convergence tracking.
- Integrate CloudWatch logging and monitoring.
- Improve chat parsing and error handling.

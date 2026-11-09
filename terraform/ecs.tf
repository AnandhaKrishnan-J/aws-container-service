resource "aws_ecs_cluster" "main" {
  name = "aws-container-service-cluster"

  tags = {
    Name = "aws-container-service-cluster"
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "aws-container-ecs-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "aws-container-ecs-task-execution"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "aws-container-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "aws-container-ecs-task"
  }
}

resource "aws_iam_role_policy" "ecs_management" {
  name = "aws-container-ecs-management"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ecs:DescribeServices",
          "ecs:UpdateService"
        ]

        Resource = "arn:aws:ecs:ap-southeast-2:${data.aws_caller_identity.current.account_id}:service/${aws_ecs_cluster.main.name}/aws-container-service"
      }
    ]
  })
}

# --------------------------------------------------
# AWS Account Information
# --------------------------------------------------

data "aws_caller_identity" "current" {}


# --------------------------------------------------
# ECS Task Definition
# --------------------------------------------------

resource "aws_ecs_task_definition" "app" {
  family                   = "aws-container-service"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = 256
  memory = 512

  # ECS uses this role to pull images and write logs
  execution_role_arn = aws_iam_role.ecs_task_execution.arn

  # Application uses this role to call AWS APIs
  task_role_arn = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "health-api"
      image     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.ap-southeast-2.amazonaws.com/aws-container-service:v2"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
    }
  ])

  tags = {
    Name = "aws-container-service-task"
  }
}


# --------------------------------------------------
# ECS Service
# --------------------------------------------------

resource "aws_ecs_service" "app" {
  name            = "aws-container-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id
    ]

    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "health-api"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.app,
    aws_iam_role_policy_attachment.ecs_task_execution,
    aws_iam_role_policy.ecs_management
  ]

  tags = {
    Name = "aws-container-service"
  }
}

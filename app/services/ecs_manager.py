
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
ECS_CLUSTER = os.getenv(
    "ECS_CLUSTER",
    "aws-container-service-cluster",
)
ECS_SERVICE = os.getenv(
    "ECS_SERVICE",
    "aws-container-service",
)


class ECSManager:
    def __init__(self):
        self.ecs = boto3.client(
            "ecs",
            region_name=AWS_REGION,
        )

    def update_desired_count(self, count: int) -> dict:
        try:
            response = self.ecs.update_service(
                cluster=ECS_CLUSTER,
                service=ECS_SERVICE,
                desiredCount=count,
            )

            service = response["service"]

            return {
                "success": True,
                "message": (
                    f"ECS accepted the request to scale "
                    f"the service to {count} tasks. "
                    f"Currently running: {service['runningCount']}."
                ),
                "desired_count": service["desiredCount"],
                "running_count": service["runningCount"],
            }

        except (ClientError, BotoCoreError) as error:
            return {
                "success": False,
                "message": f"ECS operation failed: {error}",
            }


ecs_manager = ECSManager()

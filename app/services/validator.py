from app.services.parser import ParsedOperation


MIN_TASKS = 1
MAX_TASKS = 5

FARGATE_CONFIGURATIONS = {
    256: [512, 1024, 2048],
    512: [1024, 2048, 3072, 4096],
    1024: list(range(2048, 8193, 1024)),
}

ALLOWED_IMAGE_TAGS = {"v1", "v2", "latest"}


def validate_operation(operation: ParsedOperation) -> tuple[bool, str]:
    if operation.operation == "unknown":
        return False, "Unsupported operation."

    if operation.value is None:
        return False, "A configuration value is required."

    value = operation.value

    if operation.operation == "set_desired_count":
        if not isinstance(value, int) or not MIN_TASKS <= value <= MAX_TASKS:
            return False, f"Task count must be between {MIN_TASKS} and {MAX_TASKS}."

        return True, "Task count is valid."

    if operation.operation == "set_cpu":
        if not isinstance(value, int) or value not in FARGATE_CONFIGURATIONS:
            return False, "CPU must be 256, 512, or 1024 CPU units."

        return True, "CPU value is valid."

    if operation.operation == "set_memory":
        if not isinstance(value, int):
            return False, "Memory must be an integer value in MiB."

        supported = {
            memory
            for memories in FARGATE_CONFIGURATIONS.values()
            for memory in memories
        }

        if value not in supported:
            return False, "Unsupported Fargate memory value."

        return True, "Memory value is valid."

    if operation.operation == "set_image":
        if not isinstance(value, str) or value not in ALLOWED_IMAGE_TAGS:
            return False, "Image tag must be v1, v2, or latest."

        return True, "Image tag is valid."

    return False, "This operation is not supported."

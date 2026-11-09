
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.parser import parse_request
from app.services.validator import validate_operation
from app.services.ecs_manager import ecs_manager

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Interpret the user's request
    parsed = parse_request(request.message)

    if parsed.operation == "unknown":
        return ChatResponse(
            message=request.message,
            response=parsed.message,
            status="unclear",
        )

    is_valid, validation_message = validate_operation(parsed)

    if not is_valid:
        return ChatResponse(
            message=request.message,
            response=validation_message,
            status="rejected",
        )

    if parsed.operation == "set_desired_count":
        result = ecs_manager.update_desired_count(parsed.value)

        return ChatResponse(
            message=request.message,
            response=result["message"],
            status="submitted" if result["success"] else "failed",
        )

    return ChatResponse(
        message=request.message,
        response=(
            f"{validation_message} "
            f"Operation: {parsed.operation}, value: {parsed.value}. "
            "AWS execution for this operation is not implemented yet."
        ),
        status="interpreted",
    )

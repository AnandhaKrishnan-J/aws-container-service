import re
from typing import Literal

from pydantic import BaseModel


class ParsedOperation(BaseModel):
    operation: Literal[
        "set_desired_count",
        "set_cpu",
        "set_memory",
        "set_image",
        "unknown",
    ]
    value: int | str | None = None
    message: str


def parse_request(message: str) -> ParsedOperation:
    text = message.lower().strip()

    # Desired task count
    count_match = re.search(
        r"\b(?:run|start|create|launch|deploy|set|scale(?:\s+up|\s+down)?)\b"
        r".*?\b(\d+)\s+(?:containers?|tasks?)\b",
        text,
    )

    if count_match:
        return ParsedOperation(
            operation="set_desired_count",
            value=int(count_match.group(1)),
            message="Requested ECS task count identified.",
        )

    # CPU units
    cpu_match = re.search(r"\bcpu\s+(?:to\s+)?(\d+)\b", text)

    if cpu_match:
        return ParsedOperation(
            operation="set_cpu",
            value=int(cpu_match.group(1)),
            message="Requested CPU value identified.",
        )

    # Memory in MiB
    memory_match = re.search(
        r"\bmemory\s+(?:to\s+)?(\d+)\s*(?:mib|mb)?\b",
        text,
    )

    if memory_match:
        return ParsedOperation(
            operation="set_memory",
            value=int(memory_match.group(1)),
            message="Requested memory value identified.",
        )

    # Container image version
    image_match = re.search(
        r"\b(?:image|version|tag)\s+(?:to\s+)?v?([a-zA-Z0-9._-]+)\b",
        text,
    )

    if image_match:
        return ParsedOperation(
            operation="set_image",
            value=image_match.group(1),
            message="Requested image version identified.",
        )

    return ParsedOperation(
        operation="unknown",
        value=None,
        message=(
            "I couldn't understand that request. "
            "Try specifying a task count, CPU, memory, or image version."
        ),
    )

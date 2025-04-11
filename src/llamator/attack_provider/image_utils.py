import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def imgpath2base64(image_path: Union[str, Path]):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def create_vision_messages(
    image_base64: str, vision_prompt: str = "What do you see?", system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                },
            ],
        }
    ]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    return messages

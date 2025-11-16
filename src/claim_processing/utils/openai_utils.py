import os
from typing import Optional

from openai import BaseModel, OpenAI

from claim_processing.constants import MODEL_API_KEY, MODEL_API_URL


def get_image_mime_type(image_path: str) -> str:
    """Determine the MIME type based on file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }
    return mime_types.get(ext, "image/png")  # Default to PNG if unknown


def get_openai_client():
    return OpenAI(
        base_url=MODEL_API_URL,
        api_key=MODEL_API_KEY,
    )


def send_image_request_openai(
    system_prompt: str,
    image_filename: str,
    image_bytestring: str,
    vision_model_name: str,
    response_format: Optional[BaseModel] = None,
) -> str:
    client = OpenAI(
        base_url=MODEL_API_URL,
        api_key=MODEL_API_KEY,
    )

    mime_type = get_image_mime_type(image_filename)

    if response_format:
        response = client.chat.completions.parse(
            model=vision_model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_bytestring}"
                            },
                        },
                    ],
                }
            ],
            response_format=response_format,
        )
    else:
        response = client.chat.completions.create(
            model=vision_model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_bytestring}"
                            },
                        },
                    ],
                }
            ],
        )
    return response.choices[0].message.content

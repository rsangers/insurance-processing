import base64
import json

from claim_processing.constants import AUTHENTICITY_MODEL_NAME, OCR_MODEL_NAME, USE_OCR
from claim_processing.prompts import (
    AUTHENTICITY_PROMPT,
    DOCUMENT_FORMAT_PROMPT,
    OCR_PROMPT,
)
from claim_processing.pydantic_models import AuthenticityResponse, Document
from claim_processing.utils.openai_utils import send_image_request_openai


def judge_image_authenticity(image_bytestring: str, image_filename: str):
    response = send_image_request_openai(
        system_prompt=AUTHENTICITY_PROMPT,
        image_filename=image_filename,
        image_bytestring=image_bytestring,
        vision_model_name=AUTHENTICITY_MODEL_NAME,
        response_format=AuthenticityResponse,
    )
    response_json = json.loads(response)
    return response_json


def extract_text_from_doc(document: Document, use_ocr: bool = USE_OCR) -> str:
    if document.type == "text supporting document":
        return DOCUMENT_FORMAT_PROMPT.format(
            document_name=document.name, document_content=document.content
        )
    else:
        if use_ocr:
            image_content = send_image_request_openai(
                system_prompt=OCR_PROMPT,
                image_filename=document.name,
                image_bytestring=document.content,
                vision_model_name=OCR_MODEL_NAME,
            )
            return DOCUMENT_FORMAT_PROMPT.format(
                document_name=document.name, document_content=image_content
            )
        else:
            return DOCUMENT_FORMAT_PROMPT.format(
                document_name=document.name,
                document_content="Supporting document could not be read",
            )


if __name__ == "__main__":
    # file_path = "assignment/claim 7/Spanish_medical_15.webp"
    file_path = "assignment/claim 1/Spanish_medical_15.webp"

    with open(file_path, "rb") as file:
        file_bytestring = base64.b64encode(file.read()).decode("utf-8")

    # response = judge_image_authenticity(file_bytestring, file_path)
    response = extract_text_from_doc(
        Document("test", file_bytestring, "text supporting document")
    )
    print(response)

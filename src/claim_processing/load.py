import os

from claim_processing.constants import CLAIM_DIRECTORY, FILES_TO_EXCLUDE, POLICY_DIRECTORY
from claim_processing.pydantic_models import Claim, Document
from claim_processing.utils import extract_text_from_image


def load_description(claim_directory: str):
    with open(os.path.join(claim_directory, "description.txt"), "r") as file:
        return Document(name="description.txt", content=file.read(), type="description")


def load_supporting_documents(claim_directory: str):
    supporting_documents = []
    for file_name in os.listdir(claim_directory):
        file_path = os.path.join(claim_directory, file_name)
        if file_name in FILES_TO_EXCLUDE:
            continue
        elif file_name.endswith(".md"):
            with open(file_path, "r") as file:
                supporting_documents.append(
                    Document(
                        name=file_name, content=file.read(), type="supporting document"
                    )
                )
        elif file_name.endswith((".png", ".jpg", ".webp")):
            text = extract_text_from_image(file_path)
            supporting_documents.append(
                Document(name=file_name, content=text, type="supporting document")
            )
        else:
            raise ValueError(f"Unsupported file type: {file_name}")
    return supporting_documents


def load_claim(claim_id: str):
    claim_directory = os.path.join(CLAIM_DIRECTORY, "claim " + claim_id)
    description = load_description(claim_directory)
    supporting_documents = load_supporting_documents(claim_directory)
    return Claim(
        claim_id=claim_id,
        description=description,
        supporting_documents=supporting_documents,
    )


def load_policy():
    with open(os.path.join(POLICY_DIRECTORY, "policy.md"), "r") as file:
        return Document(name="policy.md", content=file.read(), type="policy")

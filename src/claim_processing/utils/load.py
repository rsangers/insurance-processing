import json
from ntpath import isdir
import os
from typing import Dict, List

from fastapi import HTTPException

from claim_processing.constants import CLAIM_DIRECTORY, FILES_TO_EXCLUDE, POLICY_DIRECTORY, RESULTS_DIRECTORY
from claim_processing.pydantic_models import Claim, ClaimDecision, Document
from claim_processing.utils.image_utils import extract_text_from_image


def load_description(claim_directory: str):
    with open(os.path.join(claim_directory, "description.txt"), "r", encoding="utf-8", errors="replace") as file:
        return Document(name="description.txt", content=file.read(), type="description")


def load_supporting_documents(claim_directory: str):
    supporting_documents = []
    for file_name in os.listdir(claim_directory):
        file_path = os.path.join(claim_directory, file_name)
        if file_name in FILES_TO_EXCLUDE:
            continue
        elif file_name.endswith(".md"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                supporting_documents.append(
                    Document(
                        name=file_name, content=file.read(), type="supporting document"
                    )
                )
        elif file_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            text = extract_text_from_image(file_path)
            supporting_documents.append(
                Document(name=file_name, content=text, type="supporting document")
            )
        else:
            raise ValueError(f"Unsupported file type: {file_name}")
    return supporting_documents


def load_claim(claim_id: int):
    claim_directory = os.path.join(CLAIM_DIRECTORY, "claim " + str(claim_id))
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


def load_claim_decision(claim_id: int) -> ClaimDecision:
    claim_decision_file = os.path.join(RESULTS_DIRECTORY, f"claim {claim_id} decision.json")

    if not os.path.exists(claim_decision_file):
        raise HTTPException(status_code=404, detail="Claim decision is not available yet")

    with open(claim_decision_file, "r") as decision_file:
        decision = json.load(decision_file)

    return ClaimDecision(reasoning=decision["reasoning"], decision=decision["decision"])

def load_all_decisions(results_dir: str = RESULTS_DIRECTORY) -> Dict[int, ClaimDecision]:
    decisions = {}
    for decision_file_name in os.listdir(results_dir):
        if decision_file_name.endswith("decision.json"):
            claim_id = int(decision_file_name.replace("claim ", "").replace(" decision.json", ""))
            with open(os.path.join(results_dir, decision_file_name), "r") as decision_file:
                decision = json.load(decision_file)
            decisions[claim_id] = ClaimDecision(reasoning=decision["reasoning"], decision=decision["decision"])
    return decisions


def load_all_answers() -> Dict[int, ClaimDecision]:
    answers = {}
    for claim_dir in os.listdir(CLAIM_DIRECTORY):
        if claim_dir.startswith("claim"):
            claim_id = int(claim_dir.replace("claim ", ""))
            with open(os.path.join(CLAIM_DIRECTORY, claim_dir, "answer.json"), "r") as answer_file:
                answer = json.load(answer_file)
            if "explanation" not in answers.keys():
                answer["explanation"] = "NA"
            answers[claim_id] = ClaimDecision(reasoning=answer["explanation"], decision=answer["decision"])

    return answers
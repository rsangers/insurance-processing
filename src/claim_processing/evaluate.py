import json
import logging
import os

import mlflow
import pandas as pd

from claim_processing.process import process_and_upload_all_claims
from claim_processing.utils.decision_engines import (
    DummyDecisionEngine,
    SimpleLLMDecisionEngine,
)
from claim_processing.utils.load import load_all_answers, load_all_decisions

logger = logging.getLogger()


def evaluate_decisions(results_dir: str):
    available_decisions = load_all_decisions(results_dir=results_dir)
    available_answers = load_all_answers()
    common_claim_ids = available_decisions.keys() & available_answers.keys()

    evaluation_data = [
        [
            claim_id,
            available_answers[claim_id].decision,
            available_decisions[claim_id].decision,
            available_answers[claim_id].reasoning,
            available_decisions[claim_id].reasoning,
        ]
        for claim_id in common_claim_ids
    ]
    evaluation_df = pd.DataFrame(
        evaluation_data,
        columns=[
            "claim_id",
            "decision_true",
            "decision_pred",
            "reasoning_true",
            "reasoning_pred",
        ],
    )
    evaluation_df.to_csv(os.path.join(results_dir, "results.csv"))

    n_correct = 0
    for _, row in evaluation_df.iterrows():
        if row["decision_true"] == row["decision_pred"]:
            n_correct += 1
    accuracy = n_correct / len(evaluation_df)

    with open(os.path.join(results_dir, "results.json"), "w") as results_file:
        json.dump({"accuracy": accuracy}, results_file)

    print(f"Accuracy: {accuracy}")


if __name__ == "__main__":
    mlflow.openai.autolog()

    decision_model = "SimpleLLM"
    check_authenticity = True
    use_ocr = True

    if decision_model == "SimpleLLM":
        decision_engine = SimpleLLMDecisionEngine()
        config_name = "SimpleLLM"
        if check_authenticity:
            config_name += "Auth"
        if use_ocr:
            config_name += "OCR"
        config_name += "ProImproved"
    elif decision_model == "DummyDeny":
        decision_engine = DummyDecisionEngine(decision="DENY")
        check_authenticity = False  # No effect to check authenticity for dummy
        use_ocr = False  # No effect to use ocr for dummy
        config_name = "DummyDeny"
    else:
        raise Exception(f"Model not supported: {decision_model}")

    logger.info(
        f"Using configuration:\nModel: {decision_model}\nCheck authenticity: {check_authenticity}\nUse OCR: {use_ocr}"
    )

    results_dir = os.path.join("results", config_name)
    process_and_upload_all_claims(
        decision_engine=decision_engine,
        results_dir=results_dir,
        check_authenticity=check_authenticity,
        use_ocr=use_ocr,
    )
    evaluate_decisions(results_dir)

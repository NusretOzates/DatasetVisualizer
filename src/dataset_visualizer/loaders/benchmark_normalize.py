"""Normalize Hugging Face benchmark rows to explorer-friendly columns."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

ANSWER_LETTERS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _letter_from_index(index: int) -> str:
    if 0 <= index < len(ANSWER_LETTERS):
        return ANSWER_LETTERS[index]
    return str(index)


def _choices_from_dict(choices: object) -> list[str]:
    if isinstance(choices, dict):
        if "text" in choices and isinstance(choices["text"], list):
            labels = choices.get("label", list(range(len(choices["text"]))))
            return [str(text) for text, label in zip(choices["text"], labels, strict=False)]
        return [str(value) for value in choices.values()]
    if isinstance(choices, list):
        return [str(item) for item in choices]
    return []


def _answer_letter_from_key(answer_key: object, choices: list[str]) -> str:
    """Resolve mixed benchmark answer keys into display letters."""
    if answer_key is None or (isinstance(answer_key, float) and pd.isna(answer_key)):
        return ""
    if isinstance(answer_key, str):
        stripped = answer_key.strip().upper()
        if len(stripped) == 1 and stripped in ANSWER_LETTERS:
            return stripped
        if stripped.isdigit():
            return _letter_from_index(int(stripped))
        for index, choice in enumerate(choices):
            if choice == answer_key:
                return _letter_from_index(index)
        resolved = stripped
    elif isinstance(answer_key, int):
        resolved = _letter_from_index(answer_key)
    else:
        resolved = str(answer_key)
    return resolved


def _ensure_sample_id(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    normalized = df.copy()
    if id_column not in normalized.columns:
        normalized[id_column] = normalized.index.astype(str)
    else:
        normalized[id_column] = normalized[id_column].astype(str)
    return normalized


def normalize_arc(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize AI2 ARC rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "choices" in normalized.columns:
        normalized["choices"] = normalized["choices"].map(_choices_from_dict)
        normalized["answer_letter"] = normalized.apply(
            lambda row: _answer_letter_from_key(row.get("answerKey"), row["choices"]),
            axis=1,
        )
    return normalized


def normalize_winogrande(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize WinoGrande rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question"] = normalized["sentence"]
    normalized["choices"] = normalized.apply(
        lambda row: [str(row["option1"]), str(row["option2"])],
        axis=1,
    )
    normalized["answer_letter"] = normalized["answer"].map(
        lambda value: "A" if str(value) == "1" else "B" if str(value) == "2" else str(value)
    )
    return normalized


def normalize_hellaswag(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize HellaSwag rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question"] = normalized.get("ctx", normalized.get("activity_label", ""))
    normalized["choices"] = normalized["endings"]
    normalized["answer_letter"] = normalized["label"].map(_letter_from_index)
    return normalized


def normalize_commonsenseqa(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize CommonsenseQA rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["choices"] = normalized["choices"].map(_choices_from_dict)
    normalized["answer_letter"] = normalized.apply(
        lambda row: _answer_letter_from_key(row.get("answerKey"), row["choices"]),
        axis=1,
    )
    return normalized


def normalize_piqa(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize PIQA rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question"] = normalized["goal"]
    normalized["choices"] = normalized.apply(
        lambda row: [str(row["sol1"]), str(row["sol2"])],
        axis=1,
    )
    normalized["answer_letter"] = normalized["label"].map(_letter_from_index)
    return normalized


def normalize_openbookqa(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize OpenBookQA rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question"] = normalized.get("question_stem", normalized.get("question", ""))
    normalized["choices"] = normalized["choices"].map(_choices_from_dict)
    normalized["answer_letter"] = normalized.apply(
        lambda row: _answer_letter_from_key(row.get("answerKey"), row["choices"]),
        axis=1,
    )
    return normalized


def normalize_zebra_logic(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize ZebraLogic rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question"] = (
        normalized["puzzle"].astype(str) + "\n\n" + normalized["question"].astype(str)
    )
    if "choices" in normalized.columns:
        normalized["choices"] = normalized["choices"].map(
            lambda value: value if isinstance(value, list) else [str(value)]
        )
        normalized["answer_letter"] = normalized["answer"].astype(str).str.upper()
    return normalized


def normalize_mmlu_redux(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize MMLU-Redux rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "choices" in normalized.columns:
        normalized["choices"] = normalized["choices"].map(
            lambda value: value if isinstance(value, list) else _choices_from_dict(value)
        )
    if "answer" in normalized.columns and "answer_letter" not in normalized.columns:
        normalized["answer_letter"] = normalized["answer"].astype(str).str.upper()
    return normalized


def normalize_gsm(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize grade-school math word problem rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "problem" not in normalized.columns and "question" in normalized.columns:
        normalized["problem"] = normalized["question"]
    if "problem_idx" not in normalized.columns:
        normalized["problem_idx"] = normalized[id_column]
    return normalized


def normalize_math_competition(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize competition math rows (MATH, MATH-500, MATH-Hard, MathArena)."""
    normalized = _ensure_sample_id(df, id_column)
    if "problem_idx" not in normalized.columns:
        normalized["problem_idx"] = normalized[id_column]
    return normalized


def normalize_code_eval(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize HumanEval/MBPP/EvoEval-style code rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "question_content" not in normalized.columns:
        normalized["question_content"] = normalized.get(
            "prompt",
            normalized.get("text", normalized.get("question", "")),
        )
    if "question_id" not in normalized.columns:
        normalized["question_id"] = normalized[id_column]
    if "canonical_solution" not in normalized.columns:
        normalized["canonical_solution"] = normalized.get(
            "code",
            normalized.get("solution", ""),
        )
    if "test_code" not in normalized.columns:
        normalized["test_code"] = normalized.get("test", normalized.get("test_list", ""))
    return normalized


def normalize_apps(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize APPS JSONL rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question_content"] = normalized["question"]
    normalized["question_id"] = normalized["id"].astype(str)
    normalized["difficulty"] = normalized.get("difficulty", "")
    normalized["starter_code"] = normalized.get("starter_code", "")
    return normalized


def normalize_mbpp(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize MBPP rows."""
    normalized = normalize_code_eval(df, id_column)
    if "text" in normalized.columns:
        normalized["question_content"] = normalized["text"]
    if "test_list" in normalized.columns:
        normalized["test_code"] = normalized["test_list"].map(
            lambda tests: "\n".join(tests) if isinstance(tests, list) else str(tests)
        )
    return normalized


def normalize_instruction(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize IFEval/IFBench rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "prompt" not in normalized.columns and "question" in normalized.columns:
        normalized["prompt"] = normalized["question"]
    return normalized


def normalize_coconot(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize CoCoNot rows."""
    normalized = _ensure_sample_id(df, id_column)
    return normalized


def normalize_agent_task(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize agent/tool benchmark rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "question" not in normalized.columns and "Question" in normalized.columns:
        normalized["question"] = normalized["Question"]
    return normalized


def normalize_gaia(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize GAIA rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "question" not in normalized.columns and "Question" in normalized.columns:
        normalized["question"] = normalized["Question"]
    if "answer" not in normalized.columns and "Final answer" in normalized.columns:
        normalized["answer"] = normalized["Final answer"]
    return normalized


def normalize_gaia2(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize GAIA2 scenario rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "scenario_config" not in normalized.columns and "data" in normalized.columns:
        normalized["scenario_config"] = normalized["data"].map(
            lambda value: (
                json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value)
            )
        )
    return normalized


def _json_ready(value: object) -> object:
    """Convert nested array-like values into JSON-serializable containers."""
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if hasattr(value, "tolist"):
        return _json_ready(value.tolist())
    return value


def normalize_arc_agi(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize ARC-AGI puzzle rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "puzzle_json" not in normalized.columns:
        normalized["puzzle_json"] = normalized["question"].map(
            lambda value: (
                json.dumps(_json_ready(value), indent=2)
                if isinstance(value, (dict, list, tuple)) or hasattr(value, "tolist")
                else str(value)
            )
        )
    return normalized


def normalize_generic(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Pass through rows with a stable sample id."""
    return _ensure_sample_id(df, id_column)


NORMALIZERS: dict[str, Any] = {
    "arc": normalize_arc,
    "winogrande": normalize_winogrande,
    "hellaswag": normalize_hellaswag,
    "commonsenseqa": normalize_commonsenseqa,
    "piqa": normalize_piqa,
    "openbookqa": normalize_openbookqa,
    "zebra_logic": normalize_zebra_logic,
    "mmlu_redux": normalize_mmlu_redux,
    "gsm": normalize_gsm,
    "math_competition": normalize_math_competition,
    "code_eval": normalize_code_eval,
    "mbpp": normalize_mbpp,
    "apps": normalize_apps,
    "instruction": normalize_instruction,
    "coconot": normalize_coconot,
    "agent_task": normalize_agent_task,
    "gaia": normalize_gaia,
    "gaia2": normalize_gaia2,
    "arc_agi": normalize_arc_agi,
    "generic": normalize_generic,
}


def normalize_benchmark(df: pd.DataFrame, profile: str, id_column: str) -> pd.DataFrame:
    """Apply a normalization profile to a raw benchmark DataFrame."""
    normalizer = NORMALIZERS.get(profile, normalize_generic)
    normalized = normalizer(df, id_column)
    if "split" not in normalized.columns:
        normalized["split"] = "test"
    return normalized

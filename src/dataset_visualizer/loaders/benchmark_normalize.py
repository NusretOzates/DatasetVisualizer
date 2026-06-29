"""Normalize Hugging Face benchmark rows to explorer-friendly columns."""

from __future__ import annotations

import ast
import json
from typing import Any

import numpy as np
import pandas as pd

from dataset_visualizer.loaders.mtob_crypto import decrypt_mtob_text

ANSWER_LETTERS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_PRESERVE_LIST_COLUMNS = frozenset({
    "choices",
    "options",
    "endings",
    "scenario_tags",
    "scenario_hints",
    "app_names",
    "events_summary",
    "predictions",
    "enabled_tools",
    "gtfa_claims",
    "trajectory",
})
GAIA2_EVENTS_SUMMARY_LIMIT = 25


def _letter_from_index(index: int | str) -> str:
    """Map a zero-based choice index to a display letter."""
    try:
        numeric_index = int(index)
    except (TypeError, ValueError):
        return str(index)
    if 0 <= numeric_index < len(ANSWER_LETTERS):
        return ANSWER_LETTERS[numeric_index]
    return str(index)


def _sequence_values(value: object) -> list[object] | None:
    """Return list contents from HF list, tuple, or ndarray cells."""
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes, dict)):
        try:
            coerced = value.tolist()
        except (TypeError, ValueError):
            return None
        if isinstance(coerced, list):
            return coerced
    return None


def _choices_from_dict(choices: object) -> list[str]:
    if isinstance(choices, dict):
        text_values = choices.get("text")
        text_seq = _sequence_values(text_values) if text_values is not None else None
        if text_seq is not None:
            labels = choices.get("label")
            label_seq = _sequence_values(labels) if labels is not None else None
            if label_seq is None:
                label_seq = list(range(len(text_seq)))
            return [str(text) for text, _label in zip(text_seq, label_seq, strict=False)]
        return [str(value) for value in choices.values()]
    text_seq = _sequence_values(choices)
    if text_seq is not None:
        return [str(item) for item in text_seq]
    if choices is None:
        return []
    return [str(choices)]


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


def _scalarize_cell(value: object, *, preserve_list: bool = False) -> object:
    """Convert HF array-like cells into hashable Python values."""
    if value is None or value is pd.NA or (isinstance(value, float) and pd.isna(value)):
        return value
    if isinstance(value, np.ndarray):
        value = value.item() if value.ndim == 0 else value.tolist()
    if isinstance(value, (list, tuple)):
        items = [_scalarize_cell(item, preserve_list=preserve_list) for item in value]
        if preserve_list:
            value = items
        elif len(items) == 1:
            value = items[0]
        elif all(isinstance(item, str) for item in items):
            value = ", ".join(sorted(items))
        else:
            value = json.dumps(items, sort_keys=True)
        return value
    if isinstance(value, dict):
        return {
            str(key): _scalarize_cell(item, preserve_list=preserve_list)
            for key, item in value.items()
        }
    return value


def _scalarize_object_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Scalarize object columns so filters can hash values."""
    normalized = df.copy()
    for column in normalized.columns:
        if normalized[column].dtype != object:
            continue
        preserve_list = column in _PRESERVE_LIST_COLUMNS
        normalized[column] = normalized[column].map(
            lambda value, preserve=preserve_list: _scalarize_cell(value, preserve_list=preserve)
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


def _gaia2_user_message(events: list[object]) -> str:
    """Return the user's opening task message from a GAIA2 event list."""
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "USER":
            continue
        action = event.get("action") or {}
        if not isinstance(action, dict) or action.get("function") != "send_message_to_agent":
            continue
        for arg in action.get("args") or []:
            if isinstance(arg, dict) and arg.get("name") == "content":
                return str(arg.get("value") or "").strip()
    return ""


def _gaia2_events_summary(events: list[object]) -> list[dict[str, object]]:
    """Summarize oracle agent actions without serializing full app state."""
    summary: list[dict[str, object]] = []
    for event in events[:GAIA2_EVENTS_SUMMARY_LIMIT]:
        if not isinstance(event, dict):
            continue
        action = event.get("action") or {}
        if not isinstance(action, dict):
            action = {}
        entry: dict[str, object] = {
            "type": event.get("event_type"),
            "app": action.get("app"),
            "function": action.get("function"),
        }
        args = action.get("args") or []
        if args and isinstance(args[0], dict):
            preview_arg = args[0]
            entry["arg"] = preview_arg.get("name")
            value = preview_arg.get("value")
            if isinstance(value, str) and len(value) > 120:
                value = f"{value[:120]}…"
            entry["value"] = value
        summary.append(entry)
    return summary


def _extract_gaia2_fields(value: object) -> dict[str, object]:
    """Extract explorer-friendly fields from a GAIA2 scenario payload."""
    if isinstance(value, str):
        try:
            payload = json.loads(value)
        except json.JSONDecodeError:
            return {"user_message": value}
    elif isinstance(value, dict):
        payload = value
    else:
        return {}

    definition = (payload.get("metadata") or {}).get("definition") or {}
    if not isinstance(definition, dict):
        definition = {}
    events = payload.get("events") or []
    if not isinstance(events, list):
        events = []
    apps = payload.get("apps") or []
    if not isinstance(apps, list):
        apps = []

    return {
        "user_message": _gaia2_user_message(events),
        "scenario_tags": definition.get("tags") or [],
        "scenario_hints": definition.get("hints") or [],
        "app_names": [
            str(app.get("name"))
            for app in apps
            if isinstance(app, dict) and app.get("name")
        ],
        "event_count": len(events),
        "events_summary": _gaia2_events_summary(events),
    }


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
    return normalized


def normalize_mmlu_redux(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize MMLU-Redux rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "choices" in normalized.columns:
        normalized["choices"] = normalized["choices"].map(
            lambda value: value if isinstance(value, list) else _choices_from_dict(value)
        )
    if "answer" in normalized.columns and "answer_letter" not in normalized.columns:
        normalized["answer_letter"] = normalized["answer"].map(_letter_from_index)
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


def _compose_scicode_prompt(row: pd.Series) -> str:
    """Build a markdown prompt from SciCode problem columns."""
    parts: list[str] = []
    name = row.get("problem_name")
    if name is not None and not (isinstance(name, float) and pd.isna(name)):
        text = str(name).strip()
        if text:
            parts.append(f"**{text}**")
    for column in ("problem_description_main", "problem_background_main"):
        value = row.get(column)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        text = str(value).strip()
        if text:
            parts.append(text)
    for column, heading in (
        ("problem_io", "I/O"),
        ("required_dependencies", "Dependencies"),
    ):
        value = row.get(column)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        text = str(value).strip()
        if text:
            parts.append(f"### {heading}\n```python\n{text}\n```")
    return "\n\n".join(parts)


def normalize_scicode(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize SciCode rows to code-eval viewer columns."""
    normalized = normalize_code_eval(df, id_column)
    if "problem_description_main" not in normalized.columns:
        return normalized
    normalized["question_content"] = normalized.apply(_compose_scicode_prompt, axis=1)
    if "general_solution" in normalized.columns:
        normalized["canonical_solution"] = normalized["general_solution"]
    if "general_tests" in normalized.columns:
        normalized["test_code"] = normalized["general_tests"]
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


def _is_null_value(value: object) -> bool:
    """Return whether an instruction kwargs value should be omitted from display."""
    if value is None:
        return True
    return isinstance(value, float) and pd.isna(value)


def _compact_kwargs(value: object) -> object | None:
    """Drop null entries from IFEval/IFBench kwargs payloads."""
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        return _compact_kwargs(parsed)

    if isinstance(value, dict):
        compact = {
            key: inner for key, inner in value.items() if not _is_null_value(inner)
        }
        return compact or None

    if isinstance(value, list):
        compact_items = [_compact_kwargs(item) for item in value]
        compact_items = [
            item for item in compact_items if item is not None and item != {}
        ]
        return compact_items or None

    return value


def normalize_instruction(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize IFEval/IFBench rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "prompt" not in normalized.columns and "question" in normalized.columns:
        normalized["prompt"] = normalized["question"]
    if "kwargs" in normalized.columns:
        normalized["kwargs"] = normalized["kwargs"].map(_compact_kwargs)
    return normalized


def normalize_coconot(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize CoCoNot rows."""
    normalized = _ensure_sample_id(df, id_column)
    return normalized


def normalize_agent_task(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize agent/tool benchmark rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "Question" in normalized.columns:
        if "question" not in normalized.columns:
            normalized["question"] = normalized["Question"]
        normalized = normalized.drop(columns=["Question"])
    if "Annotator Metadata" in normalized.columns:
        normalized = normalized.rename(columns={"Annotator Metadata": "annotator_metadata"})
    return normalized


def _unescape_hub_string(text: str) -> str:
    """Decode common escaped sequences in malformed Hub string literals."""
    return (
        text.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\'", "'")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def _fallback_pythonish_list(text: str) -> list[str]:
    """Best-effort parse when upstream list literals contain unescaped quotes."""
    stripped = text.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if inner.startswith("'"):
            body = inner[1:]
            if body.endswith("'"):
                body = body[:-1]
            return [_unescape_hub_string(body)]
    return [stripped]


def _parse_pythonish_list(value: object) -> list[Any]:
    """Parse list-like Hub strings stored as Python literals."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    seq = _sequence_values(value)
    if seq is not None:
        return [str(item) for item in seq]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return _fallback_pythonish_list(text)
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def _parse_json_list(value: object) -> list[Any]:
    """Parse JSON-encoded list columns from Hub exports."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    seq = _sequence_values(value)
    if seq is not None:
        return seq
    text = str(value).strip()
    if not text:
        return []
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    return [parsed]


def normalize_mcp_atlas(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize ScaleAI MCP-Atlas tool-use benchmark rows."""
    normalized = df.copy()
    renames = {
        "TASK": "task_id",
        "PROMPT": "prompt",
        "ENABLED_TOOLS": "enabled_tools_raw",
        "GTFA_CLAIMS": "gtfa_claims_raw",
        "TRAJECTORY": "trajectory_raw",
    }
    for old_name, new_name in renames.items():
        if old_name in normalized.columns:
            normalized = normalized.rename(columns={old_name: new_name})

    if "task_id" not in normalized.columns and id_column in normalized.columns:
        normalized["task_id"] = normalized[id_column]

    normalized = _ensure_sample_id(normalized, "task_id")
    prompt = normalized.get("prompt", pd.Series(dtype=str)).astype(str)
    normalized["question"] = prompt
    normalized["prompt_preview"] = prompt.str.slice(0, 120)
    normalized["enabled_tools"] = normalized["enabled_tools_raw"].map(_parse_pythonish_list)
    normalized["enabled_tool_count"] = normalized["enabled_tools"].map(len)
    normalized["gtfa_claims"] = normalized["gtfa_claims_raw"].map(_parse_pythonish_list)
    normalized["gtfa_claim_count"] = normalized["gtfa_claims"].map(len)
    normalized["trajectory"] = normalized["trajectory_raw"].map(_parse_json_list)
    normalized["trajectory_step_count"] = normalized["trajectory"].map(len)
    raw_columns = ("enabled_tools_raw", "gtfa_claims_raw", "trajectory_raw")
    drop_cols = [col for col in raw_columns if col in normalized.columns]
    if drop_cols:
        normalized = normalized.drop(columns=drop_cols)
    return normalized


def normalize_gaia(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize GAIA rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "question" not in normalized.columns and "Question" in normalized.columns:
        normalized["question"] = normalized["Question"]
    if "answer" not in normalized.columns and "Final answer" in normalized.columns:
        normalized["answer"] = normalized["Final answer"]
    if "level" not in normalized.columns and "Level" in normalized.columns:
        normalized["level"] = normalized["Level"]
    if "Annotator Metadata" in normalized.columns:
        normalized = normalized.rename(columns={"Annotator Metadata": "annotator_metadata"})
    return normalized


def normalize_gaia2(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize GAIA2 scenario rows."""
    normalized = _ensure_sample_id(df, id_column)
    if "data" in normalized.columns:
        extracted = normalized["data"].map(_extract_gaia2_fields)
        for field in (
            "user_message",
            "scenario_tags",
            "scenario_hints",
            "app_names",
            "event_count",
            "events_summary",
        ):
            normalized[field] = extracted.map(lambda fields, key=field: fields.get(key))
        normalized = normalized.drop(columns=["data"])
    if "scenario_config" in normalized.columns:
        normalized = normalized.drop(columns=["scenario_config"])
    return normalized


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


def normalize_mtob(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Decrypt MTOB ciphertext columns into readable source/target text."""
    normalized = _ensure_sample_id(df, id_column)

    def _decrypt_row(row: pd.Series) -> pd.Series:
        try:
            source = decrypt_mtob_text(str(row["original_nonce"]), str(row["original_ciphertext"]))
            target = decrypt_mtob_text(
                str(row["ground_truth_nonce"]),
                str(row["ground_truth_ciphertext"]),
            )
        except (KeyError, TypeError, ValueError) as err:
            msg = f"MTOB decryption failed: {err}"
            raise ValueError(msg) from err
        row = row.copy()
        row["source_text"] = source
        row["target_text"] = target
        return row

    required = {
        "original_nonce",
        "original_ciphertext",
        "ground_truth_nonce",
        "ground_truth_ciphertext",
    }
    if not required.issubset(normalized.columns):
        missing = ", ".join(sorted(required - set(normalized.columns)))
        msg = f"MTOB rows are missing encryption columns: {missing}"
        raise ValueError(msg)

    return normalized.apply(_decrypt_row, axis=1)


def normalize_futurebench(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Group FutureBench model runs into one row per forecast event."""
    normalized = _ensure_sample_id(df, id_column)
    if "event_id" not in normalized.columns:
        return normalized

    rows: list[dict[str, object]] = []
    for event_id, group in normalized.groupby("event_id", sort=False):
        first = group.iloc[0]
        predictions = [
            {
                "algorithm_name": row.get("algorithm_name"),
                "actual_prediction": row.get("actual_prediction"),
                "prediction_created_at": row.get("prediction_created_at"),
                "source": row.get("source"),
            }
            for _, row in group.iterrows()
        ]
        rows.append(
            {
                id_column: str(event_id),
                "sample_id": str(event_id),
                "event_id": str(event_id),
                "question": first.get("question"),
                "event_type": first.get("event_type"),
                "open_to_bet_until": first.get("open_to_bet_until"),
                "result": first.get("result"),
                "model_count": len(predictions),
                "predictions": predictions,
                "split": first.get("split"),
            }
        )
    return pd.DataFrame(rows)


def _split_semicolon_list(value: object) -> list[str]:
    """Split Hub semicolon-delimited reference strings into a list."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def normalize_aa_lcr(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize Artificial Analysis long-context reasoning rows."""
    normalized = df.copy()
    if "Unnamed: 0" in normalized.columns:
        normalized = normalized.drop(columns=["Unnamed: 0"])
    normalized["sample_id"] = (
        normalized["document_set_id"].astype(str) + "_" + normalized["question_id"].astype(str)
    )
    normalized = _ensure_sample_id(normalized, "sample_id")
    normalized["category"] = normalized["document_category"]
    normalized["source_filenames"] = normalized["data_source_filenames"].map(_split_semicolon_list)
    normalized["source_urls"] = normalized["data_source_urls"].map(_split_semicolon_list)
    normalized["source_file_count"] = normalized["source_filenames"].map(len)
    question = normalized["question"].astype(str)
    normalized["question_preview"] = question.str.slice(0, 160)
    return normalized


def normalize_aa_omniscience(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize AA-Omniscience public knowledge rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["category"] = normalized["domain"]
    question = normalized["question"].astype(str)
    normalized["question_preview"] = question.str.slice(0, 160)
    return normalized


def normalize_critpt(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    """Normalize CritPt physics research coding rows."""
    normalized = _ensure_sample_id(df, id_column)
    normalized["question_content"] = normalized["problem_description"]
    normalized["canonical_solution"] = normalized["answer_code"]
    normalized["starter_code"] = normalized["code_template"]
    normalized["question_id"] = normalized[id_column]
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
    "scicode": normalize_scicode,
    "mbpp": normalize_mbpp,
    "apps": normalize_apps,
    "instruction": normalize_instruction,
    "coconot": normalize_coconot,
    "agent_task": normalize_agent_task,
    "mcp_atlas": normalize_mcp_atlas,
    "gaia": normalize_gaia,
    "gaia2": normalize_gaia2,
    "arc_agi": normalize_arc_agi,
    "mtob": normalize_mtob,
    "futurebench": normalize_futurebench,
    "aa_lcr": normalize_aa_lcr,
    "aa_omniscience": normalize_aa_omniscience,
    "critpt": normalize_critpt,
    "generic": normalize_generic,
}


def normalize_benchmark(df: pd.DataFrame, profile: str, id_column: str) -> pd.DataFrame:
    """Apply a normalization profile to a raw benchmark DataFrame."""
    normalizer = NORMALIZERS.get(profile, normalize_generic)
    normalized = normalizer(df, id_column)
    if "split" not in normalized.columns:
        normalized["split"] = "test"
    return _scalarize_object_columns(normalized)

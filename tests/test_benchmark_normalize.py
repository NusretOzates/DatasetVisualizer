"""Tests for benchmark normalization helpers."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from dataset_visualizer.loaders.benchmark_normalize import (
    _parse_pythonish_list,
    normalize_agent_task,
    normalize_arc,
    normalize_arc_agi,
    normalize_benchmark,
    normalize_commonsenseqa,
    normalize_futurebench,
    normalize_gaia,
    normalize_gaia2,
    normalize_hellaswag,
    normalize_instruction,
    normalize_mcp_atlas,
    normalize_mmlu_redux,
    normalize_piqa,
    normalize_scicode,
    normalize_winogrande,
)


def test_normalize_arc_maps_answer_key() -> None:
    df = pd.DataFrame(
        {
            "id": ["1"],
            "question": ["What is 2+2?"],
            "choices": [{"text": ["3", "4"], "label": ["A", "B"]}],
            "answerKey": ["B"],
        }
    )
    normalized = normalize_arc(df, "id")
    assert normalized["choices"].iloc[0] == ["3", "4"]
    assert normalized["answer_letter"].iloc[0] == "B"


def test_normalize_arc_maps_numpy_choice_arrays() -> None:
    df = pd.DataFrame(
        {
            "id": ["1"],
            "question": ["Ramp experiment?"],
            "choices": [
                {
                    "label": np.array(["A", "B", "C", "D"]),
                    "text": np.array(
                        [
                            "Put the objects in groups.",
                            "Change the height of the ramp.",
                            "Choose different objects to roll.",
                            "Record the steps they took.",
                        ]
                    ),
                }
            ],
            "answerKey": ["D"],
        }
    )
    normalized = normalize_arc(df, "id")
    assert normalized["choices"].iloc[0] == [
        "Put the objects in groups.",
        "Change the height of the ramp.",
        "Choose different objects to roll.",
        "Record the steps they took.",
    ]
    assert normalized["answer_letter"].iloc[0] == "D"


def test_normalize_commonsenseqa_maps_numpy_choice_arrays() -> None:
    df = pd.DataFrame(
        {
            "id": ["1"],
            "question": ["Where is the library?"],
            "choices": [
                {
                    "label": np.array(["A", "B", "C", "D", "E"]),
                    "text": np.array(["bank", "library", "store", "mall", "park"]),
                }
            ],
            "answerKey": ["B"],
        }
    )
    normalized = normalize_commonsenseqa(df, "id")
    assert normalized["choices"].iloc[0] == ["bank", "library", "store", "mall", "park"]
    assert normalized["answer_letter"].iloc[0] == "B"


def test_normalize_winogrande_maps_options() -> None:
    df = pd.DataFrame(
        {
            "sentence": ["The trophy does not fit in the suitcase because it is too large."],
            "option1": ["the trophy"],
            "option2": ["the suitcase"],
            "answer": ["1"],
        }
    )
    normalized = normalize_winogrande(df, "sample_id")
    assert normalized["choices"].iloc[0] == ["the trophy", "the suitcase"]
    assert normalized["answer_letter"].iloc[0] == "A"


def test_normalize_hellaswag_maps_endings() -> None:
    df = pd.DataFrame(
        {
            "ctx": ["A person opens a door"],
            "endings": [["then leaves", "then sings"]],
            "label": [0],
        }
    )
    normalized = normalize_hellaswag(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "A"
    assert normalized["choices"].iloc[0] == ["then leaves", "then sings"]


def test_normalize_hellaswag_accepts_string_labels() -> None:
    df = pd.DataFrame(
        {
            "ctx": ["A person opens a door"],
            "endings": [["then leaves", "then sings"]],
            "label": ["1"],
        }
    )
    normalized = normalize_hellaswag(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "B"


def test_normalize_piqa_maps_solutions() -> None:
    df = pd.DataFrame(
        {
            "goal": ["Boil water"],
            "sol1": ["Use a kettle"],
            "sol2": ["Use a freezer"],
            "label": [0],
        }
    )
    normalized = normalize_piqa(df, "sample_id")
    assert normalized["answer_letter"].iloc[0] == "A"


def test_normalize_benchmark_scalarizes_ndarray_cells() -> None:
    df = pd.DataFrame(
        {
            "problem": ["Compute 1+1", "Solve for x"],
            "problem_type": [
                np.array(["Number Theory"], dtype=object),
                np.array(["Algebra", "Number Theory"], dtype=object),
            ],
            "answer": ["2", "4"],
        }
    )

    normalized = normalize_benchmark(df, "math_competition", "problem_idx")

    assert normalized["problem_type"].tolist() == ["Number Theory", "Algebra, Number Theory"]


def test_normalize_arc_agi_serializes_nested_arrays() -> None:
    df = pd.DataFrame(
        {
            "question": [
                {
                    "train": [
                        {
                            "input": np.array([[0, 1], [1, 0]]),
                            "output": np.array([[1, 0], [0, 1]]),
                        }
                    ],
                    "test": [{"input": [[0]], "output": [[1]]}],
                }
            ],
        }
    )

    normalized = normalize_arc_agi(df, "sample_id")

    assert '"train"' in normalized["puzzle_json"].iloc[0]
    assert "array(" not in normalized["puzzle_json"].iloc[0]


def test_normalize_gaia_maps_annotator_metadata_and_level() -> None:
    df = pd.DataFrame(
        {
            "task_id": ["task-1"],
            "Question": ["What is 2+2?"],
            "Final answer": ["4"],
            "Level": ["1"],
            "Annotator Metadata": [{"Steps": "Add the numbers.", "Number of steps": "1"}],
        }
    )

    normalized = normalize_gaia(df, "task_id")

    assert normalized["question"].iloc[0] == "What is 2+2?"
    assert normalized["answer"].iloc[0] == "4"
    assert normalized["level"].iloc[0] == "1"
    assert normalized["annotator_metadata"].iloc[0]["Steps"] == "Add the numbers."
    assert "Annotator Metadata" not in normalized.columns


def test_normalize_gaia2_extracts_scenario_summary_and_drops_raw_payload() -> None:
    payload = {
        "metadata": {
            "definition": {
                "scenario_id": "scenario-1",
                "hints": ["Check the calendar"],
                "tags": ["Adaptability"],
            }
        },
        "apps": [{"name": "Calendar"}, {"name": "Emails"}],
        "events": [
            {
                "event_type": "USER",
                "action": {
                    "function": "send_message_to_agent",
                    "args": [{"name": "content", "value": "Book a meeting tomorrow."}],
                },
            },
            {
                "event_type": "AGENT",
                "action": {
                    "app": "Calendar",
                    "function": "add_calendar_event",
                    "args": [{"name": "title", "value": "Meeting"}],
                },
            },
        ],
    }
    df = pd.DataFrame(
        {
            "id": ["scenario-1"],
            "scenario_id": ["adaptability"],
            "data": [json.dumps(payload)],
        }
    )

    normalized = normalize_gaia2(df, "id")

    assert "data" not in normalized.columns
    assert "scenario_config" not in normalized.columns
    assert normalized["user_message"].iloc[0] == "Book a meeting tomorrow."
    assert normalized["scenario_tags"].iloc[0] == ["Adaptability"]
    assert normalized["scenario_hints"].iloc[0] == ["Check the calendar"]
    assert normalized["app_names"].iloc[0] == ["Calendar", "Emails"]
    assert normalized["event_count"].iloc[0] == 2
    assert normalized["events_summary"].iloc[0][1]["function"] == "add_calendar_event"


def test_normalize_benchmark_preserves_gaia2_list_columns() -> None:
    payload = {
        "metadata": {"definition": {"tags": ["Adaptability"], "hints": []}},
        "apps": [{"name": "Calendar"}],
        "events": [
            {
                "event_type": "AGENT",
                "action": {
                    "app": "Calendar",
                    "function": "add_calendar_event",
                    "args": [{"name": "title", "value": "Meeting"}],
                },
            }
        ],
    }
    df = pd.DataFrame({"id": ["scenario-1"], "data": [json.dumps(payload)]})
    normalized = normalize_benchmark(df, "gaia2", "id")
    assert normalized["scenario_tags"].iloc[0] == ["Adaptability"]
    assert normalized["app_names"].iloc[0] == ["Calendar"]
    assert isinstance(normalized["events_summary"].iloc[0], list)


def test_normalize_instruction_compacts_ifbench_kwargs() -> None:
    df = pd.DataFrame(
        {
            "prompt": ["Write a poem."],
            "kwargs": [
                {
                    "keyword1": "kaleidoscope",
                    "keyword2": None,
                    "num_words": float("nan"),
                    "relation": None,
                }
            ],
        }
    )

    normalized = normalize_instruction(df, "sample_id")

    assert normalized["kwargs"].iloc[0] == {"keyword1": "kaleidoscope"}


def test_normalize_instruction_compacts_ifeval_kwargs_json() -> None:
    kwargs = [
        {"num_words": None, "relation": None},
        {"num_highlights": 3, "relation": None},
    ]
    df = pd.DataFrame(
        {
            "prompt": ["Summarize the text."],
            "kwargs": [json.dumps(kwargs)],
        }
    )

    normalized = normalize_instruction(df, "sample_id")

    assert normalized["kwargs"].iloc[0] == [{"num_highlights": 3}]


def test_normalize_scicode_maps_code_eval_columns() -> None:
    df = pd.DataFrame(
        {
            "problem_name": ["ewald_summation"],
            "problem_id": ["10"],
            "problem_description_main": ["Calculate Ewald energy."],
            "problem_background_main": [""],
            "problem_io": ["def foo(): pass"],
            "required_dependencies": ["import numpy as np"],
            "sub_steps": ['[{"step_number": "10.1"}]'],
            "general_solution": ["def foo(): return 1"],
            "general_tests": ["assert foo() == 1"],
        }
    )

    normalized = normalize_scicode(df, "problem_id")

    assert normalized["question_id"].iloc[0] == "10"
    assert "Calculate Ewald energy." in normalized["question_content"].iloc[0]
    assert "import numpy as np" in normalized["question_content"].iloc[0]
    assert normalized["canonical_solution"].iloc[0] == "def foo(): return 1"
    assert normalized["test_code"].iloc[0] == "assert foo() == 1"
    assert normalized["sub_steps"].iloc[0] == '[{"step_number": "10.1"}]'


def test_normalize_benchmark_scicode_profile() -> None:
    df = pd.DataFrame(
        {
            "problem_id": ["1"],
            "problem_name": ["demo"],
            "problem_description_main": ["Do science."],
            "general_solution": ["pass"],
            "general_tests": ["pass"],
        }
    )

    normalized = normalize_benchmark(df, "scicode", "problem_id")

    assert normalized["question_id"].iloc[0] == "1"
    assert normalized["question_content"].iloc[0]
    assert normalized["canonical_solution"].iloc[0] == "pass"


def test_normalize_agent_task_unifies_livemcpbench_columns() -> None:
    df = pd.DataFrame(
        {
            "task_id": ["task-1"],
            "Question": ["Analyze the audio file."],
            "answers": [""],
            "category": ["Leisure"],
            "file_name": ["/root/music/sample.wav"],
            "Annotator Metadata": [{"Number of steps": "5", "Steps": "Load the audio file"}],
        }
    )

    normalized = normalize_agent_task(df, "task_id")

    assert "Question" not in normalized.columns
    assert "Annotator Metadata" not in normalized.columns
    assert normalized["question"].iloc[0] == "Analyze the audio file."
    assert normalized["annotator_metadata"].iloc[0]["Number of steps"] == "5"


def test_normalize_mcp_atlas_parses_tool_claim_and_trajectory_fields() -> None:
    trajectory = json.dumps(
        [
            {
                "content": "Looking up the repository.",
                "role": "assistant",
                "tool_calls": [{"function": {"name": "github_search_repositories"}}],
            }
        ]
    )
    df = pd.DataFrame(
        {
            "TASK": ["task-abc"],
            "PROMPT": ["Find the repository creation year."],
            "ENABLED_TOOLS": ['["github_search_repositories", "whois_whois_domain"]'],
            "GTFA_CLAIMS": "['Claim one.', 'Claim two.']",
            "TRAJECTORY": trajectory,
        }
    )

    normalized = normalize_mcp_atlas(df, "task_id")

    assert normalized["task_id"].iloc[0] == "task-abc"
    assert normalized["question"].iloc[0] == "Find the repository creation year."
    assert normalized["enabled_tools"].iloc[0] == [
        "github_search_repositories",
        "whois_whois_domain",
    ]
    assert normalized["gtfa_claims"].iloc[0] == ["Claim one.", "Claim two."]
    assert normalized["trajectory_step_count"].iloc[0] == 1


def test_parse_pythonish_list_falls_back_for_malformed_gtfa_claim() -> None:
    malformed = (
        "['The very first version of the main README, translated into Croatian is:\\n\\n```\\n"
        "# mcp-calculator\\n```\\n']"
    )
    claims = _parse_pythonish_list(malformed)
    assert len(claims) == 1
    assert "mcp-calculator" in claims[0]
    assert "```" in claims[0]


def test_normalize_futurebench_groups_model_runs_by_event() -> None:
    df = pd.DataFrame(
        {
            "event_id": ["120", "120", "121"],
            "question": [
                "Will airport reopen?",
                "Will airport reopen?",
                "Will rates rise?",
            ],
            "event_type": ["news", "news", "market"],
            "open_to_bet_until": ["2025-06-18", "2025-06-18", "2025-07-01"],
            "result": ["Yes", "Yes", "No"],
            "algorithm_name": ["model-a", "model-b", "model-a"],
            "actual_prediction": ["No", "Yes", "No"],
            "prediction_created_at": ["t1", "t2", "t3"],
            "source": ["app", "app", "app"],
            "split": ["train", "train", "train"],
        }
    )

    normalized = normalize_futurebench(df, "event_id")

    assert len(normalized) == 2
    event_120 = normalized[normalized["event_id"] == "120"].iloc[0]
    assert event_120["question"] == "Will airport reopen?"
    assert event_120["model_count"] == 2
    assert len(event_120["predictions"]) == 2
    assert event_120["predictions"][0]["algorithm_name"] == "model-a"


def test_normalize_mmlu_redux_maps_numeric_answer_to_letter() -> None:
    df = pd.DataFrame(
        {
            "question": ["Which bundle is correct?"],
            "choices": [["Option A", "Option B", "Option C", "Option D"]],
            "answer": [1],
            "subject": ["anatomy"],
        }
    )

    normalized = normalize_mmlu_redux(df, "sample_id")

    assert normalized["answer_letter"].iloc[0] == "B"

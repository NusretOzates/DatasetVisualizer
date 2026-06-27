# MCP-Atlas

**Source:** [`ScaleAI/MCP-Atlas`](https://huggingface.co/datasets/ScaleAI/MCP-Atlas) (`train` split, 500 tasks)  
**Archetype:** MCP tool-use agent task  
**Loader:** `dataset_visualizer.loaders.hf_benchmark` with `profile: mcp_atlas`

MCP-Atlas evaluates multi-step tool orchestration across real MCP servers. The public Hub release is a 500-task subset with prompts, enabled tool subsets, ground-truth-for-answer (GTFA) claims, and reference trajectories.

## Normalized columns

| Column | Description |
|--------|-------------|
| `task_id` | 24-character task identifier |
| `prompt` / `question` | Natural-language user request |
| `prompt_preview` | Truncated prompt for overview tables |
| `enabled_tools` | Parsed list of tool names exposed to the agent |
| `enabled_tool_count` | Number of enabled tools |
| `gtfa_claims` | Parsed list of verifiable answer claims |
| `gtfa_claim_count` | Number of GTFA claims |
| `trajectory` | Parsed reference tool-call trajectory (JSON messages) |
| `trajectory_step_count` | Number of trajectory steps |

## UI notes

- **Overview** — generic HF overview with row metadata.
- **Sample inspector** — prompt, enabled tools, GTFA claims, collapsible reference trajectory JSON.

## Links

- [MCP-Atlas paper](https://huggingface.co/papers/2504.12516) (see dataset card for current paper link)

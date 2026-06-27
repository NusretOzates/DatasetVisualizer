# Toolathlon

**Source:** [hkust-nlp/Toolathlon](https://github.com/hkust-nlp/Toolathlon)  
**Trajectories:** [hkust-nlp/Toolathlon-Trajectories](https://huggingface.co/datasets/hkust-nlp/Toolathlon-Trajectories) on Hugging Face  
**Paper:** [The Tool Decathlon (arXiv:2510.25726)](https://arxiv.org/abs/2510.25726)  
**Archetype:** MCP / tool-use agent task  
**Loader:** `dataset_visualizer.loaders.toolathlon` (`load_toolathlon`)

Toolathlon benchmarks language agents on 108 realistic, long-horizon tasks that combine MCP servers (filesystem, GitHub, Snowflake, …) with local tools (web search, terminal, context management). This app loads task prompts and tool requirements from the GitHub `tasks/finalpool/` tree. Model execution trajectories (17 models × 3 runs) live in the separate Hugging Face dataset.

## Category

Registered under **Agentic tasks** with GAIA, MCP-Atlas, and other agent benchmarks.

## Normalized columns

| Column | Description |
|--------|-------------|
| `task_id` / `sample_id` | Task slug (directory name under `finalpool`) |
| `task_name` | Same as `task_id` |
| `task_pool` | Upstream pool name (`finalpool`) |
| `question` / `instruction` | Natural-language task from `docs/task.md` |
| `instruction_preview` | Truncated prompt for overview tables |
| `needed_mcp_servers` | MCP servers required for the task |
| `needed_local_tools` | Built-in local tools (web search, claim_done, …) |
| `primary_mcp` | First MCP server (used for overview filters) |
| `mcp_server_count` / `local_tool_count` | Tool counts |
| `split` | Pool label (`finalpool`) |

## UI notes

- **Overview** — task count, MCP/tool averages, distribution by primary MCP server (browse individual tasks via filters and the sample inspector).
- **Filters** — primary MCP server multiselect.
- **Sample inspector** — full task markdown plus MCP/local tool badges.

## Cache

GitHub archive cached under `data/cache/toolathlon/`.

## Links

- [Project README](https://github.com/hkust-nlp/Toolathlon)
- [Trajectory dataset](https://huggingface.co/datasets/hkust-nlp/Toolathlon-Trajectories)

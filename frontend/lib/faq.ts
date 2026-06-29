export type FaqItem = {
  id: string;
  question: string;
  answer: string;
};

export const FAQ_ITEMS: FaqItem[] = [
  {
    id: "mmlu-differences",
    question: "What are the differences between MMLU datasets?",
    answer: `This catalog includes five related multiple-choice benchmarks:

- **[MMLU](/dataset/mmlu/)** — The original Massive Multitask Language Understanding suite: 57 academic subjects, four options per question, and \`test\` / \`validation\` / \`dev\` splits from \`cais/mmlu\`.
- **[MMLU-Pro](/dataset/mmlu_pro/)** — A harder successor with up to ten options, broader discipline categories, and chain-of-thought rationales. Better for stress-testing reasoning, not apples-to-apples with classic MMLU scores.
- **[MMLU-Redux](/dataset/mmlu_redux/)** — A cleaned, re-annotated subset of original MMLU items with error-type metadata. Useful when you care about label quality and failure modes, not full-subject coverage.
- **[Global-MMLU](/dataset/global_mmlu/)** — Cohere Labs' multilingual extension across 42 languages, with cultural-sensitivity and required-knowledge annotations. Pick a language config before loading.
- **[MMMLU](/dataset/mmmlu/)** — OpenAI's professionally translated MMLU test set in 14 locales. Same subject taxonomy as MMLU, but non-English only; load one locale at a time.

**Rule of thumb:** use **MMLU** for standard English knowledge scores, **MMLU-Pro** for harder reasoning, **MMLU-Redux** for label-quality analysis, and **Global-MMLU** / **MMMLU** for multilingual evaluation.`,
  },
  {
    id: "global-mmlu-vs-mmmlu",
    question: "Global-MMLU vs MMMLU — which should I use?",
    answer: `Both extend MMLU-style multiple choice to non-English locales, but they are not interchangeable:

- **[Global-MMLU](/dataset/global_mmlu/)** — 42 language configs from Cohere Labs, plus annotations for cultural sensitivity and required knowledge. Supports \`dev\` and \`test\` splits; pick a language in the sidebar before loading.
- **[MMMLU](/dataset/mmmlu/)** — 14 professionally translated locales from OpenAI (\`DE_DE\`, \`JA_JP\`, \`ZH_CN\`, etc.). \`test\` split only; one locale at a time.

**Rule of thumb:** choose **Global-MMLU** for broad language coverage and cultural-metadata analysis; choose **MMMLU** for OpenAI's fixed 14-locale translation suite.`,
  },
  {
    id: "math-differences",
    question: "What are the differences between the math benchmarks?",
    answer: `Math entries fall into four families:

**Grade-school word problems (GSM lineage)**
- **[GSM8K](/dataset/gsm8k/)** — Classic 8k grade-school problems; the usual baseline for chain-of-thought math.
- **[GSM1K](/dataset/gsm1k/)** — A 1k-problem holdout designed to reduce contamination concerns vs GSM8K.
- **[GSM-Plus](/dataset/gsm_plus/)** — Harder, perturbed variants of GSM-style problems.
- **[GSM-Symbolic](/dataset/gsm_symbolic/)** — Symbolic rewrites of GSM8K to test robustness beyond memorized number patterns.

**Competition / proof-style math**
- **[MATH](/dataset/math/)** — Full Hendrycks MATH corpus across difficulty levels and subjects (multi-config).
- **[MATH-500](/dataset/math_500/)** — A fixed 500-problem subset commonly used for fast evals.
- **[MATH-Hard](/dataset/math_hard/)** — Harder-filtered MATH problems.
- **[Math-Arena](/dataset/math_arena/)** — Paper-style competition problems from recent MathArena releases.

**Timed competition**
- **[AIME 2026](/dataset/aime_2026/)** — AIME-style integer-answer problems with official solutions.

**Research inspection**
- **[ArXiv Math 0526](/dataset/arxivmath_0526/)** — ArXiv problems paired with model outputs for comparing reasoning traces, not a standard leaderboard set.

**Rule of thumb:** **GSM8K** for grade-school, **MATH** / **MATH-500** for competition math, **AIME 2026** for olympiad-style answers, **ArXiv Math** when you need to inspect model runs.`,
  },
  {
    id: "code-gen-differences",
    question: "What are the differences between the code-generation benchmarks?",
    answer: `Python function-completion and broader coding evals serve different goals:

**Classic completion suites**
- **[HumanEval](/dataset/humaneval/)** — 164 small Python functions with unit tests; the original LLM coding sanity check.
- **[HumanEval+](/dataset/humaneval_plus/)** — Same prompts as HumanEval with stricter tests from EvalPlus.
- **[MBPP](/dataset/mbpp/)** — Mostly basic Python programming problems stated in plain language.
- **[MBPP+](/dataset/mbpp_plus/)** — MBPP with expanded, harder tests (EvalPlus). Scores are not comparable to base MBPP.

**Harder / broader coding**
- **[APPS](/dataset/apps/)** — Thousands of problems from introductory to competition difficulty with larger test harnesses.
- **[EvoEval Difficult](/dataset/evoeval_difficult/)** — Semantically rewritten HumanEval items labeled difficult.
- **[LiveCodeBench v6](/dataset/livecodebench_v6/)** — Contamination-resistant, regularly updated competitive programming tasks (manual loader with dated releases).

**Scientific / domain coding**
- **[SciCode](/dataset/scicode/)** — Research coding with decomposed scientific subproblems across STEM fields (also part of the Artificial Analysis Intelligence Index).

**Rule of thumb:** **HumanEval/MBPP** for quick baselines, **+** variants when you care about test rigor, **LiveCodeBench** for modern contest problems, **SciCode** for science-oriented code.`,
  },
  {
    id: "swe-bench-differences",
    question: "What are the differences between SWE-Bench datasets?",
    answer: `All three variants share the same issue-resolution shape — GitHub \`problem_statement\`, gold \`patch\`, and pass/fail test lists — but target different evaluation goals:

- **[SWE-Bench Verified](/dataset/swe_bench_verified/)** — 500 human-validated Python repair tasks from real repos. This is the standard "official" subset for comparing coding agents on trustworthy gold patches. Includes a \`difficulty\` field.
- **[SWE-Bench Multilingual](/dataset/swe_bench_multilingual/)** — 300 tasks across nine programming languages. Same repair workflow as Verified, but tests cross-language issue resolution instead of Python-only performance.
- **[SWE-Bench PRO](/dataset/swe_bench_pro/)** — 731 larger, enterprise-style tasks with richer metadata (\`requirements\`, \`interface\`, \`repo_language\`, issue categories, setup commands). Harder and more heterogeneous than Verified.

**Rule of thumb:** use **Verified** for mainstream Python agent benchmarks, **Multilingual** when language coverage matters, and **PRO** for harder, production-flavored repair scenarios.`,
  },
  {
    id: "aa-intelligence-index",
    question: "What is the Artificial Analysis Intelligence Index?",
    answer: `The **Artificial Analysis Intelligence Index v4.1** is a composite score that tracks frontier model capability across reasoning, coding, knowledge, and agentic work. All nine components are in this catalog:

**Agents (34% combined)**
- **[GDPval](/dataset/gdpval/)** (20%) — Real occupation-style deliverables across 44 jobs.
- **[τ³-Bench](/dataset/tau3_bench/)** (14%) — Tool–user–agent simulations (banking domain in the index; the catalog includes airline, retail, telecom, and banking tasks).
- **[Terminal-Bench 2.1](/dataset/terminal_bench_21/)** (16%) — Containerized CLI / systems tasks.

**Coding (24%)**
- **[SciCode](/dataset/scicode/)** (8%) — Scientific coding subproblems.

**Scientific reasoning (24%)**
- **[Humanity's Last Exam](/dataset/hle/)** (12%) — Hard multimodal academic QA.
- **[GPQA Diamond](/dataset/gpqa_diamond/)** (6%) — Graduate-level science MCQ (gated).
- **[CritPt](/dataset/critpt/)** (6%) — Research-level physics with Python answers.

**General (18%)**
- **[AA-LCR](/dataset/aa_lcr/)** (6%) — ~100k-token multi-document reasoning.
- **[AA-Omniscience](/dataset/aa_omniscience/)** (12%) — Factual recall and hallucination across domains (600-question public subset).

Weights are from [Artificial Analysis](https://artificialanalysis.ai/methodology/intelligence-benchmarking). Scores across components are not directly comparable — use this app to inspect each benchmark's tasks separately.`,
  },
  {
    id: "gaia-gdpval-differences",
    question: "What are the differences between GAIA, GAIA2, and GDPval?",
    answer: `All three are **agentic** benchmarks, but they stress different real-world workflows:

- **[GAIA](/dataset/gaia/)** — Original GAIA assistant tasks (level 1 validation split) requiring web search, files, and tools. Short, verifiable answers. **Gated** on Hugging Face.
- **[GAIA2](/dataset/gaia2/)** — Meta's asynchronous agent scenarios across adaptability, ambiguity, execution, and time-sensitive subsets. Multi-config Hub dataset with rich scenario metadata.
- **[GDPval](/dataset/gdpval/)** — OpenAI tasks spanning 44 occupations with reference files, rubrics, and deliverable expectations — closer to knowledge-work simulation than trivia QA.

**Rule of thumb:** **GAIA** for classic assistant tool-use, **GAIA2** for complex multi-step agent scenarios, **GDPval** for open-ended work products. **GDPval** is the highest-weighted single component in the Intelligence Index.`,
  },
  {
    id: "ifeval-vs-ifbench",
    question: "IFEval vs IFBench — what's the difference?",
    answer: `Both test instruction following, but at different difficulty levels:

- **[IFEval](/dataset/ifeval/)** — Google's benchmark of verifiable constraints (format, length, keywords, etc.) checked programmatically. A common baseline for "can the model follow explicit rules?"
- **[IFBench](/dataset/ifbench/)** — AllenAI's harder suite with 58+ diverse, out-of-domain constraints. Frontier models began saturating it; Artificial Analysis **removed IFBench from the Intelligence Index** in v4.1 but still publishes standalone results.

**Rule of thumb:** start with **IFEval** for standard IF capability; use **IFBench** when you need to separate top-tier models on novel constraint types.`,
  },
];

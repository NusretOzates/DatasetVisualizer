export type FaqItem = {
  id: string;
  question: string;
  answer: string;
};

export const SIDEBAR_FAQ: FaqItem[] = [
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
    id: "swe-bench-differences",
    question: "What are the differences between SWE-Bench datasets?",
    answer: `All three variants share the same issue-resolution shape — GitHub \`problem_statement\`, gold \`patch\`, and pass/fail test lists — but target different evaluation goals:

- **[SWE-Bench Verified](/dataset/swe_bench_verified/)** — 500 human-validated Python repair tasks from real repos. This is the standard "official" subset for comparing coding agents on trustworthy gold patches. Includes a \`difficulty\` field.
- **[SWE-Bench Multilingual](/dataset/swe_bench_multilingual/)** — 300 tasks across nine programming languages. Same repair workflow as Verified, but tests cross-language issue resolution instead of Python-only performance.
- **[SWE-Bench PRO](/dataset/swe_bench_pro/)** — 731 larger, enterprise-style tasks with richer metadata (\`requirements\`, \`interface\`, \`repo_language\`, issue categories, setup commands). Harder and more heterogeneous than Verified.

**Rule of thumb:** use **Verified** for mainstream Python agent benchmarks, **Multilingual** when language coverage matters, and **PRO** for harder, production-flavored repair scenarios.`,
  },
];

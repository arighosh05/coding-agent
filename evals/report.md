<p align="center">
  <img src="../img/eval_pic_2.png" alt="logo" width="600">
</p>

<p align="center">
  <img src="../img/eval_pic_1.png" alt="logo" width="600">
</p>

<h1 align="center">Report</h1>

## Introduction

As automated coding agents become increasingly sophisticated, systematic assessment of their performance, capabilities, and limitations becomes essential for understanding their potential practical applications. This report presents an evaluation of our coding agent across multiple dimensions of software development tasks. Due to resource constraints, our analysis provides a targeted assessment rather than a comprehensive evaluation. The primary objectives of this evaluation include characterizing the agent's performance, identifying strengths and weaknesses, and providing a structured analysis that can inform the development lifecycle of agentic systems.

## Methodology

We conducted a comparative evaluation of our coding agent against OpenAI's ChatGPT using a standardized set of code review and improvement tasks. The evaluation consisted of 15 distinct code and context pairs, with both systems utilizing the 4o model to ensure a consistent baseline for comparison.

For each prompt, the following protocol was followed:

- Provide code and contextual information to both the coding agent and ChatGPT
- Prompt for a comprehensive code review
- If potential improvements were identified, request code refinement

Note that the neither the coding agent nor ChatGPT were prompted with additional human feedback.

The coding agent was utilized with preloaded tools from the tool registry and supplementary text files ingested into the knowledge store.

Find the output codes from the agent in the `agent` directory and from ChatGPT in the `llm` directory. The code and context pairs are provided in the `issues` directory, and the JSON files documenting each trial are provided in the `data` directory.

## Results

The coding agent consistently produced more verbose and comprehensive code compared to ChatGPT's more concise implementations. Despite this difference, both systems demonstrated equivalent logical correctness and problem-solving capabilities. The observed variation in code verbosity suggests that the custom agent could potentially be optimized through targeted prompt engineering to modulate code generation verbosity. While current performance appears comparable, we hypothesize that parallelized architectural approaches may provide advantages in handling larger codebases that exceed traditional context window limitations.

The coding agent exhibited increased susceptibility to being misled or manipulated. This vulnerability appears to stem from the agent's complex information processing pipeline, which integrates multiple data sources including the tool registry and RAG system. The lack of independent safety mechanisms beyond the base LLM's guardrails creates potential compounding risks if initial safety checks fail. In contrast, ChatGPT demonstrated more robust built-in safety mechanisms. The web interface's multi-layered guardrails effectively mitigated potential attempts to generate problematic or dangerous code.

## Conclusion

The results underscore the nuanced challenges in developing autonomous coding systems. The trade-offs between comprehensiveness, safety, and adaptability represent critical areas for future research and system design.

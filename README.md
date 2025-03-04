<p align="center">
  <img src="./img/agent_logo.png" alt="logo" width="100">
</p>


<div align="center">

  <b>Coding Agent</b>
----------------------
a coding agent for code review

</div>

<p align="center">
  <a href="https://opensource.org/license/mit">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
</p>

## About

In this work, we present an experimental framework that enhances the code review process via augmenting the core developer workflow. Our coding agent is built on the belief that the future reveals itself not in systems that act independently, but in architectures that breathe alongside us, enhancing the uniquely human capacity for creative insight. 

To this end, our agent is composed of a thoughtfully crafted workflow with augmented LLM blocks and deliberate human checkpoints to streamline the code review process. To evaluate our agent, we compare our approach with direct foundation model use.

This work hopes to serve as a thoughtful comma in an ongoing dialogue about what we build, why we build it, and who we become alongside our creations. 

## Workflow

The workflow of the agent is represented by the diagram below:

<p align="center">
  <img src="./img/high_level_diagram.png" alt="image" width="950">
</p>

> At a high-level, the agent takes in as input some code with its corresponding context and spits out as output a comprehensive code review.  Furthermore, if the user opts for it, the agent generates improved code based on the previously generated code review and optional human feedback. 

Let's dive deeper into the technical elements that compose the agent.

The agent has access to a ***knowledge store***. The idea behind the knowledge store is to augment the knowledge of the LLMs. In essence, the agent retrieves relevant information from ingested documents to fill in any knowledge gaps. This approach is generally called **Retrieval Augmented Generation** or **RAG** for short. The agent is optimized to perform ***contextual retrieval***, wherin, instead of just embedding raw text chunks, the agent makes LLM calls to generate a brief contextual summary for each chunk. The entire process is greately parallelized, meaning that embeddings and contextual summaries are generated in parallel, significantly reducing processing time. The implementation includes methods to save and load the vector database, making it persistent across sessions. It uses FAISS for efficient similarity search, which allows for extremely fast nearest-neighbor queries. The system supports caching query embeddings and performing top-k similarity searches, making it adaptable to various retrieval scenarios.

The agent has access to a ***tool registry***. The idea behind the tool registry is to provide comprehensive, multi-dimensional code evaluation tools through a pluggable and extensible architecture. It provides a mapping of the various analysis aspects to specialized functions designed to perform static code analysis. The registry comes preloaded with hand-crafted functions that employ multiple advanced static code analysis techniques including abstract syntax tree parsing, regular expression-based pattern matching, recursive code traversal, and comprehensive code pattern detection. The modular design of the tool registry allows easy addition of new analysis tools. The agent is optimized to front-load the computational work by directly passing the code as input to the analysis functions, bypassing traditional function-calling and making the generation phase more efficient.

## Notes

## Meta

Aritra Ghosh – aritraghosh543@gmail.com

Distributed under the MIT license. See `LICENSE` for more information.

[https://github.com/arighosh05/](https://github.com/arighosh05/)

## Contributing

1. Fork it (<https://github.com/arighosh05/coding-agent/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

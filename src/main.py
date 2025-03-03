import json
import asyncio
import os
from typing import Dict, List
from openai import AsyncOpenAI
from modules.knowledge_store import KnowledgeStore
from modules.tool_registry import get_tool_by_aspect
from tabulate import tabulate

OPENAI_API_KEY = "api-key"


class CodeReviewAgent:
    """agent orchestrating multiple LLM calls to analyze diverse aspects of the code."""

    def __init__(self, model="gpt-4o"):
        """an augmented LLM block : gpt-4o + knowledge_store"""

        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.knowledge_store = KnowledgeStore(name="knowledge_repo")

        self.aspects = {
            "time_complexity": "Analyze the time complexity of this code. "
                               "Identify inefficiencies and suggest optimizations.",
            "space_complexity": "Analyze the space complexity of this code. "
                                "Identify inefficiencies and suggest optimizations.",
            "edge_cases": "Identify potential edge cases that this code might not handle properly."
                          "Explain potential issues and how to fix them. ",
            "code_clarity": "Evaluate code readability and maintainability. "
                            "Identify confusing sections, poor variable names, or complex logic. Suggest improvements.",
            "security": "Identify security vulnerabilities in this code. "
                        "Suggest security best practices and fixes for any identified issues.",
            "correctness": "Identify any logical errors or bugs in the code. "
                           "Suggest improvements for the code to achieve desired functionality. ",
            "scalability": "Identify if the code relies on any single bottleneck or resource. "
                           "Suggest improvements for horizontal or vertical scaling if usage grows",
            "extensibility": "Ensure new features can be added to the code with minimal refactoring. "
                             "Recommend any design patterns that enhance extensibility.",
            "dependency": "Verify that external libraries have compatible licenses. "
                          "Check if third-party dependencies are updated or pinned to stable versions. "
                          "Recommend suggestions if issue arises."
        }

    async def analyze_aspect(self, code: str, aspect: str, prompt: str, context: str) -> Dict:
        """analyze a single aspect of the code"""
        system_prompt = f"You are a code review expert focusing specifically on {aspect}. {prompt}"

        # RAG
        query = f"{aspect} review for {context}"
        relevant_info = await self.knowledge_store.search(query, k=3)

        retrieved_context = ""

        if relevant_info:
            retrieved_context = "Relevant information from knowledge base:\n"
        for info in relevant_info:
            retrieved_context += f"- {info['metadata']['original_content']}\n"

        # --- Function Calling via Tool Registry ---
        # Attempt to get a tool function for the given aspect.
        tool_func = get_tool_by_aspect(aspect)
        tool_result = ""
        if tool_func:
            # Call the tool function synchronously.
            tool_result = tool_func(code)

        # Combine the retrieved context with the tool output.
        combined_context = f"{retrieved_context}\nTool analysis result:\n{tool_result}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"\nReview this code:\n```\n{code}\n```"
                                                f"\nContext for this code:\n{context}\n"
                                                f"\n{combined_context}"}
                ],
                max_tokens=1000
            )
            return {
                "aspect": aspect,
                "analysis": response.choices[0].message.content
            }
        except Exception as e:
            return {
                "aspect": aspect,
                "analysis": f"Error analyzing {aspect}: {str(e)}"
            }

    async def analyze_code(self, code:str, context:str) -> List[Dict]:
        """analyze multiple aspects of the code in parallel """
        tasks = []
        for aspect, prompt in self.aspects.items():
            tasks.append(self.analyze_aspect(code, aspect, prompt, context))

        return await asyncio.gather(*tasks)

    async def code_review(self, code: str, context: str) -> Dict:
        """executes the code review workflow via sectioning"""

        print("analyzing code on multiple aspects....\n")
        sectioned_reviews = await self.analyze_code(code, context)

        print("aggregating reviews....\n")

        aggregated_review = {r["aspect"]: r["analysis"] for r in sectioned_reviews}

        return aggregated_review


class CodeGenerationAgent:
    """agent conducting evaluator-optimizer workflow to generate code."""

    def __init__(self, model="gpt-4o"):
        """a vanilla dual LLM block"""

        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.planner = model
        self.executor = model

    async def planner_executor(self, feedback: str, code: str, context: str, review: Dict) -> str:
        planner_prompt = """
        You are an expert code improvement planner. Your task is to create a detailed plan for improving code 
        based on a code review. Make sure you give high priority to the human feedback.
        
        Please follow these steps:
        
        1. Analyze the key issues identified in the review
        2. Prioritize the issues based on severity and impact
        3. Create a step-by-step action plan to address each issue
        4. Identify potential challenges in implementing the improvements
        5. Suggest design patterns or best practices to incorporate
        
        Your output should be a structured plan with the following sections:
        - Summary of Issues (brief overview of main problems)
        - Prioritized Action Items (list each change needed in priority order)
        - Implementation Strategy (overall approach to making changes)
        - Potential Challenges (what might be difficult about these changes)
        - Success Criteria (how to verify the improvements work)
        
        Be specific and focus on concrete, actionable steps. Consider the provided context about what the code 
        is intended to do when making your plan.
        """

        json_string_review = json.dumps(review)

        planner_messages = [
            {"role": "system", "content": planner_prompt},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nCODE:\n```\n{code}\n```\n\nCODE REVIEW:\n"
                                        f"{json_string_review}\nFEEDBACK OF CODE REVIEW:\n{feedback}"}
        ]

        planner_response = await self.client.chat.completions.create(
            model=self.planner,
            messages=planner_messages,
            max_tokens=2000
        )

        plan = planner_response.choices[0].message.content

        executor_prompt = """
        You are an expert code implementer. You have been given a detailed improvement plan for code modification.
        Your task is to implement this plan by writing the improved code. Make sure you give high priority to the
        human feedback.

        Follow these guidelines:
        1. Implement each action item from the plan in the priority order specified
        2. Maintain the existing functionality while addressing the issues
        3. Follow the best practices suggested in the plan
        4. Add helpful comments to explain significant changes
        5. Ensure the code remains readable and maintainable

        Your output should be ONLY the complete improved code. Do not include explanations outside of code comments.
        """

        executor_response = await self.client.chat.completions.create(
            model=self.executor,
            messages=[
                {"role": "system", "content": executor_prompt},
                {"role": "user", "content": f"ORIGINAL CODE:\n```\n{code}\n```\n\nCONTEXT:\n{context}"
                                            f"\nIMPROVEMENT PLAN:\n{plan}\n"}
            ],
            max_tokens=3000
        )

        executor_code = executor_response.choices[0].message.content

        if "```" in executor_code:
            code_blocks = executor_code.split("```")
            for i in range(1, len(code_blocks), 2):
                if i < len(code_blocks):
                    # Remove language identifier if present
                    improved_code = code_blocks[i]
                    if improved_code.strip() and "\n" in improved_code:
                        first_line = improved_code.split("\n")[0].strip()
                        if not first_line.startswith("import") and not first_line.startswith("def"):
                            improved_code = "\n".join(improved_code.split("\n")[1:])
                    return improved_code.strip()

        return executor_code


    async def generate_code(self, code: str, context: str, review: Dict) -> str:
        """executes the code generation workflow via planner-executor"""

        improved_code = ""

        while True:
            feedback = "no feedback given"
            feedback_decision = input("\nwould you like to provide some feedback? (yes/no):").strip().lower()
            if feedback_decision in ["yes", "y", "true", "1"]:
                while True:
                    feedback = input("\nprovide feedback\n:")
                    if feedback.strip():
                        break
                    else:
                        print("\nno context given!\n")

                print("sending feedback....")

            print("\nimproving code....\n")

            improved_code = await self.planner_executor(feedback, code, context, review)

            print(f"\nhere's the improved_code:\n{improved_code}")

            done_decision = input("\ndo you approve the improved code? (yes/no):").strip().lower()

            if done_decision in ["yes", "y", "true", "1"]:
                break

        return improved_code


async def load_documents_for_knowledge_store(knowledge_store):
    """Properly load documents into the knowledge store"""
    documents = []
    print("\nloading documents for knowledge store...")

    while True:
        doc_input = input("\nenter document content or file path (or 'done' to finish): ")
        if doc_input.lower() == 'done':
            break

        doc_content = doc_input
        # Check if input is a file path
        if os.path.exists(doc_input):
            try:
                with open(doc_input, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
                print(f"successfully loaded file: {doc_input}")
            except Exception as e:
                print(f"error reading file {doc_input}: {str(e)}")
                continue

        doc_title = input("enter a title for this document: ")
        doc_id = len(documents) + 1

        # Ask if user wants to split into chunks
        chunk_decision = input("split this document into chunks? (yes/no): ").strip().lower()

        chunks = []
        if chunk_decision in ["yes", "y", "true", "1"]:
            # Simple approach: split by paragraphs
            chunk_paragraphs = [p.strip() for p in doc_content.split("\n\n") if p.strip()]
            for i, paragraph in enumerate(chunk_paragraphs):
                chunks.append({
                    'chunk_id': i + 1,
                    'original_index': i,
                    'content': paragraph
                })
        else:
            # Single chunk for the entire document
            chunks.append({
                'chunk_id': 1,
                'original_index': 0,
                'content': doc_content
            })

        documents.append({
            'doc_id': doc_id,
            'original_uuid': f"doc_{doc_id}_{doc_title.replace(' ', '_')}",
            'content': doc_content,
            'chunks': chunks
        })

        print(f"added document: {doc_title} with {len(chunks)} chunks")

    if documents:
        print(f"\nloading {len(documents)} documents with a total of {sum(len(doc['chunks']) for doc in documents)} chunks...")
        await knowledge_store.load_data(documents)
        print("documents successfully loaded into knowledge store.")
    else:
        print("no documents were added to the knowledge store.")


async def get_code_input():
    """Get code and context from user"""
    print("\nprovide code to review:")
    code_lines = []
    print("enter code (type 'done' on a new line when finished):")
    while True:
        line = input()
        if line.lower() == 'done':
            break
        code_lines.append(line)

    code = "\n".join(code_lines)

    print("\nprovide context for this code:")
    context_lines = []
    print("enter context (type 'done' on a new line when finished):")
    while True:
        line = input()
        if line.lower() == 'done':
            break
        context_lines.append(line)

    context = "\n".join(context_lines)

    return code, context


async def main():
    """entry point of agent"""

    print("agent logging on.... hello!\n")

    # Initialize the code review agent with KnowledgeStore integration
    code_review_agent = CodeReviewAgent()

    # Ask if user wants to load documents
    print("load docs:")
    await load_documents_for_knowledge_store(code_review_agent.knowledge_store)

    code, context = await get_code_input()

    # Perform code review
    review = await code_review_agent.code_review(code, context)

    print("\n" + "="*80)
    print("CODE REVIEW")
    print("="*80)
    table_data = [[aspect, analysis] for aspect, analysis in review.items()]
    print("\n📊 Code Review Report:\n")
    print(tabulate(table_data, headers=["Aspect", "Analysis"], tablefmt="fancy_grid"))
    print("\n" + "="*80)

    fix_decision = input("\nwould you like the code to be fixed? (yes/no): ").strip().lower()

    if fix_decision in ["yes", "y", "true", "1"]:
        code_generation_agent = CodeGenerationAgent()
        generated_code = await code_generation_agent.generate_code(code, context, review)

        print("\n" + "="*80)
        print("IMPROVED CODE")
        print("="*80)
        print(generated_code)
        print("\n" + "="*80)
        print("agent logging off.... goodbye!")

    else:
        print("agent logging off.... goodbye!")


if __name__ == "__main__":
    asyncio.run(main())

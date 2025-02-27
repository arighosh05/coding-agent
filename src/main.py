import os
import json
import asyncio
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI
from modules.tool_registry import ToolRegistry
from modules.knowledge_store import KnowledgeStore

OPENAI_API_KEY = "openai-api-key"


class CodeReviewAgent:
    """agent orchestrating multiple LLM calls to analyze diverse aspects of the code."""

    def __init__(self, model="gpt-4o"):
        """an augmented LLM block : gpt-4o + knowledge_store + tool_registry"""

        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.knowledge_store = KnowledgeStore()
        self.tool_registry = ToolRegistry()

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

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"\nReview this code:\n```\n{code}\n```\nContext for this code:\n{context}\n"}
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
        """a vanilla LLM block"""

        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model

    async def generate_code(self, review: Dict) -> Dict:
        """executes the code generation workflow via evaluator-optimizer"""
        pass


async def main():
    """entry point of agent"""

    print("agent logging on.... hello!")

    while True:
        code = input("provide code :\n")
        if code.strip():
            break
        else:
            print("no code given!")

    while True:
        context = input("provide context :\n")
        if context.strip():
            break
        else:
            print("no context given!")

    code_review_agent = CodeReviewAgent()
    review = await code_review_agent.code_review(code, context)

    if review.get("status") == "completed":
        print("\n" + "="*80)
        print("agent workflow terminated successfully!")
        print("\n" + "="*80)
    else:
        print("\n" + "="*80)
        print(f"agent workflow terminated: {review.get('reason', 'unknown reason')}")
        print("="*80)

    print("\n" + "="*80)
    print("CODE REVIEW")
    print("="*80)
    print(review["comprehensive_review"])
    print("\n" + "="*80)

    fix_decision = input("\nwould you like the code to be fixed? (yes/no): ").strip().lower()

    if fix_decision in ["yes", "y", "true", "1"] :
        code_generation_agent = CodeGenerationAgent()
        generated_code = await code_generation_agent.generate_code(review)

        if generated_code.get("status") == "completed":
            print("\n" + "="*80)
            print("agent workflow terminated successfully!")
            print("\n" + "="*80)
        else:
            print("\n" + "="*80)
            print(f"agent workflow terminated: {generated_code.get('reason', 'unknown reason')}")
            print("="*80)

        print("\n" + "="*80)
        print("IMPROVED CODE")
        print("="*80)
        print(generated_code["improved_code"])
        print("\n" + "="*80)

        print("agent logging off.... goodbye!")

    else:
        print("agent logging off.... goodbye!")


if __name__ == "__main__":
    asyncio.run(main())


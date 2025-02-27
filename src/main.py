import os
import json
import asyncio
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI
# from modules.tool_registry import ToolRegistry
# from modules.knowledge_store import KnowledgeStore
from tabulate import tabulate

OPENAI_API_KEY = "api-key"



class CodeReviewAgent:
    """agent orchestrating multiple LLM calls to analyze diverse aspects of the code."""

    def __init__(self, model="gpt-4o"):
        """an augmented LLM block : gpt-4o + knowledge_store + tool_registry"""

        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        # self.knowledge_store = KnowledgeStore()
        # self.tool_registry = ToolRegistry()

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
                    {"role": "user", "content": f"\nReview this code:\n```\n{code}\n```"
                                                f"\nContext for this code:\n{context}\n"}
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
        implementation_prompt =
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


async def main():
    """entry point of agent"""

    print("agent logging on.... hello!\n")

    # while True:
    #     code = input("provide code :\n")
    #     if code.strip():
    #         break
    #     else:
    #         print("no code given!\n")
    #
    # while True:
    #     context = input("\nprovide context :\n")
    #     if context.strip():
    #         print("\n")
    #         break
    #     else:
    #         print("no context given!\n")

    code = """
    class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Check each pair of numbers to see if they sum to the target.
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        # This return is just for completeness; the problem guarantees exactly one solution.
        return []
    """

    context = """
    Given an array of integers nums and an integer target, return the indices of the two numbers such that they add up to the target. 
    You may assume that each input would have exactly one solution, and you may not use the same element twice.
    """

    code_review_agent = CodeReviewAgent()
    review = await code_review_agent.code_review(code, context)

    print("\n" + "="*80)
    print("CODE REVIEW")
    print("="*80)
    table_data = [[aspect, analysis] for aspect, analysis in review.items()]
    print("\n📊 Code Review Report:\n")
    print(tabulate(table_data, headers=["Aspect", "Analysis"], tablefmt="fancy_grid"))
    print("\n" + "="*80)

    fix_decision = input("\nwould you like the code to be fixed? (yes/no): ").strip().lower()

    if fix_decision in ["yes", "y", "true", "1"] :
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

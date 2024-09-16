from openai import OpenAI
import json
import asyncio
import time
import aiohttp
import os
import logging
from pdf_process.extract_text import extract_text_from_pdf
from llm.generate import query_gpt_async
import requests
from config import OPENAI_API_KEY , SLACK_BOT_TOKEN , SLACK_CHANNEL_ID
from typing import List
import argparse
from slack_api.post_to_slack import post_to_slackapi,post_to_slackapi_pretty
from typing import List, Dict, Any
import ast
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# AI Agent Class with Function Calling
class AIAgentWithFunctionCalling:
    def __init__(self, slack_webhook_url):
        self.slack_webhook_url = slack_webhook_url
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def answer_multiqueries(self, questions: List[str], pdf_path: str):
        """Asynchronously answer multiple questions from a PDF."""
        text = extract_text_from_pdf(pdf_path)
        
        async with aiohttp.ClientSession() as session:
            tasks = [query_gpt_async(session, text, question) for question in questions]

            start_time = time.time()

            # Run tasks concurrently
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            logging.info(f"Async execution time: {end_time - start_time:.2f} seconds")

            # Return structured JSON with question-answer pairs
            qa_results = {question: answer for question, answer in zip(questions, results)}
            return qa_results

    async def post_to_slack_tool(self, results: dict):
        """Asynchronously post results to Slack using a webhook."""
        logging.info("Posting results to Slack")
        post_to_slackapi_pretty(results,SLACK_BOT_TOKEN,SLACK_CHANNEL_ID)
        logging.info(f"Results posted to Slack: {results}")
        # Simulating some network delay
        await asyncio.sleep(1)

    async def run(self):
        """Run the AI agent in a loop, waiting for tasks and invoking OpenAI's function calling."""
        while True:
            #task = self.wait_for_task()
            task = self.wait_for_task_cli()
            if task is None:
                logging.info("No task available. Waiting for the next task...")
                #await asyncio.sleep(5)
                time.sleep(5)
                continue

            logging.info(f"Received a task: {task}")

            messages = [
                {"role": "system", "content": "You are an AI agent that can help answer questions from a PDF and post results to Slack."},
                {"role": "user", "content": "Here is a task:"},
                {"role": "user", "content": json.dumps(task)}
            ]

            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "answer_multiqueries",
                        "description": "Answer multiple questions based on the content of a PDF.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "questions": {"type": "array", "items": {"type": "string"}, "description": "The questions to answer."},
                                "pdf_path": {"type": "string", "description": "The path to the PDF file to extract text from."}
                            },
                            "required": ["questions", "pdf_path"]
                        }
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "post_to_slack_tool",
                        "description": "Post question-answer results to Slack.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "results": {"type": "object", "description": "The question-answer pair results which is returned by answer_multiqueries function call."}
                            },
                            "required": ["results"]
                        }
                    },
                }
            ]


            #print("FIRST MESSAGE=========",messages)
            response =  self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="required"
            )
            
            #print(response.choices[0].message.tool_calls[0].function)
            print(response.choices[0].message.tool_calls)
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "answer_multiqueries":
                # Await the result of answer_multiqueries
                result = await self.answer_multiqueries(**function_args)
                logging.info(f"Answer results: {result}")
                messages.append({"role": "function", "name": "answer_multiqueries", "content": json.dumps(result)})
                messages.append({"role": "system", "content": "Here are the results of the multiqueries. Please call the post_to_slack_tool with the message containing the `results`. It should return results key and The message should list each question and answer pair as follows: 'Question: <question> Answer: <answer>'."})

                print("SECOND MESSAGE:",messages)
            
            else:
                logging.error(f"Unknown function: {function_name}")
                break

            # Call OpenAI again to get the next tool call
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            #print("Gkiri2------------",response.choices[0].message.tool_calls)

            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            #print("SECOND TOOL RESPONSE =",function_args)

            if function_name == "post_to_slack_tool":
                await self.post_to_slack_tool(result)
                # Break the loop as we've posted to Slack
    
            messages=[]
        logging.info("Task completed. Waiting for the next task.")

    def wait_for_task(self):
        """Simulate waiting for a task (PDF and questions)"""
        task_available = True
        if task_available:
            return {
                'pdf_path': 'C:/Users/Sai Swaroop/Downloads/agent/this_studio/docs/handbook.pdf',  # Replace with the actual PDF path
                'questions': [
                    "What is the name of the company?",
                    "Who is the CEO of the company?",
                    "What is the vacation policy?",
                    "What is the termination policy?"
                ]
            }
        else:
            return None
    
    def wait_for_task_cli(self):
        """Prompt the user to input a PDF path and a list of questions, then return the task."""
        while True:
            # Get PDF path
            pdf_path = input("Please enter the path to the PDF file (or 'q' to quit): ").strip()
            if pdf_path.lower() == 'q':
                print("Exiting the program.")
                return None
            if not pdf_path:
                print("Error: PDF path cannot be empty. Please try again.")
                continue
            if not os.path.exists(pdf_path):
                print(f"Error: File not found at '{pdf_path}'. Please try again.")
                continue

            # Get questions as a list
            print("Enter your questions as a Python list (e.g., ['Question 1', 'Question 2']):")
            print("Or enter 'q' to quit:")
            questions_input = input().strip()
            
            if questions_input.lower() == 'q':
                print("Exiting the program.")
                return None

            try:
                questions = ast.literal_eval(questions_input)
                if not isinstance(questions, list) or not all(isinstance(q, str) for q in questions):
                    raise ValueError("Input must be a list of strings.")
                if not questions:
                    raise ValueError("The list of questions is empty.")
            except (SyntaxError, ValueError) as e:
                print(f"Error: Invalid input format. {str(e)}")
                continue

            # Confirm input
            print("\nYou've entered the following:")
            print(f"PDF Path: {pdf_path}")
            print("Questions:")
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q}")
            
            confirm = input("\nIs this correct? (yes/no): ").strip().lower()
            if confirm == 'yes':
                return {
                    'pdf_path': pdf_path,
                    'questions': questions
                }
            else:
                print("Let's try again.\n")
                
if __name__ == "__main__":
    slack_webhook_url = "your_slack_webhook_url_here"  # Replace with your actual Slack webhook URL
    
    # Create the AI agent
    ai_agent = AIAgentWithFunctionCalling(slack_webhook_url)

    # Run the agent in an asynchronous loop
    asyncio.run(ai_agent.run())

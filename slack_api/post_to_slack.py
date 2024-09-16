import requests
import slack_sdk
from slack_sdk.errors import SlackApiError
import json
from slack_sdk import WebClient

def post_to_slackapi(answers, slack_token, slack_channel):
    client = WebClient(token=slack_token)
    response = client.chat_postMessage(channel=slack_channel, text=json.dumps(answers, indent=4))
    return response



def post_to_slackapi_pretty(answers, slack_token, slack_channel):
    client = WebClient(token=slack_token)
    
    # Create the main message block
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Q&A Results",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Handle different possible formats of answers
    if isinstance(answers, list):
        qa_pairs = answers
    elif isinstance(answers, dict):
        qa_pairs = [{"question": k, "answer": v} for k, v in answers.items()]
    else:
        try:
            # Try to parse as JSON
            qa_pairs = json.loads(answers)
            if isinstance(qa_pairs, dict):
                qa_pairs = [{"question": k, "answer": v} for k, v in qa_pairs.items()]
        except json.JSONDecodeError:
            print(f"Error: Unable to parse answers. Expected list or dict, got {type(answers)}")
            return None

    # Add each Q&A pair as a section
    for qa in qa_pairs:
        try:
            question = qa['question'] if isinstance(qa, dict) else qa[0]
            answer = qa['answer'] if isinstance(qa, dict) else qa[1]
            
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Question:*\n{question}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Answer:*\n{answer}"
                    }
                },
                {
                    "type": "divider"
                }
            ])
        except (KeyError, IndexError) as e:
            print(f"Error processing Q&A pair: {e}")
            continue

    try:
        # Post the message
        response = client.chat_postMessage(
            channel=slack_channel,
            blocks=blocks
        )
        print(f"Message posted successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        return None

    return response
    client = WebClient(token=slack_token)
    
    # Create the main message block
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Q&A Results",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add each Q&A pair as a section
    for qa in answers:
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Question:*\n{qa['question']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Answer:*\n{qa['answer']}"
                }
            },
            {
                "type": "divider"
            }
        ])
    
    try:
        # Post the message
        response = client.chat_postMessage(
            channel=slack_channel,
            blocks=blocks
        )
        print(f"Message posted successfully: {response['ts']}")
    except SlackApiError as e:
        print(f"Error posting message: {e}")

    return response
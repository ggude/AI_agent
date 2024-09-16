from models import Prompt

SYSTEM_PROMPT="""
You are Pdf Query application

You are requested to give the user's question's answer from given text reference found from the vector store.

You will be provided with top 4 results matching user's question.

Try you best to give the answer from the provided relevant documents.

If you feel the answer for the question is low confidence or not enough context get the answer. Always return the string "Data Not Available"

Always Replay with textual string.
"""


def get_system_prompt()-> Prompt:
    """
    Get system prompt
    """

    return Prompt(
        type="system",
        content=SYSTEM_PROMPT
    )

def get_user_prompt(question: str, texts: list) -> Prompt:
    """
    Get user prompt prepared with question and texts
    """

    relevant_text = ""
    for text in texts:
        relevant_text += text + "\n\n"

    user_prompt = f"""
    User Question : {question},

    Relevant information found for the question:
    {relevant_text}
    """

    return Prompt(
        type="human",
        content=user_prompt
    )

import logging
from openai import OpenAI
from config import OPENAI_API_KEY

api_key = OPENAI_API_KEY

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO)


def generate_response(relevant_chunks, query):
    client = OpenAI(api_key=OPENAI_API_KEY)
    context = " ".join(relevant_chunks)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"Context: {context}\n\nQuestion: {query}\n\nAnswer:",
        },
    ]

    # Log the relevant information
    logging.info(f"Generating response for query: {query}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
    )

    # Log the generated response
    logging.info(f"Generated response: {response.choices[0].message.content}")

    return response.choices[0].message.content


def answer_questions(questions, pdf_text):
    openai.api_key = OPENAI_API_KEY
    model_engine = "gpt-4o-mini"  # Adjust as needed
    answers = []
    for question in questions:
        prompt = f"Answer the question based on the provided text:\n\nText:\n{pdf_text}\n\nQuestion:\n{question}"
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5
        )
        answer = response.choices[0].text.strip()
        answers.append({"question": question, "answer": answer})
    return answers


# entire pdf text use as context
# Function to query GPT model with extracted text
def query_gpt(text, question):
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
    The following is an employee handbook document. Extract the relevant information based on the question provided:
    Document: 
    {text}
    Question: {question}
    Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2
        )
        logging.info("got the response from the gpt")
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Data Not Available: {e}")
        return None

#aysnc version
async def query_gpt_async(session, text, question):
    prompt = f"""
    The following is a pdf document. Extract the relevant information based on the question provided:
    Document: 
    {text}
    Question: {question}
    Answer:"""
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.2
    }
    
    try:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content']
            else:
                logging.error(f"Failed to get response: {response.status}, {await response.text()}")
                return None
    except Exception as e:
        logging.error(f"Data Not Available: {e}")
        return None
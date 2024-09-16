## Project_overview:

This project creates an AI agent that extracts answers from a PDF document based on given questions and posts the results on Slack.

## Getting started
1.Clone the repository:   
```
   git clone https://github.com/ggude/AI_agent.git
   cd AI_agent
```
2.Install the required packages:
```
   pip install -r requirements.txt
```
3.Run:
```
   python ai_agent.py
```
4. Give Inputs when prompted(example):
```
   pdfpath = C:\Users\Gude\Downloads\agent\this_studio\AI_agent\docs\handbook.pdf
   Questions = ["What is name of the company?","who is CEO of the company?","what is vacation policy?"]
```
## Project Implementation:
## To make the solution accurate: 
* Embedding Creation: Generate vector embeddings for text chunks using Chromadb or Weaviate.
* Semantic Search: Perform semantic search over the vector database to retrieve the most relevant information based on user queries.
* Hybrid search , Agentic search methods also used.
   






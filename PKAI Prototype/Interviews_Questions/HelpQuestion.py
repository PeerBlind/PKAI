import os
from PyPDF2 import PdfReader
import docx  # Pour les fichiers DOCX
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Utilisation de ChatOpenAI pour les modèles de chat
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()

from openai import OpenAI
client = OpenAI()
model = os.getenv('LLM_MODEL', 'gpt-4o')


def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    # Extract text from each page
    for page in reader.pages:
        #print(page.extract_text())
        text += page.extract_text()
    return text



#Suggest Questions
def suggestQuestions(Documentation, Process):
    query = f"""Use the documentation below to answer to suggest relevant Business Process Discovery Questions. Generate a list of five(5) questions relevant to the following process : 
    Process:
    {Process}. "
    Outputs must be the list of questions without any additional comments.
    Documentation:
    \"\"\"
    {Documentation}
    \"\"\"

   """

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'You answer a question to a Business Process Analyst'},
            {'role': 'user', 'content': query},
        ],
        model=model,
        temperature=0,
    )
    return (response.choices[0].message.content)



    #Answer Questions
def answerQuestions(Question, Documentation):
    query = f"""Use the documentation below to answer to the following question: {Question}. If no relevant answer can be found type 'Not Mentionned'."

    Documentation:
    \"\"\"
    {Documentation}
    \"\"\"

    Question: {Question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'You answer a question to a Business Process Analyst'},
            {'role': 'user', 'content': query},
        ],
        model=model,
        temperature=0,
    )

    return (response.choices[0].message.content)
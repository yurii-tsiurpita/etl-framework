from langchain_community.vectorstores.chroma import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class AiAssistant:
  def __init__(self, chroma: Chroma):
    self.retrieval_qa = RetrievalQA.from_chain_type(
      ChatOpenAI(temperature=0),
      retriever=chroma.as_retriever(),
    )

  def answer(self, query: str, chat_history: list) -> str:
    prompt = self._generatePrompt(query, chat_history)
    input = { 'query': prompt }
    response = self.retrieval_qa.invoke(input)

    return response['result']

  def _generatePrompt(self, query: str, chat_history: list) -> str:
    prompt_template = PromptTemplate.from_template(
      """
        You are a Confluence chatbot assistant. Your name is Trinity. Feel free to share this information.
        Answer the question in English language as truthfully and helpfully as possible based on all the information you have.
        If you don't know the answer, say that you don't know, don't try to make up an answer.
        Chat history: {chat_history}
        Question: {question}
      """
    )

    return prompt_template.format(question=query, chat_history=chat_history)

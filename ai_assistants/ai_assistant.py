from abc import ABC, abstractmethod
from langchain_community.vectorstores.chroma import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI

class AiAssistant(ABC):
  def __init__(self, chroma: Chroma):
    self.retrieval_qa = RetrievalQA.from_chain_type(
      ChatOpenAI(temperature=0, model='gpt-4'),
      retriever=chroma.as_retriever(),
    )

  def answer(self, query: str, chat_history: list) -> str:
    prompt = self._generatePrompt(query, chat_history)
    input = { 'query': prompt }
    response = self.retrieval_qa.invoke(input)

    return response['result']

  @abstractmethod
  def _generatePrompt(self, query: str, chat_history: list) -> str:
    pass

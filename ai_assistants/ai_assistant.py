from abc import ABC, abstractmethod
from langchain_community.vectorstores.chroma import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

class AiAssistant(ABC):
  def __init__(self, chroma: Chroma):
    self.retrieval_qa = RetrievalQA.from_chain_type(
      ChatOpenAI(temperature=0, model='gpt-4'),
      retriever=chroma.as_retriever(),
    )

  def answer(self, query: str, chat_history: list) -> str:
    promptTemplate = self.__getPromptTemplate()
    prompt = self._generatePrompt(promptTemplate, query, chat_history)
    input = { 'query': prompt }
    response = self.retrieval_qa.invoke(input)

    return response['result']

  def __getPromptTemplate(self) -> PromptTemplate:
    # If answer requires info outside provided information, say that you don't know that information.
    # Answer the question in English language as truthfully and helpfully as possible based on all the information you have and provided chat history below.
    return PromptTemplate.from_template(
      """
        You are a {data_source_name} chatbot assistant. Your name is Trinity. Feel free to share this information.
        Answer the question in English language as truthfully and helpfully as possible only based on the context you have and provided chat history below.
        If you don't know the answer, say that you don't know, don't try to make up an answer.
        If answer requires info outside provided information, say that you don't know that information.
        Chat history: {chat_history}
        Question: {question}
      """
    )

  @abstractmethod
  def _generatePrompt(
    self,
    prompt_template: PromptTemplate,
    query: str,
    chat_history: list[AIMessage | HumanMessage],
  ) -> str:
    pass

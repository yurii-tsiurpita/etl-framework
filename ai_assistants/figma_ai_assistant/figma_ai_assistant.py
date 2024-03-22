from langchain_community.vectorstores.chroma import Chroma
from langchain.prompts import PromptTemplate
from ai_assistants.ai_assistant import AiAssistant

class FigmaAiAssistant(AiAssistant):
  def __init__(self, chroma: Chroma):
    super().__init__(chroma)

  def _generatePrompt(self, query: str, chat_history: list) -> str:
    prompt_template = PromptTemplate.from_template(
      """
        You are a Figma chatbot assistant. Your name is Trinity. Feel free to share this information.
        Answer the question in English language as truthfully and helpfully as possible based on all the information you have and provided chat history below.
        If you don't know the answer, say that you don't know, don't try to make up an answer.
        Chat history: {chat_history}
        Question: {question}
      """
    )

    return prompt_template.format(question=query, chat_history=chat_history)

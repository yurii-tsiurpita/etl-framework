from langchain_community.vectorstores.chroma import Chroma
from langchain.prompts import PromptTemplate
from ai_assistants.ai_assistant import AiAssistant
from langchain_core.messages import AIMessage, HumanMessage

class FigmaAiAssistant(AiAssistant):
  data_source_name = 'Figma'

  def __init__(self, chroma: Chroma):
    super().__init__(chroma)

  def _generatePrompt(
    self,
    prompt_template: PromptTemplate,
    query: str,
    chat_history: list[AIMessage | HumanMessage],
  ) -> str:
    return prompt_template.format(
      question=query,
      chat_history=chat_history,
      data_source_name=self.data_source_name,
    )

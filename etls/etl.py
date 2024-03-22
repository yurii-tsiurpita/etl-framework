from abc import ABC, abstractmethod
import os
from typing import Iterable
from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings

class Etl(ABC):
  open_ai_embeddings = OpenAIEmbeddings(
    model='text-embedding-3-small',
  )

  def __init__(self, chroma_name: str):
    self.chroma_name = chroma_name

  def _execute(self, *args) -> Chroma:
    extracted_documents = self._extract(args[0])
    transformed_documents = self.__transform(extracted_documents)
    chroma = self.__load(transformed_documents)

    return chroma

  def _getChroma(self) -> Chroma:
    return Chroma(
      persist_directory=f'./data/{ self.chroma_name }',
      embedding_function=self.open_ai_embeddings,
    )

  @abstractmethod
  def _extract(self, *args) -> list[Document]:
    pass

  def __transform(self, documents: Iterable[Document]) -> list[Document]:
    if not documents:
      return []

    recursive_character_text_splitter = RecursiveCharacterTextSplitter(
      separators=['.', '!', '\n']
    )
    character_splitted_documents = recursive_character_text_splitter.split_documents(
      documents
    )
    token_text_splitter = TokenTextSplitter()

    return token_text_splitter.split_documents(character_splitted_documents)

  def __load(self, documents: list[Document]) -> Chroma:
    if os.path.exists(f'./data/{ self.chroma_name }'):
      chroma = self._getChroma()
      documentIds = chroma.get()['ids']
      chroma.delete(ids=documentIds)

    return Chroma.from_documents(
      documents,
      embedding=self.open_ai_embeddings,
      persist_directory=f'./data/{ self.chroma_name }'
    )

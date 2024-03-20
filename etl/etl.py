import os
import shutil
from typing import Iterable
from langchain_community.document_loaders.confluence import ConfluenceLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings
from confluence.typed_dicts.confluence_config import ConfluenceConfig
from etl.constants.etl_constants import CONFLUENCE_CHROMA_NAME

class Etl:
  def __init__(self, confluenceConfig: ConfluenceConfig):
    self.confluenceConfig: ConfluenceConfig = confluenceConfig
    self.open_ai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
      model='text-embedding-3-small',
    )

  def execute(self, spaceKeys: list[str]) -> Chroma | None:
    if not spaceKeys:
      print('ETL process did not start because space keys are missing')
      return

    extracted_documents = self._extract(spaceKeys)
    transformed_documents = self._transform(extracted_documents)
    chroma = self._load(transformed_documents)
    print('ETL process for Confluence data successfully completed')

    return chroma

  def getChroma(self) -> Chroma:
    if not os.path.exists(f'./data/{ CONFLUENCE_CHROMA_NAME }'):
      raise Exception('Confluence data is missing. You must complete the ETL process first.')

    return Chroma(
      persist_directory=f'./data/{ CONFLUENCE_CHROMA_NAME }',
      embedding_function=self.open_ai_embeddings,
    )

  def _extract(self, spaceKeys: list[str]) -> list[Document]:
    documents: list[Document] = []

    if not spaceKeys:
      return documents

    for spaceKey in spaceKeys:
      loader = ConfluenceLoader(
        url=self.confluenceConfig['url'],
        username=self.confluenceConfig['username'],
        api_key=self.confluenceConfig['api_key'],
        space_key=spaceKey,
      )

      documents.extend(loader.load())

    return documents

  def _transform(self, documents: Iterable[Document]) -> list[Document]:
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

  def _load(self, documents: list[Document]) -> Chroma:
    if os.path.exists(f'./data/{ CONFLUENCE_CHROMA_NAME }'):
      shutil.rmtree(f'./data/{ CONFLUENCE_CHROMA_NAME }')

    return Chroma.from_documents(
      documents,
      embedding=self.open_ai_embeddings,
      persist_directory=f'./data/{ CONFLUENCE_CHROMA_NAME }'
    )

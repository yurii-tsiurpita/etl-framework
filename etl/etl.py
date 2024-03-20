import os
import shutil
from typing import Iterable
from langchain_community.document_loaders.confluence import ConfluenceLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings
from etl.constants.etl_constants import CONFLUENCE_CHROMA_NAME
from etl.typed_dicts.etl_config import EtlConfig

class Etl:
  def __init__(self, etlConfig: EtlConfig):
    self.url: str = etlConfig['url']
    self.username: str = etlConfig['username']
    self.api_key: str = etlConfig['api_key']
    self.space_key: str = etlConfig['space_key']
    self.open_ai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
      model='text-embedding-3-small',
    )

  def execute(self) -> None:
    extracted_documents = self._extract()
    transformed_documents = self._transform(extracted_documents)
    self._load(transformed_documents)
    print('ETL process for Confluence data successfully completed')

  def getChroma(self) -> Chroma:
    if not os.path.exists(f'./data/{ CONFLUENCE_CHROMA_NAME }'):
      raise Exception('Confluence data is missing. You must complete the ETL process first.')

    return Chroma(
      persist_directory=f'./data/{ CONFLUENCE_CHROMA_NAME }',
      embedding_function=self.open_ai_embeddings,
    )

  def _extract(self) -> list[Document]:
    loader = ConfluenceLoader(
      url=self.url,
      username=self.username,
      api_key=self.api_key,
      space_key=self.space_key,
    )

    return loader.load()

  def _transform(self, documents: Iterable[Document]) -> list[Document]:
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

import os
import shutil
from typing import Iterable
from langchain_community.document_loaders.confluence import ConfluenceLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain_core.documents.base import Document
from langchain_openai import OpenAIEmbeddings
from confluence.classes.confluence_config import ConfluenceConfig
from langchain_community.document_loaders.sharepoint import SharePointLoader

class SharepointEtl:
  def __init__(self, sharepoint_config: SharepointConfig):
    self.sharepointConfig: SharepointConfig = sharepoint_config
    self.open_ai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
      model='text-embedding-3-small',
    )

  def execute(self, document_library_id: str) -> Chroma | None:
    extracted_documents = self._extract(document_library_id)
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

  def _extract(self, document_library_id: str) -> list[Document]:
    sharepoint_loader = SharePointLoader(document_library_id=document_library_id)

    return sharepoint_loader.load()

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
    chroma = self.getChroma()
    documentIds = chroma.get()['ids']
    chroma.delete(ids=documentIds)

    return Chroma.from_documents(
      documents,
      embedding=self.open_ai_embeddings,
      persist_directory=f'./data/{ CONFLUENCE_CHROMA_NAME }'
    )

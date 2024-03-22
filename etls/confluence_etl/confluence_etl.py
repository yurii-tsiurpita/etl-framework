import os
from langchain_community.document_loaders.confluence import ConfluenceLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents.base import Document
from confluence.classes.confluence_config import ConfluenceConfig
from etls.constants.etl_constants import CONFLUENCE_CHROMA_NAME
from etls.etl import Etl

class ConfluenceEtl(Etl):
  def __init__(self, confluenceConfig: ConfluenceConfig):
    super().__init__(CONFLUENCE_CHROMA_NAME)
    self.confluenceConfig = confluenceConfig

  def execute(self, spaceKeys: list[str]) -> Chroma | None:
    if not spaceKeys:
      print('ETL process did not start because space keys are missing')
      return

    chroma = super()._execute(spaceKeys)

    print('ETL process for Confluence data successfully completed')

    return chroma

  def getChroma(self) -> Chroma:
    if not os.path.exists(f'./data/{ self.chroma_name }'):
      raise Exception('Confluence data is missing. You must complete the ETL process first.')

    return super()._getChroma()

  def _extract(self, spaceKeys: list[str]) -> list[Document]:
    documents: list[Document] = []

    if not spaceKeys:
      return documents

    for spaceKey in spaceKeys:
      loader = ConfluenceLoader(
        url=self.confluenceConfig.url,
        username=self.confluenceConfig.username,
        api_key=self.confluenceConfig.api_key,
        space_key=spaceKey,
      )

      documents.extend(loader.load())

    return documents

import os
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents.base import Document
from langchain_community.document_loaders.figma import FigmaFileLoader
from etls.constants.etl_constants import FIGMA_CHROMA_NAME
from etls.etl import Etl

class FigmaEtl(Etl):
  def __init__(self, figma_access_token: str):
    super().__init__(FIGMA_CHROMA_NAME)
    self.figma_access_token = figma_access_token

  def execute(self, fileKeys: list[str]) -> Chroma | None:
    if not fileKeys:
      print('ETL process did not start because file keys are missing')
      return

    chroma = super()._execute(fileKeys)

    print('ETL process for Figma data successfully completed')

    return chroma

  def getChroma(self) -> Chroma:
    if not os.path.exists(f'./data/{ FIGMA_CHROMA_NAME }'):
      raise Exception('Figma data is missing. You must complete the ETL process first.')

    return super()._getChroma()

  def _extract(self, fileKeys: list[str]) -> list[Document]:
    documents: list[Document] = []

    if not fileKeys:
      return documents

    for fileKey in fileKeys:
      loader = FigmaFileLoader(
        access_token=self.figma_access_token,
        ids='0-0',
        key=fileKey,
      )

      documents.extend(loader.load())

    return documents

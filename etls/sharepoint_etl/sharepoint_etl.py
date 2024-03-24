import os
from langchain_community.document_loaders.sharepoint import SharePointLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents.base import Document
from etls.constants.etl_constants import SHAREPOINT_CHROMA_NAME
from etls.etl import Etl
from langchain_community.document_loaders.confluence import ConfluenceLoader

class SharepointEtl(Etl):
  def __init__(self):
    super().__init__(SHAREPOINT_CHROMA_NAME)

  def execute(self, spaceKeys: list[str]) -> Chroma | None:
    if not spaceKeys:
      print('ETL process did not start because sites are missing')
      return

    chroma = super()._execute(spaceKeys)

    print('ETL process for Sharepoint data successfully completed')

    return chroma

  def getChroma(self) -> Chroma:
    if not os.path.exists(f'./data/{ self.chroma_name }'):
      raise Exception('Sharepoint data is missing. You must complete the ETL process first.')

    return super()._getChroma()

  def _extract(self, spaceKeys: list[str]) -> list[Document]:
    # loader = SharePointLoader(
    #   document_library_id='b!WIeO8zgV10i-BnvN1BfaRrX0rJ-UOIpMoLBDrEExntA3JaNoB4BdT6Pm_W3CZnYw',
    # )

    # return loader.load()

    documents: list[Document] = []

    if not spaceKeys:
      return documents

    for spaceKey in spaceKeys:
      loader = ConfluenceLoader(
        url=os.environ['CONFLUENCE_URL'],
        username=os.environ['CONFLUENCE_USERNAME'],
        api_key=os.environ['CONFLUENCE_API_TOKEN'],
        space_key=spaceKey,
      )

      documents.extend(loader.load())

    return documents

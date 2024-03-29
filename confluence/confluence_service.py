from atlassian import Confluence
from confluence.classes.confluence_config import ConfluenceConfig
from confluence.classes.confluence_space_data import ConfluenceSpaceData

class ConfluenceService:
  def __init__(self, confluenceConfig: ConfluenceConfig):
    print(f'ConfluenceService initialized with { confluenceConfig }')
    self.confluence = Confluence(
      url=confluenceConfig['url'],
      username=confluenceConfig['username'],
      password=confluenceConfig['api_key'],
    )

  def getSpacesData(self) -> list[ConfluenceSpaceData]:
    getAllSpacesResData = self.confluence.get_all_spaces(
      space_status='current',
    )

    spacesData: list[ConfluenceSpaceData] = []

    if type(getAllSpacesResData) is not dict:
      return spacesData

    for spaceData in getAllSpacesResData['results']:
      spacesData.append(
        ConfluenceSpaceData(
          name=spaceData['name'],
          key=spaceData['key'],
        ))

    return spacesData

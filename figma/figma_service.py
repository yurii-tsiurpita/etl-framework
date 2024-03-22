import requests
from figma.classes.figma_config import FigmaConfig
from figma.classes.figma_file_data import FigmaFileData
from figma.typed_dicts.figma_file import FigmaFile

class FigmaService:
  def __init__(self, figmaConfig: FigmaConfig):
    self.config: FigmaConfig = figmaConfig

  def getFilesData(self) -> list[FigmaFileData]:
    projectFiles = self._getProjectFiles()

    figmaFilesData: list[FigmaFileData] = []

    for projectFile in projectFiles:
      figmaFilesData.append(
        FigmaFileData(
          name=projectFile['name'],
          key=projectFile['key'],
        ))

    return figmaFilesData

  def _getProjectFiles(self) -> list[FigmaFile]:
    getProjectFilesResData = requests.get(
      f"https://api.figma.com/v1/projects/{self.config['project_id']}/files",
      headers={ 'X-FIGMA-TOKEN': self.config['access_token'] },
    ).json()
    print(f'getProjectFilesResData: { getProjectFilesResData }')

    return getProjectFilesResData['files']

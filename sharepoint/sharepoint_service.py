from sharepoint.classes.sharepoint_config import SharepointConfig

class SharepointService:
  def __init__(self, sharepointConfig: SharepointConfig):
    self.config = sharepointConfig

  def getSites(self) -> list[str]:
    return ['Earth', 'Hackathon']

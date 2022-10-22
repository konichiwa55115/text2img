from utils.settings import Settings
from text2image.stable_diffusion.api import Api as StableDiffusionApi
from text2image.stable_diffusion.self_host import SelfHost as StableDiffusionSelfHost

class Text2Image:
    METHOD_STABLE_DIFFUSION_API = 'stable_diffusion_api'
    METHOD_STABLE_DIFFUSION_SELF_HOST = 'stable_diffusion_self_host'

    __method = None
    __mediaDirectoryPath = None

    def __init__(self, mediaDirectoryPath: str):
        self.__mediaDirectoryPath = mediaDirectoryPath

        mainConfig = Settings().getMainConfig()

        method = mainConfig['text2image_method']

        if method == self.METHOD_STABLE_DIFFUSION_API:
            self.__method = StableDiffusionApi()
        elif method == self.METHOD_STABLE_DIFFUSION_SELF_HOST:
            self.__method = StableDiffusionSelfHost()
        else:
            raise Exception('Invalid Text To Image Method "%s"' % method)

    def createImageByPrompt(self, prompt: str, fileName: str) -> str:
        filePath = '%s/%s.png' % (self.__mediaDirectoryPath, fileName)

        self.__method.createImageByPrompt(prompt, filePath)

        return filePath

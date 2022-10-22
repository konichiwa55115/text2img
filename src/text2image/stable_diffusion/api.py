import os
import io
import random
import pathlib
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from typing import Union, Generator
from stability_sdk import client
from utils.settings import Settings
from PIL import Image
from text2image.exceptions.bad_prompt import BadPrompt
from utils.telegram.telegram import Telegram

class Api:
    __generation_steps = 0
    __random_seed = 54321
    __debug_mode = False
    __debug_image_file_path = False
    __effects = ['RTX', '4K', 'Cinematic', 'HD', 'Detailed', 'Realistic', 'Photo']
    __auto_improved_prompt = 'Photo of %s, 4k, HD, rtx, detailed, cinematic, photo, realisitc'
    __use_auto_improved_prompt = False
    __use_default_effects = False
    __filter_error_message = 'Your request activated the safety filters and could not be processed. Please modify the prompt and try again'

    def __init__(self):
        stableDiffusionConfig = Settings().getStableDiffusionConfig()
        mainConfig = Settings().getMainConfig()

        self.__generation_steps = stableDiffusionConfig['generation_steps']

        if mainConfig['debug_mode']:
            self.__debug_mode = mainConfig['debug_mode']
            self.__debug_image_file_path = '%s/data/media/debug.png' % pathlib.Path().resolve()
            self.__generation_steps = int(self.__generation_steps / 10)

        os.environ['STABILITY_HOST'] = stableDiffusionConfig['api_host']
        os.environ['STABILITY_KEY'] = stableDiffusionConfig['api_key']

    def createImageByPrompt(self, prompt: str, filePath: str) -> None:
        if not self.__debug_mode:
            self.__random_seed = random.randint(0, 99999)

        if len(prompt) > 1:
            self.__use_auto_improved_prompt = prompt[0] == '!'
            self.__use_default_effects = prompt[0] == '@'

        if (
            len(prompt) > 2 and (
                self.__use_auto_improved_prompt or
                self.__use_default_effects
            )
        ):
            self.__use_auto_improved_prompt = prompt[1] == '!'
            self.__use_default_effects = prompt[1] == '$'

        prompts = prompt.split('/')

        if len(prompts) == 1:
            binaryImage = self.__sendPromptToRemote(prompt, self.__generation_steps)
        else:
            prompt = prompts[0]
            prompts[0] = None
            binaryImage = self.__sendPromptToRemote(prompt, self.__generation_steps)

        self.__sendIntermediateImageToAdmin('INITAL', binaryImage)

        if len(prompts) > 1:
            for effectPrompt in prompts:
                effectPrompt = str(effectPrompt)
                
                if effectPrompt == 'None' or len(effectPrompt) < 1:
                    continue

                effectStrength = 0.3
                generationSteps = 20

                effectPromptParams = effectPrompt.split(':')

                if len(effectPromptParams) > 1:
                    effectStrength = effectPromptParams[1]

                if len(effectPromptParams) > 2:
                    generationSteps = effectPromptParams[2]

                binaryImage = self.__addEffect(
                    effectPrompt,
                    float(effectStrength),
                    int(generationSteps),
                    binaryImage
                )

        if self.__use_default_effects:
            effectStrength=0.55
            generationSteps=25

            for effect in self.__effects:
                binaryImage = self.__addEffect(
                    effect,
                    float(effectStrength),
                    int(generationSteps),
                    binaryImage
                )

        if self.__use_default_effects or len(prompts) > 1:
            binaryImage = self.__sendPromptWithImageToRemote(
                prompt,
                self.__generation_steps,
                0.75,
                binaryImage
            )

        filePointer = open(filePath, "wb")
        filePointer.write(binaryImage)
        filePointer.close()

    def __sendPromptToRemote(self, prompt: str, generationSteps: int) -> Union[bytes, None]:
        stabilityApi = self.__getStabilityApiInference()

        if (self.__use_auto_improved_prompt):
            prompt = self.__auto_improved_prompt % prompt

        if generationSteps < 5:
            generationSteps = 5

        if generationSteps > 150:
            generationSteps = 150

        apiResponse = stabilityApi.generate(
            prompt=prompt,
            seed=self.__random_seed,
            steps=self.__generation_steps
        )

        return self.__getBinaryImageFromApiResponse(apiResponse)

    def __sendPromptWithImageToRemote(
        self,
        prompt: str,
        generationSteps: int,
        initImageStrength: float,
        binaryImage: bytes
    ) -> Union[bytes, None]:
        img = Image.open(io.BytesIO(binaryImage))

        stabilityApi = self.__getStabilityApiInference()

        initImageStrength = initImageStrength

        if generationSteps < 5:
            generationSteps = 5

        if generationSteps > 150:
            generationSteps = 150

        if initImageStrength < 0.01:
            initImageStrength = 0.01

        if initImageStrength > 0.99:
            initImageStrength = 0.99

        apiResponse = stabilityApi.generate(
            prompt=prompt,
            seed=self.__random_seed,
            init_image=img,
            steps=generationSteps,
            start_schedule=initImageStrength
        )

        return self.__getBinaryImageFromApiResponse(apiResponse)

    def __addEffect(
        self,
        effectPrompt: str,
        effectStrength: float,
        generationSteps: int,
        binaryImage: bytes
    ) -> Union[bytes, None]:
        binaryImage = self.__sendPromptWithImageToRemote(effectPrompt, generationSteps, effectStrength, binaryImage)

        self.__sendIntermediateImageToAdmin('Effect: "%s"' % effectPrompt, binaryImage)

        return binaryImage

    def __sendIntermediateImageToAdmin(self, message: str, binaryImage: bytes) -> None:
        if not self.__debug_mode:
            return

        intermediateFilePaths = list()
        intermediateFilePath = self.__debug_image_file_path

        testFilePointer = open(intermediateFilePath, "wb")
        testFilePointer.write(binaryImage)
        testFilePointer.close()

        intermediateFilePaths.append(intermediateFilePath)

        telegramConfig = Settings().getTelegramConfig()

        telegram = Telegram()
        telegram.sendPhotos(message, telegramConfig['admin_chat_id'], intermediateFilePaths)

        os.remove(intermediateFilePath)

    def __getStabilityApiInference(self) -> client.StabilityInference:
        return client.StabilityInference(
            key=os.environ['STABILITY_KEY'],
            verbose=False,
        )

    def __getBinaryImageFromApiResponse(
        self,
        responseGenerator: Generator[generation.Answer, None, None]
    ) -> Union[bytes, None]:
        for response in responseGenerator:
            for artifact in response.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    raise BadPrompt(self.__filter_error_message)
                if artifact.type == generation.ARTIFACT_IMAGE:
                    return artifact.binary

        return None

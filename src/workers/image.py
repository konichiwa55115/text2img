import pathlib
import os
from text2image.exceptions.bad_prompt import BadPrompt
from utils.logger import Logger
from user.user import User
from text2image.text2image import Text2Image
from utils.telegram.telegram import Telegram
from utils.telegram.message import Message as TelegramMessage

class Image:
    __logger = None
    __telegram = None
    __text2image = None

    def __init__(self) -> None:
        self.__logger = Logger()
        self.__telegram = Telegram()
        self.__text2image = Text2Image('%s/data/media' % pathlib.Path().resolve())

    def createFromText(
        self,
        userId: int,
        userName: str,
        chatId: int,
        messageId: int,
        text: str
    ) -> None:
        try:
            user = User.getFromStoreOrCreate(userId, userName)

            self.__logger.log('Check User Credits. User ID: %s' % user.getId())

            if not user.isHaveCredits():
                self.__logger.log('User Has Not Enough Credits. User ID: %s' % user.getId())

                self.__logger.log(
                    'Sending User Message About Credits. User ID: %s. Chat ID: %s' % (
                        user.getId(),
                        chatId
                    )
                )

                self.__telegram.sendMessageWithButtons(
                    'You have not enough credits',
                    {
                        'title': '🎁 Request more credit',
                        'callback_values': 'n=%s,uid=%s,cid=%s' % (
                            TelegramMessage.CALLABCK_CREDITS_REQUEST,
                            user.getId(),
                            chatId
                        )
                    },
                    chatId
                )

                return

            if user.getStatus() == User.STATUS_BAN:
                self.__logger.log('User Is Banned. User ID: %s' % user.getId())

                self.__logger.log(
                    'Sending User Message About Ban. User ID: %s. Chat ID: %s' % (
                        user.getId(),
                        chatId
                    )
                )

                self.__telegram.sendMessage('⛔ You got a ban. Sorry', chatId)

                return

            user.setCredits(user.getCredits() - 1)

            User.updateInStore(user)

            self.__logger.log(
                'Sending User Message About Starting Creating Image. User ID: %s. Chat ID: %s' % (
                    user.getId(),
                    chatId
                )
            )

            self.__telegram.sendMessage(
                '🚀 Started to draw a picture for you. You have *%d* unused credits' % user.getCredits(),
                chatId,
                True
            )

            self.__logger.log('Start Creatimg Image(s) By Text "%s"' % text)

            imageFilePaths = list()
            imageFilePaths.append(self.__text2image.createImageByPrompt(text, '%s_%d_%d' % (userId, chatId, messageId)))

            self.__logger.log('End Creatimg Image(s) By Text "%s"' % text)

            self.__logger.log(
                'Sending Image(s) To User. User ID: %s. Chat ID: %s' % (
                    user.getId(),
                    chatId
                )
            )

            self.__telegram.sendPhotos('🖼 %s' % text, chatId, imageFilePaths)

            for imageFilePath in imageFilePaths:
                self.__logger.log('Removing Local Image. Image File Path: %s' % imageFilePath)
                os.remove(imageFilePath)
        except BadPrompt as exp:
            self.__telegram.sendMessage(
                '🚨 %s' % exp.message,
                chatId,
                True
            )

            self.__logger.log(
                'Bad User Prompt. Prompt: "%s". Error: "%s". User ID: %s. Chat ID: %s' % (
                    text,
                    exp.message,
                    userId,
                    chatId
                )
            )

            return
        except Exception as exp:
            self.__telegram.sendMessage(
                '🚨 Internal server error. Please try again',
                chatId,
                True
            )

            raise exp

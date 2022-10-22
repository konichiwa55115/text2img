import json
from utils.telegram.telegram import Telegram
from utils.telegram.message import Message as TelegramMessage
from utils.logger import Logger
from utils.queue.queue import Queue
from utils.queue.job import Job
from text.text import Text

class Input():
    __logger = None
    __telegram = None
    __queue = None
    __text = None

    def __init__(self):
        self.__logger = Logger()
        self.__telegram = Telegram()
        self.__queue = Queue()
        self.__text = Text()

    def handleInputs(self) -> None:
        telegramMessages = self.__telegram.getMessages()

        if not len(telegramMessages) > 0 :
            return

        for telegramMessage in telegramMessages:
            if (
                telegramMessage.getUser().isBot() or
                telegramMessage.isSystemMessageType() or
                not telegramMessage.getChat().isSupported() or
                not telegramMessage.getChat().isPrivateType() # only PM are supported
            ):
                continue

            if telegramMessage.isMessageType():
                self.__doHamdleMessage(telegramMessage)
                continue

            if telegramMessage.isCommandType():
                self.__doHamdleCommand(telegramMessage)
                continue

            if telegramMessage.isCallbackType():
                self.__doHamdleCallback(telegramMessage)
                continue

    def __doHamdleCommand(self, telegramMessage: TelegramMessage) -> None:
        self.__logger.log(
            'Telegram command "%s" (message_id: %d, user_id: %d, chat_id: %d)' % (
                telegramMessage.getText(),
                telegramMessage.getId(),
                telegramMessage.getUser().getId(),
                telegramMessage.getChat().getId()
            )
        )

        if telegramMessage.getText() == TelegramMessage.COMMAND_CREATE_RANDOM_IMAGE:
            self.__doRandomImage(telegramMessage)
            return

    def __doHamdleMessage(self, telegramMessage: TelegramMessage) -> None:
        self.__logger.log(
            'Telegram message "%s" (message_id: %s, user_id: %d, user_name: %s, chat_id: %d)' % (
                telegramMessage.getText(),
                telegramMessage.getId(),
                telegramMessage.getUser().getId(),
                telegramMessage.getUser().getName(),
                telegramMessage.getChat().getId()
            )
        )

        self.__doImageFromPrompt(
            telegramMessage.getId(),
            telegramMessage.getUser().getId(),
            telegramMessage.getUser().getName(),
            telegramMessage.getChat().getId(),
            telegramMessage.getText()
        )

    def __doHamdleCallback(self, telegramMessage: TelegramMessage) -> None:
        self.__logger.log(
            'Telegram callback "%s" (callback_id: %d, callback_data: %s, parent_message_id: %d, user_id: %d, chat_id: %d)' % (
                telegramMessage.getText(),
                telegramMessage.getId(),
                json.dumps(telegramMessage.getCallbackValues()),
                telegramMessage.getParentMessage().getId(),
                telegramMessage.getUser().getId(),
                telegramMessage.getChat().getId()
            )
        )

        if telegramMessage.getText() == TelegramMessage.CALLABCK_CREDITS_REQUEST:
            self.__doCreditsRequest(telegramMessage)
            return

        if telegramMessage.getText() == TelegramMessage.CALLABCK_CREDITS_APPROVE:
            self.__doCreditsApprove(telegramMessage)
            return

        if telegramMessage.getText() == TelegramMessage.CALLABCK_CREDITS_REJECT:
            self.__doCreditsReject(telegramMessage)
            return

    def __doCreditsRequest(self, telegramMessage: TelegramMessage) -> None:
        userId = telegramMessage.getUser().getId()
        chatId = telegramMessage.getChat().getId()

        additionalValues = {
            'parent_message_id': telegramMessage.getParentMessage().getId(),
            'callback_values': telegramMessage.getCallbackValues()
        }

        queueJobId = 'credits_request_%s_%s_%s' % (userId, chatId, telegramMessage.getId())

        self.__queue.addJob(queueJobId, Job.TYPE_CREDIT_REQUEST, additionalValues)

    
    def __doCreditsApprove(self, telegramMessage: TelegramMessage) -> None:
        userId = telegramMessage.getUser().getId()
        chatId = telegramMessage.getChat().getId()

        additionalValues = {
            'parent_message_id': telegramMessage.getParentMessage().getId(),
            'callback_values': telegramMessage.getCallbackValues()
        }

        queueJobId = 'credits_approve_%s_%s_%s' % (userId, chatId, telegramMessage.getId())

        self.__queue.addJob(queueJobId, Job.TYPE_CREDIT_APPROVE, additionalValues)

    def __doCreditsReject(self, telegramMessage: TelegramMessage) -> None:
        userId = telegramMessage.getUser().getId()
        chatId = telegramMessage.getChat().getId()

        additionalValues = {
            'parent_message_id': telegramMessage.getParentMessage().getId(),
            'callback_values': telegramMessage.getCallbackValues()
        }

        queueJobId = 'credits_reject_%s_%s_%s' % (userId, chatId, telegramMessage.getId())

        self.__queue.addJob(queueJobId, Job.TYPE_CREDIT_REJECT, additionalValues)

    def __doRandomImage(self, telegramMessage: TelegramMessage) -> None:
        randomText = self.__text.getRandomText()

        self.__doImageFromPrompt(
            telegramMessage.getId(),
            telegramMessage.getUser().getId(),
            telegramMessage.getUser().getName(),
            telegramMessage.getChat().getId(),
            randomText
        )

    def __doImageFromPrompt(
        self,
        messageId: int,
        userId:    int,
        userName:  str,
        chatId:    int,
        text:      str
    ) -> None:
        additionalValues = {
            'user_id': userId,
            'user_name': userName,
            'chat_id': chatId,
            'message_id': messageId,
            'text': text
        }

        queueJobId = 'image_by_prompt_%s_%s_%s' % (userId, chatId, messageId)

        self.__queue.addJob(queueJobId, Job.TYPE_CREATE_IMAGE_BY_PROMPT, additionalValues)

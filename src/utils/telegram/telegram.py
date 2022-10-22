import requests
import json

from urllib3 import encode_multipart_formdata
from utils.telegram.message import Message
from typing import Union
from utils.settings import Settings

class Telegram:
    __HTTP_STATUS_OK = 200

    __GET_MESSAGES_LIMIT = 100

    __GET_MESSAGES_URL = 'https://api.telegram.org/bot%s/getUpdates?offset=%d&limit=%d&allowed_updates=["message", "callback_query"]'
    __SEND_MESSAGE_URL = 'https://api.telegram.org/bot%s/sendMessage?%schat_id=%s&text=%s'
    __SEND_MESSAGE_WITH_BUTTON_URL = 'https://api.telegram.org/bot%s/sendMessage?parse_mode=markdown&chat_id=%s&text=%s&reply_markup={"inline_keyboard":%s}'
    __SEND_PHOTO_URL = 'https://api.telegram.org/bot%s/sendPhoto?parse_mode=markdown'
    __SEND_PHOTOS_URL = 'https://api.telegram.org/bot%s/sendMediaGroup?parse_mode=markdown'
    __UPDATE_MESSAGE_URL = 'https://api.telegram.org/bot%s/editMessageText?parse_mode=markdown&chat_id=%s&message_id=%s&text=%s'
    __DELETE_MESSAGE_URL = 'https://api.telegram.org/bot%s/deleteMessage?chat_id=%s&message_id=%s'

    __logChatId = None
    __token     = None

    def __init__(self):
        config = Settings().getTelegramConfig()

        self.__token     = config['bot_token']
        self.__logChatId = config['log_chat_id']

    def sendMessage(self, message: str, chatId: int, isMarkdown: bool = False) -> bool:
        return self.__send(chatId, message, isMarkdown)

    def sendPhotos(self, caption: str, chatId: int, filePathes: list) -> bool:
        if len(filePathes) > 1:
            return self.__sendPhotos(chatId, caption, filePathes)

        return self.__sendPhoto(chatId, caption, filePathes[0])

    def deleteMessage(self, chatId: int, messageId: int) -> bool:
        return self.__delete(chatId, messageId)

    def updateMessage(self, message: str, chatId: int, messageId: int) -> bool:
        return self.__update(chatId, messageId, message)

    def sendMessageWithButtons(self, message: str, buttons: Union[dict, tuple], chatId: int) -> bool:
        buttonsJson = list()

        if (type(buttons) == dict):
            button = buttons
            buttons = list()
            buttons.append(button)

        for button in buttons:
            buttonJson = self.__buttonJson(button)

            buttonsJson.append(buttonJson)

        return self.__sendWithButtons(chatId, message, json.dumps(buttonsJson))

    def sendMessageToLogChat(self, message: str) -> bool:
        return self.__send(self.__logChatId, message)

    def getMessages(self) -> list:
        responseRows = self.__get()

        if responseRows == None :
            return list()

        messages = list(map(lambda responseRow : Message(responseRow), responseRows))

        return messages

    def __get(self) -> Union[list, None]:
        url = self.__GET_MESSAGES_URL % (self.__token, Message.getLastUpdateId() + 1, self.__GET_MESSAGES_LIMIT)

        response = requests.get(url)

        if response.status_code != self.__HTTP_STATUS_OK :
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return response

        return None

    def __send(self, idChat: str, message: str, isMarkdown: bool = False) -> Union[Message, None]:
        markdownUrlParam = ''

        if isMarkdown:
            markdownUrlParam = 'parse_mode=markdown&'

        url = self.__SEND_MESSAGE_URL % (self.__token, markdownUrlParam, idChat, message)

        response = requests.get(url)

        if response.status_code != self.__HTTP_STATUS_OK :
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return Message(response)

        return None

    def __sendPhotos(self, idChat: str, caption: str, filePaths: list) -> Union[Message, None]:
        data = {"chat_id": idChat, "caption": caption}
        url = self.__SEND_PHOTOS_URL % self.__token
        for filePath in filePaths:
            with open(filePath, "rb") as image_file:
                response = requests.post(url, data=data, files={"photo": image_file})

        if response.status_code != self.__HTTP_STATUS_OK:
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return Message(response)

        return None

    def __sendPhoto(self, idChat: str, caption: str, filePath: str) -> Union[Message, None]:
        data = {"chat_id": idChat, "caption": caption}
        url = self.__SEND_PHOTO_URL % self.__token

        with open(filePath, "rb") as image_file:
            response = requests.post(url, data=data, files={"photo": image_file})

        if response.status_code != self.__HTTP_STATUS_OK:
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return Message(response)

        return None

    def __update(self, idChat: str, idMessage: str, message: str) -> Union[Message, None]:
        url = self.__UPDATE_MESSAGE_URL % (self.__token, idChat, idMessage, message)

        response = requests.get(url)

        if response.status_code != self.__HTTP_STATUS_OK :
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return Message(response)

        return None

    def __delete(self, idChat: str, idMessage: str) -> Union[Message, None]:
        url = self.__DELETE_MESSAGE_URL % (self.__token, idChat, idMessage)

        response = requests.get(url)

        if response.status_code != self.__HTTP_STATUS_OK :
            return None

        response = json.loads(response.content)

        if not (
            'ok' in response and
            'result' in response and
            response['result'] == True
        ) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        return None

    def __sendWithButtons(
        self,
        idChat: str,
        message: str,
        buttonsJson: str
    ) -> Union[Message, None]:
        url = self.__SEND_MESSAGE_WITH_BUTTON_URL % (self.__token, idChat, message, buttonsJson)

        response = requests.get(url)

        if response.status_code != self.__HTTP_STATUS_OK :
            return None

        response = json.loads(response.content)

        if not self.__isResponseHaveValidFormat(response) :
            raise Exception('Telegram Respose Has Invalid Forrmat. Respose: %s' % json.dumps(response))

        response = response['result']

        if len(response) > 0 :
            return Message(response)

        return None

    def __isResponseHaveValidFormat(self, response: dict) -> bool:
        return (
            'ok' in response and
            'result' in response and
            (
                type(response['result']) == list or
                type(response['result']) == dict
            )
        )

    def __buttonJson(self, button: dict) -> list:
        buttonJson = list()

        buttonJson.append({
            'text': button['title'],
            'callback_data': button['callback_values']
        })

        return buttonJson

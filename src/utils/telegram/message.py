import json
import re
import time

from os import getcwd, path
from typing import Union

from utils.telegram.user import User
from utils.telegram.chat import Chat

class Message:
    COMMAND_CREATE_RANDOM_IMAGE = '/random'

    CALLABCK_CREDITS_REQUEST = 'credits_request'
    CALLABCK_CREDITS_APPROVE = 'credits_approve'
    CALLABCK_CREDITS_REJECT = 'credits_reject'

    __TYPE_MESSAGE = 'message'
    __TYPE_SYSTEM_MESSAGE = 'system_message'
    __TYPE_COMMAND = 'command'
    __TYPE_CALLBACK = 'callback'

    __LAST_UPDATE_ID_FILE_PATH = '%s/data/telegram_last_update_id.txt'

    __id = None
    __update_id = None
    __type = None
    __text = None
    __date = None
    __user = None
    __chat = None
    __parent_message = None
    __callback_values = None

    def __init__(self, values: dict):
        if 'callback_query' in values:
            self.__mapCallbackValues(values)
        else:
            self.__mapMessageValues(values)

        if (self.getUpdateId() != None):
            self.__saveLastUpdateId(self.getUpdateId())

    def __mapCallbackValues(self, values: dict):
        if not self.__isValuesHaveValidCallbackFormat(values):
            raise Exception('Telegram Callback Values Have Invalid Format. Values: %s' % json.dumps(values))

        self.__setType(self.__TYPE_CALLBACK)

        self.__setId(int(values['callback_query']['id']))
        self.__setDate(int(time.time()))
        self.__setUser(values['callback_query']['from'])
        self.__setChat(values['callback_query']['message']['chat'])
        self.__setUpdateId(int(values['update_id']))
        self.__setParetnMessage(values['callback_query']['message'])
        self.__setText(str(values['callback_query']['data']))

        if len(values['callback_query']['data'].split(',')) > 1:
            self.__parseCallbackValues(values)

    def __parseCallbackValues(self, values: dict):
        callbackValues = {}

        for callbackValue in values['callback_query']['data'].split(','):
            callbackValue = callbackValue.split('=')

            if len(callbackValue) != 2:
                raise Exception('Telegram Callback Values Have Invalid Format. Values: %s' % json.dumps(values))

            if callbackValue[0] == 'n':
                self.__setText(str(callbackValue[1]))
                continue

            if callbackValue[0] == 'cid':
                callbackValues['chat_id'] = callbackValue[1]
                continue

            if callbackValue[0] == 'uid':
                callbackValues['user_id'] = callbackValue[1]
                continue

            callbackValues[callbackValue[0]] = callbackValue[1]

        if len(callbackValues):
            self.__setCallbackValues(callbackValues)

    def __mapMessageValues(self, values: dict):
        # if message index is missing but result exists (in case when it is respose after sending message)
        if 'message' not in values and 'message_id' in values:
            values = dict({'message': values})

        if not self.__isValuesHaveValidMessageFormat(values):
            raise Exception('Telegram Message Values Have Invalid Format. Values: %s' % json.dumps(values))

        self.__setType(self.__TYPE_MESSAGE)

        self.__setId(int(values['message']['message_id']))
        self.__setDate(int(values['message']['date']))
        self.__setUser(values['message']['from'])
        self.__setChat(values['message']['chat'])

        if 'text' in values['message']:
            self.__setText(str(values['message']['text']))

        if 'update_id' in values:
            self.__setUpdateId(int(values['update_id']))

        if not 'text' in values['message']:
            self.__setType(self.__TYPE_SYSTEM_MESSAGE)

        if 'text' in values['message'] and self.__isBotComand(values['message']['text']):
            self.__setType(self.__TYPE_COMMAND)

    def getId(self) -> int:
        return self.__id

    def getUpdateId(self) -> Union[int, None]:
        return self.__update_id

    def getText(self) -> Union[str, None]:
        return self.__text

    def getDate(self) -> int:
        return self.__date

    def getType(self) -> str:
        return self.__type

    def isMessageType(self) -> str:
        return self.__type == self.__TYPE_MESSAGE

    def isSystemMessageType(self) -> str:
        return self.__type == self.__TYPE_SYSTEM_MESSAGE

    def isCommandType(self) -> str:
        return self.__type == self.__TYPE_COMMAND

    def isCallbackType(self) -> str:
        return self.__type == self.__TYPE_CALLBACK

    def getUser(self) -> User:
        return self.__user

    def getChat(self) -> Chat:
        return self.__chat

    def getParentMessage(self) -> Union['Message', None]:
        return self.__parent_message

    def getCallbackValues(self) -> Union[dict, None]:
        return self.__callback_values

    @staticmethod
    def getLastUpdateId() -> int:
        lastUpdateIdFilePath = Message.__getLastUpdateIdFilePath()

        if not path.exists(lastUpdateIdFilePath) or not path.isfile(lastUpdateIdFilePath):
            return 0

        lastUpdateIdFile = open(lastUpdateIdFilePath, 'r')

        lastUpdateId = lastUpdateIdFile.read()

        lastUpdateIdFile.close()

        if lastUpdateId == '':
            return 0

        return int(lastUpdateId)

    def __saveLastUpdateId(self, lastUpdateId: int) -> None:
        lastUpdateIdFilePath = self.__getLastUpdateIdFilePath()

        lastUpdateIdFromFile = self.getLastUpdateId()

        if lastUpdateIdFromFile > lastUpdateId:
            return

        lastUpdateIdFile = open(lastUpdateIdFilePath, 'w')
        lastUpdateIdFile.write(str(lastUpdateId))
        lastUpdateIdFile.close()

    def __setId(self, id: int) -> None:
        self.__id = id

    def __setUpdateId(self, updateId: int) -> None:
        self.__update_id = updateId

    def __setText(self, text: str) -> None:
        self.__text = text

    def __setDate(self, date: int) -> None:
        self.__date = date

    def __setType(self, type: str) -> None:
        self.__type = type

    def __setUser(self, values: dict) -> None:
        self.__user = User(values)

    def __setChat(self, values: dict) -> None:
        self.__chat = Chat(values)

    def __setParetnMessage(self, values: dict) -> None:
        self.__parent_message = Message(values)

    def __setCallbackValues(self, values: dict) -> None:
        self.__callback_values = values

    def __isBotComand(self, text: str) -> bool:
        pattern = re.compile('^\/([a-z]+)((\s$)|$)')

        return pattern.match(text)

    def __isValuesHaveValidMessageFormat(self, values: dict) -> bool:
        return (
            'message' in values and
            type(values['message']) == dict and
            'message_id' in values['message'] and
            'date' in values['message'] and
            'from' in values['message'] and
            'chat' in values['message'] and
            type(values['message']['from']) == dict and
            type(values['message']['chat']) == dict
        )

    def __isValuesHaveValidCallbackFormat(self, values: dict) -> bool:
        return (
            'callback_query' in values and
            type(values['callback_query']) == dict and
            'update_id' in values and
            'data' in values['callback_query'] and
            'from' in values['callback_query'] and
            'message' in values['callback_query'] and
            type(values['callback_query']['message']) == dict and
            'chat' in values['callback_query']['message'] and
            type(values['callback_query']['message']['chat']) == dict
        )

    @staticmethod
    def __getLastUpdateIdFilePath() -> str:
        return Message.__LAST_UPDATE_ID_FILE_PATH % getcwd()

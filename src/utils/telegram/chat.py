import json

class Chat:
    __TYPE_PRIVATE = 'private'
    __TYPE_GROUP = 'group'
    __TYPE_UNSUPPORTED = 'unsupported'

    __REMOTE_TYPE_PRIVATE= 'private'
    __REMOTE_TYPE_GROUP = 'supergroup'

    __id = None
    __title = None
    __type = __TYPE_UNSUPPORTED

    def __init__(self, values: dict):
        if not self.__isValuesHaveValidFormat(values):
            raise Exception('Telegram Chat Values Have Invalid Format. Values: %s' % json.dumps(values))

        self.__setId(int(values['id']))
        self.__setTitle(values)
        self.__setType(str(values['type']))

    def getId(self) -> int:
        return self.__id

    def getTitle(self) -> str:
        return self.__title

    def getType(self) -> str:
        return self.__type

    def isPrivateType(self) -> str:
        return self.__type == self.__TYPE_PRIVATE

    def isGroupType(self) -> str:
        return self.__type == self.__TYPE_GROUP

    def isSupported(self) -> bool:
        return self.__type != self.__TYPE_UNSUPPORTED

    def __setId(self, id: int) -> None:
        self.__id = id

    def __setTitle(self, values: dict) -> None:
        self.__title = 'chat_%d' % int(values['id'])

        if 'title' in values:
            self.__title = str(values['title'])

    def __setType(self, type: str) -> None:
        if type == self.__REMOTE_TYPE_PRIVATE:
            self.__type = self.__TYPE_PRIVATE

        if type == self.__REMOTE_TYPE_GROUP:
            self.__type = self.__TYPE_GROUP

    def __isValuesHaveValidFormat(self, values: dict) -> bool:
        return 'id' in values and 'type' in values

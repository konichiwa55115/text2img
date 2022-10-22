import json

from store import Store

class User:
    STATUS_ACTIVE = 0
    STATUS_BAN = 1

    TYPE_FREE = 0
    TYPE_PREMIUM = 1
    TYPE_SUPER_PREMIUM = 2

    CREDITS_BATCH_SIZE_FREE = 10
    CREDITS_BATCH_SIZE_PREMIUM = 100

    __id = None
    __name = None
    __type = None
    __status = None
    __credits = None
    __created_at = None
    __updated_at = None

    def __init__(self, values: dict):
        if not self.__isValuesHaveValidFormat(values):
            raise Exception('User Values Have Invalid Format. Values: %s' % json.dumps(values))

        self.__setId(str(values['id']))
        self.__setName(str(values['name']))
        self.__setType(int(values['type']))
        self.__setCreatedAt(int(values['created_at']))
        self.setCredits(int(values['credits']))
        self.setStatus(int(values['status']))

        if 'updated_at' in values:
            self.__setUpdatedAt(str(values['updated_at']))

    def getId(self) -> int:
        return self.__id

    def getName(self) -> str:
        return self.__name

    def getType(self) -> int:
        return self.__type

    def getStatus(self) -> str:
        return self.__status

    def getCredits(self) -> int:
        return self.__credits

    def getCreatedAt(self) -> int:
        return int(self.__created_at)

    def getUpdatedAt(self) -> int:
        return int(self.__updated_at)

    def setStatus(self, status: int) -> None:
        if not self.__isValidStatus(status):
            raise Exception('Invalid User Status "%s"' % status)

        self.__status = status

    def setCredits(self, credits: int) -> None:
        self.__credits = credits

    @staticmethod
    def getTypeTitle(type: int) -> str:
        if type == User.TYPE_FREE:
            return 'Free'

        if type == User.TYPE_PREMIUM:
            return 'Premium'

        if type == User.TYPE_SUPER_PREMIUM:
            return 'Super Premium'

        return 'Unknown'

    @staticmethod
    def getStatusTitle(status: int) -> str:
        if status == User.STATUS_ACTIVE:
            return 'Active'

        if status == User.STATUS_BAN:
            return 'Ban'

        return 'Unknown'

    @staticmethod
    def getFromStore(userId: int) -> 'User':
        store = Store()

        row = store.getUserById(userId)

        if row == None:
            raise Exception('User Not Found. User ID: %s' % userId)

        return User(row)

    @staticmethod
    def getFromStoreOrCreate(userId: int, userName: str) -> 'User':
        store = Store()

        row = store.getUserById(userId)

        if row == None:
            store.insertUser(
                userId,
                userName,
                User.TYPE_FREE,
                User.STATUS_ACTIVE,
                User.CREDITS_BATCH_SIZE_FREE
            )

            row = store.getUserById(userId)

        if row == None:
            raise Exception(
                'Can Not Create User. User ID: %d. User Name: "%s"' % (
                    userId,
                    userName
                )
            )

        return User(row)

    @staticmethod
    def updateInStore(user: 'User') -> None:
        store = Store()

        store.updateUser(
            user.getId(),
            user.getStatus(),
            user.getCredits()
        )

    def isHaveCredits(self) -> bool:
        if self.getType() == self.TYPE_SUPER_PREMIUM:
            return True

        if self.getCredits() < 1:
            return False

        return True

    def __setId(self, id: int) -> None:
        self.__id = id

    def __setName(self, name: str) -> None:
        self.__name = name

    def __setType(self, type: int) -> None:
        if not self.__isValidType(type):
            raise Exception('Invalid User Type "%s"' % type)

        self.__type = type

    def __setCreatedAt(self, createdAt: int) -> None:
        self.__created_at = createdAt

    def __setUpdatedAt(self, updatedAt: int) -> None:
        self.__updated_at = updatedAt

    def __isValuesHaveValidFormat(self, values: dict) -> bool:
        return (
            'id' in values and
            'name' in values and
            'type' in values and
            'status' in values and
            'credits' in values
            and 'created_at' in values
        )

    def __isValidStatus(self, status: int) -> bool:
        if status == self.STATUS_ACTIVE:
            return True

        if status == self.STATUS_BAN:
            return True

        return False

    def __isValidType(self, type: int) -> bool:
        if type == self.TYPE_FREE:
            return True

        if type == self.TYPE_PREMIUM:
            return True

        if type == self.TYPE_SUPER_PREMIUM:
            return True

        return False

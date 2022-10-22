import json

from typing import Union

class Job:
    STATUS_PENDING = 0
    STATUS_IN_PROGRESS = 1
    STATUS_DONE = 2
    STATUS_ERROR = 3

    TYPE_CREATE_IMAGE_BY_PROMPT = 0
    TYPE_CREDIT_REQUEST = 1
    TYPE_CREDIT_APPROVE = 2
    TYPE_CREDIT_REJECT = 3

    TIMEOUT = 60 * 60 * 24 * 2

    __id = None
    __type = None
    __additional_values = None
    __status = None
    __errorMessage = None
    __created_at = None
    __updated_at = None

    def __init__(self, values: dict):
        if not self.__isValuesHaveValidFormat(values):
            raise Exception('Queue Job Values Have Invalid Format. Values: %s' % json.dumps(values))

        self.__setId(str(values['id']))
        self.__setType(int(values['type']))
        self.__setCreatedAt(int(values['created_at']))
        self.setStatus(int(values['status']))

        if 'additional_values' in values:
            self.__setAdditionalValues(values['additional_values'])

        if 'additional_values_json' in values:
            self.__setAdditionalValuesJson(values['additional_values_json'])

        if 'error_message' in values:
            self.setErrorMessage(str(values['error_message']))

        if 'updated_at' in values:
            self.__setUpdatedAt(str(values['updated_at']))

    def getId(self) -> str:
        return self.__id

    def getType(self) -> int:
        return self.__type

    def getAdditionalValues(self) -> Union[dict, None]:
        return self.__additional_values

    def getAdditionalValuesJson(self) -> str:
        additionalValuesJson = self.__additional_values
        
        if additionalValuesJson != None:
            additionalValuesJson = json.load(additionalValuesJson)

        return str(additionalValuesJson)

    def getStatus(self) -> str:
        return self.__status

    def getErrorMessage(self) -> Union[str, None]:
        return self.__errorMessage

    def getCreatedAt(self) -> int:
        return int(self.__created_at)

    def getUpdatedAt(self) -> int:
        return int(self.__updated_at)

    def setStatus(self, status: int) -> None:
        if not self.__isValidStatus(status):
            raise Exception('Invalid Queue Job Status "%s"' % status)

        self.__status = status

    def setErrorMessage(self, errorMessage: str) -> None:
        self.__errorMessage = errorMessage

    @staticmethod
    def getTypeTitle(type: int) -> str:
        if type == Job.TYPE_CREATE_IMAGE_BY_PROMPT:
            return 'Create Image By Prompt'

        if type == Job.TYPE_CREDIT_REQUEST:
            return 'Credits Request'

        if type == Job.TYPE_CREDIT_APPROVE:
            return 'Credits Approve'

        if type == Job.TYPE_CREDIT_REJECT:
            return 'Credits Reject'

        return 'Unknown'

    @staticmethod
    def getStatusTitle(status: int) -> str:
        if status == Job.STATUS_PENDING:
            return 'Pending'

        if status == Job.STATUS_IN_PROGRESS:
            return 'In progress'

        if status == Job.STATUS_DONE:
            return 'Done'

        if status == Job.STATUS_ERROR:
            return 'Error'

        return 'Unknown'

    def __setId(self, id: str) -> None:
        self.__id = id

    def __setType(self, type: int) -> None:
        if not self.__isValidType(type):
            raise Exception('Invalid Queue Job Type "%s"' % type)

        self.__type = type

    def __setAdditionalValues(self, additionalValues: Union[dict, None]) -> None:
        self.__additional_values = additionalValues

    def __setCreatedAt(self, createdAt: int) -> None:
        self.__created_at = createdAt

    def __setUpdatedAt(self, updatedAt: int) -> None:
        self.__updated_at = updatedAt

    def __setAdditionalValuesJson(self, additionalValuesJson: Union[str, None]) -> None:
        if additionalValuesJson != None and additionalValuesJson != '':
            self.__additional_values = json.loads(additionalValuesJson)

    def __isValuesHaveValidFormat(self, values: dict) -> bool:
        if (
            'additional_values' in values and
            values['additional_values'] != None and
            type(values['additional_values']) != 'dict'
        ):
            return False

        return (
            'id' in values and
            'type' in values and
            'status' in values and
            'created_at' in values
        )

    def __isValidStatus(self, status: int) -> bool:
        if status == self.STATUS_PENDING:
            return True

        if status == self.STATUS_IN_PROGRESS:
            return True

        if status == self.STATUS_DONE:
            return True

        if status == self.STATUS_ERROR:
            return True

        return False

    def __isValidType(self, type: int) -> bool:
        if type == self.TYPE_CREATE_IMAGE_BY_PROMPT:
            return True

        if type == self.TYPE_CREDIT_REQUEST:
            return True

        if type == self.TYPE_CREDIT_APPROVE:
            return True

        if type == self.TYPE_CREDIT_REJECT:
            return True

        return False

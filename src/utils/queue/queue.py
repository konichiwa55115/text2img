import json
import time
from typing import Union
from utils.queue.job import Job
from utils.logger import Logger
from store import Store
from workers.image import Image
from workers.credits import Credits

class Queue:
    __logger = None
    __store = None
    __image_worker = None
    __credits_worker = None

    def __init__(self) -> None:
        self.__store = Store()
        self.__logger = Logger()
        self.__image_worker = Image()
        self.__credits_worker = Credits()

    def doJobs(self) -> None:
        self.__doCleanJobs()

        job = self.__getPendingJob()

        while job != None:
            self.__doLogJobsCount()

            self.__doJob(job)

            job = self.__getPendingJob()

        return True

    def addJob(self, jobId: str, type: int, additionalValues: Union[dict, None]) -> None:
        additionalValuesJson = None
        
        if additionalValues != None:
            additionalValuesJson = json.dumps(additionalValues)
        
        additionalValuesJson = str(additionalValuesJson)

        self.__logger.log(
            'Add Job To Queue. Job ID: %s, Type: "%s", Additional Params: %s' % (
                jobId,
                Job.getTypeTitle(type),
                additionalValuesJson
            )
        )

        self.__store.insertJob(
            jobId,
            type,
            additionalValuesJson,
            Job.STATUS_PENDING,
            None
        )

    def __doCleanJobs(self) -> None:
        self.__doCleanDoneJobs()
        self.__setOutdatedJobsToError()
        self.__doCleanErrorJobs()

    def __doCleanDoneJobs(self) -> None:
        self.__store.removeJobByStatus(Job.STATUS_DONE)

    def __setOutdatedJobsToError(self) -> None:
        job = self.__getOutdatedJob()

        while job != None:
            if job.getStatus() == Job.STATUS_DONE or job.getStatus() == Job.STATUS_ERROR:
                continue

            errorMessage = 'Queue Job Was Removed From Queue Due Reaching Timeout'

            job.setErrorMessage(errorMessage)
            job.setStatus(Job.STATUS_ERROR)

            errorMessage = '%s. Job ID: %s' % (errorMessage, job.getId())

            self.__logger.logError(errorMessage)

            self.__updateJob(job)

            job = self.__getOutdatedJob()

    def __doCleanErrorJobs(self) -> None:
        self.__store.removeJobByStatus(Job.STATUS_ERROR)

    def __doLogJobsCount(self) -> None:
        jobsCount = self.__store.getJobsCount()

        if (jobsCount['all'] < 1):
            return

        logMessage = 'Jobs In Queue: %d (' % int(jobsCount['all'])

        for jobStatusTitle in jobsCount.keys():
            if jobStatusTitle == 'all':
                continue

            logMessage = '%s%s: %d, ' % (logMessage, jobStatusTitle, int(jobsCount[jobStatusTitle]))

        logMessage = logMessage[:len(logMessage) - 2]
        logMessage = '%s)' % logMessage

        self.__logger.log(logMessage)

    def __getPendingJob(self) -> Union[Job, None]:
        row = self.__store.getJobByStatus(Job.STATUS_PENDING)

        if row == None:
            return None

        return Job(row)

    def __getOutdatedJob(self) -> Union[Job, None]:
        createdAt = int(time.time()) - Job.TIMEOUT

        row = self.__store.getJobByCreatedAt(createdAt)

        if row == None:
            return None

        job = Job(row)

        if job.getStatus() == Job.STATUS_DONE or job.getStatus() == Job.STATUS_ERROR:
            return None

        return job

    def __doJob(self, job: Job) -> None:
        self.__logger.log('Start job id: %s' % job.getId())

        job.setStatus(Job.STATUS_IN_PROGRESS)
        self.__updateJob(job)

        try:
            additionalValues = job.getAdditionalValues()

            if job.getType() == Job.TYPE_CREATE_IMAGE_BY_PROMPT:
                self.__image_worker.createFromText(
                    additionalValues['user_id'],
                    additionalValues['user_name'],
                    additionalValues['chat_id'],
                    additionalValues['message_id'],
                    additionalValues['text']
                )
            elif job.getType() == Job.TYPE_CREDIT_REQUEST:
                self.__credits_worker.request(
                    int(additionalValues['callback_values']['user_id']),
                    int(additionalValues['callback_values']['chat_id']),
                    int(additionalValues['parent_message_id'])
                )
            elif job.getType() == Job.TYPE_CREDIT_APPROVE:
                self.__credits_worker.approve(
                    int(additionalValues['callback_values']['user_id']),
                    int(additionalValues['callback_values']['chat_id']),
                    int(additionalValues['parent_message_id'])
                )
            elif job.getType() == Job.TYPE_CREDIT_REJECT:
                self.__credits_worker.reject(
                    int(additionalValues['callback_values']['user_id']),
                    int(additionalValues['callback_values']['chat_id']),
                    int(additionalValues['parent_message_id'])
                )
            else:
                raise Exception(
                    'Unsupported Queue Job Type. Job ID: %s, Type ID: %d' % (
                        job.getId(), job.getType()
                    )
                )
        except Exception as exp:
            if hasattr(exp, 'message'):
                errorMessage = exp.message
            else:
                errorMessage = str(exp)

            job.setStatus(Job.STATUS_ERROR)
            job.setErrorMessage(errorMessage)
            self.__updateJob(job)

            raise Exception(errorMessage)

        job.setStatus(Job.STATUS_DONE)
        self.__updateJob(job)

        self.__logger.log('End job id: %s' % job.getId())

        return

    def __updateJob(self, job: Job) -> None:
        self.__store.updateJob(
            job.getId(),
            job.getStatus(),
            job.getErrorMessage()
        )

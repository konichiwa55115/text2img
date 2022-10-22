from utils.logger import Logger
from user.user import User
from utils.telegram.telegram import Telegram
from utils.telegram.message import Message as TelegramMessage
from utils.settings import Settings

class Credits:
    __logger = None
    __telegram = None
    __settings = None

    def __init__(self) -> None:
        self.__logger = Logger()
        self.__telegram = Telegram()
        self.__settings = Settings()

    def request(
        self,
        userId: int,
        chatId: int,
        perentMessageId: int
    ) -> None:
        try:
            self.__logger.log('Cheking User Credits. User ID: %d' % userId)

            user = User.getFromStore(userId)

            if user.isHaveCredits():
                self.__logger.log('User Have Credits. Request Is Not Needed. User ID: %s' % user.getId())

                self.__logger.log('Removing Request Message For User. User ID: %s' % user.getId())

                self.__telegram.deleteMessage(
                    chatId,
                    perentMessageId
                )

                return

            telegramConfig = self.__settings.getTelegramConfig()

            self.__logger.log(
                'Sending Credit Request Message To Admin. User ID: %s. Admin ID: %s' % (
                    user.getId(),
                    telegramConfig['admin_chat_id']
                )
            )

            self.__telegram.sendMessageWithButtons(
                'User *%s* is asking more credits' % user.getName(),
                (
                    {
                        'title': '✅ Approve request',
                        'callback_values': 'n=%s,uid=%s,cid=%s' % (
                            TelegramMessage.CALLABCK_CREDITS_APPROVE,
                            user.getId(),
                            chatId
                        )
                    },
                    {
                        'title': '❌ Reject request',
                        'callback_values': 'n=%s,uid=%s,cid=%s' % (
                            TelegramMessage.CALLABCK_CREDITS_REJECT,
                            user.getId(),
                            chatId
                        )
                    }
                ),
                telegramConfig['admin_chat_id']
            )

            self.__telegram.updateMessage(
                '\n✉️ Request for credits sent. Waiting for admin approval',
                chatId,
                perentMessageId
            )
        except Exception as exp:
            self.__telegram.sendMessage(
                '🚨 Internal server error. Please try again',
                chatId,
                True
            )

            raise exp

    def approve(
        self,
        userId: int,
        chatId: int,
        perentMessageId: int
    ) -> None:
        try:
            self.__logger.log('Cheking User Credits. User ID: %d' % userId)

            user = User.getFromStore(userId)

            telegramConfig = self.__settings.getTelegramConfig()
            adminChatId = telegramConfig['admin_chat_id']

            if user.isHaveCredits():
                self.__logger.log('User Have Credits. Request Is Not Needed. User ID: %s' % user.getId())

                self.__logger.log('Updating Request Message For Admin. Admin ID: %s' % adminChatId)

                self.__telegram.updateMessage(
                    'User *%s* already have credits' % user.getName(),
                    adminChatId,
                    perentMessageId
                )

                return

            creditsCount = User.CREDITS_BATCH_SIZE_FREE

            if user.getType() == user.TYPE_PREMIUM:
                creditsCount = User.CREDITS_BATCH_SIZE_PREMIUM

            self.__logger.log(
                'Add %s Credits To User. User ID: %s' % (
                    creditsCount,
                    user.getId()
                )
            )

            user.setCredits(creditsCount)

            User.updateInStore(user)

            self.__logger.log('Updating Request Message For Admin. Admin ID: %s' % adminChatId)

            self.__telegram.updateMessage('Request approved', adminChatId, perentMessageId)

            self.__logger.log('Sending Approval Notification To User. User ID: %s' % userId)

            self.__telegram.sendMessage(
                '🎉 You request was approved. You have *%d* unused credits' % user.getCredits(),
                chatId,
                True
            )
        except Exception as exp:
            telegramConfig = self.__settings.getTelegramConfig()
            adminChatId = telegramConfig['admin_chat_id']

            self.__telegram.sendMessage(
                '🚨 Internal server error. Please try again',
                adminChatId,
                True
            )

            raise exp

    def reject(
        self,
        userId: int,
        chatId: int,
        perentMessageId: int
    ) -> None:
        try:
            self.__logger.log('Cheking User Credits. User ID: %d' % userId)

            user = User.getFromStore(userId)

            telegramConfig = self.__settings.getTelegramConfig()
            adminChatId = telegramConfig['admin_chat_id']

            if user.isHaveCredits():
                self.__logger.log('User Have Credits. Request Is Not Needed. User ID: %s' % user.getId())

                self.__logger.log('Updating Request Message For Admin. Admin ID: %s' % adminChatId)

                self.__telegram.updateMessage(
                    'User *%s* already have credits' % user.getName(),
                    adminChatId,
                    perentMessageId
                )

                return

            self.__logger.log('Rejecting Request For Credits. User ID: %s' % user.getId())

            self.__logger.log('Updating Request Message For Admin. Admin ID: %s' % adminChatId)

            self.__telegram.updateMessage('Request rejected', adminChatId, perentMessageId)

            self.__logger.log('Sending Approval Notification To User. User ID: %s' % userId)

            self.__telegram.sendMessage('❌ You request was rejected. Sorry', chatId, True)
        except Exception as exp:
            telegramConfig = self.__settings.getTelegramConfig()
            adminChatId = telegramConfig['admin_chat_id']

            self.__telegram.sendMessage(
                '🚨 Internal server error. Please try again',
                adminChatId,
                True
            )

            raise exp

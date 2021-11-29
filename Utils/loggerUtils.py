from enum import Enum

from os import getenv

DEBUG = (True if getenv('BOT_DEBUG') == 'True' else False)


class logType(Enum):
    SEVERE = '[ SEVERE ] '  # if something critical is caught
    WARN = '[ WARN ] '  # not critical, but still bad
    # something good happens that might not always happen
    OK = '[ OK ] '
    # prefix for log entries when debugging
    DEBUG = '[ BOT-DEBUG ] '
    LOG = '[ BOT-LOG ] '  # prefix for all other log entries
    USRMSG = '[ MESSAGE ] '  # prefix for captured messages
    # prefix for messages by the bot (  i.e. [ MESSAGE ] [ BOT ] Botname: Message  )
    BOTMSG = '[ BOT MSG ] '
    # Same as above, but for system messages like topic changes
    SYSMSG = '[ GroupMe ] '


class LOGGER:
    # suffix for log entries (normally just clears formatting)
    logTail = ''

    @staticmethod
    def warn(msg):
        print(logType.WARN.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def severe(msg):
        print(logType.SEVERE.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def ok(msg):
        print(logType.OK.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def debug(msg):
        if DEBUG:
            print(logType.DEBUG.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def log(msg):
        print(logType.LOG.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def userMsg(msg):
        print(logType.USRMSG.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def botmsg(msg):
        print(logType.BOTMSG.value + str(msg) + LOGGER.logTail)

    @staticmethod
    def sysmsg(msg):
        print(logType.SYSMSG.value + str(msg) + LOGGER.logTail)

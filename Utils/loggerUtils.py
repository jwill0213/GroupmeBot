from enum import Enum

from os import getenv

DEBUG = (True if getenv('BOT_DEBUG') == 'True' else False)


class logType(Enum):
    SEVERE = '\033[31m[ SEVERE ]\033[00m '  # if something critical is caught
    WARN = '\033[33m[ WARN ]\033[0m '  # not critical, but still bad
    # something good happens that might not always happen
    OK = '\033[32m[ OK ]\033[00m '
    # prefix for log entries when debugging
    DEBUG = '\033[35m[ BOT-DEBUG ]\033[00m '
    LOG = '\033[36m[ BOT-LOG ]\033[00m '  # prefix for all other log entries
    USRMSG = '\033[36m[ MESSAGE ]\033[00m '  # prefix for captured messages
    # prefix for messages by the bot (  i.e. [ MESSAGE ] [ BOT ] Botname: Message  )
    BOTMSG = '\033[33m[ BOT MSG ]\033[00m '
    # Same as above, but for system messages like topic changes
    SYSMSG = '\033[00m[ GroupMe ]\033[00m '


class LOGGER:
    # suffix for log entries (normally just clears formatting)
    logTail = '\033[00m'

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

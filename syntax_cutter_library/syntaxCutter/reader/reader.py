import logging
import sys
import datetime


class Reader():

    __verbose = None
    __logger = None

    def logInfo(self, messages):
        self.__logger.info(messages)

    def logError(self, messages):
        self.__logger.error(messages)

    def __init__(self):

        # create formatter and add it to the handlers
        self.__logger = logging.getLogger("Reader")
        # stop propagating to root logger
        self.__logger.propagate = False
        set = True
        for handler in self.__logger.handlers:
            set = False
            break
        if set:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.__logger.addHandler(ch)

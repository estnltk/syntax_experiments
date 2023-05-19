import logging


class BaseReader:
	__verbose = None
	__logger = None

	def log_info(self, messages):
		self.__logger.info(messages)

	def log_error(self, messages):
		self.__logger.error(messages)

	def __init__(self):

		# create formatter and add it to the handlers
		self.__logger = logging.getLogger("Reader")
		# stop propagating to root logger
		self.__logger.propagate = False
		logger_set = True
		# TODO! rewrite
		for handler in self.__logger.handlers:
			logger_set = False
			break
		if logger_set:
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			ch = logging.StreamHandler()
			ch.setFormatter(formatter)
			self.__logger.addHandler(ch)


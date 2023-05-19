class ListUtils:

	@staticmethod
	def list_intersection(a, b):
		"""
		kahe listi ühisosa
		"""
		return list(set(a).intersection(b))

	@staticmethod
	def is_list_consecutive(array):
		"""
		tagastab, kas listis on järjestikulised numbrid
		eeldab, et listi liikmed on int
		"""

		# kui listi liikmed pole unikaalsed
		if len(array) != len(list(set(array))):
			return False

		# kui listis on 1 v 0 elementi
		if len(array) < 2:
			return True

		# järjestikuliste numbrite puhul max - min + 1 = listi pikkus
		return max(array) - min(array) + 1 == len(array)

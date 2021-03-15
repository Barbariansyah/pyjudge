# Copyright - see copyright.txt

class Predicate:
	"""Predicate is one specific ``if'' encountered during the program execution.
	   """
	def __init__(self, st, result):
		# print(st.expr[1].name, st.expr[0], st.expr[2].name, result)
		self.symtype = st
		self.result = result

	def getVars(self):
		return self.symtype.getVars()

	def __eq__(self, other):
		if isinstance(other, Predicate):
			res = self.result == other.result and self.symtype.symbolicEq(other.symtype)
			return res
		else:
			return False

	def __hash__(self):
		return hash(self.symtype)

	def __str__(self):
		return self.symtype.toString() + " (%s)" % (self.result)

	def __repr__(self):
		return self.__str__()

	def negate(self):
		"""Negates the current predicate"""
		assert(self.result is not None)
		self.result = not self.result


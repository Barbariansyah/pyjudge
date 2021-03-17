from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .z3_translator import Z3Translator
from .path_constraint import PathConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type, SymbolicType

log = logging.getLogger("se.conc")

class GradingEngine:
	def __init__(self, funcinv, solver="z3"):
		self.invocation = funcinv
		# the input to the function
		self.symbolic_inputs = {}  # string -> SymbolicType
		# initialize
		for n in funcinv.getNames():
			self.symbolic_inputs[n] = funcinv.createArgumentValue(n)

		# print(self.symbolic_inputs)

		self.constraints_to_solve = deque([])
		self.num_processed_constraints = 0
		
		self.path_constraints = deque([])

		self.path = PathConstraint(lambda c : self.addConstraint(c), lambda p: self.addToPathConstraint(p))
		# link up SymbolicObject to PathToConstraint in order to intercept control-flow
		symbolic_type.SymbolicObject.SI = self.path

		self.solver = Z3Wrapper()
		self.translator = Z3Translator()

		# outputs
		self.generated_inputs = []
		self.execution_return_values = []

	def addConstraint(self, constraint):
		self.constraints_to_solve.append(constraint)
		# make sure to remember the input that led to this constraint
		constraint.inputs = self._getInputs()

	def addToPathConstraint(self, pred):
		self.path_constraints.append(pred)

	def grade(self, generated_inputs, execution_return_values):
		print(generated_inputs)
		print(execution_return_values)
		for inp in generated_inputs[0]:
			self._updateSymbolicParameter(inp[0], inp[1])
		ret = self.invocation.callFunction(self.symbolic_inputs)
		# self._printPCDeque()
		self.translator.pcToZ3(self.path_constraints)
		print(ret)
		return
	
	def explore(self, max_iterations=0):
		# print('==============================================')
		# print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
		# print('==============================================')
		# print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
		# print('==============================================')
		self._oneExecution()
		iterations = 1
		if max_iterations != 0 and iterations >= max_iterations:
			log.debug("Maximum number of iterations reached, terminating")
			return self.execution_return_values

		while not self._isExplorationComplete():
			# print('\n')
			# print('\n')
			# print("before====")
			# self._printConstraintsDeque()
			# print("*************")
			selected = self.constraints_to_solve.popleft()
			# print("remaining====")
			# print(self.constraints_to_solve)
			# print("*************")
			# print("selected====")
			# print(selected)
			# print("============")
			if selected.processed:
				continue
			self._setInputs(selected.inputs)			

			log.info("Selected constraint %s" % selected)
			asserts, query = selected.getAssertsAndQuery()
			model = self.solver.findCounterexample(asserts, query)

			# print("--model--")
			# print(model)
			if model == None:
				continue
			else:
				for name in model.keys():
					self._updateSymbolicParameter(name,model[name])

			self._oneExecution(selected)

			iterations += 1			
			self.num_processed_constraints += 1

			if max_iterations != 0 and iterations >= max_iterations:
				log.info("Maximum number of iterations reached, terminating")
				break

		return self.generated_inputs, self.execution_return_values, self.path

	# private

	def _updateSymbolicParameter(self, name, val):
		self.symbolic_inputs[name] = self.invocation.createArgumentValue(name,val)

	def _getInputs(self):
		return self.symbolic_inputs.copy()

	def _setInputs(self,d):
		self.symbolic_inputs = d

	def _isExplorationComplete(self):
		num_constr = len(self.constraints_to_solve)
		if num_constr == 0:
			log.info("Exploration complete")
			return True
		else:
			log.info("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
			return False

	def _getConcrValue(self,v):
		if isinstance(v,SymbolicType):
			return v.getConcrValue()
		else:
			return v

	def _recordInputs(self):
		args = self.symbolic_inputs
		inputs = [ (k,self._getConcrValue(args[k])) for k in args ]
		self.generated_inputs.append(inputs)
		print('inp=',inputs)
		
	def _oneExecution(self,expected_path=None):
		self._recordInputs()
		self.path.reset(expected_path)
		# print('sym_inp=',self.symbolic_inputs['a'].toString())
		
		ret = self.invocation.callFunction(self.symbolic_inputs)
		self._printPCDeque()
		print('ret=',ret)
		self.execution_return_values.append(ret)
		self.path_constraints.clear()

	def _printConstraintsDeque(self):
		for i in self.constraints_to_solve:
			print(i)
			print('---\n')

	def _printPCDeque(self):
		for i in self.path_constraints:
			print(i)
			print('---\n')
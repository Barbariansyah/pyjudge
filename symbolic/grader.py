from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .z3_translator import Z3Translator
from .path_constraint import PathConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type, SymbolicType
from .symbolic_types.symbolic_int import SymbolicInteger
from z3 import *

log = logging.getLogger("se.conc")

class GradingEngine:
	def __init__(self, funcinv, funcinvStudent, solver="z3"):
		self.tested_case = {}
		self.wrong_case = {}
		self.invocation = funcinv
		self.invocationStudent = funcinvStudent
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
		for generated_input in generated_inputs:
			# print('from set: ')
			pc, pcStudent, ret, retStudent = self.execute_program(generated_input)
			# if ret.val != retStudent.val:
			# 	print(ret.val)
			# 	print(retStudent.val)
			# 	print('implementation is incorrect')
			self.add_to_tested(generated_input, ret, retStudent)
			pathDeviationForm = self.path_deviation_builder(pc, pcStudent)
			sat, res = self.z3_solve(pathDeviationForm)
			if sat != 'sat':
				# print('no path deviation, skipping...')
				continue
			# print('from path dev: ')
			pc, pcStudent, ret, retStudent = self.execute_program(res)
			# if ret.val != retStudent.val:
			# 	print(ret.val)
			# 	print(retStudent.val)
			# 	print('implementation is incorrect')
			self.add_to_tested(res, ret, retStudent)
			if not isinstance(ret, SymbolicInteger) or not isinstance(retStudent, SymbolicInteger):
				continue
			retSym = self.translator.symToZ3(ret.name)
			retStudentSym = self.translator.symToZ3(retStudent.name)
			pathEquivalenceForm = self.path_equivalence_builder(pc, pcStudent, retSym, retStudentSym)
			sat, res = self.z3_solve(pathEquivalenceForm)
			if sat != 'sat':
				# print('path is equivalent, skipping...')
				continue
			# print('from path equiv: ')
			pc, pcStudent, ret, retStudent = self.execute_program(res)
			# if ret.val != retStudent.val:
			# 	print(ret.val)
			# 	print(retStudent.val)
			# 	print('implementation is incorrect')
			self.add_to_tested(res, ret, retStudent)
		return self.tested_case, self.wrong_case
	
	def add_to_tested(self, case, output_ref, output_stud):
		if isinstance(output_ref, SymbolicInteger):
			output_ref = output_ref.val
		if isinstance(output_stud, SymbolicInteger):
			output_stud = output_stud.val
		if tuple(sorted(case)) in self.tested_case:
			pass
		if output_ref == output_stud:
			self.tested_case[tuple(sorted(case))] = (output_ref, output_stud)
		else:
			self.tested_case[tuple(sorted(case))] = (output_ref, output_stud)
			self.wrong_case[tuple(sorted(case))] = (output_ref, output_stud)
	
	def execute_program(self, sym_inp):
		# print(sym_inp)
		for inp in sym_inp:
			self._updateSymbolicParameter(inp[0], inp[1])
		ret = self.invocation.callFunction(self.symbolic_inputs)
		# print('ret: '+str(ret.val))
		# self._printPCDeque()
		pc = self.translator.pcToZ3(self.path_constraints)
		self.path_constraints = deque([])
		retStudent = self.invocationStudent.callFunction(self.symbolic_inputs)
		# print('retStudent: '+str(retStudent.val))
		# self._printPCDeque()
		pcStudent = self.translator.pcToZ3(self.path_constraints)
		self.path_constraints = deque([])
		# ret is SymbolicInteger
		# ret.name
		# ret.val
		return And(pc), And(pcStudent), ret, retStudent

	def path_deviation_builder(self, a, b):
		return Or(And(a, Not(b)), And(b, Not(a)))

	def path_equivalence_builder(self, a, b, oa, ob):
		return And(oa!=ob, And(a, b))

	def z3_solve(self, formula):
		s = Solver()
		s.add(formula)
		sat = s.check()
		# print(s)
		# print(s.check())
		# print(s.model())
		# print(formula)
		if repr(sat) == 'sat':
			res = self.translator.modelToInp(s.model())
			return 'sat', res
		else:
			return 'unsat', None

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
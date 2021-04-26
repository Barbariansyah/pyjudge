import os
import sys
import logging
import traceback
from optparse import OptionParser

from symbolic.loader import *
from symbolic.explore import ExplorationEngine
from symbolic.grader import GradingEngine

def tracefunc(frame, event, arg, indent=[0]):
      if event == "call":
          indent[0] += 2
          print("-" * indent[0] + "> call function", frame.f_code.co_name)
      elif event == "return":
          print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
          indent[0] -= 2
      return tracefunc

# uncomment to trace function call
# sys.setprofile(tracefunc)

sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

usage = "usage: %prog [options] <path to reference *.py file> <path to submission *.py file>"
parser = OptionParser(usage=usage)

parser.add_option("-l", "--log", dest="logfile", action="store", help="Save log output to a file", default="")
parser.add_option("-m", "--max-iters", dest="max_iters", type="int", help="Run specified number of iterations", default=0)

(options, args) = parser.parse_args()

if not (options.logfile == ""):
	logging.basicConfig(filename=options.logfile,level=logging.DEBUG)

if len(args) == 0 or not os.path.exists(args[0]):
	parser.error("Missing app to execute")
	sys.exit(1)

filename = os.path.abspath(args[0])
filenameStudent = os.path.abspath(args[1])
	
# Get the object describing the application
app = loaderFactory(filename)
appStudent = loaderFactory(filenameStudent)
if app == None or appStudent == None:
	sys.exit(1)

print ("Reference: " + app.getFile() + "." + app.getEntry())
print ("Grading: " + appStudent.getFile() + "." + appStudent.getEntry())


result = None
try:
	explorationEngine = ExplorationEngine(app.createInvocation(), "z3")
	generatedInputs, returnVals, path = explorationEngine.explore(options.max_iters)
	explorationEngineStudent = ExplorationEngine(appStudent.createInvocation(), "z3")
	generatedInputsStudent, returnValsStudent, pathStudent = explorationEngineStudent.explore(options.max_iters)
	generatedInputs += generatedInputsStudent
	returnVals += returnValsStudent
	gradingEngine = GradingEngine(app.createInvocation(), appStudent.createInvocation(), "z3")
	tested_case, wrong_case = gradingEngine.grade(generatedInputs, returnVals)
	
	tested_case_from_formula = tested_case.copy()
	wrong_case_from_formula = wrong_case.copy()
	for generated_input in generatedInputs:
		generated_input_tuple = tuple(sorted(generated_input))
		if generated_input_tuple in tested_case_from_formula:
			del tested_case_from_formula[generated_input_tuple]
		if generated_input_tuple in wrong_case_from_formula:
			del wrong_case_from_formula[generated_input_tuple]

	print('======')
	print('RESULT')
	print('======')
	print('\ntested: ')
	print(tested_case)
	print('\ntested from path dev or path eq: ')
	print(tested_case_from_formula)
	print('\nwrong: ')
	print(wrong_case)
	print('\nwrong from path dev or path eq: ')
	print(wrong_case_from_formula)
	print('\ngrade: ')
	final_grade = (len(tested_case) - len(wrong_case)) / len(tested_case) * 100
	print(str(final_grade)+'%')
	# check the result
	result = app.executionComplete(returnVals)

except ImportError as e:
	# createInvocation can raise this
	logging.error(e)
	sys.exit(1)

if result == None or result == True:
	sys.exit(0);
else:
	sys.exit(1);	

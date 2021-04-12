# pyjudge
<img src="/pyjudge-logo.png" width="96">
Concolic execution based automatic grader

## What is this?
PyJudge is an automatic grading tools that takes a reference implementation and a student implementation then finds an input that causes a different output

This code used and is a modified version of [PyExZ3](https://github.com/thomasjball/PyExZ3) that is a Dynamic Symbolic Execution Engine for Python

This program is the deliverable of my [final project]()

## Getting Started
1. Make sure you have Python 3.x installed
2. Install Z3 here https://github.com/Z3Prover/z3
3. For MacOS, open `setup.sh` and change the path according to your local machine then run:
```
. pyjudge/setup.sh
```
4. try grade something
```
python grade.py test/max_3.py test/max_3_1.py
```

## Usage
```
python grade.py <reference_implementation>.py <student_implementation>.py
```

### How does it do that?
...coming soon

### Limitation
- can only operates on Integers

### Literature
...coming soon

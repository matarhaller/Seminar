CalCalc module with method calculate.

First it tries to evaluate the input (a string) (disables the builtin functions and loading the math module locally). In that case, calculate will return an integer

If that doesn't work then it access wolfram alpha (runwolfram)

runwolfram calls makeurl to format the string in an encoding which will fit the wolfram alpha api

Then runwolfram calls the api (using the urllib2 module) and then parses the xml (ElementTree from xml.etree)

runwolfram simply returns the plaintext string from the xml source code.

If wolfram doesn't know the answer (or doesn't understand the question), calculate doesn't break (returns the string "Wolfram Alpha doesn't know the answer...")

Also included are five test cases.

Can be called either from the command line or from the interpreter.
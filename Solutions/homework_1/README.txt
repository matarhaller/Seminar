This is the CalCalc module, a solution to Python for Science's
homework 1, Fall 2012.

Use it from the command line:
$ python CalCalc.py -s 'mass of the moon in kg'
$ 7.3459*10**22 kg  (kilograms)

Or use it from within Python:
>>> from CalCalc import calculate
>>> calculate('mass of the moon in kg', return_float=True) * 10
>>> 7.3459e+23


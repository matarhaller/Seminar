#!/usr/bin/env python
'''
This file provides the calculate function,
which is both a local Python evaluator and W|A interrogator.

Isaac Shivvers, 2012, PySci

'''

from __future__ import division 
import math, urllib, re
def calculate(eval_string, return_float=False):
    '''
    Calculates the expression contained in 'eval_string'
    If the expression is a basic Python calculation, return the evaluation.
    Otherwise, query the WolframAlpha API and return what it thinks the best answer is.
    If return_float: attempt to force the answer into a float (not always successful)
    otherwise: return a string
    '''
    
    wolfram_string = 'http://api.wolframalpha.com/v2/query?input={}&appid=UAGAWR-3X6Y8W777Q'
    # note: urllib handles spaces gracefully, so no need to worry about them!
    
    try:
        result = eval(eval_string, {}, vars(math))
        if not return_float: #to yield consistant behavior, return a string unless we ask for a float
            result = str(result)
    except Exception:
        result = 'what?' #placeholder in case we just can't understand
        # Hit this if python doesn't understand the query. Call in the big guns!
        query_result = urllib.urlopen(wolfram_string.format(eval_string)).read()
        query_result = query_result.split('</pod>') #Wolfram returns values encapsulted in 'pods'
        try:
            for pod in query_result:
                if "primary='true'" in pod: #this indicates that Wolfram thinks that this is the best answer
                    result = re.findall('<plaintext>.+</plaintext>', pod)[0]
                    result = result.strip('<plaintext>').strip('</plaintext>')
                    if '\xc3\x97' in result: #replace weird \times character
                        result = result.replace('\xc3\x9710^', '*10**') #replace x10^ string with Python formatting
                    if return_float:
                        # minimal attempt at understanding the numerical result
                        #  WARNING: not guaranteed to be correct
                        result = result.strip('.') #trailing ellipses is used to show approximations - get rid of it
                        matches = result.split(' ')
                        for val in matches[::-1]:
                            try:
                                result = eval(val, {}, vars(math))
                            except Exception:
                                pass
        except:
            # hit here if we can't parse the W|A output
            pass
    return result


# tests
def test_sin():
    #test basic math usage
    val = math.sin(.2)
    assert abs(val - calculate('sin(.2)', True)) < .001

def test_sin2():
    #test numerical W|A usage
    val = math.sin(.2)
    assert abs(val - calculate('sin .2', True)) < .001

def test_exponent():
    #test exponentiation
    val = 23**2
    assert abs(val - calculate('23**2', True)) < .001

def test_WA_query():
    #test whether WA gives the correct moon mass
    val = 7.3459e+22
    assert abs(val/10**22 - calculate('mass of moon in kg', True)/10**22) < .001

def test_WA_unit_conversions():
    #test whether unit conversions work
    val = 100.
    assert abs(val - calculate('convert 1m to cm', True)) < .01

def test_WL_integrations():
    #test whether we interpret integral outputs correctly
    val = 15./4.
    assert abs(val - calculate('integral of x**3 from x=1 to x=2', True)) < .001

# main
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', default='0', dest='eval_string', help='The string which you wish to evaluate')
    parser.add_argument('-f', action='store_true', default=False, dest='return_float',
                        help='Attempt to force the answer into a float before returning it.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()
    
    result = calculate(args.eval_string, return_float=args.return_float)
    print result

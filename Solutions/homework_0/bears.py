'''
Python Computing for Science, Fall 2012

#### Homework 0 Solutions ####
This file contains the bear class, used to answer the homework questions 
in answers.py

Isaac Shivvers
ishivvers@berkeley.edu
'''

from random import gauss

class bear():
    ''' Go Bears! '''
    def __init__(self, sex='M', name='Adam', mother='Earth', father='Thor'):
        # initialize the variables
        self.age  = 0
        self.sex  = sex
        self.name = name
        self.mom  = mother
        self.dad  = father
        # it's destiny...set a death age:
        self.death = int(gauss(35, 5))
        self.years_since_procreation = 0

    def age_thyself(self, years=1):
        ''' Age <self> by <years>.  Returns False if bear dies this year, True otherwise. '''
        self.age += years
        self.years_since_procreation += years
        if self.age >= self.death:
            # the end is now
            return False
        else:
            return True
    
    def request_procreation(self, other):
        '''
        try an intimate request to <other>.
        Returns True good match, and False if not.
        '''
        if self.years_since_procreation >= 5 and other.years_since_procreation >=5 \
        and abs(self.age - other.age) <= 10 \
        and self.age >= 5 and other.age >= 5 and self.sex != other.sex \
        and (self.mom != other.mom or self.dad != other.dad) \
        and self.mom != other.name and self.dad != other.name:
            # good to go
            self.years_since_procreation = 0
            other.years_since_procreation = 0
            return True
        else:
            return False

        
        
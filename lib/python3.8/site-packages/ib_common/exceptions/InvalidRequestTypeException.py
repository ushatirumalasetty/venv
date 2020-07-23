"""
Created on 09/03/17

@author: revanth
"""


class InvalidRequestTypeException(Exception):
    def __init__(self, message='[Custom Exception] Invalid Request type argument', errors=None):

        super(InvalidRequestTypeException, self).__init__(message)

        if errors is None:
            errors = []
        self.errors = errors

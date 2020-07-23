"""
Created on 09/03/17

@author: revanth
"""


class InvalidResponseTypeException(Exception):
    def __init__(self, message='[Custom Exception] invalid response type returned or is none', errors=None):

        super(InvalidResponseTypeException, self).__init__(message)

        if errors is None:
            errors = []
        self.errors = errors

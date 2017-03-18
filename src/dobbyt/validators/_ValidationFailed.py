"""

Exception class, thrown by validators when they fail

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""



class ValidationFailed(BaseException):

    """ An application validation has failed """


    def __init__(self, err_code, message, validator):
        self._err_code = err_code
        self._message = message
        self._validator = validator


    @property
    def err_code(self):
        return self._err_code

    @property
    def message(self):
        return self._message

    @property
    def validator(self):
        return self._validator



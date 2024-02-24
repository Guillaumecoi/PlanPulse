from django.forms import ValidationError
from datetime import timedelta
from decimal import Decimal


class Metric:
    '''
    Base class that coverts between Decimal values and the appropriate metric type
    '''
    def get(self, value):
        raise NotImplementedError('Subclasses must implement this method')

    def put(self, value):
        raise NotImplementedError('Subclasses must implement this method')

    def add(self, value, value2):
        raise NotImplementedError('Subclasses must implement this method')
    
    def subtract(self, value1, value2):
        raise NotImplementedError('Subclasses must implement this method')
    

class Number(Metric):
    '''
    Class that coverts between Decimal values and the appropriate number type
    '''
    def get(self, value):
        self.isNumber(value)
        return int(value)

    def put(self, value):
        self.isNumber(value)
        return value  # is converted automatically

    def add(self, value1, value2):
        self.isNumber(value1)
        self.isNumber(value2)
        return value1 + value2
    
    def subtract(self, value1, value2):
        self.isNumber(value1)
        self.isNumber(value2)
        return value1 - value2
    
    def isNumber(self, value):
        if value < 0:
            raise ValidationError('Invalid number value')
        


class Time(Metric):
    '''
    Class that coverts between Decimal in seconds values and timedelta type
    '''
    def get(self, value):
        self.isTimeDecimal(value)
        return timedelta(seconds=int(value))

    def isTimeDecimal(self, value):
        if not isinstance(value, Decimal):
            raise ValidationError('Invalid time value: not a decimal')
        if value < 0:
            raise ValidationError('Invalid time value: negative')
    

class Boolean(Metric):
    def get(self, value):
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise ValidationError('Invalid boolean value')

    def put(self, value):
        return 1 if value else 0
    
    def add(self, value1, value2):
        raise ValidationError('Cannot add boolean values')
    
    def subtract(self, value1, value2):
        raise ValidationError('Cannot subtract boolean values')
    

class Percentage(Metric):
    def get(self, value):
        return value
    

    

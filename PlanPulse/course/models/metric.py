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

    def put(self, value):
        self.isTimeDelta(value)
        return Decimal(value.total_seconds())
    
    def add(self, value1, value2):
        self.isTimeDelta(value1)
        self.isTimeDelta(value2)
        return value1 + value2

    def subtract(self, value1, value2):
        self.isTimeDelta(value1)
        self.isTimeDelta(value2)
        if value1 < value2:
            raise ValidationError('Invalid time value: negative result')
        return value1 - value2

    def isTimeDecimal(self, value):
        if not isinstance(value, Decimal):
            raise ValidationError('Invalid time value: not a decimal')
        if value < 0:
            raise ValidationError('Invalid time value: negative')
    
    def isTimeDelta(self, value):
        if not isinstance(value, timedelta):
            raise ValidationError('Invalid time value: not a timedelta')
        if value < timedelta(0):
            raise ValidationError('Invalid time value: negative')
    

class Boolean(Metric):
    '''
    Class that coverts between Decimal values and the appropriate boolean type
    '''
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
    '''
    Class that coverts between Decimal values and the appropriate percentage type
    '''
    def get(self, value):
        self.isPercentage(value)
        return value
    
    def put(self, value):
        self.isPercentage(value)
        return value
    
    def add(self, value1, value2):
        self.isPercentage(value1)
        self.isPercentage(value2)
        if value1 + value2 > 100:
            raise ValidationError('Invalid percentage value')
        return value1 + value2

    def subtract(self, value1, value2):
        self.isPercentage(value1)
        self.isPercentage(value2)
        if value1 - value2 < 0:
            raise ValidationError('Invalid percentage value')
        return value1 - value2

    def isPercentage(self, value):
        if not isinstance(value, Decimal):
            raise ValidationError('Invalid percentage value')
        if not 0 <= value <= 100:
            raise ValidationError('Invalid percentage value')
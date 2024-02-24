from django.forms import ValidationError


class Metric:
    '''
    Base class that coverts Decimal values to the appropriate metric type
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
    def get(self, value):
        if value < 0:
            raise ValidationError('Invalid number value')
        return int(value)

    def put(self, value):
        if value < 0:
            raise ValidationError('Invalid number value')
        return value  # is converted automatically

    def add(self, value1, value2):
        if value1 < 0 or value2 < 0:
            raise ValidationError('Invalid number value')
        return value1 + value2
    
    def subtract(self, value1, value2):
        if value1 < 0 or value2 < 0:
            raise ValidationError('Invalid number value')
        return value1 - value2


class Time(Metric):
    def get(self, value):
        return value
    

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
    

    

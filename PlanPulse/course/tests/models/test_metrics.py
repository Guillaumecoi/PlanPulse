import unittest

from django.forms import ValidationError
from datetime import timedelta
from decimal import Decimal

from course.models.metric import Number, Boolean, Time, Percentage

class NumberTest(unittest.TestCase):
    def setUp(self):
        self.number = Number()

    def test_get(self):
        self.assertEqual(self.number.get(5.00), 5)
        with self.assertRaises(ValidationError):
            self.number.get(-5.00)

    def test_put(self):
        self.assertEqual(self.number.put(5), 5)
        with self.assertRaises(ValidationError):
            self.number.put(-5)

    def test_add(self):
        self.assertEqual(self.number.add(2, 3), 5)
        with self.assertRaises(ValidationError):
            self.number.add(-2, 3)
            self.number.add(2, -3)
            self.number.add(-2, -3)

    def test_subtract(self):
        self.assertEqual(self.number.subtract(5, 3), 2)
        with self.assertRaises(ValidationError):
            self.number.subtract(-5, 3)
            self.number.subtract(5, -3)
            self.number.subtract(-5, -3)


class TestBoolean(unittest.TestCase):
    def setUp(self):
        self.boolean = Boolean()

    def test_get(self):
        self.assertEqual(self.boolean.get(0), False)
        self.assertEqual(self.boolean.get(1), True)
        with self.assertRaises(ValidationError):
            self.boolean.get(2)

    def test_put(self):
        self.assertEqual(self.boolean.put(False), 0)
        self.assertEqual(self.boolean.put(True), 1)

    def test_add(self):
        with self.assertRaises(ValidationError):
            self.boolean.add(True, False)

    def test_subtract(self):
        with self.assertRaises(ValidationError):
            self.boolean.subtract(True, False)


class TestTime(unittest.TestCase):
    def setUp(self):
        self.time = Time()

    def test_get(self):
        self.assertEqual(self.time.get(Decimal('5.00')), timedelta(seconds=5))
        self.assertEqual(self.time.get(Decimal('0.00')), timedelta(seconds=0))
        self.assertEqual(self.time.get(Decimal('60.00')), timedelta(minutes=1))
        self.assertEqual(self.time.get(Decimal('3600.00')), timedelta(hours=1))

        with self.assertRaises(ValidationError):
            self.time.get(Decimal('-5.00'))
            self.time.get(-5)
            self.time.get(True)
            
    def test_put(self):
        self.assertEqual(self.time.put(timedelta(seconds=5)), Decimal('5.00'))
        self.assertEqual(self.time.put(timedelta(seconds=0)), Decimal('0.00'))
        self.assertEqual(self.time.put(timedelta(minutes=1)), Decimal('60.00'))
        self.assertEqual(self.time.put(timedelta(hours=1)), Decimal('3600.00'))

        with self.assertRaises(ValidationError):
            self.time.put(timedelta(seconds=-5))
            self.time.put(-5)
            self.time.put(True)

    

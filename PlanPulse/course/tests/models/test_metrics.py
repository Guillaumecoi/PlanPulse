import unittest

from django.forms import ValidationError
from course.models.metric import Number

class NumberTest(unittest.TestCase):
    def setUp(self):
        self.number = Number()

    def test_get_positive_value(self):
        result = self.number.get(5.00)
        self.assertEqual(result, 5)

    def test_get_negative_value(self):
        with self.assertRaises(ValidationError):
            self.number.get(-5.00)

    def test_put_positive_value(self):
        result = self.number.put(5)
        self.assertEqual(result, 5)

    def test_put_negative_value(self):
        with self.assertRaises(ValidationError):
            self.number.put(-5)

    def test_add_positive_values(self):
        result = self.number.add(2, 3)
        self.assertEqual(result, 5)

    def test_add_negative_values(self):
        with self.assertRaises(ValidationError):
            self.number.add(-2, 3)

        with self.assertRaises(ValidationError):
            self.number.add(2, -3)

        with self.assertRaises(ValidationError):
            self.number.add(-2, -3)

    def test_subtract_positive_values(self):
        result = self.number.subtract(5, 3)
        self.assertEqual(result, 2)

    def test_subtract_negative_values(self):
        with self.assertRaises(ValidationError):
            self.number.subtract(-5, 3)

        with self.assertRaises(ValidationError):
            self.number.subtract(5, -3)

        with self.assertRaises(ValidationError):
            self.number.subtract(-5, -3)

if __name__ == '__main__':
    unittest.main()
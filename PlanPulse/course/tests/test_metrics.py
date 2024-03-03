import unittest

from django.forms import ValidationError
from datetime import timedelta
from decimal import Decimal

from PlanPulse.course.progress.metric import Number, Boolean, Time, Percentage

class NumberTest(unittest.TestCase):
    def setUp(self):
        self.number = Number()

    def test_get(self):
        self.assertEqual(self.number.get(Decimal(5.00)), 5)
        with self.assertRaises(ValidationError):
            self.number.get(Decimal(-5.00))

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

    def test_number_sum(self):
        number = Number()
        result = number.sum([Decimal(1.00), Decimal(2.00), Decimal(3.00), Decimal(4.00), Decimal(5.00)])
        self.assertEqual(result, 15)


class TestBoolean(unittest.TestCase):
    def setUp(self):
        self.boolean = Boolean()

    def test_get(self):
        self.assertEqual(self.boolean.get(Decimal(0.00)), False)
        self.assertEqual(self.boolean.get(Decimal(1.00)), True)
        with self.assertRaises(ValidationError):
            self.boolean.get(Decimal(5.00))

    def test_put(self):
        self.assertEqual(self.boolean.put(False), Decimal(0.00))
        self.assertEqual(self.boolean.put(True), Decimal(1.00))

    def test_add(self):
        with self.assertRaises(ValidationError):
            self.boolean.add(True, False)

    def test_subtract(self):
        with self.assertRaises(ValidationError):
            self.boolean.subtract(True, False)

    def test_boolean_sum(self):
        boolean = Boolean()
        with self.assertRaises(ValidationError):
            boolean.sum([Decimal(1.00), Decimal(0.00), Decimal(1.00)])


class TestTime(unittest.TestCase):
    def setUp(self):
        self.time = Time()

    def test_get(self):
        self.assertEqual(self.time.get(Decimal(5.00)), timedelta(seconds=5))
        self.assertEqual(self.time.get(Decimal(0.00)), timedelta(seconds=0))
        self.assertEqual(self.time.get(Decimal(60.00)), timedelta(minutes=1))
        self.assertEqual(self.time.get(Decimal(3600.00)), timedelta(hours=1))

        with self.assertRaises(ValidationError):
            self.time.get(Decimal(-5.00))
            self.time.get(-5)
            self.time.get(True)
            
    def test_put(self):
        self.assertEqual(self.time.put(timedelta(seconds=5)), Decimal(5.00))
        self.assertEqual(self.time.put(timedelta(seconds=0)), Decimal(0.00))
        self.assertEqual(self.time.put(timedelta(minutes=1)), Decimal(60.00))
        self.assertEqual(self.time.put(timedelta(hours=1)), Decimal(3600.00))

        with self.assertRaises(ValidationError):
            self.time.put(timedelta(seconds=-5))
            self.time.put(-5)
            self.time.put(True)

    def test_add(self):
        # Timedelta as input
        self.assertEqual(self.time.add(timedelta(seconds=5), timedelta(seconds=3)), Decimal(8))
        self.assertEqual(self.time.add(timedelta(seconds=0), timedelta(seconds=0)), Decimal(0))
        self.assertEqual(self.time.add(timedelta(minutes=1), timedelta(seconds=0)), Decimal(60))
        self.assertEqual(self.time.add(timedelta(hours=1), timedelta(seconds=0)), Decimal(3600))
        self.assertEqual(self.time.add(timedelta(hours=1), timedelta(minutes=1)), Decimal(3660))

        with self.assertRaises(ValidationError):
            self.time.add(timedelta(seconds=-5), timedelta(seconds=3))
            self.time.add(timedelta(seconds=5), timedelta(seconds=-3))
            self.time.add(timedelta(seconds=-5), timedelta(seconds=-3))

        # Decimal as input
        self.assertEqual(self.time.add(Decimal(5), Decimal(3)), Decimal(8))
        self.assertEqual(self.time.add(Decimal(0), Decimal(0)), Decimal(0))
        self.assertEqual(self.time.add(Decimal(60), Decimal(0)), Decimal(60))
        self.assertEqual(self.time.add(Decimal(3600), Decimal(0)), Decimal(3600))
        self.assertEqual(self.time.add(Decimal(3600), Decimal(60)), Decimal(3660))

        with self.assertRaises(ValidationError):
            self.time.add(Decimal(-5), Decimal(3))
            self.time.add(Decimal(5), Decimal(-3))
            self.time.add(Decimal(-5), Decimal(-3))

        # Mixed input
        self.assertEqual(self.time.add(Decimal(5), timedelta(seconds=3)), Decimal(8))
        self.assertEqual(self.time.add(timedelta(seconds=5), Decimal(3)), Decimal(8))

        with self.assertRaises(ValidationError):
            self.time.add(Decimal(-5), timedelta(seconds=3))
            self.time.add(timedelta(seconds=5), Decimal(-3))

    def test_subtract(self):
        # Timedelta as input
        self.assertEqual(self.time.subtract(timedelta(seconds=5), timedelta(seconds=3)), Decimal(2))
        self.assertEqual(self.time.subtract(timedelta(seconds=0), timedelta(seconds=0)), Decimal(0))
        self.assertEqual(self.time.subtract(timedelta(minutes=1), timedelta(seconds=0)), Decimal(60))
        self.assertEqual(self.time.subtract(timedelta(hours=1), timedelta(seconds=0)), Decimal(3600))
        self.assertEqual(self.time.subtract(timedelta(hours=1), timedelta(minutes=1)), Decimal(3540))

        with self.assertRaises(ValidationError):
            self.time.subtract(timedelta(seconds=5), timedelta(seconds=10))
            self.time.subtract(timedelta(seconds=-5), timedelta(seconds=3))
            self.time.subtract(timedelta(seconds=5), timedelta(seconds=-3))
            self.time.subtract(timedelta(seconds=-5), timedelta(seconds=-3))

        # Decimal as input
        self.assertEqual(self.time.subtract(Decimal(5), Decimal(3)), Decimal(2))
        self.assertEqual(self.time.subtract(Decimal(0), Decimal(0)), Decimal(0))
        self.assertEqual(self.time.subtract(Decimal(60), Decimal(0)), Decimal(60))
        self.assertEqual(self.time.subtract(Decimal(3600), Decimal(0)), Decimal(3600))
        self.assertEqual(self.time.subtract(Decimal(3600), Decimal(60)), Decimal(3540))

        with self.assertRaises(ValidationError):
            self.time.subtract(Decimal(5), Decimal(10))
            self.time.subtract(Decimal(-5), Decimal(3))
            self.time.subtract(Decimal(5), Decimal(-3))
            self.time.subtract(Decimal(-5), Decimal(-3))

        # Mixed input
        self.assertEqual(self.time.subtract(Decimal(5), timedelta(seconds=3)), Decimal(2))
        self.assertEqual(self.time.subtract(timedelta(seconds=5), Decimal(3)), Decimal(2))

        with self.assertRaises(ValidationError):
            self.time.subtract(Decimal(5), timedelta(seconds=10))
            self.time.subtract(timedelta(seconds=5), Decimal(-3))

    def test_time_sum(self):
        # Timedelta as input
        self.assertEqual(self.time.sum([timedelta(seconds=10), timedelta(seconds=20), timedelta(seconds=30)]), Decimal(60))
        self.assertEqual(self.time.sum([timedelta(seconds=10), timedelta(seconds=20)]), Decimal(30))
        self.assertEqual(self.time.sum([timedelta(seconds=10)]), Decimal(10))

        with self.assertRaises(ValidationError):
            self.time.sum([timedelta(seconds=10), timedelta(seconds=20), timedelta(seconds=-40)])


        # Decimal as input
        self.assertEqual(self.time.sum([Decimal(10), Decimal(20), Decimal(30)]), Decimal(60))
        self.assertEqual(self.time.sum([Decimal(10), Decimal(20)]), Decimal(30))
        self.assertEqual(self.time.sum([Decimal(10)]), Decimal(10))

        with self.assertRaises(ValidationError):
            self.time.sum([Decimal(10), Decimal(20), Decimal(-40)])

        # Mixed input
        self.assertEqual(self.time.sum([Decimal(10), timedelta(seconds=20), Decimal(30)]), Decimal(60))
        self.assertEqual(self.time.sum([timedelta(seconds=10), Decimal(20)]), Decimal(30))


class TestPercentage(unittest.TestCase):
    def setUp(self):
        self.percentage = Percentage()

    def test_get(self):
        self.assertEqual(self.percentage.get(Decimal(5.00)), Decimal(5.00))
        self.assertEqual(self.percentage.get(Decimal(0.00)), Decimal(0.00))
        self.assertEqual(self.percentage.get(Decimal(100.00)), Decimal(100.00))

        with self.assertRaises(ValidationError):
            self.percentage.get(Decimal(-5.00))
            self.percentage.get(-5)
            self.percentage.get(True)
            self.percentage.get(Decimal(101.00))

    def test_put(self):
        self.assertEqual(self.percentage.put(Decimal(5.00)), Decimal(5.00))
        self.assertEqual(self.percentage.put(Decimal(0.00)), Decimal(0.00))
        self.assertEqual(self.percentage.put(Decimal(100.00)), Decimal(100.00))

        with self.assertRaises(ValidationError):
            self.percentage.put(Decimal(-5.00))
            self.percentage.put(-5)
            self.percentage.put(True)
            self.percentage.put(Decimal(101.00))

    def test_add(self):
        self.assertEqual(self.percentage.add(Decimal(5.00), Decimal(3.00)), Decimal(8.00))
        self.assertEqual(self.percentage.add(Decimal(0.00), Decimal(0.00)), Decimal(0.00))
        self.assertEqual(self.percentage.add(Decimal(100.00), Decimal(0.00)), Decimal(100.00))

        with self.assertRaises(ValidationError):
            self.percentage.add(Decimal(-5.00), Decimal(3.00))
            self.percentage.add(Decimal(5.00), Decimal(-3.00))
            self.percentage.add(Decimal(-5.00), Decimal(-3.00))
            self.percentage.add(Decimal(95.00), Decimal(10.00)) # 95 + 10 = 105
            self.percentage.add(Decimal(101.00), Decimal(3.00))

    def test_subtract(self):
        self.assertEqual(self.percentage.subtract(Decimal(5.00), Decimal(3.00)), Decimal(2.00))
        self.assertEqual(self.percentage.subtract(Decimal(0.00), Decimal(0.00)), Decimal(0.00))
        self.assertEqual(self.percentage.subtract(Decimal(100.00), Decimal(0.00)), Decimal(100.00))

        with self.assertRaises(ValidationError):
            self.percentage.subtract(Decimal(5.00), Decimal(10.00))
            self.percentage.subtract(Decimal(-5.00), Decimal(3.00))
            self.percentage.subtract(Decimal(5.00), Decimal(-3.00))
            self.percentage.subtract(Decimal(-5.00), Decimal(-3.00))
            self.percentage.subtract(Decimal(101.00), Decimal(3.00))

    def test_percentage_sum(self):
        result = self.percentage.sum([Decimal(10.5), Decimal(20.5), Decimal(30.5)])
        self.assertEqual(result, Decimal(61.5))

        with self.assertRaises(ValidationError):
            self.percentage.sum([Decimal(10.5), Decimal(20.5), Decimal(30.5), Decimal(99)])
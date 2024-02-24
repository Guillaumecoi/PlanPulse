import unittest
from django.test import TestCase
from datetime import timedelta
from decimal import Decimal
from course.models.progressmetric import ProgressMetrics
from course.models.metric import Number, Time, Boolean, Percentage

class ProgressMetricsTest(TestCase):
    def setUp(self):
        self.progress_metric_number = ProgressMetrics(name='Test Metric', metric_type='number')
        self.progress_metric_time = ProgressMetrics(name='Test Metric', metric_type='time')
        self.progress_metric_boolean = ProgressMetrics(name='Test Metric', metric_type='boolean')
        self.progress_metric_percentage = ProgressMetrics(name='Test Metric', metric_type='percentage')

    def test_getMetric(self):
        self.assertIsInstance(self.progress_metric_number.getMetric(), Number)
        self.assertIsInstance(self.progress_metric_time.getMetric(), Time)
        self.assertIsInstance(self.progress_metric_boolean.getMetric(), Boolean)
        self.assertIsInstance(self.progress_metric_percentage.getMetric(), Percentage)

    def test_get_correct(self):
        self.assertEqual(self.progress_metric_number.get(Decimal(5.00)), 5)
        self.assertEqual(self.progress_metric_time.get(Decimal(5.00)), timedelta(seconds=5))
        self.assertEqual(self.progress_metric_boolean.get(1), True)
        self.assertEqual(self.progress_metric_percentage.get(Decimal(5.00)), Decimal(5.00))

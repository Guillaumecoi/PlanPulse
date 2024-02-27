import unittest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from course.models.progressmetric import AchievementChange, ProgressMetrics, CourseMetrics, AchievementMetric, InstanceMetric, InstanceAchievement, StudySession
from course.models.metric import Number, Time, Boolean, Percentage
from course.models.course import Course, Chapter

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

    def test_get_incorrect(self):
        with self.assertRaises(ValidationError):
            self.progress_metric_number.get(Decimal(-5.00))
            self.progress_metric_time.get(Decimal(-5.00))
            self.progress_metric_boolean.get(5)
            self.progress_metric_percentage.get(Decimal(-5.00))

    def test_put_correct(self):
        self.assertEqual(self.progress_metric_number.put(5), 5)
        self.assertEqual(self.progress_metric_time.put(timedelta(seconds=5)), Decimal(5.00))
        self.assertEqual(self.progress_metric_boolean.put(True), 1)
        self.assertEqual(self.progress_metric_percentage.put(Decimal(5.00)), Decimal(5.00))

    def test_put_incorrect(self):
        with self.assertRaises(ValidationError):
            self.progress_metric_number.put(-5)
            self.progress_metric_time.put(timedelta(seconds=-5))
            self.progress_metric_boolean.put(5)
            self.progress_metric_percentage.put(Decimal(-5.00))

    def test_add_correct(self):
        self.assertEqual(self.progress_metric_number.add(2, 3), 5)
        self.assertEqual(self.progress_metric_time.add(timedelta(seconds=2), timedelta(seconds=3)), timedelta(seconds=5))
        self.assertEqual(self.progress_metric_percentage.add(Decimal(2.00), Decimal(3.00)), Decimal(5.00))

    def test_add_incorrect(self):
        with self.assertRaises(ValidationError):
            self.progress_metric_number.add(-2, 3)
            self.progress_metric_time.add(timedelta(seconds=-2), timedelta(seconds=3))
            self.progress_metric_boolean.add(True, False)
            self.progress_metric_percentage.add(Decimal(-2.00), Decimal(3.00))

    def test_subtract_correct(self):
        self.assertEqual(self.progress_metric_number.subtract(5, 3), 2)
        self.assertEqual(self.progress_metric_time.subtract(timedelta(seconds=5), timedelta(seconds=3)), timedelta(seconds=2))
        self.assertEqual(self.progress_metric_percentage.subtract(Decimal(5.00), Decimal(3.00)), Decimal(2.00))

    def test_subtract_incorrect(self):
        with self.assertRaises(ValidationError):
            self.progress_metric_number.subtract(-5, 3)
            self.progress_metric_time.subtract(timedelta(seconds=-5), timedelta(seconds=3))
            self.progress_metric_boolean.subtract(True, False)
            self.progress_metric_percentage.subtract(Decimal(-5.00), Decimal(3.00))
            

class CourseMetricsTest(TestCase):
    def setUp(self):
        self.progress_metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), title='Test Course')
        self.course_metric = CourseMetrics.objects.create(course=self.course, metric=self.progress_metric)

    def test_str(self):
        self.assertEqual(str(self.course_metric), 'Test Course - Pages')

    def test_clean_negative_metric_max(self):
        self.course_metric.metric_max = -5
        with self.assertRaises(ValidationError):
            self.course_metric.save()
            self.course_metric.full_clean()


class AchievementMetricTest(TestCase):
    def setUp(self):
        self.progress_metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), title='Test Course')
        self.course_metric = CourseMetrics.objects.create(course=self.course, metric=self.progress_metric)
        self.achievement_level = AchievementMetric.objects.create(course_metric=self.course_metric, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))

    def test_str(self):
        self.assertEqual(str(self.achievement_level), 'Test Course - Pages Done')

    def test_clean_negative_weight(self):
        self.achievement_level.weight = -5
        with self.assertRaises(ValidationError):
            self.achievement_level.full_clean()

    def test_clean_over_100_weight(self):
        self.achievement_level.weight = 101
        with self.assertRaises(ValidationError):
            self.achievement_level.full_clean()

    def test_clean_negative_time_estimate(self):
        self.achievement_level.time_estimate = timedelta(minutes=-1)
        with self.assertRaises(ValidationError):
            self.achievement_level.full_clean()

    def test_clean_negative_value(self):
        self.achievement_level.value = -5
        with self.assertRaises(ValidationError):
            self.achievement_level.full_clean()

    def test_clean_value_exceeds_max(self):
        self.achievement_level.value = 15
        with self.assertRaises(ValidationError):
            self.achievement_level.clean()

class InstanceMetricTest(TestCase):
    def setUp(self):
        self.progress_metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), title='Test Course')
        self.chapter = Chapter.objects.create(course=self.course, title='Test Chapter')
        self.course_metric = CourseMetrics.objects.create(course=self.course, metric=self.progress_metric)
        self.content_type = ContentType.objects.get_for_model(self.chapter)
        self.progress_instance = InstanceMetric.objects.create(content_type=self.content_type, object_id=self.chapter.id, course_metric=self.course_metric, metric_max=10)
    
    def test_str(self):
        self.assertEqual(str(self.progress_instance), 'Test Course - Test Chapter - Pages: 10')

    def test_clean_negative_metric_max(self):
        self.progress_instance.metric_max = -5
        with self.assertRaises(ValidationError):
            self.progress_instance.full_clean()

    def test_metric_max_update(self):
        # Save the initial metric_max of course_metric
        self.course_metric.refresh_from_db()
        initial_metric_max = self.course_metric.metric_max
        # Check if the metric_max has been updated to 10
        self.assertEqual(initial_metric_max, 10)

        # Increase the metric_max of progress_instance and save it
        self.progress_instance.metric_max += 10
        self.progress_instance.save()

        # Reload course_metric from the database
        self.course_metric.refresh_from_db()

        # Check if course_metric.metric_max has been increased by the same amount
        self.assertEqual(self.course_metric.metric_max, 20)

        self.progress_instance.metric_max -= 15
        self.progress_instance.save()
        self.course_metric.refresh_from_db()

        self.assertEqual(self.course_metric.metric_max, 5)

    def test_metric_max_update_with_none(self):
        # Save the initial metric_max of course_metric
        self.course_metric.refresh_from_db()
        initial_metric_max = self.course_metric.metric_max
        # Check if the metric_max has been updated to 10
        self.assertEqual(initial_metric_max, 10)

        # Increase the metric_max of progress_instance and save it
        self.progress_instance.metric_max = None
        self.progress_instance.save()

        # Reload course_metric from the database
        self.course_metric.refresh_from_db()

        # Check if course_metric.metric_max has been increased by the same amount
        self.assertEqual(self.course_metric.metric_max, 0)

    def test_metric_max_update_with_multiple_instances(self):
        # create a second chapter
        chapter2 = Chapter.objects.create(course=self.course, title='Test Chapter 2')
        content_type2 = ContentType.objects.get_for_model(chapter2)
        progress_instance2 = InstanceMetric.objects.create(content_type=content_type2, object_id=chapter2.id, course_metric=self.course_metric, metric_max=20)

        self.course_metric.refresh_from_db()
        initial_metric_max = self.course_metric.metric_max
        # Check if the metric_max has been updated to 10
        self.assertEqual(initial_metric_max, 30)

        # Change the metric_max of both progress_instances and save it
        self.progress_instance.metric_max += 10
        progress_instance2.metric_max -= 5
        self.progress_instance.save()
        progress_instance2.save()

        self.course_metric.refresh_from_db()
        self.assertEqual(self.course_metric.metric_max, 35)

class InstanceAchievementTest(TestCase):
    def setUp(self):
        self.progress_metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), title='Test Course')
        self.chapter = Chapter.objects.create(course=self.course, title='Test Chapter')
        self.course_metric = CourseMetrics.objects.create(course=self.course, metric=self.progress_metric)
        self.content_type = ContentType.objects.get_for_model(self.chapter)
        self.progress_instance = InstanceMetric.objects.create(content_type=self.content_type, object_id=self.chapter.id, course_metric=self.course_metric, metric_max=10)
        self.achievement_metric = AchievementMetric.objects.create(course_metric=self.course_metric, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))
        self.achievement = InstanceAchievement.objects.create(progress_instance=self.progress_instance, achievement_metric=self.achievement_metric, value=5, achieved_at=None)

    def test_str(self):
        self.assertEqual(str(self.achievement), 'Test Course - Test Chapter - 5/10 Pages Done')

    def test_clean_value_exceeds_max(self):
        self.achievement.value = 15
        with self.assertRaises(ValidationError):
            self.achievement.clean()

    def test_clean_value_negative(self):
        self.achievement.value = -5
        with self.assertRaises(ValidationError):
            self.achievement.full_clean()

    def test_clean_different_course_metric(self):
        course_metric2 = CourseMetrics.objects.create(course=self.course, metric=ProgressMetrics.objects.create(name='Slides', metric_type='number'))
        achievement_metric2 = AchievementMetric.objects.create(course_metric=course_metric2, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))
        self.achievement.achievement_metric = achievement_metric2
        with self.assertRaises(ValidationError):
            self.achievement.clean()

    def test_achievement_metric_update(self):
        # Save the initial value of achievement_metric
        self.achievement_metric.refresh_from_db()
        initial_value = self.achievement_metric.value
        # Check if the value has been updated to 5
        self.assertEqual(initial_value, 5)

        # Increase the value of achievement and save it
        self.achievement.value += 5
        self.achievement.save()

        # Reload achievement_metric from the database
        self.achievement_metric.refresh_from_db()

        # Check if achievement_metric.value has been increased by the same amount
        self.assertEqual(self.achievement_metric.value, 10)

        self.achievement.value -= 5
        self.achievement.save()
        self.achievement_metric.refresh_from_db()

        self.assertEqual(self.achievement_metric.value, 5)

    def test_achievement_metric_update_with_none(self):
        # Save the initial value of achievement_metric
        self.achievement_metric.refresh_from_db()
        initial_value = self.achievement_metric.value
        # Check if the value has been updated to 5
        self.assertEqual(initial_value, 5)

        # Increase the value of achievement and save it
        self.achievement.value = None
        self.achievement.save()

        # Reload achievement_metric from the database
        self.achievement_metric.refresh_from_db()

        # Check if achievement_metric.value has been increased by the same amount
        self.assertEqual(self.achievement_metric.value, 0)

    def test_achievement_metric_with_multiple_achievements(self):
        # create a second progress_instance
        chapter2 = Chapter.objects.create(course=self.course, title='Test Chapter 2')
        content_type2 = ContentType.objects.get_for_model(chapter2)
        progress_instance2 = InstanceMetric.objects.create(content_type=content_type2, object_id=chapter2.id, course_metric=self.course_metric, metric_max=20)
        achievement2 = InstanceAchievement.objects.create(progress_instance=progress_instance2, achievement_metric=self.achievement_metric, value=15, achieved_at=None)

        self.achievement_metric.refresh_from_db()
        initial_value = self.achievement_metric.value
        # Check if the value has been updated to 20
        self.assertEqual(initial_value, 20)


class AchievementChangeTest(TestCase):
    def setUp(self):
        self.progress_metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(user=self.user, title='Test Course')
        self.chapter = Chapter.objects.create(course=self.course, title='Test Chapter')
        self.course_metric = CourseMetrics.objects.create(course=self.course, metric=self.progress_metric)
        self.content_type = ContentType.objects.get_for_model(self.chapter)
        self.progress_instance = InstanceMetric.objects.create(content_type=self.content_type, object_id=self.chapter.id, course_metric=self.course_metric, metric_max=10)
        self.achievement_metric = AchievementMetric.objects.create(course_metric=self.course_metric, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))
        self.achievement = InstanceAchievement.objects.create(progress_instance=self.progress_instance, achievement_metric=self.achievement_metric)

        self.study_session = StudySession.objects.create(user=self.user, start_time=timezone.now(), end_time=timezone.now() + timedelta(minutes=30), time_spent=timedelta(minutes=30))
        self.achievement_change = AchievementChange.objects.create(instance_achievement=self.achievement, study_session=self.study_session, value=5)  

    def test_str(self):
        self.assertEqual(str(self.achievement_change), 'Test Course - Test Chapter - 5/10 Pages Done - 5')

    def test_clean_negative_value(self):
        self.achievement_change.value = -5
        with self.assertRaises(ValidationError):
            self.achievement_change.full_clean()

    def test_clean_different_user(self):
        user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.study_session.user = user2
        with self.assertRaises(ValidationError):
            self.achievement_change.clean()

    def test_update_achievement(self):
        # The value grows
        self.achievement_change.value = 10
        self.achievement_change.save()
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.value, 10)

        # The value decreases
        self.achievement_change.value = 3
        self.achievement_change.save()
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.value, 3)

        # The value becomes None
        self.achievement_change.value = None
        self.achievement_change.save()
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.value, 0)

    def test_delete(self):
        self.achievement_change.delete()
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.value, 0)

    
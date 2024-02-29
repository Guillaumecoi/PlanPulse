from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from course.models.progressmetric import CourseMetrics, AchievementMetric, InstanceMetric, InstanceAchievement
from course.models.metric import Number, Time, Boolean, Percentage
from course.models.course import Course, Chapter

          
class CourseMetricsTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), name='Test Course')
        self.course_metric = CourseMetrics.objects.create(course=self.course, name='Pages', metric_type='number')

    def test_str(self):
        self.assertEqual(str(self.course_metric), 'Test Course - Pages')

    def test_getMetric(self):
        # Arrange
        number_metric = CourseMetrics.objects.create(course=self.course, name='number', metric_type='number')
        time_metric = CourseMetrics.objects.create(course=self.course, name='time', metric_type='time')
        boolean_metric = CourseMetrics.objects.create(course=self.course, name='boolean', metric_type='boolean')
        percentage_metric = CourseMetrics.objects.create(course=self.course, name='percentage', metric_type='percentage')

        # Act & Assert
        self.assertIsInstance(number_metric.getMetric(), Number)
        self.assertIsInstance(time_metric.getMetric(), Time)
        self.assertIsInstance(boolean_metric.getMetric(), Boolean)
        self.assertIsInstance(percentage_metric.getMetric(), Percentage)


class AchievementMetricTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), name='Test Course')
        self.course_metric = CourseMetrics.objects.create(course=self.course, name='Pages', metric_type='number')
        self.achievement_metric = AchievementMetric.objects.create(course_metric=self.course_metric, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))

    def test_str(self):
        self.assertEqual(str(self.achievement_metric), 'Test Course - Pages Done')

    def test_clean_negative_weight(self):
        self.achievement_metric.weight = -5
        with self.assertRaises(ValidationError):
            self.achievement_metric.full_clean()

    def test_clean_over_100_weight(self):
        self.achievement_metric.weight = 101
        with self.assertRaises(ValidationError):
            self.achievement_metric.full_clean()

    def test_clean_negative_time_estimate(self):
        self.achievement_metric.time_estimate = timedelta(minutes=-1)
        with self.assertRaises(ValidationError):
            self.achievement_metric.full_clean()


class InstanceMetricTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), name='Test Course')
        self.chapter = Chapter.objects.create(course=self.course, name='Test Chapter')
        self.course_metric = CourseMetrics.objects.create(course=self.course, name='Pages', metric_type='number')
        self.content_type = ContentType.objects.get_for_model(self.chapter)
        self.progress_instance = InstanceMetric.objects.create(content_type=self.content_type, object_id=self.chapter.id, course_metric=self.course_metric, value=10)

    def test_clean_negative_value(self):
        self.progress_instance.value = -5
        with self.assertRaises(ValidationError):
            self.progress_instance.full_clean()

    def test_value_update(self):
        self.assertEqual(self.course_metric.get_total(), 10)

        # Increase the value of progress_instance and save it
        self.progress_instance.value += 10
        self.progress_instance.save()
        self.assertEqual(self.course_metric.get_total(), 20)

        self.progress_instance.value -= 15
        self.progress_instance.save()
        self.assertEqual(self.course_metric.get_total(), 5)

        # Increase the value of progress_instance and save it
        self.progress_instance.value = None
        self.progress_instance.save()
        self.assertEqual(self.course_metric.get_total(), 0)

    def test_value_update_with_multiple_instances(self):
        # create a second chapter
        chapter2 = Chapter.objects.create(course=self.course, name='Test Chapter 2')
        content_type2 = ContentType.objects.get_for_model(chapter2)
        progress_instance2 = InstanceMetric.objects.create(content_type=content_type2, object_id=chapter2.id, course_metric=self.course_metric, value=20)

        initial_value = self.course_metric.get_total()
        self.assertEqual(initial_value, 30)

        # Change the value of both progress_instances and save it
        self.progress_instance.value += 10
        progress_instance2.value -= 5
        self.progress_instance.save()
        progress_instance2.save()
        self.assertEqual(self.course_metric.get_total(), 35)

    def test_delete(self):
        self.progress_instance.delete()
        self.assertEqual(self.course_metric.get_total(), 0)

class InstanceAchievementTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(user=User.objects.create_user(username='testuser', password='testpassword'), name='Test Course')
        self.chapter = Chapter.objects.create(course=self.course, name='Test Chapter')
        self.course_metric = CourseMetrics.objects.create(course=self.course, name='Pages', metric_type='number')
        self.content_type = ContentType.objects.get_for_model(self.chapter)
        self.progress_instance = InstanceMetric.objects.create(content_type=self.content_type, object_id=self.chapter.id, course_metric=self.course_metric, value=10)
        self.achievement_metric = AchievementMetric.objects.create(course_metric=self.course_metric, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))
        self.achievement = InstanceAchievement.objects.create(progress_instance=self.progress_instance, achievement_metric=self.achievement_metric, value=5, achieved_at=None)

    def test_clean_value_exceeds_max(self):
        self.achievement.value = 15
        with self.assertRaises(ValidationError):
            self.achievement.clean()

    def test_clean_value_negative(self):
        self.achievement.value = -5
        with self.assertRaises(ValidationError):
            self.achievement.full_clean()

    def test_clean_different_course_metric(self):
        course_metric2 = CourseMetrics.objects.create(course=self.course, name='Slides', metric_type='number')
        achievement_metric2 = AchievementMetric.objects.create(course_metric=course_metric2, achievement_level='Done', weight=1, time_estimate=timedelta(minutes=1))
        self.achievement.achievement_metric = achievement_metric2
        with self.assertRaises(ValidationError):
            self.achievement.clean()

    def test_achievement_metric_update(self):
        # Save the initial value of achievement_metric
        initial_value = self.achievement_metric.get_total()
        self.assertEqual(initial_value, 5)

        # Increase the value of achievement and save it
        self.achievement.value += 5
        self.achievement.save()
        self.assertEqual(self.achievement_metric.get_total(), 10)

        # Decrease the value of achievement and save it
        self.achievement.value -= 5
        self.achievement.save()
        self.assertEqual(self.achievement_metric.get_total(), 5)

        # Set the value of achievement to None and save it
        self.achievement.value = None
        self.achievement.save()
        self.assertEqual(self.achievement_metric.get_total(), 0)

    def test_achievement_metric_with_multiple_achievements(self):
        # create a second progress_instance
        chapter2 = Chapter.objects.create(course=self.course, name='Test Chapter 2')
        content_type2 = ContentType.objects.get_for_model(chapter2)
        progress_instance2 = InstanceMetric.objects.create(content_type=content_type2, object_id=chapter2.id, course_metric=self.course_metric, value=20)
        achievement2 = InstanceAchievement.objects.create(progress_instance=progress_instance2, achievement_metric=self.achievement_metric, value=15, achieved_at=None)

        initial_value = self.achievement_metric.get_total()
        self.assertEqual(initial_value, 20)

        # Change the value of both achievements and save it
        self.achievement.value += 5
        achievement2.value -= 10
        self.achievement.save()
        achievement2.save()
        self.assertEqual(self.achievement_metric.get_total(), 15)

    def test_delete(self):
        self.achievement.delete()
        self.assertEqual(self.achievement_metric.get_total(), 0)
    
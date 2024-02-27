from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from course.models.course import Course, Chapter
from course.models.progressmetric import ProgressMetrics, CourseMetrics

class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(user=self.user, title='Test Course')

    def test_modified_method(self):
        old_modified_date = self.course.date_modified
        self.course.modified()
        self.assertNotEqual(old_modified_date, self.course.date_modified)

    def test_has_access_method(self):
        self.assertTrue(self.course.has_access(self.user))
        self.assertFalse(self.course.has_access(User.objects.create_user(username='testuser2', password='testpassword')))

    def test_complete_method(self):
        self.course.complete()
        self.assertIsNotNone(self.course.date_completed)

    def test_add_metric(self):
        # Act
        self.course.add_metric('Pages', 'number', achievement_level='Done' , weigth=1, time_estimate=timedelta(hours=1))
        self.course.add_metric('Pages', 'number', achievement_level='Summarized', weigth=2, time_estimate=timedelta(hours=2))
        metric = ProgressMetrics.objects.get(name='Pages', metric_type='number')
        course_metric1 = CourseMetrics.objects.get(course=self.course, metric=metric, achievement_level='Done')
        course_metric2 = CourseMetrics.objects.get(course=self.course, metric=metric, achievement_level='Summarized')

        # Assert
        self.assertEqual(metric.name, 'Pages')
        self.assertEqual(metric.metric_type, 'number')

        self.assertEqual(course_metric1.course, self.course)
        self.assertEqual(course_metric1.metric, metric)
        self.assertEqual(course_metric1.achievement_level, 'Done')
        self.assertEqual(course_metric1.metric_value, 0)
        self.assertEqual(course_metric1.metric_max, 0)
        self.assertEqual(course_metric1.weigth, 1)
        self.assertEqual(course_metric1.time_estimate, timedelta(hours=1))

        self.assertEqual(course_metric2.course, self.course)
        self.assertEqual(course_metric2.metric, metric)
        self.assertEqual(course_metric2.achievement_level, 'Summarized')
        self.assertEqual(course_metric2.metric_value, 0)
        self.assertEqual(course_metric2.metric_max, 0)
        self.assertEqual(course_metric2.weigth, 2)
        self.assertEqual(course_metric2.time_estimate, timedelta(hours=2))


class ChapterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(user=self.user, title='Test Course')
        self.chapter = Chapter.objects.create(title='Test Chapter', course=self.course)

    def test_complete(self):
        # make sure the chapter is not completed
        self.assertIsNone(self.chapter.date_completed)

        # Act
        self.chapter.complete()

        # Assert
        self.assertIsNotNone(self.chapter.date_completed)

    def test_auto_increment_order(self):
        # Arrange
        course_increment = Course.objects.create(user=self.user, title='Test increment Course')

        # Act
        chapter1 = Chapter.objects.create(title='Chapter 1', course=course_increment)
        chapter2 = Chapter.objects.create(title='Chapter 2', course=course_increment)
        chapter3 = Chapter.objects.create(title='Chapter 3', course=course_increment)

        # Assert
        self.assertEqual(chapter1.order, 1)
        self.assertEqual(chapter2.order, 2)
        self.assertEqual(chapter3.order, 3)

    def test_auto_decrement_order(self):
        # Arrange
        course_dencrement = Course.objects.create(user=self.user, title='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(title='Chapter 1', course=course_dencrement)
        chapter2 = Chapter.objects.create(title='Chapter 2', course=course_dencrement)
        chapter3 = Chapter.objects.create(title='Chapter 3', course=course_dencrement)

        # Act
        chapter2.delete()
        chapter1.refresh_from_db()
        chapter3.refresh_from_db()

        # Assert
        self.assertEqual(chapter1.order, 1)
        self.assertEqual(chapter3.order, 2)

    def test_move_order_up(self):
        # Arrange
        course_move = Course.objects.create(user=self.user, title='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(title='Chapter 1', course=course_move)
        chapter2 = Chapter.objects.create(title='Chapter 2', course=course_move)
        chapter3 = Chapter.objects.create(title='Chapter 3', course=course_move)
        chapter4 = Chapter.objects.create(title='Chapter 4', course=course_move)

        # Act
        chapter3.move_order(1, save=True)
        chapter1.refresh_from_db()
        chapter2.refresh_from_db()
        chapter3.refresh_from_db()
        chapter4.refresh_from_db()

        # Assert
        self.assertEqual(chapter1.order, 2)
        self.assertEqual(chapter2.order, 3)
        self.assertEqual(chapter3.order, 1)
        self.assertEqual(chapter4.order, 4)

    def test_move_order_down(self):
        # Arrange
        course_move = Course.objects.create(user=self.user, title='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(title='Chapter 1', course=course_move)
        chapter2 = Chapter.objects.create(title='Chapter 2', course=course_move)
        chapter3 = Chapter.objects.create(title='Chapter 3', course=course_move)
        chapter4 = Chapter.objects.create(title='Chapter 4', course=course_move)

        # Act
        chapter1.move_order(3, save=True)
        chapter1.refresh_from_db()
        chapter2.refresh_from_db()
        chapter3.refresh_from_db()
        chapter4.refresh_from_db()

        # Assert
        self.assertEqual(chapter1.order, 3)
        self.assertEqual(chapter2.order, 1)
        self.assertEqual(chapter3.order, 2)
        self.assertEqual(chapter4.order, 4)

    def test_has_access(self):
        # Arrange
        no_access_user = User.objects.create_user(username='testuser1', password='testpassword')

        # Act
        self.assertTrue(self.chapter.has_access(self.user))
        self.assertFalse(self.chapter.has_access(no_access_user))

    def test_add_subchapter(self):
        # Act
        subchapter = self.chapter.add_subchapter('Subchapter 1')

        # Assert
        self.assertEqual(subchapter.title, 'Subchapter 1')
        self.assertEqual(subchapter.course, self.course)
        self.assertEqual(subchapter.parent_chapter, self.chapter)
        self.assertEqual(subchapter.order, 1)
        self.assertTrue(subchapter.is_numbered)


    def test_add_progressinstance(self):
        # Arrange
        metric = ProgressMetrics.objects.create(name='Pages', metric_type='number')
        course_metric = CourseMetrics.objects.create(course=self.course, metric=metric, achievement_level='Done')

        # Act
        progress_instance = self.chapter.add_progressinstance(course_metric, 15)

        # Assert
        self.assertEqual(progress_instance.content_object, self.chapter)
        self.assertEqual(progress_instance.course_metric, course_metric)
        self.assertEqual(progress_instance.metric_value, 0)
        self.assertEqual(progress_instance.metric_max, 15)


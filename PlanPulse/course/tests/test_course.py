from django.test import TestCase
from django.contrib.auth.models import User
from course.models.models import Course, Chapter

class CourseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(user=self.user, name='Test Course')

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


class ChapterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(user=self.user, name='Test Course')
        self.chapter = Chapter.objects.create(name='Test Chapter', course=self.course)

    def test_complete(self):
        # make sure the chapter is not completed
        self.assertIsNone(self.chapter.date_completed)

        # Act
        self.chapter.complete()

        # Assert
        self.assertIsNotNone(self.chapter.date_completed)

    def test_auto_increment_order(self):
        # Arrange
        course_increment = Course.objects.create(user=self.user, name='Test increment Course')

        # Act
        chapter1 = Chapter.objects.create(name='Chapter 1', course=course_increment)
        chapter2 = Chapter.objects.create(name='Chapter 2', course=course_increment)
        chapter3 = Chapter.objects.create(name='Chapter 3', course=course_increment)

        # Assert
        self.assertEqual(chapter1.order, 1)
        self.assertEqual(chapter2.order, 2)
        self.assertEqual(chapter3.order, 3)

    def test_auto_decrement_order(self):
        # Arrange
        course_dencrement = Course.objects.create(user=self.user, name='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(name='Chapter 1', course=course_dencrement)
        chapter2 = Chapter.objects.create(name='Chapter 2', course=course_dencrement)
        chapter3 = Chapter.objects.create(name='Chapter 3', course=course_dencrement)

        # Act
        chapter2.delete()
        chapter1.refresh_from_db()
        chapter3.refresh_from_db()

        # Assert
        self.assertEqual(chapter1.order, 1)
        self.assertEqual(chapter3.order, 2)

    def test_move_order_up(self):
        # Arrange
        course_move = Course.objects.create(user=self.user, name='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(name='Chapter 1', course=course_move)
        chapter2 = Chapter.objects.create(name='Chapter 2', course=course_move)
        chapter3 = Chapter.objects.create(name='Chapter 3', course=course_move)
        chapter4 = Chapter.objects.create(name='Chapter 4', course=course_move)

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
        course_move = Course.objects.create(user=self.user, name='Test increment Course')
        # Depends on auto_increment_order working
        chapter1 = Chapter.objects.create(name='Chapter 1', course=course_move)
        chapter2 = Chapter.objects.create(name='Chapter 2', course=course_move)
        chapter3 = Chapter.objects.create(name='Chapter 3', course=course_move)
        chapter4 = Chapter.objects.create(name='Chapter 4', course=course_move)

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
        self.assertEqual(subchapter.name, 'Subchapter 1')
        self.assertEqual(subchapter.course, self.course)
        self.assertEqual(subchapter.parent_chapter, self.chapter)
        self.assertEqual(subchapter.order, 1)
        self.assertTrue(subchapter.is_numbered)


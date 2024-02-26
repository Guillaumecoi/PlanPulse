import importlib
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.contrib.auth.models import User
from .interfaces import Trackable


class Course(Trackable):
    '''
    Model for a course
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    institution = models.CharField(null=True, blank=True, max_length=100)
    instructor = models.CharField(null=True, blank=True , max_length=100)
    description = models.TextField(null=True, blank=True)
    study_points = models.PositiveIntegerField(null=True, blank=True)

    # meta data
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['date_modified',]
        unique_together = ('user', 'title')

    def __str__(self):
        return self.title
    
    def complete(self):
        self.date_completed = timezone.now()
        self.save()
    
    def modified(self):
        self.date_modified = timezone.now()
        self.save()
        
    def has_access(self, user):
        return self.user == user
    
    def add_chapter(self, title, order=None, is_numbered=True):
        return Chapter.objects.get_or_create(course=self, title=title, order=order, is_numbered=is_numbered)

    def add_metric(self, metric_name, metric_type, achievement_level=None, weigth=None, time_estimate=None):
        # To avoid circular import
        ProgressMetrics = importlib.import_module('course.models.progressmetric').ProgressMetrics
        CourseMetrics = importlib.import_module('course.models.progressmetric').CourseMetrics
        # Create the metric
        metric, created = ProgressMetrics.objects.get_or_create(name=metric_name, metric_type=metric_type)
        return CourseMetrics.objects.get_or_create(course=self, metric=metric, achievement_level=achievement_level, metric_value=0, metric_max=0, weigth=weigth, time_estimate=time_estimate)


class Chapter(Trackable):
    '''
    Model for a chapter
    '''
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    parent_chapter = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_numbered = models.BooleanField(default=True)
    content = models.TextField(null=True, blank=True)

    # meta data
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['order',]
        unique_together = ('course', 'parent_chapter', 'order')

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):        
        # auto increment order
        if self._state.adding:
            self.auto_increment_order(None)
                
        # Update the course's date_modified
        self.course.modified()
        super().save(*args, **kwargs)

    def complete(self):
        self.date_completed = timezone.now()
        self.save()

    def delete(self, *args, **kwargs):
        # Decrement the order of chapters with a bigger order
        self.auto_decrement_order(None)
        super().delete(*args, **kwargs)

    def modified(self):
        self.date_modified = timezone.now()
        self.course.modified()
        self.save()

    def auto_increment_order(self, new_order):
        if new_order is None:
            max_order = Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter).aggregate(models.Max('order'))['order__max']
            if max_order is not None:
                self.order = max_order + 1
        else:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gte=new_order, order__lt=self.order).update(order=models.F('order') + 1)
            
    def auto_decrement_order(self, new_order):
        if new_order is None:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gt=self.order).update(order=models.F('order') - 1)
        else:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gt=self.order, order__lte=new_order).update(order=models.F('order') - 1)
        
    def move_order(self, new_order):
        current_order = self.order

        if new_order == current_order:
            return

        if new_order < current_order:
            self.auto_increment_order(new_order)
        else:
            self.auto_decrement_order(new_order)

        self.order = new_order
        self.save()

    def add_subchapter(self, title, order=None, is_numbered=True):
        return Chapter.objects.get_or_create(course=self.course, title=title, parent_chapter=self, order=order, is_numbered=is_numbered)
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel

class Trackable(PolymorphicModel):
    '''
    Base model for trackable objects
    '''
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    # Meta data
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True

    def complete(self):
        self.date_completed = timezone.now()
        self.save()
    
    def modified(self):
        self.date_modified = timezone.now()
        self.save()


class Course(Trackable):
    '''
    Model for a course
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.CharField(null=True, blank=True, max_length=100)
    instructor = models.CharField(null=True, blank=True , max_length=100)
    study_points = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['date_modified',]
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name
        
    def has_access(self, user):
        return self.user == user
    
    def add_chapter(self, name, is_numbered=True):
        return Chapter.objects.get_or_create(course=self, name=name, is_numbered=is_numbered)


class Chapter(Trackable):
    '''
    Model for a chapter
    '''
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    parent_chapter = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_numbered = models.BooleanField(default=True)

    class Meta:
        ordering = ['order',]
        unique_together = ('course', 'parent_chapter', 'order')

    def __str__(self):
        return f"{self.course.name} - {self.name}"
    
    def save(self, *args, **kwargs):        
        # auto increment order
        if not self.pk:
            self.auto_increment_order(None)           
        super().save(*args, **kwargs)
        self.course.modified()  # Update the course modified date

    def delete(self, *args, **kwargs):
        # Decrement the order of chapters with a bigger order
        self.auto_decrement_order(None)
        self.order = None
        super().delete(*args, **kwargs)

    def auto_increment_order(self, new_order):
        if new_order is None:
            self.order = self.get_max_order() + 1
        else:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gte=new_order, order__lt=self.order).update(order=models.F('order') + 1)
            
    def auto_decrement_order(self, new_order):
        if new_order is None:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gt=self.order).update(order=models.F('order') - 1)
        else:
            Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter, order__gt=self.order, order__lte=new_order).update(order=models.F('order') - 1)
        
    def move_order(self, new_order, save=False):
        current_order = self.order

        if new_order == current_order:
            return

        if new_order < current_order:
            self.auto_increment_order(new_order)
        else:
            self.auto_decrement_order(new_order)

        self.order = new_order
        if save:
            self.save()

    def get_max_order(self):
        max_order = Chapter.objects.filter(course=self.course, parent_chapter=self.parent_chapter).aggregate(models.Max('order'))['order__max']
        if max_order is None:
            max_order = 0
        return max_order

    def has_access(self, user):
        return self.course.has_access(user)

    def add_subchapter(self, name, is_numbered=True):
        return Chapter.objects.create(course=self.course, name=name, parent_chapter=self, is_numbered=is_numbered)
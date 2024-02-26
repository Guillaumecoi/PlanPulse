from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from .course import Course
from .metric import Metric, Number, Time, Boolean, Percentage

class ProgressMetrics(models.Model):
    '''
    Standard metrics for tracking progress in a course
    '''
    TYPE_CHOICES = (
        ('number', 'Number'),
        ('time', 'Time'),
        ('boolean', 'Boolean'),
        ('percentage', 'Percentage'),
    )
    name = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def getMetric(self):
        '''
        Returns the metric object
        '''
        metric_class = {
            'number': Number,
            'time': Time,
            'boolean': Boolean,
            'percentage': Percentage,
        }.get(self.metric_type, Metric)  # Fallback to the base Metric class, which raises NotImplementedError
    
        return metric_class()

    def get(self, value):
        '''
        Gets the data for the metric
        '''
        return self.getMetric().get(value)

    def put(self, value):
        '''
        Puts the data for the metric
        '''
        return self.getMetric().put(value)
        
    def add(self, value1, value2):
        '''
        Adds the data to the metric
        '''
        return self.getMetric().add(value1, value2)
    
    def subtract(self, value1, value2):
        '''
        Subtracts the data from the metric
        '''
        return self.getMetric().subtract(value1, value2)

    def __str__(self):
        return self.name


class CourseMetrics(models.Model):
    '''
    Tracks the progress of a user in a course using a specific metric
    '''
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    metric = models.ForeignKey(ProgressMetrics, on_delete=models.CASCADE)
    metric_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metric_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weigth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    time_estimate = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ('course', 'metric')

    def __str__(self):
        return f"{self.course.name} - {self.metric.name}"
    
    def save(self, *args, **kwargs):
        self.course.modified()
        super().save(*args, **kwargs)


class ProgressInstance(models.Model):
    '''
    Tracks the progress of a user in a specific instance (e.g., course, chapter) using a specific metric
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Reference to the content type shoud be a trackable object
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user_course_metric = models.ForeignKey(CourseMetrics, on_delete=models.CASCADE)
    metric_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metric_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    time_estimate = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user_course_metric')

    def __str__(self):
        # Adjust the string representation as needed
        return f"{self.content_object} progress - {self.user_course_metric.metric.name}: {self.metric_value}"

    def clean(self):
        # Your validation logic here, adjusted for the new structure
        pass

    def save(self, *args, **kwargs):
        # Adjust save method accordingly
        super().save(*args, **kwargs)


class StudySession(models.Model):
    '''
    Represents a study session, which can include progress on multiple instances (e.g., chapters, courses)
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you have a User model
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)  # Automatically calculated or manually entered

    # Optional: if you want to directly link study sessions to progress instances
    progress_instances = models.ManyToManyField(ProgressInstance, related_name='study_sessions', blank=True)

    def __str__(self):
        return f"Study Session for {self.user.username} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if self.end_time:
            self.time_spent = self.end_time - self.start_time
        super().save(*args, **kwargs)


    
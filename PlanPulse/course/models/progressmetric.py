from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.forms import ValidationError
from datetime import timedelta
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
    metric_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='number', editable=False)

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
    metric_max = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('course', 'metric')

    def __str__(self):
        return f"{self.course.title} - {self.metric.name}"
    
    def clean(self):
        if self.metric_max != self.get_metric_max():
            raise ValidationError("The maximum metric value cannot be less than the sum of the metric values of the progress instances")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course.modified()

    def update_metric_max(self, value):
        '''
        Sets the maximum metric value
        '''
        self.metric_max = self.get_metric_max()
        self.save()

    def get_metric_max(self):
        return InstanceMetric.objects.filter(course_metric=self).aggregate(models.Sum('metric_max'))['metric_max__sum'] or 0


class AchievementMetric(models.Model):
    '''
    Tracks different achievement levels within a course metric.
    '''
    course_metric = models.ForeignKey(CourseMetrics, on_delete=models.CASCADE, related_name='achievement_levels')
    achievement_level = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(100)])
    time_estimate = models.DurationField(null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('course_metric', 'achievement_level')

    def __str__(self):
        return f"{self.course_metric} {self.achievement_level}"
    
    def clean(self):
        if self.value > self.course_metric.metric_max:
            raise ValidationError("The value cannot exceed the maximum metric value")
        
        if self.value != self.get_value():
            raise ValidationError("The value cannot be less than the sum of the values of the instance achievements")
        
        if self.time_estimate:
            if self.time_estimate < timedelta(0):
                raise ValidationError("The time estimate cannot be negative")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course_metric.course.modified()
        
    def update_value(self):
        self.value = self.get_value()
        self.save()

    def get_value(self):
        return InstanceAchievement.objects.filter(achievement_metric=self).aggregate(models.Sum('value'))['value__sum'] or 0


class InstanceMetric(models.Model):
    '''
    Tracks the progress of a user in a specific instance (e.g., course, chapter) using a specific metric
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Reference to the content type shoud be a trackable object
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    course_metric = models.ForeignKey(CourseMetrics, on_delete=models.CASCADE)
    metric_max = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('content_type', 'object_id', 'course_metric')

    def __str__(self):
        # Adjust the string representation as needed
        return f"{self.content_object} - {self.course_metric.metric.name}: {self.metric_max}"

    def save(self, *args, **kwargs):
        if self.metric_max is None:
            self.metric_max = 0

        # If this instance already exists, calculate the difference
        if self.pk:
            orig = InstanceMetric.objects.get(pk=self.pk)
            diff = self.metric_max - orig.metric_max

        else:
            diff = self.metric_max

        self.course_metric.metric_max += diff
        self.course_metric.save()

        super().save(*args, **kwargs)


class InstanceAchievement(models.Model):
    '''
    Tracks specific achievements or milestones within a progress instance.
    '''
    progress_instance = models.ForeignKey(InstanceMetric, on_delete=models.CASCADE, related_name='achievements')
    achievement_metric = models.ForeignKey(AchievementMetric, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    achieved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('progress_instance', 'achievement_metric')

    def __str__(self):
        return f"{self.progress_instance.content_object} - {self.value}/{self.progress_instance.metric_max} {self.progress_instance.course_metric.metric} {self.achievement_metric.achievement_level}"
    
    def clean(self):
        if self.value > self.progress_instance.metric_max:
            raise ValidationError("The value cannot exceed the maximum metric value")
        
        if self.progress_instance.course_metric != self.achievement_metric.course_metric:
            raise ValidationError("The achievement metric must belong to the same course metric as the progress instance")
    
    def save(self, *args, **kwargs):
        if self.value is None:
            self.value = 0

        # If this instance already exists, calculate the difference
        if self.pk:
            orig = InstanceAchievement.objects.get(pk=self.pk)
            diff = self.value - orig.value

        else:
            diff = self.value

        self.achievement_metric.value += diff
        self.achievement_metric.save()

        super().save(*args, **kwargs)


class AchievementChange(models.Model):
    '''
    Tracks changes in the value of an achievement for a specific study session
    '''
    study_session = models.ForeignKey('StudySession', on_delete=models.CASCADE)
    instance_achievement = models.ForeignKey('InstanceAchievement', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.instance_achievement} - {self.value}"
    
    def clean(self):
        if self.study_session.user != self.instance_achievement.achievement_metric.course_metric.course.user:
            raise ValidationError("The user of the study session must be the same as the user of the course")
    
    def save(self, *args, **kwargs):
        if self.value is None:
            self.value = 0
        # If this instance already exists, calculate the difference
        if self.pk:
            orig = InstanceAchievement.objects.get(pk=self.pk)
            diff = self.value - orig.value
        else:
            diff = self.value

        self.update_instance_achievement(diff)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.update_instance_achievement(-self.value)
        super().delete(*args, **kwargs)

    def update_instance_achievement(self, value_change):
        self.instance_achievement.value += value_change
        self.instance_achievement.save()


class StudySession(models.Model):
    '''
    Represents a study session, which can include progress on multiple instances/achievements
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)

    def clean(self):
        if self.end_time and self.start_time:
            if self.end_time < self.start_time:
                raise ValidationError("The end time cannot be earlier than the start time")
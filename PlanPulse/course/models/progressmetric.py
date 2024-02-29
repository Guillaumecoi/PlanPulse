from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.forms import ValidationError
from datetime import timedelta
from .course import Course
from .metric import Metric, Number, Time, Boolean, Percentage


class CourseMetrics(models.Model):
    '''
    Tracks the progress of a user in a course using a specific metric
    '''
    TYPE_CHOICES = (
        ('number', 'Number'),
        ('time', 'Time'),
        ('boolean', 'Boolean'),
        ('percentage', 'Percentage'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='number', editable=False)

    class Meta:
        unique_together = ('course', 'name')

    def __str__(self):
        return f"{self.course.title} - {self.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course.modified()

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
    
    def getTotal(self):
        '''
        Returns the total value of the metric
        '''
        return InstanceMetric.objects.filter(course_metric=self).aggregate(models.Sum('value'))['value__sum'] or 0
    
    def add_achievement_metric(self, achievement_level, weight, time_estimate=None, value=0):
        '''
        Adds a new achievement metric to the course metric
        '''
        return AchievementMetric.objects.create(course_metric=self, achievement_level=achievement_level, weight=weight, time_estimate=time_estimate)


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
        #TODO control based on the metric type
        return InstanceAchievement.objects.filter(achievement_metric=self).aggregate(models.Sum('value'))['value__sum'] or 0


class InstanceMetric(models.Model):
    '''
    Tracks the progress of a user in a specific instance (e.g., course, chapter) using a specific metric
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Reference to the content type shoud be a trackable object
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    course_metric = models.ForeignKey(CourseMetrics, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('content_type', 'object_id', 'course_metric')

    def save(self, *args, **kwargs):
        if self.value is None:
            self.value = 0
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

    def clean(self):
        if self.value > self.progress_instance.value:
            raise ValidationError("The value cannot exceed the maximum metric value")
        
        if self.progress_instance.course_metric != self.achievement_metric.course_metric:
            raise ValidationError("The achievement metric must belong to the same course metric as the progress instance")
    
    def save(self, *args, **kwargs):
        if self.value is None:
            self.value = 0
        super().save(*args, **kwargs)
        self.achievement_metric.update_value()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.achievement_metric.update_value()

    def update_value(self):
        values = list(AchievementChange.objects.filter(instance_achievement=self).values_list('value', flat=True))
        self.value = values  #TODO control based on the metric type
        self.save()

    def get_metric(self):
        return self.progress_instance.course_metric.getMetric()


class AchievementChange(models.Model):
    '''
    Tracks changes in the value of an achievement for a specific study session
    '''
    study_session = models.ForeignKey('StudySession', on_delete=models.CASCADE)
    instance_achievement = models.ForeignKey('InstanceAchievement', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    def clean(self):
        if self.study_session.user != self.instance_achievement.achievement_metric.course_metric.course.user:
            raise ValidationError("The user of the study session must be the same as the user of the course")
    
    def save(self, *args, **kwargs):
        if self.value is None:
            self.value = 0
        super().save(*args, **kwargs)
        self.instance_achievement.update_value()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.instance_achievement.update_value()


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
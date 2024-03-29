from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.forms import ValidationError
from datetime import timedelta
from ..models.models import Course, Trackable
from .metric import Metric, Number, Time, Boolean, Percentage


class CourseMetric(models.Model):
    '''
    Tracks the progress of a user in a course using a specific metric
    '''
    TYPE_CHOICES = (
        ('number', 'Number'),
        ('time', 'Time'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='number', editable=False)

    class Meta:
        unique_together = ('course', 'name')

    def __str__(self):
        return f"{self.course.name} - {self.name}"
    
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
        }.get(self.metric_type, Metric)  # Fallback to the base Metric class, which raises NotImplementedError
    
        return metric_class()
    
    def get_total(self):
        '''
        Returns the total value of the metric
        '''
        instances = InstanceMetric.objects.filter(course_metric=self).values_list('value', flat=True)
        return self.getMetric().sum(instances)
        
    def add_achievement_metric(self, achievement_level, weight, time_estimate=None, value=0):
        '''
        Adds a new achievement metric to the course metric
        '''
        return AchievementMetric.objects.create(course_metric=self, achievement_level=achievement_level, weight=weight, time_estimate=time_estimate)


class AchievementMetric(models.Model):
    '''
    Tracks different achievement levels within a course metric.
    '''
    course_metric = models.ForeignKey(CourseMetric, on_delete=models.CASCADE, related_name='achievement_levels')
    achievement_level = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(100)])
    time_estimate = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ('course_metric', 'achievement_level')

    def __str__(self):
        return f"{self.course_metric} {self.achievement_level}"
    
    def clean(self):              
        if self.time_estimate:
            if self.time_estimate < timedelta(0):
                raise ValidationError("The time estimate cannot be negative")

    def get_total(self):
        achievements = Achievement.objects.filter(achievement_metric=self).values_list('value', flat=True)
        return self.get_metric().sum(achievements)
    
    def get_metric(self):
        return self.course_metric.getMetric()


class InstanceMetric(models.Model):
    '''
    Tracks the progress of a user in a specific instance (e.g., course, chapter) using a specific metric
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    course_metric = models.ForeignKey(CourseMetric, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('content_type', 'object_id', 'course_metric')

    def clean(self):
        if self.value is None:
            self.value = 0

        # Validate that the content_object is an instance of a Trackable subclass
        if not isinstance(self.content_object, Trackable):
            raise ValidationError('Content object must be an instance of a Trackable subclass.')

    def save(self, *args, **kwargs):
        self.clean()           
        super().save(*args, **kwargs)


class Achievement(models.Model):
    '''
    Tracks specific achievements or milestones within a progress instance.
    '''
    progress_instance = models.ForeignKey(InstanceMetric, on_delete=models.CASCADE, related_name='achievements')
    achievement_metric = models.ForeignKey(AchievementMetric, on_delete=models.CASCADE)
    study_session = models.ForeignKey('StudySession', on_delete=models.CASCADE, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('progress_instance', 'achievement_metric', 'study_session')

    def clean(self):  
        if self.value is None:
            self.value = 0
     
        if self.progress_instance.course_metric != self.achievement_metric.course_metric:
            raise ValidationError("The achievement metric must belong to the same course metric as the progress instance")
        
        if self.study_session:
            if self.study_session.user != self.progress_instance.course_metric.course.user:
                raise ValidationError("The study session must belong to the same user as the progress instance")

        instance_Achievements = (Achievement.objects  # Sum of all achievements for the same progress instance excluding the current one
                                 .filter(progress_instance=self.progress_instance)
                                 .exclude(id=self.id)
                                 .aggregate(models.Sum('value'))['value__sum'] or 0)
        instance_Achievements += self.value  # Add the current achievement value

        if self.progress_instance.value < instance_Achievements:
            raise ValidationError("The sum of the achievement values cannot exceed the progress instance value")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_metric(self):
        return self.progress_instance.course_metric.getMetric()


class StudySession(models.Model):
    '''
    Represents a study session, which can include progress on multiple instances/achievements
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def clean(self):
        if self.duration:
            if self.duration < timedelta(0):
                raise ValidationError("The time spent cannot be negative")
            
        if self.end_time and self.start_time:
            if self.end_time < self.start_time:
                raise ValidationError("The end time cannot be earlier than the start time")
                 
        if self.duration and self.end_time and self.start_time:
            if self.duration > self.end_time - self.start_time:
                raise ValidationError("The time spent cannot exceed the difference between the end and start time")
            
        if self.start_time or self.end_time:
            if not self.end_time or not self.start_time:
                raise ValidationError("Both start and end time or neither must be set")
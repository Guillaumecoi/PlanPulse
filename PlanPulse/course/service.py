from django.contrib.contenttypes.models import ContentType
from .models.course import Course, Chapter
from .models.progressmetric import CourseMetric, AchievementMetric, InstanceMetric, Achievement, StudySession

def create_course(user, name, description, institution, instructor, study_points):
    return Course.objects.create(user=user, name=name, description=description, institution=institution, instructor=instructor, study_points=study_points)

def create_course_metric(course, name, metric_type):
    return CourseMetric.objects.create(course=course, name=name, metric_type=metric_type)

def create_instance_metric(course_metric, value, object):
    content_object = ContentType.objects.get_for_model(object)
    return InstanceMetric.objects.create(course_metric=course_metric, value=value, content_object=content_object)

def create_study_session(user, start_time, end_time, duration):
    return StudySession.objects.create(user=user, start_time=start_time, end_time=end_time, duration=duration)

def create_achievement(course_metric, achievement_level, weight, time_estimate):
    return AchievementMetric.objects.create(course_metric=course_metric, achievement_level=achievement_level, weight=weight, time_estimate=time_estimate)




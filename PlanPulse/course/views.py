from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course


class CreateCourseView(CreateView):
    '''
    View for creating a course
    '''
    model = Course
    fields = ['name', 'description', 'institution', 'instructor', 'study_points']
    template_name = 'course/create_course.html'
    success_url = reverse_lazy('course:course_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Course'
        return context
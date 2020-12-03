# django imports
from django.contrib import admin
from courses.models import Subject, Course, Module

# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    '''
        this class inherit ModelAdmin class to register and display model on admin panel
    '''
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
    '''
        This class inherit the StackedInline class to add the modules of any
        course on the same page on admin panel.
    '''
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    '''
        this class inherit ModelAdmin class to register and display model on admin panel
    '''
    list_display = ['title', 'subject', 'created_at']
    fields = ['owner','subject',('title', 'slug'),'overview']

    # admin can be filter data with these two fields
    list_filter = ['created_at', 'subject']

    # to search any any field with title or overview
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}

    # to add modules of the courses on admin panel of courses.
    inlines = [ModuleInline]

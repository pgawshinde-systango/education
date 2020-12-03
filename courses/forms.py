from django import forms
from django.forms.models import inlineformset_factory


from courses.models import Course, Module

'''
    to save multiple form in one take we use inlineformset.
    here course model is parent model and module model is child
    its syntax is parent model followed by course model.
    then what are the fields to diplay and how many extra forms.
'''
ModuleFormSet = inlineformset_factory(Course,Module,
                                      fields=['title','description'],
                                      extra=2,
                                      can_delete=True)

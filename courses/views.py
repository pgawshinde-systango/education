# django imports
from django.apps import apps
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.contrib.auth import authenticate,login,logout
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin,\
                                        PermissionRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView,\
                                    DetailView, ListView, DeleteView, View

# Local imports
from courses.forms import ModuleFormSet
from students.forms import CourseEnrollForm
from courses.models import Course, Module, Content, Subject

#third party import
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


class OwnerMixin(object):

    def get_queryset(self):
        '''
            override the get_queryset() method of the view to retrieve only courses
            created by the current user.
        '''
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):

    def form_valid(self, form):
        '''
            override form validate method used by other view to validate forms
        '''
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    '''
        PermissionRequiredMixin checks that the user accessing the view has the
        permission specified in the permission_required attribute. Views are
        now only accessible to users with proper permissions.
    '''

    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    '''
        this class will generate form and perform form validations.
    '''
    template_name = 'courses/course_form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    '''
        This class will manage the list of courses.
    '''
    template_name = 'courses/course_list.html'

    #check user have permission or not to access this view
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    '''
        This class is use to create the courses.
    '''

    #check user have permission or not to access this view
    permission_required = 'courses.add_course'
    pass


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    '''
        This class is use to update the courses.
    '''

    #check user have permission or not to access this view
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    '''
        This class is used to delete the courses.
    '''
    template_name = 'courses/course_delete.html'

    #check user have permission or not to access this view
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    '''
        this class is used to update the course modules or create new ones.
    '''

    template_name = 'courses/course_formset.html'
    course = None

    def get_formset(self, data=None):
        '''
            to define a form.
        '''
        return ModuleFormSet(instance=self.course,data=data)

    def dispatch(self, request, pk):
        '''
            to fetch the course.
        '''
        self.course = get_object_or_404(Course,id=pk,owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    '''
        to create the content of module.
    '''
    module = None
    model = None
    obj = None
    template_name = 'courses/content_form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)

        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created_at', 'modified_at'])

        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)

        if id:
            self.obj = get_object_or_404(self.model, id=id,owner=request.user)

        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    '''
        to delete the content of the courses.
    '''
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    '''
        to display the list of module content.
    '''
    template_name = 'courses/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                    id=module_id,
                                    course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})



class CourseListView(TemplateResponseMixin, View):
    '''
        to list the course present in one subject and the modules
        present in particular course.
    '''
    model = Course
    template_name = 'courses/course_list_new.html'
    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})


class CourseDetailView(DetailView):
    '''
        detail view of course.
    '''
    model = Course
    template_name = 'courses/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context

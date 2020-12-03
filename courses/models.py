'''
    This file contains all the models of courses application
'''
# django imports
from django.db import models
from courses.fields import OrderField
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class Subject(models.Model):
    '''
        subject model to store all the subjects of this platform
    '''
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        '''
            meta class to provide info about outer class.
        '''
        ordering = ['title']

    def __str__(self):
        '''
            to print the title of the subject on admin panel
        '''
        return self.title


class Course(models.Model):
    '''
        course model to store the information about course owner and subjects
    '''
    # owner is the instructor who created this course.
    owner = models.ForeignKey(User,
                              related_name='courses_created',
                              on_delete=models.CASCADE)

    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        '''
            meta class to provide info about outer class.
        '''
        ordering = ['-created_at']

    def __str__(self):
        '''
            to print the title of the course on admin panel.
        '''
        return self.title


class Module(models.Model):
    '''
        module model to stroe the information about courses.
    '''
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        '''
            meta class is to provide the info about outer class.
        '''
        ordering = ['order']

    def __str__(self):
        '''
            to print the title of course on admin panel.
        '''
        return f'{self.order}. {self.title}'


class Content(models.Model):
    '''
        this model is used to point the other models content.
    '''
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                                        'text',
                                                        'video',
                                                        'image',
                                                        'file')})

    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        '''
            meta class is to provide the info about outer class.
        '''
        ordering = ['order']


class ItemBase(models.Model):
    '''
        this class is used to provide common fields to other classes.
        this is also an abstract class.
    '''
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)

    title = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        '''
            this abstract is equals to true means the outer class of
            this meta class is an abstract class.
        '''
        abstract = True

    def __str__(self):
        '''
            to print hte title of items on admin panel.
        '''
        return self.title

    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html',{'item': self})


class Text(ItemBase):
    '''
        this class inherit the fields of ItemBasem class
    '''
    content = models.TextField()


class File(ItemBase):
    '''
        this class inherit the fields of ItemBasem class
    '''
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    '''
        this class inherit the fields of ItemBasem class
    '''
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    '''
        this class inherit the fields of ItemBasem class
    '''
    url = models.URLField()

from django.contrib import admin
from base.models import *
from base.forms import AdvancedSearchForm
from django.forms.formsets import formset_factory
from django.db.models import Q
import re
from django.forms import Textarea, ModelChoiceField, ModelForm
from django.utils.translation import ugettext_lazy as _
from base.utils import update_display_fields
from mptt.admin import MPTTModelAdmin
from suit_ckeditor.widgets import CKEditorWidget
from mptt.forms import TreeNodeChoiceField
from django import forms
from django.contrib.admin.views.main import ChangeList
from django.utils.http import urlencode
from django.contrib import messages
from django.contrib.auth.models import User
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget

OPERATOR = (
    ('and', 'AND'),
    ('or', 'OR'),
)

SEARCH_TYPE = (
    ('icontains', 'contains'),
    ('not_icontains', 'does not contain'),
    ('exact', 'equals'),
    ('not_exact', 'does not equal'),
    ('blank', 'is blank'),
    ('not_blank', 'is not blank'),
    ('istartswith', 'starts with'),
    ('not_istartswith', 'does not start with'),
    ('iendswith', 'ends with'),
    ('not_iendswith', 'does not end with'),
    ('gt', 'is greater than'),
    ('gte', 'is greater than or equal to'),
    ('lt', 'is less than'),
    ('lte', 'is less than or equal to'),
)

CONTROL_SEARCH_TYPE = (
    ('exact', 'equals'),
    ('not_exact', 'does not equal'),
)

""" SPECIAL FORM FIELDS """
class LocationChoices(AutoModelSelect2Field):
    queryset = Location.objects
    search_fields = ['title__icontains',]

""" LIST FILTERS """

class ControlFieldTypeListFilter(admin.SimpleListFilter):
    """ Modified Descriptive Property filter that only includes Descriptive
    Properties marked as control_field = true """
    
    title = _('type')
    parameter_name = 'field_type'

    def lookups(self, request, model_admin):
        control_fields = tuple((prop.id, prop.property) for prop in DescriptiveProperty.objects.filter(control_field=True))
        return control_fields

    def queryset(self, request, queryset):
        if self.value():
            prop_id = self.value()
            return queryset.filter(type__id = prop_id)
            
""" FORMS """
        
class AdminAdvSearchForm(forms.Form):
    """ Used on the Subject Admin page to search objects by related Properties """
    
    # controlled properties
    cp1 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.filter(control_field = True))
    cst1 = forms.ChoiceField(label='', required=False, choices=CONTROL_SEARCH_TYPE)
    cv1 = forms.ChoiceField(label='', required=False, choices=(('default', 'Select a Property'),))
    cp2 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.filter(control_field = True))
    cst2 = forms.ChoiceField(label='', required=False, choices=CONTROL_SEARCH_TYPE)
    cv2 = forms.ChoiceField(label='', required=False, choices=(('default', 'Select a Property'),))
    cp3 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.filter(control_field = True))
    cst3 = forms.ChoiceField(label='', required=False, choices=CONTROL_SEARCH_TYPE)
    cv3 = forms.ChoiceField(label='', required=False, choices=(('default', 'Select a Property'),))     
    
    # free-form properties
    fp1 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.all())
    fst1 = forms.ChoiceField(label='', required=False, choices=SEARCH_TYPE)
    fv1 = forms.CharField(label='', required=False)
    op1 = forms.ChoiceField(label='', required=False, choices=OPERATOR)
    fp2 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.all())
    fst2 = forms.ChoiceField(label='', required=False, choices=SEARCH_TYPE)
    fv2 = forms.CharField(label='', required=False)
    op2 = forms.ChoiceField(label='', required=False, choices=OPERATOR)
    fp3 = forms.ModelChoiceField(label='', required=False, queryset=DescriptiveProperty.objects.all())
    fst3 = forms.ChoiceField(label='', required=False, choices=SEARCH_TYPE)
    fv3 = forms.CharField(label='', required=False)
    
    # filters
    loc = TreeNodeChoiceField(label='Context', required=False, queryset=Location.objects.all())
    img = forms.ChoiceField(label='Has Image', required=False, choices=(('default', '---'), ('yes', 'Yes'), ('no', 'No')))
    pub = forms.ModelChoiceField(label='Published', required=False, queryset=Media.objects.filter(type_id=2).order_by('title'))
    last_mod = forms.ModelChoiceField(label='Last Editor', required=False, queryset=User.objects.all())

class ControlFieldForm(ModelForm):
    """ Used on Control Field Change Form page to edit what is displayed on Control Field value public pages """
    
    class Meta:
  
        _ck_editor_toolbar = [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph',
             'groups': ['list', 'indent', 'blocks', 'align']},
            {'name': 'document', 'groups': ['mode']}, '/',
            {'name': 'styles'}, {'name': 'colors'},
            {'name': 'insert_custom',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule']},
            {'name': 'links'},
            {'name': 'about'}]

        _ck_editor_config = {'autoGrow_onStartup': True,
                             'autoGrow_minHeight': 100,
                             'autoGrow_maxHeight': 250,
                             'extraPlugins': 'autogrow',
                             'toolbarGroups': _ck_editor_toolbar}            
  
        widgets = {
            'notes': CKEditorWidget(editor_options=_ck_editor_config),
        }

class BlogPostForm(ModelForm):
    """ Used on Blog Post Change Form page to edit blog posts """
    
    class Meta:
  
        _ck_editor_toolbar = [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph',
             'groups': ['list', 'indent', 'blocks', 'align']},
            {'name': 'document', 'groups': ['mode']}, '/',
            {'name': 'styles'}, {'name': 'colors'},
            {'name': 'insert_custom',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule']},
            {'name': 'links'},
            {'name': 'about'}]

        _ck_editor_config = {'autoGrow_onStartup': True,
                             'autoGrow_minHeight': 100,
                             'autoGrow_maxHeight': 250,
                             'extraPlugins': 'autogrow',
                             'toolbarGroups': _ck_editor_toolbar}            
  
        widgets = {
            'body': CKEditorWidget(editor_options=_ck_editor_config),
        }

class LocObjRelForm(ModelForm):
    location = LocationChoices(
        label = Location._meta.verbose_name.capitalize(),
        widget = AutoHeavySelect2Widget(
            select2_options = {
                'width': '220px',
                'placeholder': 'Lookup %s ...' % Location._meta.verbose_name
            }
        )
    )

    class Meta:
        model = LocationSubjectRelations       

""" TABULAR INLINES """

""" LINKED DATA INLINES """

class ControlFieldLinkedDataInline(admin.TabularInline):
    model = ControlFieldLinkedData
    fields = ['source', 'link']    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    extra = 1
    
class PersonOrgLinkedDataInline(admin.TabularInline):
    model = PersonOrgLinkedData
    fields = ['source', 'link']    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    extra = 1    

""" DESCRIPTIVE PROPERTY & CONTROLLED PROPERTY INLINES """

""" PROPERTY VALUE INLINES """

class SubjectControlPropertyInline(admin.TabularInline):
    
    model = SubjectControlProperty
    fields = ['control_property', 'control_property_value', 'notes', 'last_mod_by'] 
    readonly_fields = ('last_mod_by',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_classes = 'suit-tab suit-tab-general'
    extra = 3
    template = 'admin/base/subject/tabular.html'
    ordering = ('control_property__order',)
    
    # for control property form dropdown, only show descriptive properties marked as control_field = true
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'control_property':
            kwargs["queryset"] = DescriptiveProperty.objects.filter(control_field = True)
        return super(SubjectControlPropertyInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

""" COLLECTION INLINES """

class SubjectCollectionInline(admin.TabularInline):
    model = SubjectCollection 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    extra = 1         

""" ADMINS """

""" LINKED DATA ADMIN """

class LinkedDataSourceAdmin(admin.ModelAdmin):    
    search_fields = ['title']
    list_display = ('title', 'link')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    
admin.site.register(LinkedDataSource, LinkedDataSourceAdmin)   
    
""" DESCRIPTIVE PROPERTY & CONTROLLED PROPERTY ADMIN """    
    
class ControlFieldAdmin(MPTTModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')    
    inlines = [ControlFieldLinkedDataInline]
    search_fields = ['title', 'definition']
    list_display = ('ancestors', 'title', 'definition', 'type')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    list_filter = (ControlFieldTypeListFilter,)
    list_display_links = ('title',)
    change_form_template = 'admin/base/change_form_tree_models.html'
    suit_form_includes = (
        ('admin/base/control_field_search.html', 'bottom'),
    )
    form = ControlFieldForm
    fields = ('title', 'definition', 'notes', 'type', 'parent', 'created', 'modified', 'last_mod_by')
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, ControlFieldLinkedData): #Check if it is the correct type of inline
                instance.last_mod_by = request.user            
                instance.save()
                
    # limit types visible on change form to descriptive properties marked as control_field = true
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs["queryset"] = DescriptiveProperty.objects.filter(control_field = True)
        return super(ControlFieldAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(ControlField, ControlFieldAdmin)

""" COLLECTION ADMIN """    
    
class CollectionAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified')    
    inlines = [SubjectCollectionInline]
    search_fields = ['title', 'notes']
    list_display = ('title', 'notes', 'owner')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }

admin.site.register(Collection, CollectionAdmin)

""" SITE SETTINGS ETC ADMIN """    
    
class ResultPropertyAdmin(admin.ModelAdmin):
    readonly_fields = ('display_field',)
    search_fields = ['display_field', 'field_type']
    list_display = ('human_title', 'field_type')
    list_editable = ('field_type',)

    def save_model(self, request, obj, form, change):
        subjects = Subject.objects.all()
        for subj in subjects:
            update_display_fields(subj.id, 'subj')    
    
admin.site.register(ResultProperty, ResultPropertyAdmin)

class StatusFilter(admin.SimpleListFilter):

    title = 'Status'
    
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        properties = tuple((prop.id, prop.property) for prop in DescriptiveProperty.objects.all())    
        return properties

    def queryset(self, request, queryset):
        if self.value():
            prop_id = self.value()
            return queryset.filter(subjectproperty__property = prop_id)

class SubjectPropertyInline(admin.TabularInline):
    model = SubjectProperty
    fields = ['property', 'property_value', 'notes', 'inline_notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    ordering = ('property__order',)
    suit_classes = 'suit-tab suit-tab-general'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'property':
            kwargs["queryset"] = DescriptiveProperty.objects.filter(Q(primary_type='SO') | Q(primary_type='AL') | Q(primary_type='SL')).exclude(control_field = True)
        return super(SubjectPropertyInline, self).formfield_for_foreignkey(db_field, request, **kwargs) 
        
class MediaSubjectRelationsInline(admin.TabularInline):
    model = MediaSubjectRelations
    fields = ['media', 'relation_type', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_classes = 'suit-tab suit-tab-general'
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'media':
            kwargs["queryset"] = Media.objects.filter(type__type = 'publication').order_by('title')
        elif db_field.name == 'relation_type':
            kwargs["queryset"] = Relations.objects.filter(Q(pk=2) | Q(pk=5))
        return super(MediaSubjectRelationsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def get_queryset(self, request):
        qs = super(MediaSubjectRelationsInline, self).get_queryset(request)
        return qs.filter(Q(relation_type=2) | Q(relation_type=5))

class LocationTreeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        level = obj.level
        padding = ''
        while (level > 0):
            padding = padding + '+--'
            level = level - 1
        return padding + obj.title
        
class LocationRelationAdminForm(ModelForm):
    location = LocationChoices(
        label = Location._meta.verbose_name.capitalize(),
        widget = AutoHeavySelect2Widget(
            select2_options = {
                'width': '220px',
                'placeholder': 'Lookup %s ...' % Location._meta.verbose_name
            }
        )
    )
    
    class Meta:
          model = LocationSubjectRelations
        
class LocationSubjectRelationsInline(admin.TabularInline):
    model = LocationSubjectRelations
    fields = ['location', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_classes = 'suit-tab suit-tab-general'
    extra = 1
    form = LocationRelationAdminForm
        
class SubjectSubjectRelationsInline(admin.TabularInline):
    model = SubjectSubjectRelations
    fk_name = "subject1"
    fields = ['subject2', 'relation_type', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_classes = 'suit-tab suit-tab-general'    
        
class FileInline(admin.TabularInline):
    model = File
    fields = ['get_thumbnail', 'media', 'relation_type', 'notes', 'last_mod_by']
    readonly_fields = ('get_thumbnail', 'last_mod_by', 'media', 'relation_type')        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_classes = 'suit-tab suit-tab-files'
    extra = 0
    max_num = 0
        
class SubjectAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')    
    inlines = [SubjectPropertyInline, SubjectControlPropertyInline, MediaSubjectRelationsInline, FileInline, LocationSubjectRelationsInline]
    search_fields = ['title', 'title1', 'title2', 'title3', 'desc1', 'desc2', 'desc3']
    list_display = ('title1', 'title2', 'title3', 'desc1', 'desc2', 'desc3', 'created', 'modified')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    suit_form_tabs = (('general', 'General'), ('files', 'Files'))
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ['title', 'notes', 'created', 'modified', 'last_mod_by']
        }),
    ]
    advanced_search_form = AdminAdvSearchForm()
    
    change_list_template = 'admin/base/subject/change_list.html'
    change_form_template = 'admin/base/change_form.html'
    
    """ Query set for this admin module will only include subjects of type "object" """
    def queryset(self, request):
        qs = super(SubjectAdmin, self).queryset(request)
        return qs.filter(type__type='object')
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.type_id = 1 #sets any object created from this admin module to type "object"
        obj.save()
        update_display_fields(obj.id, 'subj')
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, SubjectProperty):
            
                # automatically adding museum control field value if museum number is entered
                prop_id = instance.property_id
                existing_museum = SubjectControlProperty.objects.filter(subject_id = instance.subject_id, control_property_id = 59)
                nums = []
                warning = 'You have added/updated/deleted a Museum Number. If a new type of museum number was added, the system has automatically updated the controlled Museum field. HOWEVER, the system does NOT delete existing Museum fields. If you are concerned, please double check that the Museum field for this object is correct.'
                if existing_museum:
                    for item in existing_museum:
                        nums.append(item.control_property_value_id)
                if (prop_id == 31 or prop_id == 33 or prop_id == 45 or prop_id == 43) and (401 not in nums):
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=401), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)
                elif prop_id == 32 and 402 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=402), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif (prop_id == 34 or prop_id == 36 or prop_id == 44) and (398 not in nums):
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=398), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif prop_id == 35 and 403 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=403), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif prop_id == 38 and 404 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=404), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif prop_id == 40 and 405 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=405), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif prop_id == 42 and 406 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=406), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                    
                elif prop_id == 73 and 407 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=407), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)
                elif prop_id == 128 and 435 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=435), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)
                elif prop_id == 129 and 447 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=447), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)   
                elif prop_id == 130 and 448 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=448), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)   
                elif prop_id == 131 and 449 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=449), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)   
                elif prop_id == 132 and 450 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=450), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)   
                elif prop_id == 133 and 451 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=451), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)
                elif prop_id == 146 and 771 not in nums:
                    m = SubjectControlProperty(subject = instance.subject, control_property = DescriptiveProperty.objects.get(pk=59), control_property_value = ControlField.objects.get(pk=771), last_mod_by = request.user)
                    m.save()
                    messages.add_message(request, messages.WARNING, warning)                     
                
                instance.last_mod_by = request.user            
                instance.save()
                update_display_fields(instance.subject_id, 'subj')            

            if isinstance(instance, MediaSubjectRelations) or isinstance (instance, SubjectControlProperty): #Check if it is the correct type of inline
                instance.last_mod_by = request.user            
                instance.save()

            if isinstance (instance, LocationSubjectRelations):
                instance.relation_type = Relations.objects.get(pk=4)
                instance.last_mod_by = request.user            
                instance.save()                
            
    # advanced search form based on https://djangosnippets.org/snippets/2322/ and http://stackoverflow.com/questions/8494200/django-admin-custom-change-list-arguments-override-e-1 

    def get_changelist(self, request, **kwargs):
        adv_search_fields = {}
        asf = self.advanced_search_form
        for key in asf.fields.keys():
            temp = self.other_search_fields.get(key, None)
            if temp:
                adv_search_fields[key] = temp[0]
            else:
                adv_search_fields[key] = ''
        
        class AdvChangeList(ChangeList):
            
            def get_query_string(self, new_params=None, remove=None):
                """ Overriding get_query_string ensures that the admin still considers
                the additional search fields as parameters, even tho they are popped from 
                the request.GET """
                
                if new_params is None:
                    new_params = {}
                if remove is None:
                    remove = []
                p = self.params.copy()
                for r in remove:
                    for k in list(p):
                        if k.startswith(r):
                            del p[k]
                for k, v in new_params.items():
                    if v is None:
                        if k in p:
                            del p[k]
                    else:
                        p[k] = v
                
                extra_params = ''
                for field, val in adv_search_fields.items():
                    extra_params += '&' + field + '=' + val
                
                return '?%s%s' % (urlencode(sorted(p.items())), extra_params)
                
        return AdvChangeList
        
    def lookup_allowed(self, key, value):
        if key in self.advanced_search_form.fields.keys():
            return True
        return super(SubjectAdmin, self).lookup_allowed(key, value)
        
    def changelist_view(self, request, extra_context=None, **kwargs):
        self.other_search_fields = {}
        asf = self.advanced_search_form
        extra_context = {'asf': asf}
        
        request.GET._mutable = True
        
        for key in asf.fields.keys():
            try:
                temp = request.GET.pop(key)
            except KeyError:
                pass
            else:
                if temp != ['']:
                    self.other_search_fields[key] = temp
                    
        request.GET._mutable = False
        return super(SubjectAdmin, self).changelist_view(request, extra_context = extra_context)
        
    def get_search_results(self, request, queryset, search_term):
        """ Performs either a simple search using the search_term or an 
        advanced search using values taken from the AdvancedSearchForm """
        
        queryset, use_distinct = super(SubjectAdmin, self).get_search_results(request, queryset, search_term)
        
        # get all the fields from the adv search form
        adv_fields = {}
        asf = self.advanced_search_form
        for key in asf.fields.keys():
            temp = self.other_search_fields.get(key, None)
            if temp:
                adv_fields[key] = temp[0]
            else:
                adv_fields[key] = ''
        
        # NOTE: simple search has already been applied
        
        # RELATED TABLES FILTER
        loc = adv_fields['loc']
        if loc != '':
            queryset = queryset.filter(locationsubjectrelations__location_id=loc)
            
        img = adv_fields['img']
        if img != 'default':
            if img == 'yes':
                queryset = queryset.filter(mediasubjectrelations__relation_type=3)
            else:
                queryset = queryset.exclude(mediasubjectrelations__relation_type=3)
                
        pub = adv_fields['pub']
        if pub != '':
            queryset = queryset.filter(mediasubjectrelations__media=pub)
            
        last_mod = adv_fields['last_mod']
        if last_mod != '':
            queryset = queryset.filter(last_mod_by = last_mod)            
        
        # CONTROL PROPERTY FILTER
        for i in range(1, 4):
            cp = adv_fields['cp' + str(i)]
            cst = adv_fields['cst' + str(i)]
            cv = adv_fields['cv' + str(i)]
            
            if cp != '' and cv != 'default':
                cf = ControlField.objects.filter(pk = cv)
                cf_desc = cf[0].get_descendants(include_self=True)
                ccq = Q()
                for field in cf_desc:
                    if cst == 'exact':
                        ccq |= Q(subjectcontrolproperty__control_property_value = field.id)
                    else:
                        ccq &= ~Q(subjectcontrolproperty__control_property_value = field.id)
                        
                queryset = queryset.filter(ccq)
                
        # FREE FORM PROPERTY FILTER
        for i in range (1, 4):
            if i != 1:
                op = adv_fields['op' + str(i - 1)]
            else:
                op = ''
            fp = adv_fields['fp' + str(i)]
            fst = adv_fields['fst' + str(i)]
            fv = adv_fields['fv' + str(i)]

            negate = False # whether or not the query will be negated
            kwargs = {}
            cq = Q()
            
            # remove and save negation, if present
            if fst.startswith('not'):
                negate = True
                fst = fst[4:]
            
            if not(fv == '' and fst != 'blank'):
                
                if fst == 'blank':
                    #if property is Any, then skip all b/c query asks for doc with 'any' blank properties
                    if fp == '':
                        continue
                
                    # BLANK is a special case negation (essentially a double negative), so handle differently
                    if negate:
                        cq = Q(subjectproperty__property = fp)
                    else:
                        cq = ~Q(subjectproperty__property = fp)
                        
                else:
                    kwargs = {str('subjectproperty__property_value__%s' % fst) : str('%s' % fv)}
                    
                    # check if a property was selected and build the current query
                    if fp == '':
                        # if no property selected, than search thru ALL properties
                        if negate:
                            cq = ~Q(**kwargs)
                        else:
                            cq = Q(**kwargs)
                    else:
                        if negate:
                            cq = Q(Q(subjectproperty__property = fp) & ~Q(**kwargs))
                        else:
                            cq = Q(Q(subjectproperty__property = fp) & Q(**kwargs))
                            
            # modify query set
            if op == 'or':
                queryset = queryset | self.model.objects.filter(cq)
            else:
                # if connector wasn't set, use &
                queryset = queryset.filter(cq)
        
        if queryset.ordered:
            return queryset.distinct(), use_distinct
        else:
            return queryset.order_by('-modified').distinct(), use_distinct

admin.site.register(Subject, SubjectAdmin)

class MediaPropertyInline(admin.TabularInline):
    model = MediaProperty
    fields = ['property', 'property_value', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "property":
            kwargs["queryset"] = DescriptiveProperty.objects.filter(Q(primary_type='MP') | Q(primary_type='AL'))
        return super(MediaPropertyInline, self).formfield_for_foreignkey(db_field, request, **kwargs)    

class MediaAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['title', 'type', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['title', 'type', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    inlines = [MediaPropertyInline]
    search_fields = ['title', 'notes']
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, MediaProperty) : #Check if it is the correct type of inline
                instance.last_mod_by = request.user            
                instance.save()
    
admin.site.register(Media, MediaAdmin)

class MediaPersonOrgRelationsInline(admin.TabularInline):
    model = MediaPersonOrgRelations
    fields = ['media', 'relation_type', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'media':
            kwargs["queryset"] = Media.objects.filter(type__type = 'publication').order_by('title')
        elif db_field.name == 'relation_type':
            kwargs["queryset"] = Relations.objects.filter(Q(pk=2) | Q(pk=5))
        return super(MediaPersonOrgRelationsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def get_queryset(self, request):
        qs = super(MediaPersonOrgRelationsInline, self).get_queryset(request)
        return qs.filter(Q(relation_type=2) | Q(relation_type=5))    

class PersonOrgPropertyInline(admin.TabularInline):
    model = PersonOrgProperty
    extra = 3
    fields = ['property', 'property_value', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',) 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }    

class PersonOrgAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['title', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['title', 'notes', 'created', 'modified', 'last_mod_by']
    inlines = [PersonOrgPropertyInline, MediaPersonOrgRelationsInline, PersonOrgLinkedDataInline]
    search_fields = ['title']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    } 

    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, PersonOrgProperty) or isinstance(instance, MediaPersonOrgRelations) or isinstance(instance, PersonOrgLinkedData) : #Check if it is the correct type of inline
                instance.last_mod_by = request.user            
                instance.save()    

admin.site.register(PersonOrg, PersonOrgAdmin)

class GlobalVarsAdmin(admin.ModelAdmin):
    readonly_fields = ('human_title', 'variable')
    list_display = ['human_title', 'val']
    search_fields = ['human_title']
    fields = ['human_title', 'val']
    
admin.site.register(GlobalVars, GlobalVarsAdmin)

class SiteContentForm(ModelForm):
    class Meta:
  
        _ck_editor_toolbar = [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph',
             'groups': ['list', 'indent', 'blocks', 'align']},
            {'name': 'document', 'groups': ['mode']}, '/',
            {'name': 'styles'}, {'name': 'colors'},
            {'name': 'insert_custom',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule']},
            {'name': 'links'},
            {'name': 'about'}]

        _ck_editor_config = {'autoGrow_onStartup': True,
                             'autoGrow_minHeight': 100,
                             'autoGrow_maxHeight': 250,
                             'extraPlugins': 'autogrow',
                             'toolbarGroups': _ck_editor_toolbar}            
  
        widgets = {
            'val': CKEditorWidget(editor_options=_ck_editor_config),
        }

class SiteContentAdmin(admin.ModelAdmin):
    readonly_fields = ('human_title', 'variable')
    list_display = ['human_title', 'val']
    search_fields = ['human_title']
    form = SiteContentForm
    fieldsets = [
        ('Edit Text', {
            'classes': ('full-width',),
            'fields': ['val']})        
    ]
    
admin.site.register(SiteContent, SiteContentAdmin)

admin.site.register(MediaType)

class DescriptivePropertyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['property', 'primary_type', 'order', 'data_source_type', 'visible', 'solr_type', 'facet', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['property', 'primary_type', 'order', 'data_source_type', 'visible', 'solr_type', 'facet', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    search_fields = ['property']
    list_filter = ('primary_type', 'visible', 'solr_type', 'facet', 'data_source_type')
    list_editable = ('primary_type', 'order', 'visible', 'solr_type', 'facet', 'notes', 'data_source_type')
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()

admin.site.register(DescriptiveProperty, DescriptivePropertyAdmin)
admin.site.register(MediaProperty)
admin.site.register(FeaturedImgs)

class SubjectPropertyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['subject', 'property', 'property_value', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['subject', 'property', 'property_value', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()

admin.site.register(SubjectProperty, SubjectPropertyAdmin)
admin.site.register(Relations)

# class MediaSubjectRelationsForm(ModelForm):
    # class Meta:
        # widgets = {
            # 'subject': LinkedSelect
        # }

class MediaSubjectRelationsAdmin(admin.ModelAdmin):
    readonly_fields = ('subject', 'created', 'modified', 'last_mod_by')
    fields = ['media', 'subject', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['media', 'subject', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    search_fields = ['notes']
#    form = MediaSubjectRelationsForm
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()

admin.site.register(MediaSubjectRelations, MediaSubjectRelationsAdmin)

class LocationSubjectRelationsAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['location', 'subject', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['location', 'subject', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()

admin.site.register(LocationSubjectRelations, LocationSubjectRelationsAdmin)

class SubjectSubjectRelationsAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['subject1', 'subject2', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['subject1', 'subject2', 'relation_type', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()

admin.site.register(SubjectSubjectRelations, SubjectSubjectRelationsAdmin)
admin.site.register(MediaPersonOrgRelations)
admin.site.register(PersonOrgProperty)

class StatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'last_mod_by')
    fields = ['status', 'notes', 'created', 'modified', 'last_mod_by']
    list_display = ['status', 'notes', 'created', 'modified', 'last_mod_by']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2})},
    }
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
    
admin.site.register(Status, StatusAdmin)

class LocationPropertyInline(admin.TabularInline):
    model = LocationProperty
    fields = ['property', 'property_value', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    ordering = ('property__order',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'property':
            kwargs["queryset"] = DescriptiveProperty.objects.filter(Q(primary_type='AL') | Q(primary_type='SL'))
        return super(LocationPropertyInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
class MediaLocationRelationsInline(admin.TabularInline):
    model = MediaLocationRelations
    fields = ['media', 'relation_type', 'notes', 'last_mod_by']
    readonly_fields = ('last_mod_by',)        
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'media':
            kwargs["queryset"] = Media.objects.filter(type__type = 'publication').order_by('title')
        elif db_field.name == 'relation_type':
            kwargs["queryset"] = Relations.objects.filter(Q(pk=2) | Q(pk=5))
        return super(MediaLocationRelationsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def get_queryset(self, request):
        qs = super(MediaLocationRelationsInline, self).get_queryset(request)
        return qs.filter(Q(relation_type=2) | Q(relation_type=5))        

class LocationAdmin(MPTTModelAdmin):
    readonly_fields = ('last_mod_by',)    
    inlines = [LocationPropertyInline, MediaLocationRelationsInline]
    search_fields = ['title']
    list_display = ('title', 'notes', 'type', 'ancestors')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    list_filter = ['type']
    
    change_form_template = 'admin/base/location/change_form.html'    
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, LocationProperty) or isinstance(instance, MediaLocationRelations): #Check if it is the correct type of inline
                instance.last_mod_by = request.user            
                instance.save()

admin.site.register(Location, LocationAdmin)

class PostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    list_display = ['title']
    list_filter = ['published', 'created']
    search_fields = ['title', 'body']
    date_hierarchy = 'created'
    save_on_top = True
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Post, PostAdmin)

class AdminCommentInline(admin.StackedInline):
    model = AdminComment
    extra = 0
    readonly_fields = ('author', 'created')
    template = 'admin/edit_inline/stacked_adminpost.html'
    
    def queryset(self, request):
        qs = super(AdminCommentInline, self).queryset(request)
        return qs.filter(Q(published = True) | Q(published = False, author = request.user))       

class AdminPostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    readonly_fields = ('author', 'created')
    inlines = [AdminCommentInline]
    list_display = ['title', 'author', 'created', 'published']
    list_filter = ['published', 'created']
    search_fields = ['title', 'body']
    date_hierarchy = 'created'
    save_on_top = True
    change_form_template = 'admin/base/adminpost/change_form_adminpost.html'
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
            obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, AdminComment): #Check if it is the correct type of inline
                instance.author = request.user            
                instance.save()        
        
    def queryset(self, request):
        qs = super(AdminPostAdmin, self).queryset(request)
        return qs.filter(Q(published = True) | Q(published = False, author = request.user))
        
    def has_delete_permission(self, request, obj = None):
        if obj is not None:
            if request.user == obj.author:
                return True
        return False

admin.site.register(AdminPost, AdminPostAdmin)

class ObjectTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('last_mod_by',)
    list_display = ('type', 'notes', 'control_field')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    
    def save_model(self, request, obj, form, change):
        obj.last_mod_by = request.user
        obj.save()
        
admin.site.register(ObjectType, ObjectTypeAdmin)

class LinkedDataAdmin(admin.ModelAdmin):
    list_display = ['control_field', 'source', 'show_url']
    search_fields = ['control_field']
    
    def show_url(self, obj):
        return '<a href="%s">%s</a>' % (obj.link, obj.link)
    show_url.allow_tags = True
    show_url.short_description = "Link"

admin.site.register(ControlFieldLinkedData, LinkedDataAdmin)

'''class PublicationSubjectRelationFilter(admin.SimpleListFilter):
    """ Allows filtering of subjects by related Publications """
    
    title = _('publication')
    
    parameter_name = 'pub'
    
    def lookups(self, request, model_admin):
        pubs = Media.objects.filter(type=2) # select media with type = 'publication'
        publist = []
        
        # create list of lookups; url coded value is ID of media item, displayed name is media title
        for pub in pubs:
            item = (pub.id, _(pub.title))
            publist.append(item)
        
        return publist
        
    def queryset(self, request, queryset):
        mediaid = self.value() # id of publication in media table
        
        # get all subjects with a relation to the given publication
        if mediaid:
            return queryset.filter(mediasubjectrelations__media_id = mediaid)
        return queryset'''
    
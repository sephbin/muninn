from django.contrib import admin
from .models import *

# Register your models here.
class finishInline(admin.TabularInline):
    model = rel_finish
    classes = ['collapse']
    verbose_name = "Schedule"
    verbose_name_plural = "Schedules"
    fields = ('rfinish_schedule',)
    extra = 0 # how many rows to show

class spaceElementInline(admin.TabularInline):
    model = space_element_quantity
    classes = ['collapse']
    verbose_name = "Element Quantity"
    verbose_name_plural = "Element Quantities"
    fields = ('quantity','space',)
    extra = 0 # how many rows to show

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(spaceElementInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        field.queryset = field.queryset.filter(project = request._obj_.project)  
        return field

class finishAdmin(admin.ModelAdmin):
    list_filter = ['supplier','schedules']
    list_display = ('finish','image_tag','supplytext')
    inlines = (finishInline,)

    fieldsets = [
        (None,         {'fields': ['image','image_tag',]}),
        ('Finish', {'fields': ['fin_product','fin_finish','fin_colour','fin_code','fin_size','fin_notes',], 'classes': ['collapse']}),
        ('Supplier', {'fields': ['supplier',], 'classes': ['collapse']}),
    ]
    readonly_fields = ('image_tag',)


class scheduleAdmin(admin.ModelAdmin):
    readonly_fields = ('revision',)
    fieldsets = [
        (None,{'fields': ['project','revision']}),
    ]

class typeAdmin(admin.ModelAdmin):
    search_fields=["type_name","data_text",]
    list_filter = ('project',)
    list_display = ['project','type_name','data_text',]
    list_editable = ['type_name','data_text',]
    readonly_fields = ('data',)
    fieldsets = [
        (None,{'fields': ['project','type_name','data_text','data']}),
    ]

class roomAdmin(admin.ModelAdmin):
    search_fields=("element_id", "room_name", "data_text", 'source_file', )
    readonly_fields = ('data', 'contentlist', 'doorslist', )
    list_display = ["element_id","number_store",'room_name','room_type',
    # 'data',
    'source_file','project']
    list_filter = ('project', 
        # "room_type",
        )
    list_per_page = 300
    fieldsets = [
        (None,{'fields': ['element_id','source_file','project','room_name','room_type','data_text',
            'data',
            'contentlist',
            'doorslist'
            ]}),
    ]

class doorAdmin(admin.ModelAdmin):
    search_fields=("mark", "data_text" , "from_room__element_id", "to_room__element_id",)
    readonly_fields = ( 'data', 'family', 'mark' )
    list_display = ['element_id','mark', 'family','parent_room','from_room','to_room','data',]
    list_filter = ('project',)
    fieldsets = [
        (None,{'fields': ['element_id','project','from_room','to_room','parent_room','data_text','data', 'mark']}),
    ]

class elementAdmin(admin.ModelAdmin):
    list_filter = ('project',)

class element_typeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['supplier',]
    filter_horizontal = ('projects',)
    # list_editable = ['projects',]
    list_display = ('item','element_type','description_tag','dimension_tag','image_tag','comment_tag','supplytext_tag','code',)
    readonly_fields = ('image_tag', )

class project_element_typesAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ['project',]
    list_editable = ['quantity','code',]
    list_display_links = ('description_tag',)
    inlines = (spaceElementInline,)
    # filter_horizontal = ('project',)
    list_display = ('code','description_tag','quantity','dimension_tag','image_tag','comment_tag','supplytext_tag', 'space_tag')
    readonly_fields = ('image_tag', )
    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(project_element_typesAdmin, self).get_form(request, obj, **kwargs)

class spaceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('project','space_name','furnitureScheduleTag')

class projectAdmin(admin.ModelAdmin):
    search_fields=("number", "name")
    filter_horizontal = ('users',)
    list_filter = ['location',]
    list_display = ["number","name","location",]



admin.site.register(finish,finishAdmin)
admin.site.register(supplier)
admin.site.register(project, projectAdmin)
admin.site.register(finish_schedule, scheduleAdmin)
admin.site.register(rel_finish)
admin.site.register(room_type,typeAdmin)
admin.site.register(room,roomAdmin)
admin.site.register(door,doorAdmin)
admin.site.register(element, elementAdmin)
admin.site.register(space, spaceAdmin)
admin.site.register(element_type,element_typeAdmin)
admin.site.register(project_element_types,project_element_typesAdmin)
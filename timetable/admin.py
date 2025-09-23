from django.contrib import admin

from .models import Subject, Class

class ClassInline(admin.TabularInline):
    model = Class
    extra = 0
    fields = ('day', 'start_time', 'end_time', 'location', 'instructor')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'user', 'color')
    search_fields = ('name', 'code', 'user__username')
    list_filter = ('user',)
    inlines = (ClassInline,)
    ordering = ('user', 'name')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('subject', 'get_subject_user', 'get_day_display', 'start_time', 'end_time', 'location', 'instructor')
    list_filter = ('day', 'subject__user')
    search_fields = ('subject__name', 'location', 'instructor')
    ordering = ('day', 'start_time')

    def get_subject_user(self, obj):
        return obj.subject.user
    get_subject_user.short_description = 'User'
    get_subject_user.admin_order_field = 'subject__user'
# ...existing code...
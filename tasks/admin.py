from django.contrib import admin
from .models import Organization, Project, Task, SubTask, TaskComment, TimeSlot


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'track_code', 'status', 'priority', 'progress', 'start_date', 'due_date')
    list_filter = ('status', 'priority', 'track_code')
    search_fields = ('title', 'description')
    inlines = [SubTaskInline]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'department', 'team')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organization')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_time', 'end_time', 'date')

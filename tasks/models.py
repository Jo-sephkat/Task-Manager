from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=100)
    division = models.CharField(max_length=100, default='01 Division')
    department = models.CharField(max_length=100, default='01 Department')
    team = models.CharField(max_length=100, default='A Team')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.division} / {self.department} / {self.team}"


class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=20, default='blue')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        IN_PROGRESS = 'in_progress', 'In Progress'
        EDITING = 'editing', 'Editing'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    track_code = models.CharField(max_length=5, default='A')  # e.g. A, B, C, D
    track_color = models.CharField(max_length=30, default='#3B82F6')  # Hex or Tailwind color
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    progress = models.PositiveSmallIntegerField(default=0)  # 0 - 100%
    is_starred = models.BooleanField(default=False)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_tasks')
    assignees = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    
    # Dates for Gantt timeline
    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.track_code}] {self.title}"

    @property
    def completed_subtasks_count(self):
        return self.subtasks.filter(is_completed=True).count()

    @property
    def total_subtasks_count(self):
        return self.subtasks.count()


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class TimeSlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150)
    start_time = models.TimeField()
    end_time = models.TimeField()
    color = models.CharField(max_length=30, default='#3B82F6')
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}: {self.title}"

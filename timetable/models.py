from django.db import models

from django.contrib.auth.models import User
import random

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=7, default='#%06x' % random.randint(0, 0xFFFFFF))
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate a random color if not set
        if not self.color or self.color == '#%06x' % 0:
            self.color = '#%06x' % random.randint(0, 0xFFFFFF)
        super().save(*args, **kwargs)


class Class(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)
    instructor = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.subject.name} - {self.get_day_display()}"
    
    
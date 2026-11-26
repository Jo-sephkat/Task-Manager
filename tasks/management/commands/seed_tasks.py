import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Organization, Project, Task, SubTask, TimeSlot


class Command(BaseCommand):
    help = "Seeds database with multi-user live datasets"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding multi-user live task data...")

        org, _ = Organization.objects.get_or_create(
            name="Alpha Corp",
            division="01 Division",
            department="01 Department",
            team="A Team"
        )
        project, _ = Project.objects.get_or_create(
            organization=org,
            name="SaaS Overhaul",
            code="SO-2026"
        )

        # 1. Create distinct users
        users_data = [
            {'username': 'lead_engineer', 'first': 'Alex', 'last': 'Morgan', 'email': 'alex@example.com'},
            {'username': 'jkatsande', 'first': 'Joseph', 'last': 'Katsande', 'email': 'joseph@example.com'},
            {'username': 'sarah_ux', 'first': 'Sarah', 'last': 'Jenkins', 'email': 'sarah@example.com'},
            {'username': 'david_dev', 'first': 'David', 'last': 'Chen', 'email': 'david@example.com'},
        ]
        user_objects = {}
        for ud in users_data:
            u, created = User.objects.get_or_create(username=ud['username'])
            u.first_name = ud['first']
            u.last_name = ud['last']
            u.email = ud['email']
            u.set_password('pass1234')
            u.save()
            user_objects[ud['username']] = u

        # Clear existing tasks and time slots
        Task.objects.all().delete()
        TimeSlot.objects.all().delete()

        today = datetime.date.today()

        # 2. Tasks for Joseph Katsande
        t_jk1 = Task.objects.create(
            project=project,
            title="Design token refactor & CSS theme system",
            description="Extract theme tokens and harmonize Tailwind palette.",
            track_code="A",
            track_color="#3B82F6",
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.HIGH,
            progress=50,
            start_date=today,
            due_date=today + datetime.timedelta(days=4)
        )
        t_jk1.assignees.add(user_objects['jkatsande'])
        SubTask.objects.create(task=t_jk1, title="Review design mockups", is_completed=True)
        SubTask.objects.create(task=t_jk1, title="Implement responsive tokens", is_completed=False)

        t_jk2 = Task.objects.create(
            project=project,
            title="Database indexing on task search filters",
            description="Analyze EXPLAIN plans for fast query execution.",
            track_code="C",
            track_color="#EC4899",
            status=Task.Status.DONE,
            priority=Task.Priority.URGENT,
            progress=100,
            start_date=today - datetime.timedelta(days=3),
            due_date=today
        )
        t_jk2.assignees.add(user_objects['jkatsande'])
        SubTask.objects.create(task=t_jk2, title="Create composite B-tree index", is_completed=True)

        # 3. Tasks for Alex Morgan
        t_alex1 = Task.objects.create(
            project=project,
            title="OAuth2 & Session Authentication Guard",
            description="Setup session store and JWT authorization endpoints.",
            track_code="B",
            track_color="#8B5CF6",
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.HIGH,
            progress=66,
            start_date=today,
            due_date=today + datetime.timedelta(days=5)
        )
        t_alex1.assignees.add(user_objects['lead_engineer'])
        SubTask.objects.create(task=t_alex1, title="Migration for token blacklist", is_completed=True)
        SubTask.objects.create(task=t_alex1, title="Middleware auth check", is_completed=True)
        SubTask.objects.create(task=t_alex1, title="Unit tests for expired sessions", is_completed=False)

        # 4. Tasks for Sarah Jenkins
        t_sarah1 = Task.objects.create(
            project=project,
            title="Mobile Responsive Navigation & Gestures",
            description="Optimize drawer interactions on iOS Safari and Android Chrome.",
            track_code="A",
            track_color="#3B82F6",
            status=Task.Status.DRAFT,
            priority=Task.Priority.MEDIUM,
            progress=0,
            start_date=today + datetime.timedelta(days=1),
            due_date=today + datetime.timedelta(days=7)
        )
        t_sarah1.assignees.add(user_objects['sarah_ux'])
        SubTask.objects.create(task=t_sarah1, title="Draft touch prototypes", is_completed=False)

        # 5. Tasks for David Chen
        t_david1 = Task.objects.create(
            project=project,
            title="Continuous Integration & Docker runner suite",
            description="Set up automated GitHub actions and container tests.",
            track_code="D",
            track_color="#F59E0B",
            status=Task.Status.DONE,
            priority=Task.Priority.HIGH,
            progress=100,
            start_date=today - datetime.timedelta(days=2),
            due_date=today
        )
        t_david1.assignees.add(user_objects['david_dev'])
        SubTask.objects.create(task=t_david1, title="Configure workflow YAML", is_completed=True)
        SubTask.objects.create(task=t_david1, title="Run container smoke tests", is_completed=True)

        # 6. TimeSlots per user
        TimeSlot.objects.create(
            user=user_objects['jkatsande'],
            title="Frontend Review & Standup",
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            color="#3B82F6",
            date=today
        )
        TimeSlot.objects.create(
            user=user_objects['jkatsande'],
            title="Architecture Planning Sync",
            start_time=datetime.time(14, 0),
            end_time=datetime.time(15, 0),
            color="#EC4899",
            date=today
        )

        TimeSlot.objects.create(
            user=user_objects['lead_engineer'],
            title="Sprint Planning Meeting",
            start_time=datetime.time(11, 0),
            end_time=datetime.time(12, 30),
            color="#8B5CF6",
            date=today
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded personalized live datasets!"))

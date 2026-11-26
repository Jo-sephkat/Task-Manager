from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Organization, Project, Task, SubTask


class TaskManagerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        self.org = Organization.objects.create(name="Test Org", division="01 Division")
        self.project = Project.objects.create(organization=self.org, name="Platform Test")
        self.task = Task.objects.create(
            project=self.project,
            title="Initial Test Task",
            track_code="A",
            status=Task.Status.DRAFT,
            progress=0
        )
        self.task.assignees.add(self.user)
        self.subtask = SubTask.objects.create(
            task=self.task,
            title="Subtask 1",
            is_completed=False
        )

    def test_dashboard_view_loads(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Management")
        self.assertContains(response, "Initial Test Task")

    def test_task_detail_view_loads_and_edits(self):
        url = reverse('tasks:task_detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Initial Test Task")

        # Edit task via POST
        edit_response = self.client.post(url, {
            'title': 'Renamed Task Title',
            'status': Task.Status.IN_PROGRESS,
            'priority': Task.Priority.URGENT,
            'track_code': 'B',
            'progress': '75',
        })
        self.assertEqual(edit_response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Renamed Task Title')
        self.assertEqual(self.task.track_code, 'B')

    def test_toggle_subtask_updates_progress(self):
        url = reverse('tasks:toggle_subtask', args=[self.subtask.id])
        response = self.client.post(url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)

        self.subtask.refresh_from_db()
        self.assertTrue(self.subtask.is_completed)

        self.task.refresh_from_db()
        self.assertEqual(self.task.progress, 100)

    def test_unauthenticated_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)

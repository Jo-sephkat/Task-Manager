from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import datetime
from .models import Task, SubTask, TimeSlot, Organization, Project, TaskComment
from .forms import RegisterForm, LoginForm


def register_view(request):
    """User Registration."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tasks/auth/register.html', {'form': form})


def login_view(request):
    """User Login."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'tasks:dashboard'))
    else:
        form = LoginForm()
    return render(request, 'tasks/auth/login.html', {'form': form})


def logout_view(request):
    """User Logout."""
    logout(request)
    return redirect('tasks:login')


@login_required(login_url='tasks:login')
def dashboard_view(request):
    """
    Personalized Live Dashboard:
    - User sees strictly tasks concerning them (assigned to them or supervised by them).
    - If a user signs in for the first time, all counts and lists are 0.
    """
    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(name="Alpha Corp", division="01 Division", department="01 Department", team="A Team")

    # Strictly user's tasks
    user_tasks = Task.objects.prefetch_related('subtasks', 'assignees', 'comments').filter(
        Q(assignees=request.user) | Q(supervisor=request.user)
    ).distinct()

    tasks = user_tasks

    # 4-column groupings
    tasks_draft = tasks.filter(status=Task.Status.DRAFT)
    tasks_in_progress = tasks.filter(status=Task.Status.IN_PROGRESS)
    tasks_editing = tasks.filter(status=Task.Status.EDITING)
    tasks_done = tasks.filter(status=Task.Status.DONE)

    my_tasks_count = user_tasks.count()

    # Workstream Cluster Metrics (computed dynamically from the active user's tasks only)
    tracks = [
        {'code': 'A', 'title': 'Design & UX', 'color': '#3B82F6'},
        {'code': 'B', 'title': 'Core Backend & API', 'color': '#8B5CF6'},
        {'code': 'C', 'title': 'Database & Infrastructure', 'color': '#EC4899'},
        {'code': 'D', 'title': 'DevOps & Quality', 'color': '#F59E0B'},
    ]
    track_clusters = []
    for tr in tracks:
        tr_tasks = tasks.filter(track_code=tr['code'])
        cnt = tr_tasks.count()
        done_cnt = tr_tasks.filter(status=Task.Status.DONE).count()
        progress = int(tr_tasks.aggregate(Avg('progress'))['progress__avg'] or 0)
        pct_of_total = int((cnt / my_tasks_count) * 100) if my_tasks_count > 0 else 0

        track_clusters.append({
            'code': tr['code'],
            'title': tr['title'],
            'color': tr['color'],
            'total': cnt,
            'done': done_cnt,
            'progress': progress,
            'pct_of_total': pct_of_total,
        })

    # Time slots for the active user for today
    today = timezone.now().date()
    time_slots = TimeSlot.objects.filter(user=request.user, date=today)

    # Live Efficiency calculations for active user
    efficiency_stats = []
    for tr in tracks:
        tr_tasks = tasks.filter(track_code=tr['code'])
        avg_progress = tr_tasks.aggregate(Avg('progress'))['progress__avg'] or 0
        efficiency_stats.append({
            'code': tr['code'],
            'percentage': int(avg_progress),
            'color': tr['color']
        })

    # Completed tasks velocity bar chart for active user
    completed_stats = []
    max_completed = 1
    track_counts = {}
    for tr in tracks:
        cnt = tasks.filter(track_code=tr['code'], status=Task.Status.DONE).count()
        track_counts[tr['code']] = cnt
        if cnt > max_completed:
            max_completed = cnt

    for tr in tracks:
        cnt = track_counts[tr['code']]
        height_pct = max(20, int((cnt / max_completed) * 90)) if my_tasks_count > 0 and max_completed > 0 else 20
        completed_stats.append({
            'label': f"Track {tr['code']}",
            'value': cnt,
            'height': f"{height_pct}%",
            'color': tr['color']
        })

    all_users = User.objects.all()

    context = {
        'org': org,
        'tasks': tasks,
        'tasks_draft': tasks_draft,
        'tasks_in_progress': tasks_in_progress,
        'tasks_editing': tasks_editing,
        'tasks_done': tasks_done,
        'my_tasks_count': my_tasks_count,
        'track_clusters': track_clusters,
        'time_slots': time_slots,
        'efficiency_stats': efficiency_stats,
        'completed_stats': completed_stats,
        'all_users': all_users,
        'active_menu': 'dashboard',
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required(login_url='tasks:login')
def task_list_view(request):
    """
    Personalized Task Directory:
    Only displays tasks assigned to or supervised by the logged-in user.
    """
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('q', '').strip()

    # Strictly user tasks
    tasks = Task.objects.prefetch_related('subtasks', 'assignees').filter(
        Q(assignees=request.user) | Q(supervisor=request.user)
    ).distinct()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    users = User.objects.all()

    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'users': users,
        'active_menu': 'tasks',
    }
    return render(request, 'tasks/task_list.html', context)


@login_required(login_url='tasks:login')
def task_detail_view(request, task_id):
    """Task Detail & Edit screen."""
    # Allow opening tasks concerning the user or newly created by them
    task = get_object_or_404(Task.objects.prefetch_related('subtasks', 'comments__author', 'assignees'), id=task_id)
    all_users = User.objects.all()

    if request.method == 'POST':
        task.title = request.POST.get('title', task.title).strip()
        task.description = request.POST.get('description', '').strip()
        task.status = request.POST.get('status', task.status)
        task.priority = request.POST.get('priority', task.priority)
        task.track_code = request.POST.get('track_code', task.track_code).upper()
        
        color_map = {'A': '#3B82F6', 'B': '#8B5CF6', 'C': '#EC4899', 'D': '#F59E0B'}
        task.track_color = color_map.get(task.track_code, task.track_color)

        start_date = request.POST.get('start_date')
        due_date = request.POST.get('due_date')
        if start_date:
            task.start_date = start_date
        if due_date:
            task.due_date = due_date

        progress = request.POST.get('progress')
        if progress is not None and progress.isdigit():
            task.progress = min(100, max(0, int(progress)))

        assignee_ids = request.POST.getlist('assignees')
        if assignee_ids:
            task.assignees.set(assignee_ids)
        else:
            task.assignees.clear()

        task.save()
        return redirect('tasks:task_detail', task_id=task.id)

    context = {
        'task': task,
        'all_users': all_users,
        'active_menu': 'tasks',
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required(login_url='tasks:login')
@require_POST
def add_comment(request, task_id):
    """Post a comment on a task."""
    task = get_object_or_404(Task, id=task_id)
    content = request.POST.get('content', '').strip()
    if content:
        TaskComment.objects.create(task=task, author=request.user, content=content)
    return redirect('tasks:task_detail', task_id=task.id)


@login_required(login_url='tasks:login')
def planning_view(request):
    """
    Planning & Roadmap Page:
    Strictly scoped to tasks assigned to or supervised by the logged-in user.
    """
    tasks = Task.objects.prefetch_related('subtasks', 'assignees').filter(
        Q(assignees=request.user) | Q(supervisor=request.user)
    ).distinct().order_by('track_code', 'due_date')

    today = timezone.now().date()
    timeline_days = [today + timedelta(days=i) for i in range(10)]

    track_summary = []
    tracks = [
        {'code': 'A', 'title': 'Design & UX Track', 'color': '#3B82F6'},
        {'code': 'B', 'title': 'Core Backend & API', 'color': '#8B5CF6'},
        {'code': 'C', 'title': 'Database & Infrastructure', 'color': '#EC4899'},
        {'code': 'D', 'title': 'DevOps & Quality Assurance', 'color': '#F59E0B'},
    ]
    for tr in tracks:
        tr_tasks = tasks.filter(track_code=tr['code'])
        total = tr_tasks.count()
        done = tr_tasks.filter(status=Task.Status.DONE).count()
        avg_progress = tr_tasks.aggregate(Avg('progress'))['progress__avg'] or 0
        track_summary.append({
            'code': tr['code'],
            'title': tr['title'],
            'color': tr['color'],
            'total_tasks': total,
            'done_tasks': done,
            'progress': int(avg_progress),
            'tasks': tr_tasks
        })

    upcoming_tasks = tasks.exclude(status=Task.Status.DONE).order_by('due_date')

    context = {
        'tasks': tasks,
        'timeline_days': timeline_days,
        'track_summary': track_summary,
        'upcoming_tasks': upcoming_tasks,
        'today': today,
        'active_menu': 'planning',
    }
    return render(request, 'tasks/planning.html', context)


@login_required(login_url='tasks:login')
@require_POST
def plan_milestone(request):
    """Create a scheduled milestone/task directly from Planning page assigned to active user."""
    title = request.POST.get('title', '').strip()
    if title:
        track_code = request.POST.get('track_code', 'A').upper()
        start_date = request.POST.get('start_date') or timezone.now().date()
        due_date = request.POST.get('due_date') or timezone.now().date()
        priority = request.POST.get('priority', Task.Priority.HIGH)
        status = request.POST.get('status', Task.Status.IN_PROGRESS)

        color_map = {'A': '#3B82F6', 'B': '#8B5CF6', 'C': '#EC4899', 'D': '#F59E0B'}
        track_color = color_map.get(track_code, '#3B82F6')

        task = Task.objects.create(
            title=title,
            track_code=track_code,
            track_color=track_color,
            start_date=start_date,
            due_date=due_date,
            status=status,
            priority=priority,
            progress=0
        )
        task.assignees.add(request.user)

        subtasks_raw = request.POST.get('subtasks', '').strip()
        if subtasks_raw:
            for line in subtasks_raw.splitlines():
                if line.strip():
                    SubTask.objects.create(task=task, title=line.strip())

    return redirect('tasks:planning')


@login_required(login_url='tasks:login')
@require_POST
def update_task_schedule(request, task_id):
    """Edit target start and due dates for an existing task from Planning."""
    task = get_object_or_404(Task, id=task_id)
    start_date = request.POST.get('start_date')
    due_date = request.POST.get('due_date')
    track_code = request.POST.get('track_code')
    progress = request.POST.get('progress')

    if start_date:
        task.start_date = start_date
    if due_date:
        task.due_date = due_date
    if track_code:
        task.track_code = track_code
        color_map = {'A': '#3B82F6', 'B': '#8B5CF6', 'C': '#EC4899', 'D': '#F59E0B'}
        task.track_color = color_map.get(track_code, task.track_color)
    if progress is not None and progress.isdigit():
        task.progress = min(100, max(0, int(progress)))

    task.save()
    return redirect('tasks:planning')


@login_required(login_url='tasks:login')
def analytics_view(request):
    """Personalized Analytics & Performance Reports for Active User."""
    tasks = Task.objects.prefetch_related('subtasks').filter(
        Q(assignees=request.user) | Q(supervisor=request.user)
    ).distinct()

    total_tasks = tasks.count()
    done_tasks = tasks.filter(status=Task.Status.DONE).count()
    in_progress_tasks = tasks.filter(status=Task.Status.IN_PROGRESS).count()
    editing_tasks = tasks.filter(status=Task.Status.EDITING).count()
    draft_tasks = tasks.filter(status=Task.Status.DRAFT).count()

    completion_rate = int((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    avg_progress = int(tasks.aggregate(Avg('progress'))['progress__avg'] or 0)

    status_breakdown = [
        {'label': 'Done', 'count': done_tasks, 'pct': int((done_tasks/total_tasks*100)) if total_tasks else 0, 'color': '#10B981'},
        {'label': 'In Progress', 'count': in_progress_tasks, 'pct': int((in_progress_tasks/total_tasks*100)) if total_tasks else 0, 'color': '#3B82F6'},
        {'label': 'Editing', 'count': editing_tasks, 'pct': int((editing_tasks/total_tasks*100)) if total_tasks else 0, 'color': '#8B5CF6'},
        {'label': 'Draft', 'count': draft_tasks, 'pct': int((draft_tasks/total_tasks*100)) if total_tasks else 0, 'color': '#94A3B8'},
    ]

    track_performance = []
    track_meta = {
        'A': {'name': 'UX & Frontend', 'lead': request.user.get_full_name() or request.user.username},
        'B': {'name': 'API & Core Logic', 'lead': request.user.get_full_name() or request.user.username},
        'C': {'name': 'Database Optimization', 'lead': request.user.get_full_name() or request.user.username},
        'D': {'name': 'CI/CD & DevOps', 'lead': request.user.get_full_name() or request.user.username},
    }
    for code, meta in track_meta.items():
        tr_tasks = tasks.filter(track_code=code)
        tr_total = tr_tasks.count()
        tr_done = tr_tasks.filter(status=Task.Status.DONE).count()
        tr_progress = int(tr_tasks.aggregate(Avg('progress'))['progress__avg'] or 0)
        
        total_subs = SubTask.objects.filter(task__in=tr_tasks).count()
        completed_subs = SubTask.objects.filter(task__in=tr_tasks, is_completed=True).count()

        track_performance.append({
            'code': code,
            'name': meta['name'],
            'lead': meta['lead'],
            'total_tasks': tr_total,
            'done_tasks': tr_done,
            'progress': tr_progress,
            'subtasks_ratio': f"{completed_subs}/{total_subs}",
            'health': 'On Track' if tr_progress >= 70 else ('In Motion' if tr_progress >= 40 else 'Needs Attention'),
            'health_color': 'emerald' if tr_progress >= 70 else ('blue' if tr_progress >= 40 else 'amber')
        })

    recent_tasks = tasks.order_by('-updated_at')[:8]

    context = {
        'total_tasks': total_tasks,
        'done_tasks': done_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': completion_rate,
        'avg_progress': avg_progress,
        'status_breakdown': status_breakdown,
        'track_performance': track_performance,
        'recent_tasks': recent_tasks,
        'active_menu': 'analytics',
    }
    return render(request, 'tasks/analytics.html', context)


@login_required(login_url='tasks:login')
def messages_view(request):
    """Team activity discussions and message stream."""
    context = {
        'active_menu': 'messages',
    }
    return render(request, 'tasks/messages.html', context)


@login_required(login_url='tasks:login')
@require_POST
def update_task_status(request, task_id):
    """HTMX endpoint to quickly change task status or progress."""
    task = get_object_or_404(Task, id=task_id)
    new_status = request.POST.get('status')
    if new_status in Task.Status.values:
        task.status = new_status
        if new_status == Task.Status.DONE:
            task.progress = 100
        task.save()
    return render(request, 'tasks/partials/task_card.html', {'task': task})


@login_required(login_url='tasks:login')
@require_POST
def toggle_subtask(request, subtask_id):
    """HTMX endpoint to toggle subtask completion and recalculate task progress."""
    subtask = get_object_or_404(SubTask, id=subtask_id)
    subtask.is_completed = not subtask.is_completed
    subtask.save()

    parent_task = subtask.task
    total = parent_task.total_subtasks_count
    if total > 0:
        completed = parent_task.completed_subtasks_count
        parent_task.progress = int((completed / total) * 100)
        parent_task.save()

    if request.headers.get('HX-Request'):
        return render(request, 'tasks/partials/task_card.html', {'task': parent_task})
    return redirect(request.META.get('HTTP_REFERER', 'tasks:dashboard'))


@login_required(login_url='tasks:login')
@require_POST
def add_subtask(request, task_id):
    """HTMX endpoint to add a new subtask directly from a task card or detail page."""
    task = get_object_or_404(Task, id=task_id)
    title = request.POST.get('title', '').strip()
    if title:
        SubTask.objects.create(task=task, title=title, is_completed=False)
        total = task.total_subtasks_count
        completed = task.completed_subtasks_count
        task.progress = int((completed / total) * 100) if total > 0 else 0
        task.save()

    if request.headers.get('HX-Request'):
        return render(request, 'tasks/partials/task_card.html', {'task': task})
    return redirect('tasks:task_detail', task_id=task.id)


@login_required(login_url='tasks:login')
@require_POST
def create_task(request):
    """Quick task creation modal handler."""
    title = request.POST.get('title', '').strip()
    if title:
        description = request.POST.get('description', '').strip()
        track_code = request.POST.get('track_code', 'A').upper()
        status = request.POST.get('status', Task.Status.DRAFT)
        priority = request.POST.get('priority', Task.Priority.MEDIUM)
        
        color_map = {'A': '#3B82F6', 'B': '#8B5CF6', 'C': '#EC4899', 'D': '#F59E0B'}
        track_color = color_map.get(track_code, '#3B82F6')
        
        task = Task.objects.create(
            title=title,
            description=description,
            track_code=track_code,
            track_color=track_color,
            status=status,
            priority=priority,
            progress=0
        )

        assignee_id = request.POST.get('assignee')
        if assignee_id:
            task.assignees.add(assignee_id)
        else:
            task.assignees.add(request.user)

        subtasks_raw = request.POST.get('subtasks', '').strip()
        if subtasks_raw:
            for line in subtasks_raw.splitlines():
                if line.strip():
                    SubTask.objects.create(task=task, title=line.strip(), is_completed=False)

    return redirect(request.META.get('HTTP_REFERER', 'tasks:dashboard'))


@login_required(login_url='tasks:login')
@require_POST
def delete_task(request, task_id):
    """Delete task action."""
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect(request.META.get('HTTP_REFERER', 'tasks:dashboard'))

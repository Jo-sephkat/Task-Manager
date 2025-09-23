from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse, HttpResponse
from .models import Subject, Class
from .forms import CustomUserCreationForm, SubjectForm, ClassForm
import json
from django.core import serializers
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('timetable:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'timetable/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('timetable:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'timetable/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('timetable:login')

@login_required
def dashboard(request):
    subjects = Subject.objects.filter(user=request.user)
    classes = Class.objects.filter(subject__user=request.user)
    return render(request, 'timetable/dashboard.html', {
        'subjects': subjects,
        'classes': classes
    })

@login_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.user = request.user
            subject.save()
            return redirect('timetable:dashboard')
    else:
        form = SubjectForm()
    return render(request, 'timetable/add_subject.html', {'form': form})



@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, user=request.user)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('timetable:dashboard')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'timetable/add_subject.html', {
        'form': form,
        'editing': True,
        'subject': subject
    })

@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, user=request.user)
    
    if request.method == 'POST':
        subject.delete()
        return redirect('timetable:dashboard')
    
    return render(request, 'timetable/delete_subject.html', {
        'subject': subject
    })

@login_required
def add_class(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, user=request.user)
    
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.subject = subject
            class_obj.save()
            return redirect('timetable:dashboard')
    else:
        form = ClassForm()
    
    return render(request, 'timetable/add_class.html', {
        'form': form,
        'subject': subject
    })

@login_required
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id, subject__user=request.user)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            return redirect('timetable:dashboard')
    else:
        form = ClassForm(instance=class_obj)
    
    return render(request, 'timetable/add_class.html', {
        'form': form,
        'subject': class_obj.subject,
        'editing': True,
        'class_obj': class_obj
    })

@login_required
def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id, subject__user=request.user)
    
    if request.method == 'POST':
        class_obj.delete()
        return redirect('timetable:dashboard')
    
    return render(request, 'timetable/delete_class.html', {
        'class_obj': class_obj
    })

@login_required
def timetable_view(request):
    subjects = Subject.objects.filter(user=request.user)
    classes = Class.objects.filter(subject__user=request.user).select_related('subject')
    
    # Prepare classes data for JavaScript
    classes_data = []
    for class_obj in classes:
        classes_data.append({
            'id': class_obj.id,
            'day': class_obj.get_day_display(),
            'startTime': class_obj.start_time.strftime('%H:%M'),
            'endTime': class_obj.end_time.strftime('%H:%M'),
            'subject': class_obj.subject.name,
            'location': class_obj.location,
            'instructor': class_obj.instructor,
            'color': class_obj.subject.color
        })
    
    classes_json = json.dumps(classes_data)
    # Check if PDF export is requested
    if request.GET.get('export_pdf'):
        return generate_timetable_pdf(classes, request.user)
    
    return render(request, 'timetable/timetable_view.html', {
        'subjects': subjects,
        'classes': classes,
        'classes_json': classes_json
    })

def generate_timetable_pdf(classes, user):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title = Paragraph(f"{user.username}'s Weekly Timetable", styles['Title'])
    elements.append(title)
    
    # Prepare data for the table
    data = [['Day', 'Time', 'Subject', 'Location', 'Instructor']]
    
    for class_obj in classes:
        data.append([
            class_obj.get_day_display(),
            f"{class_obj.start_time.strftime('%H:%M')} - {class_obj.end_time.strftime('%H:%M')}",
            class_obj.subject.name,
            class_obj.location,
            class_obj.instructor
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='timetable.pdf')   




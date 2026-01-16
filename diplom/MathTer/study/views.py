from django.http import HttpResponse
from .models import Course
from .forms import CourseForm
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from .serializers import CourseSerializer
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm

def index(request):
    return render(request, 'study/index.html')

# Список всех курсов
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

# Создание нового курса
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form, 'action': 'Создать'})

# Редактирование курса
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form, 'action': 'Изменить'})

# Удаление курса
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'course_delete.html', {'course': course})

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

def my_view(request):
    grades = range(5, 13)
    return render(request, 'my_template.html', {'grades': grades})

from django.shortcuts import render

def index(request):
    return render(request, "study/index.html")

def register(request):
    return render(request, "study/register.html")

def dashboard_student(request):
    return render(request, "study/dashboard_student.html")

def dashboard_teacher(request):
    return render(request, "study/dashboard_teacher.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("study:dashboard_redirect")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("study:dashboard_redirect")

    return render(request, "study/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("study:dashboard_redirect")

    form = LoginForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("study:dashboard_redirect")

    return render(request, "study/login.html", {"form": form})


@login_required
def dashboard_redirect(request):
    if request.user.role == "student":
        return redirect("study:dashboard_student")
    elif request.user.role == "teacher":
        return redirect("study:dashboard_teacher")
    return redirect("study:home")


@login_required
def dashboard_student(request):
    if request.user.role != "student":
        return redirect("study:dashboard_redirect")
    return render(request, "study/dashboard_student.html")


@login_required
def dashboard_teacher(request):
    if request.user.role != "teacher":
        return redirect("study:dashboard_redirect")
    return render(request, "study/dashboard_teacher.html")


def logout_view(request):
    logout(request)
    return redirect("study:home")

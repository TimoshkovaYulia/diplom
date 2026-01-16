from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet
from . import views




urlpatterns = [
    path("", views.index, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/student/", views.dashboard_student, name="dashboard_student"),
    path("dashboard/teacher/", views.dashboard_teacher, name="dashboard_teacher"),
]

# router = DefaultRouter()
# router.register(r'courses', CourseViewSet)

# urlpatterns = router.urls

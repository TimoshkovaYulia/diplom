from django.contrib import admin
from django.urls import include, path
from study import views

urlpatterns = [
    path("study/", include("study.urls")),
    path("admin/", admin.site.urls),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('api/', include('study.urls')), 
]

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("study/", include("study.urls")),
    path("admin/", admin.site.urls),
]
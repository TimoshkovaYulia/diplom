from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet
from . import views



# urlpatterns = [
#     path("", views.index, name="index"),
# ]

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = router.urls

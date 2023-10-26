from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.document_upload, name="document_upload"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path("download/<int:id>/", views.download_file, name="download_file"),
]

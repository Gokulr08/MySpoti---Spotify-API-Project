# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]

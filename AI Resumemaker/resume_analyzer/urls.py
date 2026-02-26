from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('dashboard/<int:analysis_id>/', views.dashboard, name='dashboard'),
    path('analyses/', views.analysis_list, name='analysis_list'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('test-db/', views.test_db, name='test_db'),
]
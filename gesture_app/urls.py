from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Assuming you have an index view
    path('process_frame/', views.process_frame, name='process_frame'),
    # Add other URL patterns as needed
]

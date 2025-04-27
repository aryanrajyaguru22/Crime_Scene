# # urls.py

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.submit_report, name='submit_report'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Index page
    path('generate_report/', views.generate_report, name='generate_report'),  # Report generation
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    # path('view-mongo-file/<str:file_id>/', views.view_mongo_file, name='view_mongo_file'),
]

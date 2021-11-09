from django.urls import path

from . import views
from django.conf.urls import url

urlpatterns = [   
    path('translate', views.index, name='index'),
]

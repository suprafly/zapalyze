from django.conf.urls import include, url
from django.contrib import admin

from API import views


urlpatterns = [
    # API Get calls
    url(r'^get_task_data/$', views.get_task_data, name='get_task_data'),
]
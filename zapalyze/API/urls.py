from django.conf.urls import include, url
from django.contrib import admin

from API import views


urlpatterns = [
    # API Get calls
    url(r'^get_task_data_tsv/$', views.get_task_data_tsv, name='get_task_data_tsv'),
    url(r'^get_task_data_table_json/$', views.get_task_data_table_json, name='get_task_data_table_json'),
]
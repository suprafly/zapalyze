from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

# json imports
import json
import csv
import gviz_api
import datetime

# Models
from main.models import Zap, TaskSummary

# -------- Helpers/Functions ---------------------------------------------------------------------

range_of_datetimes = lambda start_date, day_range: [(start_date + datetime.timedelta(days=x)) for x in range(0, day_range)]
equal_length_filled_list = lambda this_list, fill_value: [fill_value for x in range(0, len(this_list))]

def get_json_data_table(schema, data):
    data_table = gviz_api.DataTable(schema)
    data_table.LoadData(data)
    return data_table.ToJSon()

def get_formatted_rows(dates, zaps, data):
    day_range = (dates[-1] - dates[0]).days + 1
    rows = []
    for date in range_of_datetimes(dates[0], day_range):
        new_row = [date.strftime('%b %d, %Y')] + equal_length_filled_list(zaps, 0)
        for i in range(len(zaps)):
            if data[zaps[i]]:
                if date in data[zaps[i]]:
                    new_row[i+1] = data[zaps[i]][date]
        rows.append(new_row)
    return rows

# -------- APIs ---------------------------------------------------------------------------------

def get_task_data_table_json(request):
    user = request.user
    ctx = { 'username': user.username }
    if user.is_authenticated():
        if request.method == 'GET':
            data = {}
            dates = []
            zaps = []
            for task_summary in TaskSummary.objects.filter(owner=user).order_by('date'):
                date = task_summary.date
                if date not in dates:
                    dates.append(date)

                zap_name = task_summary.zap.name
                if zap_name not in zaps:
                    zaps.append(zap_name)

                task_count = task_summary.number_of_tasks
                if zap_name not in data:
                    entry = { date: task_count }
                    data[zap_name] = entry
                else:
                    entry = data[zap_name]
                    entry[date] = task_count
                    data[zap_name] = entry

            type_list = ['string'] + equal_length_filled_list(zaps, 'number')
            rows = get_formatted_rows(dates, zaps, data)
            resp = get_json_data_table(zip(["Date"] + zaps, type_list), rows)
            return HttpResponse(resp, content_type="application/json")            

    # Fall through: Send them back to the main page
    return redirect('main.views.index')    

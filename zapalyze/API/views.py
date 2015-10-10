from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader

# json imports
import json
import csv
import gviz_api
import datetime

# Models
from main.models import Zap, TaskSummary


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

            row1 = ["Date"] + zaps
            type_list = ['string'] + ['number' for x in range(len(zaps))]
            rows = []
            day_range = (dates[-1] - dates[0]).days + 1
            dates = [(dates[0] + datetime.timedelta(days=x)) for x in range(0, day_range)]
            for date in dates:
                new_row = [date.strftime('%b %d, %Y')] + [0 for x in range(0, len(zaps))]
                for i in range(len(zaps)):
                    if data[zaps[i]]:
                        if date in data[zaps[i]]:
                            new_row[i+1] = data[zaps[i]][date]
                rows.append(new_row)

            data_table = gviz_api.DataTable(zip(row1, type_list))
            data_table.LoadData(rows)
            resp = data_table.ToJSon()
            return HttpResponse(resp, content_type="application/json")            

    else:
        # Send them back to the main page
        template = loader.get_template('main/index.html')
        return render(request, 'main/index.html', ctx)    




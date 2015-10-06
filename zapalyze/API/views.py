from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader

# json imports
import json
import csv

# Models
from main.models import Zap, TaskSummary


def get_task_data(request):
    user = request.user
    ctx = { 'username': user.username }
    if user.is_authenticated():
        if request.method == 'GET':
            if request.GET['task_data']:
                csv_response = HttpResponse(content_type='text/csv')
                csv_response['Content-Disposition'] = 'attachment; filename="task_data.tsv"'        
                writer = csv.writer(csv_response, delimiter='\t')

                row1 = ['Date', 'Zap', 'Task Count']
                rows = [row1]
                for task_summary in TaskSummary.objects.filter(owner=user).order_by('date'):
                    date = task_summary.date
                    zap_name = task_summary.zap.name
                    task_count = task_summary.number_of_tasks
                    new_row = [date, zap_name, task_count]
                    rows.append(new_row)

                for row in rows:
                    writer.writerow(row)
                return csv_response
    else:
        # Send them back to the main page
        template = loader.get_template('main/index.html')
        return render(request, 'main/index.html', ctx)    




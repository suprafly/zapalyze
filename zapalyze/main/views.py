from __future__ import division
from django.shortcuts import render, render_to_response

from social.backends.google import GoogleOAuth2
from django.template.context import RequestContext
import requests
import json
import base64
import email
import datetime
import re

from main.models import Zap, TaskSummary

# -------- Helpers -------------------------------------------------------------------------------

format_YYMMDD = lambda datetime_obj: datetime_obj.strftime('%Y/%m/%d')
format_daterange = lambda from_date, until_date: "after:%s before:%s" % (format_YYMMDD(from_date), format_YYMMDD(until_date))
tuple_list_from_adjacent_elements = lambda this_list: zip(this_list[0::2], this_list[1::2])
filter_email_list = lambda msg: filter(None, (msg.split('\n'))) # Remove newlines and empty strings
parse_email_by_template = lambda email_list, template: [x for x in email_list if x not in template]
extract_task_count = lambda task_str: task_str.split(' ')[1] # Use on strings with the format: 'automated 5 tasks'
text_only_payload = lambda payload_list: payload_list[0] # format of payload_list = [text_paylod, html_payload]
ms_to_sec = lambda ms: float(ms) / 1000

email_template = [
    "Learn how Zapier saved you time today",
    "Your Daily Activity",
    "View full task history",
    "See My Daily Zap Recommendations",
    "You can change the frequency of these emails in your notification settings .",
    "Just reply to this email if you need help or have questions.",
    "Thank you for using Zapier!",
    "- Mike Knoop, Co-Founder and Chief Product Officer",
    "P.S. I'd love to learn how much time Zapier saves you. If you want to help me out, click here .",
    "Hey, we're hiring!",
    "\xc2\xa9 2015 Zapier, Inc. All rights reserved.",
    "243 Buena Vista Ave #508, Sunnyvale, CA 94086",
    "Read the Blog",
    "Follow on Twitter",
    "Unsubscribe",
    "makes you happier :)"
]

# -------- Functions ------------------------------------------------------------------------------

def get_all_historical_daily_summaries(user, social):
    daterange_str = "before: %s" % format_YYMMDD(datetime.date.today())
    return get_daily_task_summary_list(user, social, daterange_str)

def get_daily_task_summary_list(user, social, daterange_str):
    mime_messages = []
    if daterange_str is None:
        # No range specified is the default case, so get them all
        daterange_str = "before: %s" % format_YYMMDD(datetime.date.today())
    api_str = 'https://www.googleapis.com/gmail/v1/users/me/messages?q="in:inbox from:\"contact@zapier.com\" %s subject:\"Your Daily Task Summary\""' % daterange_str
    response = requests.get( api_str, params={'access_token': social.extra_data['access_token']} )
    if response:
        if 'messages' in response.json():
            mime_messages = get_mime_messages(social, response.json()['messages'])
        else:
            # No messages returned
            pass
    else:
        # No response returned
        pass
    return mime_messages

def get_mime_messages(social, json_msgs):
    '''
        Return a list of tuples of the type: (mime_msg, timestamp)
    '''
    messages = []
    for msg in json_msgs:
        email_response = requests.get(
            'https://www.googleapis.com/gmail/v1/users/me/messages/%s' % msg['id'],
            params={'access_token': social.extra_data['access_token'], 'format': 'RAW'}
        )
        msg = email_response.json()
        msg_str = base64.urlsafe_b64decode(email_response.json()['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)
        timestamp = get_timestamp_from_email_subject(msg_str)
        messages.append((mime_msg, timestamp))
    return messages

def get_internal_date_timestamp(json_response):
    '''
        This is the date that Google received the email.
    '''
    epoch_secs = ms_to_sec(json_response['internalDate'])
    return datetime.datetime.fromtimestamp(epoch_secs)

def get_timestamp_from_email_subject(email_msg_str):
    '''
        This is the date for the Task Summary, stripped from the subject line.
    '''
    match = re.search('Subject: Your (\S*) Task Summary for ([\S \d]*)', email_msg_str)
    task_summary_date = match.group(2)
    return datetime.datetime.strptime(task_summary_date, '%b %d, %Y')

def get_email_payload_list(task_summary_email):
    payload_list = []
    if task_summary_email.is_multipart():
        for payload in task_summary_email.get_payload():
            payload_list.append(payload.get_payload(decode=True))
    else:    
        payload_list.append(task_summary_email.get_payload(decode=True))
    return payload_list

def get_parsed_email(email_msg):
    filtered_email_list = filter_email_list(email_msg)
    parsed_email = parse_email_by_template(filtered_email_list, email_template)
    return remove_uncaught_text(parsed_email)

def remove_uncaught_text(parsed_email):
    # Remove: 'Hey *, here's how Zapier saved you time over the past day.'
    parsed_email.pop(0)
    return parsed_email

def create_zaps_and_task_summaries(user, zap_task_tuple_list, timestamp):
    for zap_name, task_str in zap_task_tuple_list:
        number_of_tasks = extract_task_count(task_str)
        task_date = timestamp.date()
        zap = None
        if not Zap.objects.filter(owner=user, name=zap_name).exists():
            zap = Zap(owner=user, name=zap_name)
            zap.save()
        else:
            zap = Zap.objects.get(owner=user, name=zap_name)
        if not TaskSummary.objects.filter(owner=user, zap=zap, date=task_date).exists():
            new_task_summary = TaskSummary(owner=user, zap=zap, date=task_date, number_of_tasks=number_of_tasks)
            new_task_summary.save() 
             
# -------- Views --------------------------------------------------------------------------------

def index(request):
    user = request.user
    ctx = { 'request': request, 
            'user': user
            }
    context = RequestContext(request, ctx)

    if user.is_authenticated():
        social = user.social_auth.get(provider='google-oauth2')
        task_summary_list = []    
        if user.last_login.date() == user.date_joined.date():
            task_summary_list = get_all_historical_daily_summaries(user, social)
        else:
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            task_summary_list = get_daily_task_summary_list(user, social, format_daterange(yesterday, today))

        for task_summary_email, timestamp in task_summary_list:
            email_msg = text_only_payload(get_email_payload_list(task_summary_email))
            parsed_email = get_parsed_email(email_msg)
            total_automated_tasks = parsed_email.pop(0)
            zap_task_tuple_list = tuple_list_from_adjacent_elements(parsed_email)
            create_zaps_and_task_summaries(user, zap_task_tuple_list, timestamp)
        return render_to_response('main/chart.html', context_instance=context)
    else:
        return render_to_response('main/index.html', context_instance=context)



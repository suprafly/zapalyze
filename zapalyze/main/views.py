from django.shortcuts import render, render_to_response

from django.template.context import RequestContext
import requests
import json
import base64
import email
import datetime


format_YYMMDD = lambda datetime_obj: datetime_obj.strftime('%Y/%m/%d')
format_daterange = lambda from_date, until_date: "after:%s before:%s" % (format_YYMMDD(from_date), format_YYMMDD(until_date))

def get_daily_task_summary_list(user, social, daterange_str=None):
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
            #! Logger: No messages returned
            pass
    else:
        #! Logger: No response
        pass
    return mime_messages

def get_mime_messages(social, json_msgs):
    messages = []
    for msg in json_msgs:
        email_response = requests.get(
            'https://www.googleapis.com/gmail/v1/users/me/messages/%s' % msg['id'],
            params={'access_token': social.extra_data['access_token'], 'format': 'RAW'}
        )
        msg = email_response.json()
        msg_str = base64.urlsafe_b64decode(email_response.json()['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)
        messages.append(mime_msg)
    return messages

# -------- Views --------------------------------------------------------------------------------

def index(request):
    user = request.user
    if user.is_authenticated():
        social = user.social_auth.get(provider='google-oauth2')
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        task_summary_list = get_daily_task_summary_list(user, social, format_daterange(yesterday, today))

        for task_summary_email in task_summary_list:
            payload_list = []
            if task_summary_email.is_multipart():
                for payload in task_summary_email.get_payload():
                    decoded_payload = payload.get_payload(decode=True)
                    payload_list.append(decoded_payload)
            else:
                payload_list.append(task_summary_email.get_payload(decode=True))

            print payload_list[0]

    ctx = {'request': request, 'user': user}
    context = RequestContext(request, ctx)
    return render_to_response('main/index.html', context_instance=context)



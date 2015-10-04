from django.shortcuts import render, render_to_response

from django.template.context import RequestContext
import requests
import json
import base64
import email


def index(request):
    user = request.user
    if user.is_authenticated():
        social = user.social_auth.get(provider='google-oauth2')
        response = requests.get(
            'https://www.googleapis.com/gmail/v1/users/me/messages?q="in:sent after:2015/10/01 before:2015/10/03"',
            params={'access_token': social.extra_data['access_token']}
        )
        json_msg = response.json()['messages']
        for msg in json_msg:
            m_id = msg['id']

            email_response = requests.get(
                'https://www.googleapis.com/gmail/v1/users/me/messages/%s' % m_id,
                params={'access_token': social.extra_data['access_token'], 'format': 'RAW'}
            )
            msg = email_response.json()
            msg_str = base64.urlsafe_b64decode(email_response.json()['raw'].encode('ASCII'))
            mime_msg = email.message_from_string(msg_str)
            print mime_msg

    ctx = {'request': request, 'user': user}
    context = RequestContext(request, ctx)
    return render_to_response('main/index.html', context_instance=context)



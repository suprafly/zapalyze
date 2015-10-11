from django.core.files.base import ContentFile
from social.backends.google import GoogleOAuth2
import urllib2

from main.models import UserProfile

# Custom Social Auth Pipeline functions

def get_user_avatar(strategy, *args, **kwargs):
    user = kwargs['user']
    backend = kwargs['backend']
    response = kwargs['response']

    user_profile = None
    if not UserProfile.objects.filter(user=user).exists():
        user_profile = UserProfile(user=user)
    else:   # Already exists, just return.        
        return    

    if isinstance(backend, GoogleOAuth2):
        if response.get('image') and response['image'].get('url'):
            url = response['image'].get('url')
            ext = url.split('.')[-1]
            user_profile.avatar.save(
               '{0}.{1}'.format('avatar', ext),
               ContentFile(urllib2.urlopen(url).read()),
               save=False
            )
    user_profile.save()


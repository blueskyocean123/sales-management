from .models import LoginExpire

import datetime


def login_expire(request):
    if LoginExpire.objects.all().exists():
        expire_msg = LoginExpire.objects.all()[:1].get()
        date_remaining = (expire_msg.expire_date - datetime.date.today()).days
        return {
            'expire_msg': expire_msg,
            'date_remaining': date_remaining
        }
    else:
        return {'none': 'none'}
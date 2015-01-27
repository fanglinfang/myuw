from django.http import HttpRequest
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import logging
from userservice.user import get_user
from myuw_mobile.dao.pws import is_student
from myuw_mobile.logger.timer import Timer
from myuw_mobile.logger.logresp import log_invalid_netid_response
from myuw_mobile.logger.logresp import log_response_time
from myuw_mobile.views.rest_dispatch import invalid_session


@login_required
def user_login(request):
    timer = Timer()
    logger = logging.getLogger('myuw_mobile.views.mobile_login.user_login')

    netid = get_user(request)
    if netid is None:
        log_invalid_netid_response(logger, timer)
        return invalid_session()

    if is_student():
        log_response_time(logger, 'to mobile', timer)
        return redirect("myuw_mobile.views.page.index")

    log_response_time(logger, 'to desktop', timer)

    if hasattr(settings, "MYUW_USER_SERVLET_URL"):
        return redirect(settings.MYUW_USER_SERVLET_URL)
    else:
        return redirect("https://myuw.washington.edu/servlet/user")

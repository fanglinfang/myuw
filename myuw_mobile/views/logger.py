from django.http import HttpResponse
import logging
from myuw_mobile.logger.logback import log_info


def log_interaction(request, interaction_type):
    logger = logging.getLogger('myuw_mobile.views.logger')

    if interaction_type is not None:
        log_info(request, logger, "Interaction: %s" % interaction_type)

    return HttpResponse()

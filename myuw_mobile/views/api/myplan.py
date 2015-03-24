from django.http import HttpResponse
import json
from myuw_mobile.views.rest_dispatch import RESTDispatch, data_not_found
from restclients.myplan import get_plan
from restclients.sws.section import get_section_by_label
from myuw_mobile.dao.pws import get_regid_of_current_user
from myuw_mobile.dao.term import get_current_quarter
import logging

logger = logging.getLogger(__name__)


class MyPlan(RESTDispatch):
    """
    Performs actions on /api/v1/myplan
    """

    def GET(self, request, year, quarter):
        try:
            plan = get_plan(regid=get_regid_of_current_user(),
                            year=year,
                            quarter=quarter,
                            terms=1)

            base_json = plan.json_data()

            for course in base_json["terms"][0]["courses"]:
                if course["registrations_available"]:
                    for section in course["sections"]:
                        curriculum = course["curriculum_abbr"].upper()
                        section_id = section["section_id"].upper()
                        label = "%s,%s,%s,%s/%s" % (
                                                    year,
                                                    quarter.lower(),
                                                    curriculum,
                                                    course["course_number"],
                                                    section_id
                                                    )

                        sws_section = get_section_by_label(label)
                        section["section_data"] = sws_section.json_data()
            return HttpResponse(json.dumps(base_json))
        except Exception as ex:
            # Log the error, but don't have the front end complain
            print ex
            logger.error(ex)
            return HttpResponse('[]')

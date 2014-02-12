from django.http import HttpResponse
from django.utils import simplejson as json
from myuw_mobile.views.rest_dispatch import RESTDispatch
from myuw_mobile.dao.sws import Quarter, Schedule
from restclients.sws import SWS
from restclients.pws import PWS
from operator import itemgetter
from userservice.user import UserService


class Grades(RESTDispatch):
    """
    Handles /api/v1/grades/
    """
    def GET(self, request, year=None, quarter=None):
        """
        Returns grades for a given term.  If no term is given, the current
        term is used.
        """
        schedule_dao = Schedule()
        quarter_dao = Quarter()

        if year and quarter:
            term = quarter_dao.get_term(year, quarter.lower())
        else:
            term = quarter_dao.get_cur_quarter()

        if term is not None:
            schedule = schedule_dao.get_schedule(term)

        if schedule is None or not schedule.json_data():
            log_data_not_found_response(logger, timer)
            return HttpResponse({})

        colors = schedule_dao.get_colors_for_schedule(schedule)

        username = UserService().get_user()
        regid = PWS().get_person_by_netid(username).uwregid

        final_grades = SWS().grades_for_regid_and_term(regid, term)

        grade_by_section_label = {}
        for grade in final_grades.grades:
            grade_by_section_label[grade.section.section_label()] = grade

        json_data = schedule.json_data()

        section_index = 0
        for section in schedule.sections:
            section_label = section.section_label()
            section_data = json_data["sections"][section_index]
            color = colors[section_label]

            section_data["color_id"] = color

            if section_label in grade_by_section_label:
                grade_data = grade_by_section_label[section_label]
                section_data["official_grade"] = grade_data.grade

            section_index += 1

        json_data["sections"] = sorted(json_data["sections"],
                                   key=itemgetter('curriculum_abbr',
                                                  'course_number',
                                                  'section_id',
                                                  ))


        return HttpResponse(json.dumps(json_data), { "Content-Type": "application/json" })

    def _add_grades(self, source_data, section_data, section_label, source_key, source_name):
        if section_label in source_data:
            section_grades = source_data[section_label]

            data = []

            for grades in section_grades:
                data.append(grades.json_data())

            if not "assignments" in section_data:
                section_data["assignments"] = []

            section_data["assignments"].append({
                "source_id": source_key,
                "source_name": source_name,
                "data": data
            })

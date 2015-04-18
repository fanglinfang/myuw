from restclients.iasystem import evaluation
from myuw_mobile.dao.student_profile import get_profile_of_current_user
from restclients.exceptions import DataFailureException
from restclients.pws import PWS
import simplejson as json




def get_evaluations_by_section(section):
    profile = get_profile_of_current_user()
    return _get_evaluations_by_section_and_student(section, profile.student_number)

def _get_evaluations_by_section_and_student(section, student_id):
    try:
        return evaluation.search_evaluations(section.course_campus.lower(),
                                             year=section.term.year,
                                             term_name=section.term.quarter.capitalize(),
                                             curriculum_abbreviation=section.curriculum_abbr,
                                             course_number=section.course_number,
                                             section_id=section.section_id,
                                             student_id=student_id)

    except DataFailureException:
        return None

def json_for_evaluation(evaluations):
    json_data = []
    for evaluation in evaluations:
        eval_json = {}
        instructor = PWS().get_person_by_employee_id(evaluation.instructor_id)
        eval_json['instructor_name'] = instructor.display_name
        eval_json['open_date'] = evaluation.eval_open_date.isoformat()
        eval_json['close_date'] = evaluation.eval_close_date.isoformat()
        eval_json['url'] = evaluation.eval_url
        eval_json['is_online'] = evaluation.eval_is_online
        json_data.append(eval_json)


    return json_data


# def get_evaluations_for_student_term(term):
#     profile = get_profile_of_current_user()
#     return _get_evaluation_by_student_number(profile.student_number, term)
#
#
# def _get_evaluation_by_student_number(student_number, term):
#     seattle = None
#     bothell = None
#     tacoma = None
#     try:
#         seattle = evaluation.search_evaluations("seattle",
#                                                 year=term.year,
#                                                 term_name=term.quarter.capitalize(),
#                                                 student_id=student_number)
#     except DataFailureException:
#         pass
#     try:
#         tacoma = evaluation.search_evaluations("tacoma",
#                                                year=term.year,
#                                                term_name=term.quarter.capitalize(),
#                                                student_id=student_number)
#     except DataFailureException:
#         pass
#     try:
#         bothell = evaluation.search_evaluations("bothell",
#                                                 year=term.year,
#                                                 term_name=term.quarter.capitalize(),
#                                                 student_id=student_number)
#     except DataFailureException:
#         pass
#
#     return {'seattle': seattle,
#             'bothell': bothell,
#             'tacoma': tacoma}
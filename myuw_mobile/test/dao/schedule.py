from django.test import TestCase
from django.conf import settings
from myuw_mobile.dao.schedule import _get_schedule
from myuw_mobile.dao.schedule import has_summer_quarter_section
from myuw_mobile.dao.schedule import filter_schedule_sections_by_summer_term
from restclients.models import ClassSchedule, Term, Section, Person

class TestSchedule(TestCase):
    def test_has_summer_quarter_section(self):
        with self.settings(
            RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File', 
            RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):
            regid = "9136CCB8F66711D5BE060004AC494FFE"
            term = Term()
            term.year = 2012
            term.quarter = "summer"
            schedule = _get_schedule(regid, term)
            self.assertTrue(has_summer_quarter_section(schedule))

            term = Term()
            term.year = 2012
            term.quarter = "autumn"
            schedule = _get_schedule(regid, term)
            self.assertFalse(has_summer_quarter_section(schedule))

    def test_filter_schedule_sections_by_summer_term(self):
        with self.settings(
            RESTCLIENTS_SWS_DAO_CLASS='restclients.dao_implementation.sws.File', 
            RESTCLIENTS_PWS_DAO_CLASS='restclients.dao_implementation.pws.File'):
            regid = "9136CCB8F66711D5BE060004AC494FFE"
            term = Term()
            term.year = 2013
            term.quarter = "summer"
            schedule = _get_schedule(regid, term)
            #it has a B-term section
            for section in schedule.sections:
                self.assertFalse(section.summer_term=="A-term")

            filter_schedule_sections_by_summer_term(schedule, "A-term")
            # the B-term section no longer exists
            for section in schedule.sections:
                self.assertFalse(section.summer_term=="B-term")
                self.assertTrue(section.summer_term=="Full-term")

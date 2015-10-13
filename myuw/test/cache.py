from django.test import TestCase
from restclients.mock_http import MockHTTP
from myuw.util.cache_implementation import MyUWCache
from restclients.models import CacheEntryTimed
from datetime import timedelta


CACHE = 'myuw.util.cache_implementation.MyUWCache'


class TestCustomCachePolicy(TestCase):
    def test_sws_default_policies(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"

            response = cache.getCache('sws', '/student/myuwcachetest1', {})
            self.assertEquals(response, None)
            cache.processResponse("sws",
                                  "/student/myuwcachetest1",
                                  ok_response)
            response = cache.getCache('sws', '/student/myuwcachetest1', {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(
                service="sws",
                url="/student/myuwcachetest1")
            # Cached response is returned after 3 hours and 58 minutes
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = (orig_time_saved -
                                      timedelta(minutes=(60 * 4)-2))
            cache_entry.save()

            response = cache.getCache('sws', '/student/myuwcachetest1', {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 4 hours and 1 minute
            cache_entry.time_saved = (orig_time_saved -
                                      timedelta(minutes=(60 * 4)+1))
            cache_entry.save()

            response = cache.getCache('sws', '/student/myuwcachetest1', {})
            self.assertEquals(response, None)

    def test_sws_term_policy(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"

            response = cache.getCache(
                'sws', '/student/v5/term/1014,summer.json', {})
            self.assertEquals(response, None)
            cache.processResponse(
                "sws", "/student/v5/term/1014,summer.json", ok_response)
            response = cache.getCache(
                'sws', '/student/v5/term/1014,summer.json', {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(
                service="sws", url="/student/v5/term/1014,summer.json")
            # Cached response is returned after 6 days
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = orig_time_saved - timedelta(days=6)
            cache_entry.save()

            response = cache.getCache(
                'sws', '/student/v5/term/1014,summer.json', {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 31 days
            cache_entry.time_saved = orig_time_saved - timedelta(days=7)
            cache_entry.save()

            response = cache.getCache(
                'sws', '/student/v5/term/1014,summer.json', {})
            self.assertEquals(response, None)

    def test_myplan_default(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"

            response = cache.getCache('myplan', '/api/plan/xx', {})
            self.assertEquals(response, None)
            cache.processResponse("myplan", "/api/plan/xx", ok_response)
            response = cache.getCache('myplan', '/api/plan/xx', {})
            self.assertEquals(response, None)

    def test_default_policies(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"

            response = cache.getCache('no_such', '/student/myuwcachetest1', {})
            self.assertEquals(response, None)
            cache.processResponse(
                "no_such", "/student/myuwcachetest1", ok_response)
            response = cache.getCache('no_such', '/student/myuwcachetest1', {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(
                service="no_such", url="/student/myuwcachetest1")
            # Cached response is returned after 3 hours and 58 minutes
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = (orig_time_saved -
                                      timedelta(minutes=(60 * 4)-2))
            cache_entry.save()

            response = cache.getCache('no_such', '/student/myuwcachetest1', {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 4 hours and 1 minute
            cache_entry.time_saved = (orig_time_saved -
                                      timedelta(minutes=(60 * 4)+1))
            cache_entry.save()

            response = cache.getCache('no_such', '/student/myuwcachetest1', {})
            self.assertEquals(response, None)

    def test_sws_current_term_policy(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"
            url = '/student/v5/term/current.json'
            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)
            cache.processResponse("sws", url, ok_response)
            response = cache.getCache('sws', url, {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(service="sws", url=url)
            # Cached response is returned after 23 hours
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = orig_time_saved - timedelta(hours=23)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 24 hours
            cache_entry.time_saved = orig_time_saved - timedelta(days=1)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)

    def test_sws_enrollment_policy(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"
            url = "%s%s" % (
                '/student/v5/enrollment/',
                '2013_spring_12345678901234567890123456789012.json')
            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)
            cache.processResponse("sws", url, ok_response)
            response = cache.getCache('sws', url, {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(service="sws", url=url)
            # Cached response is returned within one hour
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=59)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 24 hours
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=60)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)

    def test_sws_registration_policy(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"
            url = "%s%s" % (
                '/student/v5/registration/2013_spring_',
                'ARCTIC_200_A_12345678901234567890123456789012_.json')
            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)
            cache.processResponse("sws", url, ok_response)
            response = cache.getCache('sws', url, {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(service="sws", url=url)
            # Cached response is returned within 15 minutes
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=14)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 15 minutes
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=15)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)

    def test_sws_course_policy(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
            cache = MyUWCache()
            ok_response = MockHTTP()
            ok_response.status = 200
            ok_response.data = "xx"
            url = '/student/v5/course/2013_spring_ARCTIC_200/A.json'
            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)
            cache.processResponse("sws", url, ok_response)
            response = cache.getCache('sws', url, {})
            self.assertEquals(response["response"].data, 'xx')

            cache_entry = CacheEntryTimed.objects.get(service="sws", url=url)
            # Cached response is returned within 60 minutes
            orig_time_saved = cache_entry.time_saved
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=59)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertNotEquals(response, None)

            # Cached response is not returned after 60 minutes
            cache_entry.time_saved = orig_time_saved - timedelta(minutes=60)
            cache_entry.save()

            response = cache.getCache('sws', url, {})
            self.assertEquals(response, None)

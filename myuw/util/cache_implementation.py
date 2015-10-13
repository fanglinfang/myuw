from restclients.cache_implementation import TimedCache
import re


FIFTEEN_MINS = 60 * 15
ONE_HOUR = 60 * 60
FOUR_HOURS = 60 * 60 * 4
ONE_DAY = 60 * 60 * 24
ONE_WEEK = 60 * 60 * 24 * 7


class MyUWCache(TimedCache):

    def getCache(self, service, url, headers):
        if "myplan" == service:
            return self._NoCache(url, headers)

        if "sws" == service:
            return self._getSWScache(url, headers)

        return self._FourHourCache(service, url, headers)

    def _NoCache(self, url, headers):
        return None

    def _FifteenMinCache(self, service, url, headers):
        return self._response_from_cache(service, url, headers, FIFTEEN_MINS)

    def _FourHourCache(self, service, url, headers):
        return self._response_from_cache(service, url, headers, FOUR_HOURS)

    def _OneHourCache(self, service, url, headers):
        return self._response_from_cache(service, url, headers, ONE_HOUR)

    def _OneDayCache(self, service, url, headers):
        return self._response_from_cache(service, url, headers, ONE_DAY)

    def _OneWeekCache(self, service, url, headers):
        return self._response_from_cache(service, url, headers, ONE_WEEK)

    def _getSWScache(self, url, headers):
        if re.match('^/student/v5/term/current', url):
            return self._OneDayCache('sws', url, headers)

        if re.match('^/student/v5/term', url):
            return self._OneWeekCache('sws', url, headers)

        if re.match('^/student/v5/course', url):
            return self._OneHourCache('sws', url, headers)

        if re.match('^/student/v5/enrollment', url):
            return self._OneHourCache('sws', url, headers)

        if re.match('^/student/v5/notice', url):
            return self._OneHourCache('sws', url, headers)

        if re.match('^/student/v5/registration', url):
            return self._FifteenMinCache('sws', url, headers)

        # person, AccountBalance
        return self._FourHourCache('sws', url, headers)

    def processResponse(self, service, url, response):
        return self._process_response(service, url, response)

# -*- coding: utf-8 -*-
from datetime import date, datetime
import re
from django.http.response import JsonResponse
from django.views import View

from analytics.tasks import save_page_analytics


class AnalyticsView(View):
    def __get_headers(self, request):
        regex_http_ = re.compile(r'^HTTP_.+$')
        regex_content_type = re.compile(r'^CONTENT_TYPE$')
        regex_content_length = re.compile(r'^CONTENT_LENGTH$')

        request_headers = {}
        for header in request.META:
            if regex_http_.match(header) or regex_content_type.match(header) \
                    or regex_content_length.match(header):
                request_headers[header] = request.META[header]
        return request_headers

    def __get_query_string(self, request):
        query_string = {}
        query = request.get_full_path().split('?')[0]
        params = query.split('&')
        for a_string in params:
            key, value = a_string.split('=')
            query_string.update({key: value})

        return query_string

    def get(self, request):
        now = datetime.now()
        try:
            headers = self.__get_headers(request)
            session_id = request.session.session_key
            data = dict(headers=headers, session_id=session_id,
                        domain=request.GET.get('domain', ''),
                        url=request.GET.get('url', ''),
                        title=request.GET.get('title', ''),
                        referrer=request.GET.get('ref', ''),
                        ip=request.META['REMOTE_ADDR'],
                        timestamp=now)
            save_page_analytics(data)
            return JsonResponse({'message': 'Ok'}, status=200)
        except Exception as e:
            return JsonResponse({'Error': e}, status=400)

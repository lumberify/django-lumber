import json
from lumber.handler import Handler

from django.shortcuts import get_object_or_404, render
from django.http.response import Http404, HttpResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from rest_framework import authentication, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from lumber.models import App, LogEntry

class AppView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'lumber/app.html')

class LogView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, dsn):
        body = None
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            return HttpResponse(status=400)
        app = get_object_or_404(App, pk=dsn)
        try:
            Handler.handle(app, body)
        except ValueError as value_error:
            return Response({
                'status': 'ERROR',
                'error': str(value_error),
            }, status=400)

        return Response({
            'status': 'OK',
        }, status=200)


class AppsApiView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = {}
        response['status'] = 'OK'
        response['apps'] = []
        for app in App.objects.filter(owner=request.user):
            response['apps'].append({
                'id': app.id,
                'name': app.name,
            })
        return Response(response)


class Filter:
    LEVEL = 'level'

    IN = 'in'

    def __init__(self, column, operand, value):
        self.column = column
        self.operand = operand
        self.value = value

    def __repr__(self) -> str:
        return f'{self.column} {self.operand} "{self.value}"'

    @classmethod
    def parse(cls, filters):
        parsed = []
        for entry in filters:
            parts = entry.split(',')
            column = parts.pop(0)
            operand = parts.pop(0)
            value = ','.join(parts)
            if column not in [Filter.LEVEL]:
                raise ValueError(f'Invalid column {column}')
            if operand not in [Filter.IN]:
                raise ValueError(f'Invalid operand {operand}')
            parsed.append(Filter(column, operand, value))
        return parsed

    @classmethod
    def build(cls, app:App, parsed):
        filter = Q(app=app)
        for entry in parsed:
            if entry.column == Filter.LEVEL:
                if entry.operand == Filter.IN:
                    filter = filter & Q(level__in=entry.value.split(','))
        return filter


class LogsApiView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, app_id):
        app = get_object_or_404(App, pk=app_id)
        if app.owner != request.user:
            raise Http404

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 500))
        end = offset + limit

        # GET FILTERS
        filters = request.GET.getlist('filters', None)
        parsed = Filter.parse(filters)
        filter = Filter.build(app, parsed)

        qs = LogEntry.objects.filter(filter).order_by('-created')
        response = {}
        response['status'] = 'OK'
        response['records'] = []
        response['total'] = len(qs)
        response['size'] = limit
        for entry in qs[offset:end]:
            response['records'].append({
                'id': entry.id,
                'funcname': entry.funcname,
                'level': entry.level,
                'lineno': entry.lineno,
                'message': entry.message if entry.message is not None else entry.msg,
                'name': entry.name,
                'pathname': entry.pathname,
                'process': entry.process,
                'processname': entry.processname,
                'thread': entry.thread,
                'threadname': entry.threadname,
                'created': entry.created,
            })
        return Response(response)


import json
from lumber.handler import Handler

from django.shortcuts import get_object_or_404, render
from django.http.response import Http404, HttpResponse
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin

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
        print(body)
        try:
            Handler.handle(app, body)
        except ValueError as value_error:
            print(f'Failed {str(value_error)}')
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

        response = {}
        response['status'] = 'OK'
        response['records'] = []
        qs = LogEntry.objects.filter(app=app).order_by('-created')
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
                'thread': entry.thread,
                'created': entry.created,
            })
        return Response(response)


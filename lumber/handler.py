import json
from datetime import datetime
from django.utils import timezone
from lumber.models import App, LogEntry


class Handler:
    @classmethod
    def handle(cls, app: App, payload: dict):
        if not isinstance(payload, dict):
            raise ValueError('Invalid payload (E001)')
        if 'records' not in payload:
            raise ValueError('Invalid payload (E002)')
        for record in payload['records']:
            Handler.handle_record(app, record)

    @classmethod
    def handle_record(cls, app: App, record: dict):
        _ = LogEntry.objects.create(
            app=app,
            args=json.dumps(record['args']) if record['args'] else None,
            created=timezone.make_aware(datetime.fromtimestamp(record['created'])),
            excinfo=json.dumps(record['exc_info']) if record['exc_info'] else None,
            funcname=record['funcName'],
            level=record['level'],
            lineno=record['lineno'],
            message=record['message'],
            msg=record['msg'],
            name=record['name'],
            pathname=record['pathname'],
            process=record['process'],
            processname=record['processName'],
            sinfo=json.dumps(record['sinfo']) if record['sinfo'] else None,
            thread=record['thread'],
            threadname=record['threadName'],
            raw=json.dumps(record),
        )

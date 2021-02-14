from lumber.models import App, LogEntry
from django.contrib import admin

DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['short_id', 'id', 'name', 'created_at']

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    ordering = ['-created']
    list_display = ['short_id', 'name', 'levelname', 'entry', 'created']

    def levelname(self, obj):
        if obj.level == DEBUG:
            return 'DEBUG'
        elif obj.level == INFO:
            return 'INFO'
        elif obj.level == WARNING:
            return 'WARNING'
        elif obj.level == ERROR:
            return 'ERROR'
        elif obj.level == CRITICAL:
            return 'CRITICAL'
        return obj.level
    levelname.display_name = 'Level'

    def entry(self, obj):
        return obj.message if obj.message is not None else obj.msg
    entry.display_name = 'Message'

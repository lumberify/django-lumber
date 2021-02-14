import uuid

from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def short_id(self):
        return str(self.id)[:8]

    class Meta:
        abstract = True


class App(BaseModel):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class LogEntry(BaseModel):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    args = models.TextField(blank=True, null=True, default=None)  # JSON
    created = models.DateTimeField()
    excinfo = models.TextField(blank=True, null=True, default=None)  # JSON
    funcname = models.CharField(max_length=128)
    level = models.PositiveIntegerField()
    lineno = models.PositiveIntegerField()
    message = models.TextField(blank=True, null=True, default=None)
    msg = models.TextField()
    name = models.CharField(max_length=128)
    pathname = models.CharField(max_length=1024)
    process = models.PositiveIntegerField(blank=True, null=True, default=None)
    processname = models.CharField(max_length=256, blank=True, null=True, default=None)
    sinfo = models.TextField(blank=True, null=True, default=None) # JSON
    thread = models.PositiveIntegerField(blank=True, null=True, default=None)
    threadname = models.CharField(max_length=256, blank=True, null=True, default=None)

    raw = models.TextField()

    class Meta:
        verbose_name_plural = 'Records'
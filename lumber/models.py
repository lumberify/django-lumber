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
    created = models.DateTimeField(db_index=True)
    excinfo = models.TextField(blank=True, null=True, default=None)  # JSON
    funcname = models.CharField(max_length=128, db_index=True)
    level = models.PositiveIntegerField(db_index=True)
    lineno = models.PositiveIntegerField(db_index=True)
    message = models.TextField(blank=True, null=True, default=None, db_index=True)
    msg = models.TextField(db_index=True)
    name = models.CharField(max_length=128, db_index=True)
    pathname = models.CharField(max_length=1024, db_index=True)
    process = models.PositiveIntegerField(blank=True, null=True, default=None, db_index=True)
    processname = models.CharField(max_length=256, blank=True, null=True, default=None)
    sinfo = models.TextField(blank=True, null=True, default=None) # JSON
    thread = models.PositiveBigIntegerField(blank=True, null=True, default=None, db_index=True)
    threadname = models.CharField(max_length=256, blank=True, null=True, default=None)

    raw = models.TextField()

    class Meta:
        verbose_name_plural = 'Records'
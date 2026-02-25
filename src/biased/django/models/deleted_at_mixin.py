from typing import Self

from django.db import models


class DeletedAtQuerySet(models.QuerySet):
    def not_deleted(self) -> Self:
        return self.filter(deleted_at__isnull=True)


class DeletedAtManager(models.Manager.from_queryset(DeletedAtQuerySet)):  # type: ignore[misc]
    pass


class DeletedAtMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)  # type: ignore[var-annotated]

    objects = DeletedAtManager()

    class Meta:
        abstract = True

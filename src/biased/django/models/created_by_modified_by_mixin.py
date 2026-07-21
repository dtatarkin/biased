from typing import Any

from django.conf import settings
from django.db import models

from biased.django.actor import get_current_actor


class CreatedByModifiedByMixin(models.Model):
    """Audit attribution fields stamped from the current actor (see `biased.django.actor`).

    `created_by` is stamped on insert only and never overwrites an explicitly
    assigned value; `modified_by` is set on every `save()` to the current actor.
    NULL means the save was made by the system: no authenticated request actor
    was bound (Temporal/Celery workers, management commands, anonymous requests).

    Caveats: bulk paths (`queryset.update()`, `bulk_create()`) bypass `save()`
    and stamp nothing — same limitation as `auto_now`. FKs cannot cross
    databases, so only models routed to the same database as
    `settings.AUTH_USER_MODEL` may adopt this mixin.
    """

    created_by = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        editable=False,
        related_name="+",
    )
    modified_by = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        editable=False,
        related_name="+",
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        current_actor = get_current_actor()
        if self._state.adding and self.created_by_id is None:  # type: ignore[attr-defined]
            self.created_by = current_actor
        self.modified_by = current_actor
        super().save(*args, **kwargs)

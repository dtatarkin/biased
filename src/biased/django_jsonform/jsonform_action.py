from admin_form_action import Decorator, form_action
from django import forms
from django.contrib.admin import ModelAdmin


def jsonform_action[FormT: forms.Form, ModelAdminT: ModelAdmin](
    form_class: type[FormT],
    *,
    template: str | None = None,
) -> Decorator[ModelAdminT, FormT]:
    if template is None:
        template = "admin_form_action/django_jsonform_form.html"
    return form_action(form_class=form_class, template=template)

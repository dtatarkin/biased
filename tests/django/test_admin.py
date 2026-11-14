from typing import Any

import pytest
from django.contrib.admin import AdminSite
from django.db import connection, models
from django.http import HttpRequest, HttpResponse

from biased.django.admin import ExternalIdModelAdmin, html_image_tag, url_link


class Account(models.Model):
    external_id = models.CharField(max_length=32)

    class Meta:
        app_label = "biased_django"


@pytest.fixture
def account_table():
    with connection.schema_editor() as editor:
        editor.create_model(Account)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(Account)


class _AccountAdmin(ExternalIdModelAdmin):
    """Records which view the external-id lookup handed over to."""

    def _get_obj_does_not_exist_redirect(self, request, opts, object_id):
        return HttpResponse("missing")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        return HttpResponse(f"change {object_id}")


def _external_id_view(external_id: str) -> bytes:
    model_admin = _AccountAdmin(Account, AdminSite())
    return model_admin.external_id_change_view(HttpRequest(), external_id).content


@pytest.mark.usefixtures("account_table")
def test_external_id_opens_its_object():
    account = Account.objects.create(external_id="ext")
    assert _external_id_view("ext") == f"change {account.pk}".encode()


@pytest.mark.usefixtures("account_table")
def test_unknown_external_id_redirects():
    assert _external_id_view("nope") == b"missing"


@pytest.mark.usefixtures("account_table")
def test_ambiguous_external_id_redirects():
    Account.objects.create(external_id="dup")
    Account.objects.create(external_id="dup")
    assert _external_id_view("dup") == b"missing"


def test_url_link_calls_the_wrapped_method_once():
    calls: list[Any] = []

    @url_link("Site")
    def site(self: Any, obj: Any) -> dict[str, str]:
        calls.append(obj)
        return {"url": "https://example.com/"}

    html = site(None, "row")
    assert calls == ["row"]
    assert html == '<a href="https://example.com/" target="_self">-</a>'


def test_html_image_tag_escapes_attribute_values():
    @html_image_tag("Logo", attributes={"alt": '"><script>', "hidden": True})
    def logo(self: Any, obj: Any) -> str:
        return "/logo.png"

    assert logo(None, "row") == (
        '<img src="/logo.png" alt="&quot;&gt;&lt;script&gt;" hidden/>'
    )

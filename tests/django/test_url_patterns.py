from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path
from django.utils import translation

from biased.django.aws_waf.url_patterns import iter_regex_patterns


def _view(request):
    raise NotImplementedError


_users = [path("users/<int:pk>/", _view)]


def test_path_include():
    assert list(iter_regex_patterns([path("api/", include(_users))])) == [
        (r"^api\/users\/(?P<pk>[0-9]+)\/\Z", "api/users/<int:pk>/")
    ]


def test_re_path_include():
    assert list(iter_regex_patterns([re_path(r"^api/", include(_users))])) == [
        (r"^api\/users\/(?P<pk>[0-9]+)\/\Z", "^api/users/<int:pk>/")
    ]


def test_i18n_patterns_prefix():
    with translation.override("en"):
        assert list(iter_regex_patterns(i18n_patterns(*_users))) == [
            (r"^en\/users\/(?P<pk>[0-9]+)\/\Z", "en/users/<int:pk>/")
        ]

import asyncio

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import override_settings
from django.urls import path

from biased.django.aws_waf.aws_waf_regex_pattern import (
    AwsWafRegexPatternSet,
    validate_aws_waf_regex_patterns,
)
from biased.django.aws_waf.aws_waf_whitelist_middleware import (
    AwsWafWhitelistMiddleware,
)
from biased.django.aws_waf.url_patterns import UrlArgsContext


def _view(request):
    raise NotImplementedError


# Unanchored, as AWS WAF reads it: it matches anywhere in the path.
_UNANCHORED = AwsWafRegexPatternSet(r"users\/[0-9]+\/$")


class _Middleware(AwsWafWhitelistMiddleware):
    aws_waf_regex_pattern_sets = (_UNANCHORED,)

    def build_forbidden_http_response(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("forbidden", status=403)


async def _allowed(request: HttpRequest) -> HttpResponse:
    return HttpResponse("allowed")


def _status(request_path: str) -> int:
    request = HttpRequest()
    request.path = request_path
    with override_settings(ENABLE_AWS_WAF_WHITELIST_MIDDLEWARE=True):
        middleware = _Middleware(_allowed)
    return asyncio.run(middleware(request)).status_code


def test_middleware_matches_an_unanchored_pattern_anywhere_in_the_path():
    assert _status("/api/users/5/") == 200


def test_middleware_still_forbids_a_path_no_pattern_matches():
    assert _status("/api/admin/") == 403


def test_validator_accepts_a_url_an_unanchored_pattern_covers():
    validate_aws_waf_regex_patterns(
        [path("api/users/<int:pk>/", _view)],
        [_UNANCHORED],
        UrlArgsContext(([""], {"pk": 5})),
    )


def test_validator_reports_a_url_no_pattern_covers():
    with pytest.raises(ValueError, match="No AWS WAF pattern found"):
        validate_aws_waf_regex_patterns(
            [path("api/admin/", _view)],
            [_UNANCHORED],
            UrlArgsContext(([""], {})),
        )

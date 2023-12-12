# Copyright 2023 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test for the ccx_messaging.utils.sentry module."""

import pytest
import logging

from ccx_messaging.utils.sentry import get_event_level

@pytest.mark.parametrize(
        "osenv, want",
        [
            ("False", logging.ERROR),
            ("false", logging.ERROR),
            ("0", logging.ERROR),
            ("no", logging.ERROR),
            ("No", logging.ERROR),
            ("foobar", logging.ERROR),
            ("True", logging.WARNING),
            ("true", logging.WARNING),
            ("1", logging.WARNING),
            ("Yes", logging.WARNING),
            ("yes", logging.WARNING),
        ])
def test_get_event_level(monkeypatch, osenv, want):
    """Check get_event_level returns logging.WARNING just if the SENTRY_CATCH_WARNINGS is set."""

    monkeypatch.setenv("SENTRY_CATCH_WARNINGS", osenv)
    got = get_event_level()
    assert got is want, f"got {got} want {want}"

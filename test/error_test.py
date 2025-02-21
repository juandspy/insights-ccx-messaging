# Copyright 2020 Red Hat, Inc
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

"""Tests for error classes."""

from ccx_messaging.error import CCXMessagingError


input_msg = {
    "topic": "topic name",
    "partition": "partition name",
    "offset": 1234,
    "url": "any/url",
    "identity": {"identity": {"internal": {"org_id": "12345678"}}},
    "timestamp": "2020-01-23T16:15:59.478901889Z",
    "cluster_name": "clusterName",
}


def test_error_formatting():
    """Test the error formatting."""
    err = CCXMessagingError("CCXMessagingError")
    assert err is not None

    fmt = err.format(input_msg)
    expected = (
        "Status: Error; Topic: topic name; Cause: CCXMessagingError"
    )
    assert fmt == expected

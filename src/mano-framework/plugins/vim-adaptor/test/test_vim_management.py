"""
Copyright (c) 2017 Pishahang
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of Pishahang, nor the names of its contributors
may be used to endorse or promote products derived from this software
without specific prior written permission.
"""

from uuid import uuid4

import pytest
from pytest_voluptuous import Partial, S
from voluptuous import All, Contains

from manobase.messaging import ManoBrokerRequestResponseConnection as Connection
from vim_adaptor.main import VimAdaptor
from vim_adaptor.models.vims import AwsVim, BaseVim


@pytest.fixture
def mocked_aws_resource_utilization(mocker):
    mocker.patch(
        "vim_adaptor.models.vims.AwsVim.get_resource_utilization"
    ).return_value = {}


def test_add_vim(
    adaptor: VimAdaptor, connection: Connection, mocked_aws_resource_utilization
):
    def add_vim(payload: dict):
        response = connection.call_sync(
            "infrastructure.management.compute.add", payload
        )
        assert response is not None
        return response.payload

    assert S(
        {"request_status": "ERROR", "message": All(str, Contains("type"))}
    ) == add_vim({})

    assert S(
        {
            "request_status": "ERROR",
            "message": All(str, Contains("city"), Contains("access_key")),
        }
    ) == add_vim({"type": "aws"})

    # Add OpenStack with missing tenant.external_network_id and
    # tenant.external_router_id
    assert S(
        {
            "request_status": "ERROR",
            "message": All(
                str, Contains("external_network_id"), Contains("external_router_id")
            ),
        }
    ) == add_vim(
        {
            "type": "openstack",
            "name": "OpenStack",
            "country": "my country",
            "city": "my city",
            "username": "my username",
            "password": "my password",
            "tenant": {"id": "tenant id"},
        }
    )

    assert S({"request_status": "COMPLETED", "id": str}) == add_vim(
        {
            "type": "aws",
            "name": "aws",
            "country": "my country",
            "city": "my city",
            "access_key": "access key",
            "secret_key": "secret key",
            "region": "region",
        }
    )


@pytest.fixture
def example_vim():
    return AwsVim(
        type="aws",
        country="my country",
        name="aws",
        city="my city",
        access_key="access key",
        secret_key="secret key",
        region="region",
    )


def test_list_vims(
    adaptor: VimAdaptor,
    connection: Connection,
    example_vim: AwsVim,
    mocked_aws_resource_utilization,
):
    BaseVim.objects.delete()

    def list_vims():
        response = connection.call_sync("infrastructure.management.compute.list")
        assert response is not None
        return response.payload

    assert [] == list_vims()

    example_vim.save()

    assert (
        S(
            [
                Partial(
                    {
                        "id": str(example_vim.id),
                        "name": example_vim.name,
                        "country": example_vim.country,
                        "city": example_vim.city,
                        "type": example_vim.type,
                    }
                )
            ]
        )
        == list_vims()
    )


def test_delete_vim(adaptor: VimAdaptor, connection: Connection, example_vim: AwsVim):
    BaseVim.objects.delete()

    def delete_vim(payload: dict):
        response = connection.call_sync(
            "infrastructure.management.compute.remove", payload
        )
        assert response is not None
        return response.payload

    error_schema = S({"request_status": "ERROR", "message": str})

    assert error_schema == delete_vim({})

    assert error_schema == delete_vim({"id": "1234"})

    assert error_schema == delete_vim({"id": str(uuid4())})

    example_vim.save()
    assert {"request_status": "COMPLETED"} == delete_vim({"id": str(example_vim.id)})

    assert 0 == len(BaseVim.objects)

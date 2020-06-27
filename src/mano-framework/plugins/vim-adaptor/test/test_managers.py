from pathlib import Path

from pyfakefs.fake_filesystem import FakeFilesystem

from vim_adaptor.managers.base import TerraformFunctionManager
from vim_adaptor.models.vims import BaseVim


def test_initialization(mocker, fs: FakeFilesystem):
    mocker.patch("vim_adaptor.managers.base.TerraformFunctionManager._tf_init")
    fs.create_file(
        "/my-template-dir/template.tf",
        contents=(
            "Descriptor Id: {{ descriptor.id }}\n"
            "Function Id: {{ function_id }}\n"
            "Function Instance Id: {{ function_instance_id }}\n"
            "Service Id: {{ service_id }}\n"
            "Service Instance Id: {{ service_instance_id }}"
        ),
    )

    vim = BaseVim(name="MyVIM", country="country", city="city", type="AWS")

    manager = TerraformFunctionManager(
        Path("/my-template-dir"),
        vim,
        "service-id",
        "service-instance-id",
        "function-id",
        "function-instance-id",
        {"id": "descriptor-id", "name": "descriptor-name"},
    )

    # Template(s) should have been compiled
    assert manager._work_dir.exists()
    target_file: Path = manager._work_dir / "template.tf"
    assert target_file.exists()
    with target_file.open() as f:
        assert (
            "Descriptor Id: descriptor-id\n"
            "Function Id: function-id\n"
            "Function Instance Id: function-instance-id\n"
            "Service Id: service-id\n"
            "Service Instance Id: service-instance-id"
        ) == f.read()

    # _tf_init should have been called
    manager._tf_init.assert_called()

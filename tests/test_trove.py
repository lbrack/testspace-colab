import pytest
import pathlib
import json
import testspace_colab.trove as trove_module
import testspace_colab.lib as lib_module


@pytest.fixture(scope="session")
def a_result():
    return lib_module.API().get_result_details("test_data")


@pytest.fixture()
def fake_trove(tmpdir, a_result):
    count = 0
    for org in ["org_1", "org_2"]:
        org_path = tmpdir.mkdir(org)
        for project in ["project_1", "project_2"]:
            project_path = org_path.mkdir(project)
            for space in ["space_1", "space_2"]:
                space_path = project_path.mkdir(space)
                with open(
                    str(space_path.join(f"result_{count}.json")), "w"
                ) as file_handle:
                    json.dump(a_result, file_handle)
                count += 1
    return count


def test_basic(tmpdir):
    assert (
        trove_module.Trove().path == pathlib.Path("~").expanduser() / "testspace-colab"
    )
    assert trove_module.Trove(tmpdir).path == pathlib.Path(tmpdir)

    trove = trove_module.Trove()
    assert trove.org is None
    trove.org = "foo"
    assert trove.org == "foo"
    trove.org = None
    assert trove.org is None


def test_organizations(tmpdir):
    for dirname in trove_module.Trove(tmpdir).organizations():
        assert False, f"should never enter the look {dirname}"
    dirs = ["a", "b"]
    for dir in dirs:
        tmpdir.mkdir(dir)
    for dirname in trove_module.Trove(tmpdir).organizations():
        dirs.remove(dirname)
    assert len(dirs) == 0


def test_load(fake_trove, tmpdir):
    trove = trove_module.Trove(tmpdir)
    for result in trove.load():
        assert isinstance(result, dict)
        fake_trove -= 1
    assert fake_trove == 0

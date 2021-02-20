import os
import pathlib
import pytest
import testspace_colab.elk as elk_module
import testspace_colab.ts_log

logger = testspace_colab.ts_log.get_logger("pytest.conftest")

# We use the configuration in the test directory - and avoid using the
# one from the user
config = pathlib.Path(__file__).parent / ".config" / "test"
os.environ["TS_COLAB_CONFIG_DIR"] = str(config)
print(f"setting test config dir {os.environ['TS_COLAB_CONFIG_DIR']}")

ELK_CONTAINER_TEST_NAME = elk_module.CONTAINER_NAME + "_test"


@pytest.fixture(scope="session", autouse=True)
def elk_test_instance():
    elk = elk_module.ELK()
    elk_test = elk_module.ELK(container_name=ELK_CONTAINER_TEST_NAME)
    was_running = False
    if elk.container and elk.container.status == "running":
        logger.info(
            f"Stopping ELK Container {elk.container_name} {elk.container.id} to run the tests"
        )
        was_running = True
        elk.stop()
    yield elk_test
    if elk_test.container:
        if elk_test.container.status == "running":
            elk_test.stop()
        elk_test.container.remove()
    if was_running:
        logger.info(
            f"restarting ORIGINAL ELK Container {elk.container_name} {elk.container.id}"
        )
        elk.start()


@pytest.fixture()
def elk_api(elk_test_instance, elk_state):
    """Sets the ELL docker container in the desired state

    usage::

        @pytest.mark.parametrize("elk_up", [running])
        def test_something(elk_api):
            elk_api.do_something()

    :param elk_state: If set to None, it ensures the container is removed.
                      if set to "running" ensures the container is running
                      if set to clean, ensure that the container is restarted
                      Otherwise ensure the container is stopped
    :return: And instance of testspace_colab.elk.ELK
    """
    elk = elk_module.ELK(elk_test_instance.container_name)
    if not elk_state:  # We stop and remove the container
        elk.stop()
        if elk.container:
            elk.container.remove()
    elif elk_state == "running":  # We keep it running
        if not elk.available:
            elk.stop()
        elk.start()
    elif elk_state == "clean":  # we restart it
        elk.stop()
        elk.start()
    else:  # we just stop it
        if not elk.container:
            # It was never started so we start it to stop it
            elk.start()
        elk.stop()
    yield elk
    pass

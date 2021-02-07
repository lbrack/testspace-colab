import pytest
import testspace_colab.elk as elk_module


class TestELKDocker:
    @pytest.mark.parametrize("elk_state", [None])
    def test_not_instanciated(self, elk_api):
        assert elk_api.container is None
        assert elk_api.get_health() is None
        assert elk_api.available is False
        with pytest.raises(TimeoutError):
            elk_api.wait_for_available(timeout=0.1)

    def test_tag(self):
        elk = elk_module.ELK(elk_tag="1234")
        assert elk.elk_docker_tag == "1234"

    @pytest.mark.parametrize("elk_state", [None, "running", "stopped"])
    def test_start(self, elk_api):
        elk_api.start()
        assert elk_api.container.status == "running"
        assert "cluster_name" in elk_api.get_health()
        elk_api.start()  # This should do nothing

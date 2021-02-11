import os
import pytest
import elasticsearch
import testspace_colab.elk as elk_module


@pytest.mark.skipif(
    "CODESPACES" in os.environ, reason="docker not supported in codespace yet"
)
class TestELKDocker:
    @pytest.mark.parametrize("elk_state", [None])
    def test_not_instanciated(self, elk_api):
        assert elk_api.container is None
        assert elk_api.get_health() is None
        assert elk_api.available is False
        assert elk_api.elastic_search is None
        assert elk_api.es_cluster_client is None
        with pytest.raises(TimeoutError):
            elk_api.wait_for_available(timeout=0.1)
        assert elk_api.stop() is None  # nothing should happen

    def test_tag(self):
        elk = elk_module.ELK(elk_tag="1234")
        assert elk.elk_docker_tag == "1234"

    @pytest.mark.parametrize("elk_state", [None, "running", "stopped"])
    def test_start(self, elk_api):
        elk_api.start()
        assert elk_api.container.status == "running"
        assert "cluster_name" in elk_api.get_health()
        elk_api.start()  # This should do nothing
        assert elk_api.available is True
        elk_api.wait_for_available(
            timeout=0.1
        )  # should return without triggering an exception
        assert isinstance(elk_api.elastic_search, elasticsearch.Elasticsearch)
        assert "tagline" in elk_api.elastic_search.info()

    @pytest.mark.parametrize("elk_state", ["running"])
    def test_stop(self, elk_api):
        assert elk_api.container.status == "running"
        elk_api.stop()
        assert elk_api.container.status == "exited"
        assert elk_api.get_health() is None
        assert elk_api.available is False
        assert elk_api.elastic_search is None
        assert elk_api.es_cluster_client is None

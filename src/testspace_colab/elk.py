""" ELK Client

Provides a client to interact with a ELK stack running in docker.

"""
import time
import docker
import testspace_colab.ts_log
import elasticsearch

logger = testspace_colab.ts_log.get_logger("elk")

CONTAINER_NAME = "elk-testspace-colab"
""" Default container name"""

ELK_TAG = "7.10.0"
""" Default Elastic version

    for more details, see the `sebp/elk <https://hub.docker.com/r/sebp/elk/>`_
    in the docker registry
"""


class ELK:
    """This class control the ELK stack which runs as a docker container.
    The container is based

    :param container_name: To override default container name - for testing
                           only
    """

    def __init__(self, container_name=CONTAINER_NAME, elk_tag=ELK_TAG):
        self._container_name = container_name
        self._docker = docker.from_env()
        self._elastic_search = None
        self._cluster_client = None
        self._elk_tag = elk_tag
        self.container  # To get the status

    @property
    def container_name(self):
        """Returns the name of the container running ELK"""
        return self._container_name

    @property
    def elk_docker_tag(self):
        """Returns the tag use to pull the image"""
        return self._elk_tag

    @property
    def docker(self):
        """Returns an instance to the
        `docker client <https://docker-py.readthedocs.io/en/stable/>`_
        """
        return self._docker

    @property
    def container(self):
        """Returns the a docker container structure if the container exists
        or none otherwise.

        see :class:`docker:docker.models.containers.Container` more details.
        """
        container = None
        try:
            container = self._docker.containers.get(self._container_name)
            if container.status == "running" and not self._elastic_search:
                self._elastic_search = elasticsearch.Elasticsearch()
                self._cluster_client = elasticsearch.client.ClusterClient(
                    self._elastic_search
                )

        except (docker.errors.NotFound, docker.errors.APIError):
            pass

        if container and container.status != "running":
            self._elastic_search = None
            self._cluster_client = None
        return container

    @property
    def elastic_search(self):
        """Returns an instance to the ElasticSearch client if the container
        is running.

        See :class:`elastic:elasticsearch.Elasticsearch`
        """
        return self._elastic_search

    @property
    def es_cluster_client(self):
        """Returns an instance to the ElasticSearch cluster client if the container
        is running.

        See :class:`elastic:elasticsearch.client.ClusterClient`
        """
        return self._cluster_client

    @property
    def available(self):
        """Returns True if the stack is available False otherwise"""
        if self.container is None or self.container.status != "running":
            return False
        try:
            self.get_health()
            return True
        except IOError:
            pass
        return False

    def wait_for_available(self, timeout=15):
        """Waits for the stack to be available

        :param timeout:  Time out in seconds before a timeout exception is raised.
        :raise: TimeoutError if timeout expires
        """
        start_time = time.time()

        if not self.container:
            logger.error("ELK stack not started")
            raise TimeoutError("ELK stack not started")

        while (time.time() - start_time) < (timeout / 2):
            if self.container.status == "running":
                break
        if self.container.status != "running":
            logger.error(self.container)
            raise TimeoutError("Failed to get the ELK container started")

        while True:
            if self.available:
                break
            if (time.time() - start_time) > timeout:
                logger.error("Failed to establish connection with elastic search")
                raise TimeoutError("Failed to access elastic search")
            time.sleep(1.5)
        logger.info("ELK available")

    def get_health(self):
        """Return the json structure returned by the `health` endpoint
        or None if the container is not running

        See :meth:`elastic:elasticsearch.client.ClusterClient.health`

        :raise: IOError if the container is running by the health
                endpoint times out.

        """
        if self.container is None or self.container.status != "running":
            return None
        try:
            return self._cluster_client.health()
        except elasticsearch.exceptions.ConnectionError as error:
            raise IOError(f"Connection to es server timed out {error}")

    def start(self, timeout=15):
        """Starts the ELK container

        If the container is already up, returns right away

        :param timeout: Maximum time to wait to establisg a connection with ELK
        :return: :class:`docker:docker.models.containers.Container` of the running container
        :raises: TimeoutError if timeout has been reached.
        """
        if not self.container:
            logger.info(f"Starting ELK Container {self._container_name}")
            self._docker.containers.run(
                image=f"sebp/elk:{self._elk_tag}",
                name=self._container_name,
                ports={5601: 5601, 9200: 9200, 5044: 5044},
                tty=True,
                detach=True,
            )
            time.sleep(5)
        elif self.container.status != "running":
            logger.info(
                f"Starting existing container - current state {self.container.status}"
            )
            self.container.start()
            time.sleep(5)
        logger.info(f"container id {self.container.id}")
        logger.info("Checking that the stack is up and running")
        self.wait_for_available(timeout)
        return self.container

    def stop(self):
        """Stops the ELK container if any is running

        The container state should be 'exited' but is not
        automatically removed.

        :return: :class:`docker:docker.models.containers.Container` of the running container
        :return: None if not container was running
        """
        if self.container:
            if self.container.status != "exited":
                logger.info("Stopping container")
                self.container.stop()
            logger.debug(f"container status {self.container.status}")
        return self.container

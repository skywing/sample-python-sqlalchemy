from uuid import uuid4
import time
import docker
import pytest



@pytest.fixture(scope='session')
def root_directory(request):
    """Return the project root directory so the docker API can locate the Dockerfile"""
    return str(request.config.rootdir)

@pytest.fixture(scope='session')
def session_uuid() -> str:
    """Return a unique uuid string to provide label to identify the image build for this session"""
    return str(uuid4())

@pytest.fixture(scope='package', autouse=True)
def setup_dvdrental_db_docker_image(session_uuid: str, root_directory: str):
    print(f'Session level - setup dvdrental docker database on module level for session: {session_uuid}')
    client = docker.from_env()
    images = client.images.build(
        path=root_directory,
        tag=f'unit-test-sqlaclchemy:{session_uuid}',
        nocache=True,
        rm=True,
        labels={
            'test-image-tag': f'unit-test-sqlaclchemy:{session_uuid}'
        }
    )
    if len(images) <= 0:
        raise RuntimeError('Docker fails to create the unit-test-sqlalchemy image.')

    dvdrental_db_image = images[0]
    print(f'container image name:tag value: {dvdrental_db_image.labels["test-image-tag"]}')

    container = client.containers.run(
        dvdrental_db_image,
        detach=True,
        environment={
            'POSTGRESQL_ADMIN_PASSWORD': 'postgres'
        },
        ports={
            '5432': '5438'
        }
    )
    """
        The container is in detach mode, it will need 10-15 seconds to create dvd rental database
        and restore the sample data to the dvdrental database
    """
    print('Wait for container initialization for 10 seconds...')
    time.sleep(10)
    yield container

    print('Stopping container...')
    container.stop()
    print('Removing container...')
    container.remove()
    print('Removing image...')
    client.images.remove(dvdrental_db_image.labels["test-image-tag"])

    print('Session level - done with cleaning up docker container and image.')

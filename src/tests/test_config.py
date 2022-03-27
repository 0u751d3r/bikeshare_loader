import pytest
import os
from config import Config

REPLACESTR='base_dir_replaced'


@pytest.fixture(scope='module')
def config_instance():
    return Config(REPLACESTR, os.path.join(os.path.dirname(__file__), 'test_config.yaml'))


@pytest.fixture(scope='module')
def bad_config_instance():
    return Config(REPLACESTR, 'nosuchfile')


def test_config_replace(config_instance):
    assert config_instance.get_config()['test_config']['replaced'] == REPLACESTR


def test_bad_config_replace(bad_config_instance):
    with pytest.raises(FileNotFoundError):
        bad_config_instance.get_config()

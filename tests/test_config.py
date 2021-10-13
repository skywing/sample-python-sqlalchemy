import pytest
from util.configuration import Configuration

def test_config_file_not_found():
    with pytest.raises(FileNotFoundError, match=r'\bFile not found at\b'):
        config = Configuration()
        config.load('./no_such_file.toml')

def test_empty_config_with_no_config_file():
    with pytest.raises(FileNotFoundError):
        config = Configuration()
        config.load('./this_config_not_exists.toml')
        assert config is not None

def test_config_with_wrong_key():
    with pytest.raises(KeyError):
        config = Configuration()
        config.load('./config.toml')
        config.get_config()["No_Such_Key"]


def test_config_config():
    config = Configuration()
    config.load('./config.toml')
    assert len(config.get_config()) > 0
    assert config.get_config_file_path() == './config.toml'

def test_config_project():
    config = Configuration()
    config.load('./config.toml')
    project = config.get_project()
    assert project is not None
    assert project["name"] == "Python Development Baseline Template"
    assert project["description"] == "Just a cookiecutter starter template"
    assert project["version"] == "1.0.0"
    assert project["author"] == "python engineer"

def test_config_nested_environment():
    config = Configuration()
    config.load('./config.toml')
    assert config.get_config()["environment"]["dev"]["env"] == "dev"
    assert config.get_config()["environment"]["test"]["env"] == "test"
    assert config.get_config()["environment"]["production"]["env"] == "production"

def test_config_array_tables():
    config = Configuration()
    config.load('./config.toml')
    assert len(config.get_config()["testers"]) == 2

    tester1 = config.get_config()["testers"][0]
    assert tester1 is not None
    assert tester1["id"] == 1
    assert tester1["username"] == "JohnWick"
    assert tester1["password"] == "SeeYouAt4"

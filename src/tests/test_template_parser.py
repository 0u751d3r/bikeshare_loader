import jinja2.exceptions
import pytest
from template_parser import TemplateParser


@pytest.fixture(scope="module")
def parser_instance():
    return TemplateParser(config={'a': 'b'})


def test_render(parser_instance):
    assert parser_instance.render('{{a}}') == 'b'


def test_render_key_undefined(parser_instance):
    with pytest.raises(jinja2.exceptions.UndefinedError):
        parser_instance.render('{{b}}')

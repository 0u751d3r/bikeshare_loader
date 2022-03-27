from jinja2 import Environment, StrictUndefined


class TemplateParser(object):
    def __init__(self, config):
        self.config = config

    def render(self, template: str) -> str:
        env = Environment(keep_trailing_newline=True,
                          undefined=StrictUndefined)  # StrictUndefined to make it fail in case of errors
        return env.from_string(template, self.config).render()

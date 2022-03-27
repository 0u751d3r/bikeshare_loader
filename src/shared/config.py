import yaml
import os
from template_parser import TemplateParser


class Config(object):
    def __init__(self, baseloc: str, config_location: str):
        self.config_location = config_location
        self.baseloc = baseloc

    def get_config(self) -> dict:
        with open(self.config_location, 'r') as cf:
            config = yaml.safe_load(TemplateParser({'base_dir': self.baseloc}).render(cf.read()))
        return config

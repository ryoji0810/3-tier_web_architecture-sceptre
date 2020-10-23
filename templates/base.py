from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import Dict

from troposphere import Template


class Base(metaclass=ABCMeta):
    def __init__(self, sceptre_user_data: Dict):
        self.sceptre_user_data = sceptre_user_data
        self.tpl = Template()
        self.create_template()

    @abstractmethod
    def create_template(self):
        pass

    def to_yaml(self):
        return self.tpl.to_yaml()

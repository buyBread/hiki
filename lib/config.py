import json
import sys

from typing import Union

class Config():

    def __init__(self):
        try:
            with open("config.json") as fp:
                self.config = json.load(fp)
        except FileNotFoundError:
            sys.exit("Config file doesn't exist.")

    def return_value(self, value) -> Union[str, int]:
        return self.config[value]

"""
Not implemented.
"""

import yaml

class Config():
    def __init__(self, config_file_path):
        self.file_path = config_file_path
        self.params = self.read_configuration_file()
        self.is_logging_enabled = self.parse_logging()
    
    def read_configuration_file(self):
        with open(self.file_path) as file_path:
            params = yaml.safe_load(file_path)
            return params
    
    def parse_logging(self):
        is_logging_enabled = self.params["logging"]
        return is_logging_enabled


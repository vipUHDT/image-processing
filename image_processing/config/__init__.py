"""YAML-backed runtime configuration."""

import yaml


class Config:
    """
    Load package configuration from a YAML file.

    Parameters
    ----------
    config_file_path : str
        Path to the YAML configuration file. Must contain a ``logging`` key.
    """

    def __init__(self, config_file_path):
        self.file_path = config_file_path
        self.params = self.read_configuration_file()
        self.is_logging_enabled = self.parse_logging()

    def read_configuration_file(self):
        """Parse the YAML file and return its contents as a dict."""
        with open(self.file_path) as f:
            return yaml.safe_load(f)

    def parse_logging(self):
        """Return the ``logging`` flag from the configuration."""
        return self.params["logging"]

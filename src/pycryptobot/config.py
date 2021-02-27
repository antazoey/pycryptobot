import click
import json

from pycryptobot.enum import Granularity, SimulationSpeed

_GRANULARITY_KEY = "granularity"
_GRAPHS_KEY = "graphs"


class ConfigParser:
    def __init__(self, path=None):
        self._path = path or "config.json"
        self.crypto_market = None
        self.fiat_market = None
        self.granularity = None
        self.graphs = None
        self.is_live = None
        self.is_verbose = None
        self.sim_speed = None
        self.sell_lower_percent = None
        self.sell_upper_percent = None

        # Setting API keys in the config is supported
        # but it is more secure to use the keyring method
        self.api_url = None
        self.api_key = None
        self.api_secret = None
        self.api_pass = None

    @property
    def keys_are_in_config(self):
        return (
                self.api_url is not None
                and self.api_pass is not None
                and self.api_key is not None
                and self.api_secret is not None
        )

    def _get_config_json(self):
        try:
            with open(self._path) as config_file:
                return json.load(config_file)
        except IOError:
            click.echo("warning: 'config.json' not found.")

    def load_from_local_file(self):
        config = self._get_config_json()
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")
        self.api_pass = config.get("api_pass")
        if "config" not in config:
            return

        config_section = config["config"]
        self.crypto_market = config_section.get("cryptoMarket")
        self.fiat_market = config_section.get("fiatMarket")
        self.granularity = _parse_granularity(config_section)
        self.graphs = _parse_graphs(config_section)
        self.is_live = config_section.get("live", False)
        self.is_verbose = config_section.get("verbose", False)
        self.sim_speed = _parse_simulation_speed(config_section)

        # Only set live when no simulation speed
        if not self.sim_speed:
            self.is_live = config_section.get("live", False)

        self.sell_upper_percent = _parse_sell_upper_percent(config_section)
        self.sell_lower_percent = _parse_sell_lower_percent(config_section)

    @property
    def is_simulation(self):
        return self.sim_speed is not None


def _parse_granularity(config):
    granularity = config.get(_GRANULARITY_KEY)
    if not isinstance(granularity, int) or granularity not in Granularity.all():
        return

    return granularity


def _parse_graphs(config):
    graphs_value = config.get(_GRAPHS_KEY)
    if not isinstance(graphs_value, bool):
        return

    return graphs_value


def _parse_simulation_speed(config):
    sim_speed = config.get("sim")
    if sim_speed and sim_speed in SimulationSpeed.all():
        return sim_speed


def _parse_sell_upper_percent(config):
    value = config.get("sellupperpcnt")
    if value and isinstance(value, int) and 0 < value <= 100:
        return value


def _parse_sell_lower_percent(config):
    value = config.get("selllowerpcnt")
    if value and isinstance(value, int) and -100 <= value < 0:
        return value

class ConfigParser:
    def __init__(self, path=None):
        self._path = path or "config.json"

    def _get_config_json(self):
        with open(self._path) as config_file:
            return json.load(config_file)

    def parse(self):
        try:
            config = self._get_config_json()
            if "config" not in config:
                return

            config_section = config["config"]

            if "cryptoMarket" and "fiatMarket" in config_section:
                crypto_market = config_section["cryptoMarket"]
                fiat_market = config_section["fiatMarket"]

            if "granularity" in config_section:
                if isinstance(config_section["granularity"], int):
                    if config_section["granularity"] in [
                        60,
                        300,
                        900,
                        3600,
                        21600,
                        86400,
                    ]:
                        granularity = config["config"]["granularity"]

            if "graphs" in config_section:
                if isinstance(config_section["graphs"], int):
                    if config_section["graphs"] in [0, 1]:
                        save_graphs = config["config"]["graphs"]

            if "live" in config_section:
                if isinstance(config_section["live"], int):
                    if config_section["live"] in [0, 1]:
                        is_live = config["config"]["live"]

            if "verbose" in config_section:
                if isinstance(config_section["verbose"], int):
                    if config_section["verbose"] in [0, 1]:
                        is_verbose = config["config"]["verbose"]

            if "sim" in config_section:
                if isinstance(config_section["sim"], str):
                    if config_section["sim"] in [
                        "slow",
                        "fast",
                        "slow-sample",
                        "fast-sample",
                    ]:
                        is_live = 0
                        is_sim = 1
                        sim_speed = config_section["sim"]

            if "sellupperpcnt" in config_section:
                if isinstance(config_section["sellupperpcnt"], int):
                    if 0 < config_section["sellupperpcnt"] <= 100:
                        sell_upper_pcnt = int(config_section["sellupperpcnt"])

            if "selllowerpcnt" in config["config"]:
                if isinstance(config_section["selllowerpcnt"], int):
                    if -100 <= config_section["selllowerpcnt"] < 0:
                        sell_lower_pcnt = int(config_section["selllowerpcnt"])

        except IOError:
            click.echo("warning: 'config.json' not found.")
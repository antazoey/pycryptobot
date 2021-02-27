import click

from pycryptobot.enum import market_constants
from pycryptobot.enum import Granularity
from pycryptobot.models import SupportingModels
from pycryptobot.simulator import Simulator

granularity_option = click.option(
    "--granularity", "-g",
    type=click.Choice(Granularity.all()),
    help="Desired timeslice in seconds",
    default=3600
)
live_option = click.option(
    "--live", is_flag=True, help="Is the bot live or in test/demo mode"
)
market_option = click.option(
    "--market",
    "-m",
    help="Trading market identifier",
    default="BTC-GBP",
    required=True,
    callback=lambda ctx, param, arg: arg.split("-", 2),
    type=click.Choice(market_constants()),
)
graphs_option = click.option(
    "--graphs", "-g", is_flag=True, help="Save graphs on buy and sell events"
)
simulation_option = click.option(
    "--simulate",
    "--sim",
    is_flag=True,
    help="Run a simulation on last 300 intervals of data",
    callback=lambda ctx, param, arg: Simulator(arg)
)
verbose_option = click.option(
    "--verbose", "-v", is_flag=True, help="Set to display more output"
)
sell_upper_percent_option = click.option(
    "--sell-upper-percent", "--sellupperpcnt", type=int, help="TODO", default=101
)
sell_lower_percent_option = click.option(
    "--sell-lower-percent", "--selllowerpcnt", help="TODO", default=-101
)
pass_state = click.make_pass_decorator(SupportingModels, ensure=True)


def models_option():
    def decorator(f):
        f = pass_state(f)
        return f

    return decorator

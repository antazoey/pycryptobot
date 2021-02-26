import click


granularity_option = click.option(
    "--granularity", "-g", type=int, help="Desired timeslice in seconds", default=3600
)
live_option = click.option(
    "--live", is_flag=True, help="Is the bot live or in test/demo mode"
)
market_option = click.option(
    "--market", "-m", help="Trading market identifier", default="BTC-GBP"
)
graphs_option = click.option(
    "--graphs", "-g", is_flag=True, help="Save graphs on buy and sell events"
)
simulation_option = click.option(
    "--simulate", "--sim", is_flag=True, help="Run a simulation on last 300 intervals of data"
)
verbose_option = click.option(
    "--verbose", "-v", is_flag=True, help="Set to display more output"
)

# TODO: Figure out what sell upper/lower percent actually are
sell_upper_percent_option = click.option(
    "--sell-upper-percent", "--sellupperpcnt", type=int, help="TODO", default=101
)
sell_lower_percent_option = click.option(
    "--sell-lower-percent", "--selllowerpcnt", help="TODO", default=-101
)

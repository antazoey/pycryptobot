# Based on https://github.com/whittlem/pycryptobot/blob/main/models/Trading.py by Michael Whittle.

import math

import click
import numpy as np
import pandas as pd
import re
from statsmodels.tsa.statespace.sarimax import SARIMAX


def _calculate_relative_strength_index(series, interval=14):
    """Calculates the RSI on a Pandas series of closing prices.

    Args:
        series: (pd.Series)
        interval: (int)
    """
    if len(series) < interval:
        raise IndexError("Pandas Series smaller than interval.")

    diff = series.diff(1).dropna()

    sum_gains = 0 * diff
    sum_gains[diff > 0] = diff[diff > 0]
    avg_gains = sum_gains.ewm(com=interval - 1, min_periods=interval).mean()

    sum_losses = 0 * diff
    sum_losses[diff < 0] = diff[diff < 0]
    avg_losses = sum_losses.ewm(com=interval - 1, min_periods=interval).mean()

    rs = abs(avg_gains / avg_losses)
    rsi = 100 - 100 / (1 + rs)

    return rsi


def _is_support(df, index):
    """Checks if a support level."""
    low = df["low"]
    c1 = low[index] < low[index - 1]
    c2 = low[index] < low[index + 1]
    c3 = low[index + 1] < low[index + 2]
    c4 = low[index - 1] < low[index - 2]
    support = c1 and c2 and c3 and c4
    return support


def _is_resistance(df, i):
    """Checks if a resistance level."""
    high = df["high"]
    c1 = high[i] > high[i - 1]
    c2 = high[i] > high[i + 1]
    c3 = high[i + 1] > high[i + 2]
    c4 = high[i - 1] > high[i - 2]
    resistance = c1 and c2 and c3 and c4
    return resistance


def _truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n


class TechnicalAnalysis:
    """A class that performs technical analysis on market data.

    Params:
        df (DataFrame): Expected to have keys `date`, `market`, `granularity`,
          `low`, `high`, `open`, `close`, and `volume`.
    """

    def __init__(self, df):
        self.df = df
        self.levels = None

    def add_all(self):
        """Adds analysis to the DataFrame"""

        self.add_change_percent()

        self.add_cumulative_moving_average()
        self.add_simple_moving_average(20)
        self.add_simple_moving_average(50)
        self.add_simple_moving_average(200)
        self.add_exponential_moving_average(12)
        self.add_exponential_moving_average(26)
        self.add_golden_cross()
        self.add_death_cross()

        self.add_relative_strength_index(14)
        self.add_moving_average_convergence_divergence()
        self.add_on_balance_volume()

        self.add_ema_buy_signals()
        self.add_macd_buy_signals()

        self.add_candle_hammer()
        self.add_candle_inverted_hammer()
        self.add_candle_shooting_star()
        self.add_candle_hanging_man()
        self.add_candle_three_white_soldiers()
        self.add_candle_three_black_crows()
        self.add_candle_doji()
        self.add_candle_three_line_strike()
        self.add_candle_two_black_gapping()
        self.add_candle_morning_star()
        self.add_candle_evening_star()
        self.add_candle_abandoned_baby()
        self.add_candle_morning_doji_star()
        self.add_candle_evening_doji_star()

    """Candlestick References
    https://commodity.com/technical-analysis
    https://www.investopedia.com
    https://github.com/SpiralDevelopment/candlestick-patterns
    https://www.incrediblecharts.com/candlestick_patterns/candlestick-patterns-strongest.php
    """

    def candle_hammer(self):
        return (
            (
                (self.df["high"] - self.df["low"])
                > 3 * (self.df["open"] - self.df["close"])
            )
            & (
                (
                    (self.df["close"] - self.df["low"])
                    / (0.001 + self.df["high"] - self.df["low"])
                )
                > 0.6
            )
            & (
                (
                    (self.df["open"] - self.df["low"])
                    / (0.001 + self.df["high"] - self.df["low"])
                )
                > 0.6
            )
        )

    def add_candle_hammer(self):
        self.df["hammer"] = self.candle_hammer()

    def candle_shooting_star(self):
        return (
            (
                (self.df["open"].shift(1) < self.df["close"].shift(1))
                & (self.df["close"].shift(1) < self.df["open"])
            )
            & (
                self.df["high"] - np.maximum(self.df["open"], self.df["close"])
                >= (abs(self.df["open"] - self.df["close"]) * 3)
            )
            & (
                (np.minimum(self.df["close"], self.df["open"]) - self.df["low"])
                <= abs(self.df["open"] - self.df["close"])
            )
        )

    def add_candle_shooting_star(self):
        self.df["shooting_star"] = self.candle_shooting_star()

    def calculate_candle_hanging_man(self):
        return (
            (
                (self.df["high"] - self.df["low"])
                > (4 * (self.df["open"] - self.df["close"]))
            )
            & (
                (
                    (self.df["close"] - self.df["low"])
                    / (0.001 + self.df["high"] - self.df["low"])
                )
                >= 0.75
            )
            & (
                (
                    (self.df["open"] - self.df["low"])
                    / (0.001 + self.df["high"] - self.df["low"])
                )
                >= 0.75
            )
            & (self.df["high"].shift(1) < self.df["open"])
            & (self.df["high"].shift(2) < self.df["open"])
        )

    def add_candle_hanging_man(self):
        self.df["hanging_man"] = self.calculate_candle_hanging_man()

    def candle_inverted_hammer(self):
        """* Candlestick Detected: Inverted Hammer ("Weak - Continuation - Bullish Pattern - Up")"""

        return (
            (
                (self.df["high"] - self.df["low"])
                > 3 * (self.df["open"] - self.df["close"])
            )
            & (
                (self.df["high"] - self.df["close"])
                / (0.001 + self.df["high"] - self.df["low"])
                > 0.6
            )
            & (
                (self.df["high"] - self.df["open"])
                / (0.001 + self.df["high"] - self.df["low"])
                > 0.6
            )
        )

    def add_candle_inverted_hammer(self):
        self.df["inverted_hammer"] = self.candle_inverted_hammer()

    def calculate_candle_three_white_soldiers(self):
        _open = self.df["open"]
        close = self.df["close"]
        high = self.df["high"]
        return (
            ((_open > _open.shift(1)) & (_open < close.shift(1)))
            & (close > high.shift(1))
            & (high - np.maximum(_open, close) < (abs(_open - close)))
            & ((_open.shift(1) > _open.shift(2)) & (_open.shift(1) < close.shift(2)))
            & (close.shift(1) > high.shift(2))
            & (
                high.shift(1) - np.maximum(_open.shift(1), close.shift(1))
                < (abs(_open.shift(1) - close.shift(1)))
            )
        )

    def add_candle_three_white_soldiers(self):
        self.df["three_white_soldiers"] = self.calculate_candle_three_white_soldiers()

    def calculate_candle_three_black_crows(self):
        return (
            (
                (self.df["open"] < self.df["open"].shift(1))
                & (self.df["open"] > self.df["close"].shift(1))
            )
            & (self.df["close"] < self.df["low"].shift(1))
            & (
                self.df["low"] - np.maximum(self.df["open"], self.df["close"])
                < (abs(self.df["open"] - self.df["close"]))
            )
            & (
                (self.df["open"].shift(1) < self.df["open"].shift(2))
                & (self.df["open"].shift(1) > self.df["close"].shift(2))
            )
            & (self.df["close"].shift(1) < self.df["low"].shift(2))
            & (
                self.df["low"].shift(1)
                - np.maximum(self.df["open"].shift(1), self.df["close"].shift(1))
                < (abs(self.df["open"].shift(1) - self.df["close"].shift(1)))
            )
        )

    def add_candle_three_black_crows(self):
        self.df["three_black_crows"] = self.calculate_candle_three_black_crows()

    def calculate_candle_doji(self):
        return (
            (
                (
                    abs(self.df["close"] - self.df["open"])
                    / (self.df["high"] - self.df["low"])
                )
                < 0.1
            )
            & (
                (self.df["high"] - np.maximum(self.df["close"], self.df["open"]))
                > (3 * abs(self.df["close"] - self.df["open"]))
            )
            & (
                (np.minimum(self.df["close"], self.df["open"]) - self.df["low"])
                > (3 * abs(self.df["close"] - self.df["open"]))
            )
        )

    def add_candle_doji(self):
        self.df["doji"] = self.calculate_candle_doji()

    def calculate_candle_three_line_strike(self):
        return (
            (
                (self.df["open"].shift(1) < self.df["open"].shift(2))
                & (self.df["open"].shift(1) > self.df["close"].shift(2))
            )
            & (self.df["close"].shift(1) < self.df["low"].shift(2))
            & (
                self.df["low"].shift(1)
                - np.maximum(self.df["open"].shift(1), self.df["close"].shift(1))
                < (abs(self.df["open"].shift(1) - self.df["close"].shift(1)))
            )
            & (
                (self.df["open"].shift(2) < self.df["open"].shift(3))
                & (self.df["open"].shift(2) > self.df["close"].shift(3))
            )
            & (self.df["close"].shift(2) < self.df["low"].shift(3))
            & (
                self.df["low"].shift(2)
                - np.maximum(self.df["open"].shift(2), self.df["close"].shift(2))
                < (abs(self.df["open"].shift(2) - self.df["close"].shift(2)))
            )
            & (
                (self.df["open"] < self.df["low"].shift(1))
                & (self.df["close"] > self.df["high"].shift(3))
            )
        )

    def add_candle_three_line_strike(self):
        self.df["three_line_strike"] = self.calculate_candle_three_line_strike()

    def calculate_candle_two_black_gapping(self):
        return (
            (
                (self.df["open"] < self.df["open"].shift(1))
                & (self.df["open"] > self.df["close"].shift(1))
            )
            & (self.df["close"] < self.df["low"].shift(1))
            & (
                self.df["low"] - np.maximum(self.df["open"], self.df["close"])
                < (abs(self.df["open"] - self.df["close"]))
            )
            & (self.df["high"].shift(1) < self.df["low"].shift(2))
        )

    def add_candle_two_black_gapping(self):
        self.df["two_black_gapping"] = self.calculate_candle_two_black_gapping()

    def calculate_candle_morning_star(self):
        """*** Candlestick Detected: Morning Star ("Strong - Reversal - Bullish Pattern - Up")"""

        return (
            (
                np.maximum(self.df["open"].shift(1), self.df["close"].shift(1))
                < self.df["close"].shift(2)
            )
            & (self.df["close"].shift(2) < self.df["open"].shift(2))
        ) & (
            (self.df["close"] > self.df["open"])
            & (
                self.df["open"]
                > np.maximum(self.df["open"].shift(1), self.df["close"].shift(1))
            )
        )

    def add_candle_morning_star(self):
        self.df["morning_star"] = self.calculate_candle_morning_star()

    def calculate_candle_evening_star(self):
        """*** Candlestick Detected: Evening Star ("Strong - Reversal - Bearish Pattern - Down")"""

        return (
            (
                np.minimum(self.df["open"].shift(1), self.df["close"].shift(1))
                > self.df["close"].shift(2)
            )
            & (self.df["close"].shift(2) > self.df["open"].shift(2))
        ) & (
            (self.df["close"] < self.df["open"])
            & (
                self.df["open"]
                < np.minimum(self.df["open"].shift(1), self.df["close"].shift(1))
            )
        )

    def add_candle_evening_star(self):
        self.df["evening_star"] = self.calculate_candle_evening_star()

    def calculate_candle_abandoned_baby(self):
        return (
            (self.df["open"] < self.df["close"])
            & (self.df["high"].shift(1) < self.df["low"])
            & (self.df["open"].shift(2) > self.df["close"].shift(2))
            & (self.df["high"].shift(1) < self.df["low"].shift(2))
        )

    def add_candle_abandoned_baby(self):
        self.df["abandoned_baby"] = self.calculate_candle_abandoned_baby()

    def calculate_candle_morning_doji_star(self):
        return (self.df["close"].shift(2) < self.df["open"].shift(2)) & (
            abs(self.df["close"].shift(2) - self.df["open"].shift(2))
            / (self.df["high"].shift(2) - self.df["low"].shift(2))
            >= 0.7
        ) & (
            abs(self.df["close"].shift(1) - self.df["open"].shift(1))
            / (self.df["high"].shift(1) - self.df["low"].shift(1))
            < 0.1
        ) & (
            self.df["close"] > self.df["open"]
        ) & (
            abs(self.df["close"] - self.df["open"]) / (self.df["high"] - self.df["low"])
            >= 0.7
        ) & (
            self.df["close"].shift(2) > self.df["close"].shift(1)
        ) & (
            self.df["close"].shift(2) > self.df["open"].shift(1)
        ) & (
            self.df["close"].shift(1) < self.df["open"]
        ) & (
            self.df["open"].shift(1) < self.df["open"]
        ) & (
            self.df["close"] > self.df["close"].shift(2)
        ) & (
            (
                self.df["high"].shift(1)
                - np.maximum(self.df["close"].shift(1), self.df["open"].shift(1))
            )
            > (3 * abs(self.df["close"].shift(1) - self.df["open"].shift(1)))
        ) & (
            np.minimum(self.df["close"].shift(1), self.df["open"].shift(1))
            - self.df["low"].shift(1)
        ) > (
            3 * abs(self.df["close"].shift(1) - self.df["open"].shift(1))
        )

    def add_candle_morning_doji_star(self):
        self.df["morning_doji_star"] = self.calculate_candle_morning_doji_star()

    def calculate_candle_evening_doji_star(self):
        return (self.df["close"].shift(2) > self.df["open"].shift(2)) & (
            abs(self.df["close"].shift(2) - self.df["open"].shift(2))
            / (self.df["high"].shift(2) - self.df["low"].shift(2))
            >= 0.7
        ) & (
            abs(self.df["close"].shift(1) - self.df["open"].shift(1))
            / (self.df["high"].shift(1) - self.df["low"].shift(1))
            < 0.1
        ) & (
            self.df["close"] < self.df["open"]
        ) & (
            abs(self.df["close"] - self.df["open"]) / (self.df["high"] - self.df["low"])
            >= 0.7
        ) & (
            self.df["close"].shift(2) < self.df["close"].shift(1)
        ) & (
            self.df["close"].shift(2) < self.df["open"].shift(1)
        ) & (
            self.df["close"].shift(1) > self.df["open"]
        ) & (
            self.df["open"].shift(1) > self.df["open"]
        ) & (
            self.df["close"] < self.df["close"].shift(2)
        ) & (
            (
                self.df["high"].shift(1)
                - np.maximum(self.df["close"].shift(1), self.df["open"].shift(1))
            )
            > (3 * abs(self.df["close"].shift(1) - self.df["open"].shift(1)))
        ) & (
            np.minimum(self.df["close"].shift(1), self.df["open"].shift(1))
            - self.df["low"].shift(1)
        ) > (
            3 * abs(self.df["close"].shift(1) - self.df["open"].shift(1))
        )

    def add_candle_evening_doji_star(self):
        self.df["evening_doji_star"] = self.calculate_candle_evening_doji_star()

    def change_percent(self):
        """Close change percentage"""

        close_pc = self.df["close"].pct_change() * 100
        close_pc = np.round(close_pc.fillna(0), 2)
        return close_pc

    def add_change_percent(self):
        """Adds the close percentage to the DataFrame"""

        self.df["close_pc"] = self.change_percent()

    def cumulative_moving_average(self):
        """Calculates the Cumulative Moving Average (CMA)"""

        return self.df.close.expanding().mean()

    def add_cumulative_moving_average(self):
        """Adds the Cumulative Moving Average (CMA) to the DataFrame"""

        self.df["cma"] = self.cumulative_moving_average()

    def exponential_moving_average(self, period):
        """Calculates the Exponential Moving Average (EMA)"""

        if not isinstance(period, int):
            raise TypeError("Period parameter is not perioderic.")

        if period < 5 or period > 200:
            raise ValueError("Period is out of range")

        if len(self.df) < period:
            raise Exception("Data range too small.")

        return self.df.close.ewm(span=period, adjust=False).mean()

    def add_exponential_moving_average(self, period):
        """Adds the Exponential Moving Average (EMA) the DateFrame"""

        if not isinstance(period, int):
            raise TypeError("Period parameter is not perioderic.")

        if period < 5 or period > 200:
            raise ValueError("Period is out of range")

        if len(self.df) < period:
            raise Exception("Data range too small.")

        self.df["ema" + str(period)] = self.exponential_moving_average(period)

    def moving_average_convergence_divergence(self):
        """Calculates the Moving Average Convergence Divergence (MACD)"""

        if len(self.df) < 26:
            raise Exception("Data range too small.")

        if (
            not self.df["ema12"].dtype == "float64"
            and not self.df["ema12"].dtype == "int64"
        ):
            raise AttributeError(
                "Pandas DataFrame 'ema12' column not int64 or float64."
            )

        if (
            not self.df["ema26"].dtype == "float64"
            and not self.df["ema26"].dtype == "int64"
        ):
            raise AttributeError(
                "Pandas DataFrame 'ema26' column not int64 or float64."
            )

        df = pd.DataFrame()
        df["macd"] = self.df["ema12"] - self.df["ema26"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        return df

    def add_moving_average_convergence_divergence(self):
        """Adds the Moving Average Convergence Divergence (MACD) to the DataFrame"""

        df = self.moving_average_convergence_divergence()
        self.df["macd"] = df["macd"]
        self.df["signal"] = df["signal"]

    def on_balance_volume(self):
        """Calculate On-Balance Volume (OBV)"""

        return np.where(
            self.df["close"] == self.df["close"].shift(1),
            0,
            np.where(
                self.df["close"] > self.df["close"].shift(1),
                self.df["volume"],
                np.where(
                    self.df["close"] < self.df["close"].shift(1),
                    -self.df["volume"],
                    self.df.iloc[0]["volume"],
                ),
            ),
        ).cumsum()

    def add_on_balance_volume(self):
        """Add the On-Balance Volume (OBV) to the DataFrame"""

        self.df["obv"] = self.on_balance_volume()
        self.df["obv_pc"] = self.df["obv"].pct_change() * 100
        self.df["obv_pc"] = np.round(self.df["obv_pc"].fillna(0), 2)

    def calculate_relative_strength_index(self, period):
        """Calculate the Relative Strength Index (RSI)"""

        if not isinstance(period, int):
            raise TypeError("Period parameter is not perioderic.")

        if period < 7 or period > 21:
            raise ValueError("Period is out of range")

        # calculate relative strength index
        rsi = _calculate_relative_strength_index(self.df["close"], period)
        # default to midway-50 for first entries
        rsi = rsi.fillna(50)
        return rsi

    def add_relative_strength_index(self, period):
        """Adds the Relative Strength Index (RSI) to the DataFrame"""

        if not isinstance(period, int):
            raise TypeError("Period parameter is not perioderic.")

        if period < 7 or period > 21:
            raise ValueError("Period is out of range")

        self.df["rsi" + str(period)] = self.calculate_relative_strength_index(period)
        self.df["rsi" + str(period)] = self.df["rsi" + str(period)].replace(np.nan, 50)

    def calculate_seasonal_arima_model(self):
        # parameters for SARIMAX
        model = SARIMAX(
            self.df["close"], trend="n", order=(0, 1, 0), seasonal_order=(1, 1, 1, 12)
        )
        return model.fit(disp=-1)

    def calculate_seasonal_arima_model_fitted_values(self):
        return self.calculate_seasonal_arima_model().fittedvalues

    def calculate_simple_moving_average(self, period):
        if period < 5 or period > 200:
            raise ValueError("Period is out of range")

        elif len(self.df) < period:
            raise Exception("Data range too small.")

        return self.df.close.rolling(period, min_periods=1).mean()

    def add_simple_moving_average(self, period):
        if period < 5 or period > 200:
            raise ValueError("Period is out of range")

        elif len(self.df) < period:
            raise Exception("Data range too small.")

        self.df["sma" + str(period)] = self.calculate_simple_moving_average(period)

    def add_golden_cross(self):
        if "sma50" not in self.df:
            self.add_simple_moving_average(50)

        if "sma200" not in self.df:
            self.add_simple_moving_average(200)

        self.df["goldencross"] = self.df["sma50"] > self.df["sma200"]

    def add_death_cross(self):
        if "sma50" not in self.df:
            self.add_simple_moving_average(50)

        if "sma200" not in self.df:
            self.add_simple_moving_average(200)

        self.df["deathcross"] = self.df["sma50"] < self.df["sma200"]

    def calculate_support_resistance_levels(self):
        self.levels = []
        self._calculate_support_resistance_levels()
        levels_ts = {}
        for level in self.levels:
            levels_ts[self.df.index[level[0]]] = level[1]
        # add the support levels to the DataFrame
        return pd.Series(levels_ts)

    def add_ema_buy_signals(self):
        if (
            not self.df["close"].dtype == "float64"
            and not self.df["close"].dtype == "int64"
        ):
            raise AttributeError(
                "Pandas DataFrame 'close' column not int64 or float64."
            )

        if not "ema12" or not "ema26" in self.df.columns:
            self.add_exponential_moving_average(12)
            self.add_exponential_moving_average(26)

        # true if EMA12 is above the EMA26
        self.df["ema12gtema26"] = self.df.ema12 > self.df.ema26
        # true if the current frame is where EMA12 crosses over above
        self.df["ema12gtema26co"] = self.df.ema12gtema26.ne(
            self.df.ema12gtema26.shift()
        )
        self.df.loc[self.df["ema12gtema26"] == False, "ema12gtema26co"] = False

        # true if the EMA12 is below the EMA26
        self.df["ema12ltema26"] = self.df.ema12 < self.df.ema26
        # true if the current frame is where EMA12 crosses over below
        self.df["ema12ltema26co"] = self.df.ema12ltema26.ne(
            self.df.ema12ltema26.shift()
        )
        self.df.loc[self.df["ema12ltema26"] == False, "ema12ltema26co"] = False

    def add_macd_buy_signals(self):
        if not "close" in self.df.columns:
            raise AttributeError("Pandas DataFrame 'close' column required.")

        elif (
            not self.df["close"].dtype == "float64"
            and not self.df["close"].dtype == "int64"
        ):
            raise AttributeError(
                "Pandas DataFrame 'close' column not int64 or float64."
            )

        if not "macd" or "signal" not in self.df.columns:
            self.add_moving_average_convergence_divergence()
            self.add_on_balance_volume()

        # true if MACD is above the Signal
        self.df["macdgtsignal"] = self.df.macd > self.df.signal
        # true if the current frame is where MACD crosses over above
        self.df["macdgtsignalco"] = self.df.macdgtsignal.ne(
            self.df.macdgtsignal.shift()
        )
        self.df.loc[self.df["macdgtsignal"] == False, "macdgtsignalco"] = False

        # true if the MACD is below the Signal
        self.df["macdltsignal"] = self.df.macd < self.df.signal
        # true if the current frame is where MACD crosses over below
        self.df["macdltsignalco"] = self.df.macdltsignal.ne(
            self.df.macdltsignal.shift()
        )
        self.df.loc[self.df["macdltsignal"] == False, "macdltsignalco"] = False

    def get_fibonacci_retracement_levels(self, price=0):
        price_min = self.df.close.min()
        price_max = self.df.close.max()

        diff = price_max - price_min

        data = {}

        if price != 0 and (price <= price_min):
            data["ratio1"] = float(_truncate(price_min, 2))
        elif price == 0:
            data["ratio1"] = float(_truncate(price_min, 2))

        if price != 0 and (price > price_min) and (price <= (price_max - 0.618 * diff)):
            data["ratio1"] = float(_truncate(price_min, 2))
            data["ratio0_618"] = float(_truncate(price_max - 0.618 * diff, 2))
        elif price == 0:
            data["ratio0_618"] = float(_truncate(price_max - 0.618 * diff, 2))

        if (
            price != 0
            and (price > (price_max - 0.618 * diff))
            and (price <= (price_max - 0.5 * diff))
        ):
            data["ratio0_618"] = float(_truncate(price_max - 0.618 * diff, 2))
            data["ratio0_5"] = float(_truncate(price_max - 0.5 * diff, 2))
        elif price == 0:
            data["ratio0_5"] = float(_truncate(price_max - 0.5 * diff, 2))

        if (
            price != 0
            and (price > (price_max - 0.5 * diff))
            and (price <= (price_max - 0.382 * diff))
        ):
            data["ratio0_5"] = float(_truncate(price_max - 0.5 * diff, 2))
            data["ratio0_382"] = float(_truncate(price_max - 0.382 * diff, 2))
        elif price == 0:
            data["ratio0_382"] = float(_truncate(price_max - 0.382 * diff, 2))

        if (
            price != 0
            and (price > (price_max - 0.382 * diff))
            and (price <= (price_max - 0.286 * diff))
        ):
            data["ratio0_382"] = float(_truncate(price_max - 0.382 * diff, 2))
            data["ratio0_286"] = float(_truncate(price_max - 0.286 * diff, 2))
        elif price == 0:
            data["ratio0_286"] = float(_truncate(price_max - 0.286 * diff, 2))

        if price != 0 and (price > (price_max - 0.286 * diff)) and (price <= price_max):
            data["ratio0_286"] = float(_truncate(price_max - 0.286 * diff, 2))
            data["ratio0"] = float(_truncate(price_max, 2))
        elif price == 0:
            data["ratio0"] = float(_truncate(price_max, 2))

        if price != 0 and (price > price_max) and (price <= (price_max + 0.618 * diff)):
            data["ratio0"] = float(_truncate(price_max, 2))
            data["ratio1_618"] = float(_truncate(price_max + 0.618 * diff, 2))
        elif price == 0:
            data["ratio0"] = float(_truncate(price_max, 2))

        if price != 0 and (price > (price_max + 0.618 * diff)):
            data["ratio1_618"] = float(_truncate(price_max + 0.618 * diff, 2))
        elif price == 0:
            data["ratio1_618"] = float(_truncate(price_max + 0.618 * diff, 2))

        return data

    def save_csv(self, filename="tradingdata.csv"):
        """Saves the DataFrame to an uncompressed CSV."""

        p = re.compile(r"^[\w\-. ]+$")
        if not p.match(filename):
            raise TypeError("Filename required.")

        if not isinstance(self.df, pd.DataFrame):
            raise TypeError("Pandas DataFrame required.")

        try:
            self.df.to_csv(filename)
        except OSError:
            click.echo("Unable to save: ", filename)

    def _calculate_support_resistance_levels(self):
        """Support and Resistance levels. (private function)"""

        for i in range(2, self.df.shape[0] - 2):
            if _is_support(self.df, i):
                low_val = self.df["low"][i]
                if self._is_far_from_level(low_val):
                    self.levels.append((i, low_val))
            elif _is_resistance(self.df, i):
                low_val = self.df["high"][i]
                if self._is_far_from_level(low_val):
                    self.levels.append((i, low_val))
        return self.levels

    def _is_far_from_level(self, level):
        s = np.mean(self.df["high"] - self.df["low"])
        return np.sum([abs(level - x) < s for x in self.levels]) == 0

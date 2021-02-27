from pycryptobot.util import get_attribute_keys_from_class


class Granularity:
    G60 = 60
    G300 = 300
    G900 = 900
    G3600 = 3600
    G21600 = 21600
    G86400 = 86400

    @staticmethod
    def all():
        return get_attribute_keys_from_class(Granularity)


class SimulationSpeed:
    SLOW = "slow"
    FAST = "fast"
    SLOW_SAMPLE = "slow-sample"
    FAST_SAMPLE = "fast-sample"

    @staticmethod
    def all():
        return get_attribute_keys_from_class(SimulationSpeed)


def market_constants():
    def per_fiat(fiat):
        class Market:
            BTC_USD = f"BTC-{fiat}"
            ETH_USD = f"ETH-{fiat}"
            ATOM_USD = f"ATOM-{fiat}"
            CGLD_USD = f"CGLD-{fiat}"
            REN_USD = f"REN-{fiat}"
            REP_USD = f"REP-{fiat}"
            BAT_USD = f"BAT-{fiat}"
            LTC_USD = f"LTC-{fiat}"
            AAVE_USD = f"AAVE-{fiat}"
            MKR_USD = f"MKR-{fiat}"
            ZEC_USD = f"ZEC-{fiat}"

            @staticmethod
            def all():
                return get_attribute_keys_from_class(Market)

        return Market

    return per_fiat(Currency.USD).all() + per_fiat(Currency.GBP).all()


class Currency:
    USD = "USD"
    GBP = "GBP"
    BTC = "BTC"
    ETH = "ETH"
    BAT = "BAT"
    DAI = "DAI"
    ALGO = "ALGO"
    COMP = "COMP"
    CGLD = "CGLD"
    AAVE = "AAVE"
    YFI = "YFI"
    XLM = "XLM"
    USDC = "USDC"
    UNI = "UNI"
    UMA = "UMA"
    SNX = "SNX"
    REN = "REN"
    REP = "REP"
    OXT = "OXT"
    OMG = "OMG"
    NU = "NU"
    NMR = "NMR"
    ZEC = "ZEC"
    MKR = "MKR"
    MANA = "MANA"
    WBTC = "WBTC"

    @staticmethod
    def all():
        return get_attribute_keys_from_class(Currency)


class CBUrl:
    CB_PRO = "https://api.pro.coinbase.com"
    PUBLIC_SANDBOX_1 = "https://api.pro.coinbase.com"
    PUBLIC_SANDBOX_2 = "https://api-public.sandbox.pro.coinbase.com"

    @staticmethod
    def all():
        return get_attribute_keys_from_class(CBUrl)

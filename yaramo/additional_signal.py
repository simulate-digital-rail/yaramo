from enum import Enum
from typing import List, Tuple

from yaramo.base_element import BaseElement


class AdditionalSignal(BaseElement):
    """The baseclass for AddditionalSignals. Subclasses of AddditionalSignal can be referenced by Signals.

    There are AdditionalSignalSymbols associated with each subclass of AdditionalSignal.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def to_serializable(self) -> Tuple[dict, dict]:
        """Creates a two serializable dictionaries out of the AdditionalSignal object.

        This creates a dictionary with immediately serializable attributes.

        See the description in the BaseElement class.

        Returns:
            A serializable dictionary of all attributes.
        """

        base, _ = super().to_serializable()
        return {**base, "symbols": [str(symbol) for symbol in self.symbols]}, {}


class AdditionalSignalZs1(AdditionalSignal):
    def __init__(self, symbols: List["AdditionalSignalSymbolZs1"], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__(self):
        return "AdditionalSignalZs1(kind=Zs1" + ", symbols=" + str(self.symbols) + ")"

    class AdditionalSignalSymbolZs1(Enum):
        Zs1 = 0


class AdditionalSignalZs2(AdditionalSignal):
    def __init__(self, symbols: List["AdditionalSignalSymbolZs2"], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__(self):
        return "AdditionalSignalZs2(kind=Zs2" + ", symbols=" + str(self.symbols) + ")"

    class AdditionalSignalSymbolZs2(Enum):
        A = 0
        B = 1
        C = 2
        D = 3
        E = 4
        F = 5
        H = 6
        I = 7
        J = 8
        K = 9
        L = 10
        M = 11
        N = 12
        O = 13
        P = 14
        R = 15
        S = 16
        T = 17
        U = 18
        V = 19
        W = 20
        X = 21
        Z = 22
        off = 23


class AdditionalSignalZs2v(AdditionalSignal):
    AdditionalSignalSymbolZs2v = AdditionalSignalZs2.AdditionalSignalSymbolZs2

    def __init__(self, symbols: List["AdditionalSignalSymbolZs2v"], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__(self):
        return "AdditionalSignalZs2v(kind=Zs2v" + ", symbols=" + str(self.symbols) + ")"


class AdditionalSignalZs3(AdditionalSignal):
    def __init__(self, symbols: List["AdditionalSignalSymbolZs3"], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__(self):
        return "AdditionalSignalZs3(kind=Zs3" + ", symbols=" + str(self.symbols) + ")"

    class AdditionalSignalSymbolZs3(Enum):
        OFF = 0
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        ELEVEN = 11
        TWELVE = 12
        THIRTEEN = 13
        FOURTEEN = 14
        FIFTEEN = 15
        SIXTEEN = 16

        @staticmethod
        def from_number(number: int) -> "AdditionalSignalZs3":
            return next(filter(lambda enum: enum.value == number, "AdditionalSignalSymbolZs3"))


class AdditionalSignalZs3v(AdditionalSignal):
    AdditionalSignalSymbolZs3v = AdditionalSignalZs3.AdditionalSignalSymbolZs3

    def __init__(self, symbols: List["AdditionalSignalSymbolZs3v"], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__(self):
        return "AdditionalSignalZs3v(kind=Zs3v" + ", symbols=" + str(self.symbols) + ")"

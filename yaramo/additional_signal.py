
from enum import Enum
from typing import List
from yaramo.base_element import BaseElement

class AdditionalSignal(BaseElement):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

class AdditionalSignalZs1(AdditionalSignal):
    def __init__(self, symbols: List['AdditionalSignalSymbolZs1'], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__ (self):
        return 'AdditionalSignalZs1(kind=Zs1' + ', symbols=' + str(self.symbols) + ')'

    
    class AdditionalSignalSymbolZs1(Enum):
        Zs1 = 0

class AdditionalSignalZs2(AdditionalSignal):
    def __init__(self, symbols: List['AdditionalSignalSymbolZs2'], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__ (self):
        return 'AdditionalSignalZs2(kind=Zs2' + ', symbols=' + str(self.symbols) + ')'

    
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

class AdditionalSignalZs3(AdditionalSignal):
    def __init__(self, symbols: List['AdditionalSignalSymbolZs3'], **kwargs) -> None:
        super().__init__(**kwargs)
        self.symbols = symbols

    def __str__ (self):
        return 'AdditionalSignalZs3(kind=Zs3' + ', symbols=' + str(self.symbols) + ')'
    
    class AdditionalSignalSymbolZs3(Enum):
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
        def from_number(number: int) -> 'AdditionalSignalZs3':
            return next(filter(lambda enum: enum.value == number, 'AdditionalSignalSymbolZs3'))


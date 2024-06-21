from typing import Tuple

from yaramo.base_element import BaseElement


class VacancySection(BaseElement):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def to_serializable(self) -> Tuple[dict, dict]:
        return self.__dict__, {}

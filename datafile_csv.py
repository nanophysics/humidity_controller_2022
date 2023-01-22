"""
time,fan,rh
223,34.5,78.5
"""

import csv
import pathlib
from typing import Dict


class Csv:
    def __init__(self, filename: pathlib.Path):
        assert isinstance(filename, pathlib.Path)
        self.time: int = 0
        self.fan: float = 0.0
        self.set_humi_pRH: float = 0.0
        self.humi_humi_pRH: float = 0.0
        self.stage_humi_pRH: float = 0.0
        self.humi_temp_C: float = 0.0
        self.stage_temp_C: float = 0.0
        self._names = ["time", "fan", "set_humi_pRH", "humi_humi_pRH", "stage_humi_pRH", "humi_temp_C", "stage_temp_C"]
        self._formats = {"time": '5d', "fan": "3.0f", "set_humi_pRH": "2.1f", "stage_humi_pRH": "2.1f", "humi_temp_C": "2.1f", "stage_temp_C": "2.1f"}
        self._f = filename.open('w', newline="")
        self._writer = csv.DictWriter(
            self._f, fieldnames=self._names, delimiter="\t")
        self._writer.writeheader()

    @property
    def row_dict(self) -> Dict[str, str]:
        row = {}
        for name in self._names:
            value = self.__dict__[name]
            try:
                _format = self._formats[name]
                value_str = format(value, _format)
            except KeyError:
                value_str = str(value)
            row[name] = value_str
        return row

    def write(self) -> None:
        self._writer.writerow(rowdict=self.row_dict)
        self._f.flush()

    @property
    def text(self) -> str:
        "time=xx fan=xx rh=zz"
        row_dict = self.row_dict
        list_text = [f"{name}={row_dict[name]}" for name in self._names]
        return "  ".join(list_text)


if __name__ == "__main__":
    df = Csv('test_csv.csv')
    df.rh = 33.56876986796
    df.write()
    print(df.text)
    df.close()

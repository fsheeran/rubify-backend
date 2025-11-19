from typing import NamedTuple, Protocol, Dict
import json


class PronunciationDatum(NamedTuple):
    indices: tuple[int, int]
    pronunciation: str


class CjkPronunciationEntry(NamedTuple):
    text: str
    pronunciation: str
    per_char: list[PronunciationDatum]


class CjkPronunciationProvider(Protocol):
    def __getitem__(self, text: str) -> list[CjkPronunciationEntry]: ...


def load_furigana_json(data_path: str) -> CjkPronunciationProvider:
    furigana_data = {}
    with open(data_path, "r", encoding="utf-8-sig") as f:
        raw_data = json.load(f)
        for key, entries in raw_data.items():
            processed_entries = []
            for entry in entries:
                processed_entries.append(
                    CjkPronunciationEntry(
                        text=key,
                        pronunciation=entry["pronunciation"],
                        per_char=[
                            PronunciationDatum(
                                indices=tuple(pc["indices"]),
                                pronunciation=pc["pronunciation"],
                            )
                            for pc in entry["per_char"]
                        ],
                    )
                )
            furigana_data[key] = processed_entries
    return furigana_data

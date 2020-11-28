import json
import typing

from .search import _build_index


def fuse(search: typing.Dict, filepath: str):
    """Build a JSON doc of your pages"""

    with open(filepath, "w") as jsonfile:
        return json.dump(
            [x for x in _build_index(search, id_field="id")],
            fp=jsonfile,
        )


import hashlib
import typing

from ..page import Page


def _id_hash(page: Page, *id_fields) -> str:
    """Generate a Hash from the provided fields"""
    raw_msg = "".join([getattr(page, x, "") for x in id_fields]).encode("utf-8")
    return hashlib.sha1(raw_msg).hexdigest()


def _build_index(pages: typing.Sequence[Page], id_field: str="_id", **search_params):
    """Build a page dict for the keys requested. There is a
    question if this should be replaced with a __dict__ overwrite on page."""

    for page in pages:
        page_dict = {}

        for key, key_params in search_params["fields"].items():

            if field_value := getattr(page, key, None):
                if key == "slug":
                    page_dict['slug'] = f"{search_params['site_url']}/{field_value}"

                elif key_params["type"] == "date":
                    page_dict[key] = field_value.to_rfc3339_string()

                else:
                    page_dict[key] = field_value

        page_dict[id_field] = _id_hash(page, *search_params["id_fields"])

        yield page_dict





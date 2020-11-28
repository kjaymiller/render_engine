import logging
import typing
from pathlib import Path
from typing import List

from jinja2 import Markup
from markdown2 import markdown
from slugify import slugify

from .content_parser import parse_content

# some attributes will need to be protected from manipulation


class Page:
    """Page is the base form of HTML content. It's result is a single HTML Object."""
    markdown_extras = ["fenced-code-blocks", "footnotes"]
    extension: str = ".html"

    def __init__(
        self,
    ):
        matcher: str = r"(^\w+: \b.+$)"  # expression to find attrs/vals

        if hasattr(content_path):
            content = Path(self.content_path).read_text()

            valid_attrs, self.base_content = parse_content(
                content,
                matcher=self.matcher,
            )

            for attr in valid_attrs:
                name, value = attr.split(": ", maxsplit=1)

                # comma delimit attributes.
                if name.lower() in self.list_attrs:
                    value = [attrval.lower() for attrval in value.split(", ")]

                else:
                    value = value.strip()

                setattr(self, name.lower(), value)

        if not self.title:
            self.title = self.__class__.__name__

        if not self.slug:
            self.slug = self.title or self.__class__.__name__

        self.slug = slugify(self.slug)

        logging.warning(self.image_optimizations)
        logging.warning(self.image_optimizer)

        if self.image_optimizer and self.image_optimizations:
            self.optimize_images()
            return


    @property
    def url(self):
        return f"{self.routes[0]}/{self.slug}"

    @classmethod
    def from_content_path(cls, filepath, **kwargs):
        class NewPage(cls):
            content_path = filepath

            def __init__(self, markdown_extras: typing.List[str] = []):
                for extra in markdown_extras:
                    if extra not in self.markdown_extras:
                        self.markdown_extras.append(extra)

                super().__init__()

        newpage = NewPage(**kwargs)

        return newpage

    @property
    def html(self):
        """Text from self.content converted to html"""

        if self.base_content:
            return markdown(self.base_content, extras=self.markdown_extras)

        else:
            return ""

    @property
    def markup(self):
        """html = rendered html (not marked up). Is `None` if `content == None`"""
        if self.html:
            return Markup(self.html)

        else:
            return ""

    @property
    def content(self):
        return self.markup

    def optimize_images(self):
        """Image Optimizations within a CDN are often applied"""
        for optimization in self.optimizations:
            print(optimization)
            self.image = self.optimizer.add_optimization(self.image, optimization)
            

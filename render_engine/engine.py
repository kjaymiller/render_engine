import logging
from pathlib import Path
from typing import (
        Any,
        Optional,
        Sequence,
        Type,
        Dict,
        )
import jinja2
from jinja2 import FileSystemLoader, select_autoescape
from more-itertools import flatten

from .page import Page


class Engine:
    """Engine creates decorators for writing HTML"""
    strict: bool = False
    output_path: str = 'output'
    static_path: str = 'static'
    template_path: str = 'templates'
    SITE_VARIABLES: Dict[str, str] = {
            'SITE_TITLE': 'Untitled Site',
            'SITE_URL': 'https://example.com',
            }

    @property
    def environment(self):
        return jinja2.Environment(
            autoescape=select_autoescape(), loader=FileSystemLoader(self.template_path)
        )

    def get_template(self, template: str):
        """
        fetches the requested template from the environment. Purely a
        convenience method

        Parameters:
            template : str
                the template file to look for
        """
        return self.environment.get_template(template)


    def render_collection(
            self,
            collection: typing.Type[Collection],
    ) -> None:
        """iterate through pages in the collection and generate HTML for each page"""

        for page in collection().pages:
            self.render_page(page, **SITE_VARIABLES)

    def render_page(
            self,
            page: typing.Type[Page],
    ) -> None:
        """generate HTML for the given page"""

        if getattr(page, 'template', None):
            content = self.get_template(page.template).render(**kwargs)
        else:
            content = page.content

        for route in getattr(page, routes, ['']):
            path = Path(self.output_path) / route / page.slug
            file_obj = path.write_text(content)

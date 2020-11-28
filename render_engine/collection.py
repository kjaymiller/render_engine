import collections
import itertools
import logging
import operator
import typing
from pathlib import Path

import more_itertools
from slugify import slugify

from .feeds import RSSFeed
from .page import Page


class Collection:
    """Collection objects serve as a way to quickly process pages that have a
    LARGE portion of content that is similar or file driven.

    The most common form of collection would be a Blog, but can also be
    static pages that have their content stored in a dedicated file.

    Currently, collections must come from a content_path and all be the same
    content type.


    Example
    -------
    from render_engine import Collection

    @site.register_collection()
    class BasicCollection(Collection):
        pass


    Attributes
    ----------
    engine: str, optional
        The engine that the collection will pass to each page. Site's default
        engine
    template: str
        The template that each page will use to render
    routes: List[str]
        all routes that the file should be created at. default []
    content_path: List[PathString], optional
        the filepath to load content from.
    includes: List[str], optional
        the types of files in the content path that will be processed
        default ["*.md", "*.html"]
    has_archive: Bool
        if `True`, create an archive page with all of the processed pages saved
        as `pages`. default `False`
    template: str, optional
        template filename that will be used if `has_archive==True` default: archive.html"
    slug: str, optional
        slug for rendered page if `has_archive == True` default: all_posts
    content_type: Type[Page], optional
        content_type for the rendered archive page
    _archive_reverse: Bool, optional
        should the sorted `pages` be listed in reverse order. default: False

    """

    engine: typing.Optional[str] = None
    content_items: typing.List[Page] = []
    content_path: str = ""
    content_type: typing.Type[Page] = Page
    template: str = "page.html"
    includes: typing.List[str] = ["*.md", "*.html"]
    routes: typing.List[str] = [""]
    subcollections: typing.List[str] = []
    has_archive: bool = False
    archive_template: str = "archive.html"
    archive_reverse: bool = False
    archive_sort: typing.Tuple[str] = "title"
    paginated: bool = False
    items_per_page: int = 10
    title: typing.Optional[str] = ""
    feeds: typing.List[typing.Optional[RSSFeed]] = []
    markdown_extras = ["fenced-code-blocks", "footnotes"]
    image_optimizer = None
    image_optimizations: typing.List[str] = []

    def __init__(self):
        if not self.title:
            self.title = self.__class__.__name__

    @property
    def slug(self):
        return slugify(self.title)

    @property
    def pages(self) -> typing.List[Page]:
        _pages = []

        if self.content_items:
            _pages = self.content_items

        if self.content_path:

            if Path(self.content_path).samefile("/"):
                logging.warning(
                    f"{self.content_path=}! Accessing Root Directory is Dangerous..."
                )

            for pattern in self.includes:

                for filepath in Path(self.content_path).glob(pattern):
                    page = self.content_type.from_content_path(
                        filepath,
                        markdown_extras=self.markdown_extras,
                    )
                    page.routes = self.routes
                    page.template = self.template
                    page.image_optimizations = self.image_optimizations
                    page.image_optimizer = self.image_optimizer
                    _pages.append(page)

        return _pages

    @property
    def archive(self):
        """Create a `Page` object for the pages in the collection"""

        sorted_pages = sorted(
            self.pages,
            key=lambda p: getattr(p, self.archive_sort),
            reverse=self.archive_reverse,
        )

        if self.paginated:
            pages = list(more_itertools.chunked(sorted_pages, self.items_per_page))

        else:
            pages = [sorted_pages]

        class Archive(Page):
            no_index = True
            template = self.archive_template
            routes = [self.routes[0]]
            title = self.title

        archive_pages = []

        for index, page in enumerate(pages):
            archive_page = Archive()
            archive_page.collection = self
            archive_page.routes = [self.routes[0]]
            archive_page.pages = pages[index]
            archive_page.title = self.title
            archive_page.page_index = (index, len(pages))

            if self.paginated:
                archive_page.slug = f"{archive_page.slug}-{index}"

            archive_pages.append(archive_page)

        return archive_pages

    def get_subcollections(self):
        subcollections = {}

        # get all the values for each of the subcollections
        for _subcollection in self.subcollections:
            subcollection_lists = collections.defaultdict(list)
            subcollections[_subcollection] = []

            for page in self.pages:

                if attr := getattr(page, _subcollection, None):

                    if isinstance(attr, list):

                        for attribute_item in attr:
                            subcollection_lists[attribute_item].append(page)

                    else:
                        subcollection_lists[attr].append(page)

            for attr, subcollection in subcollection_lists.items():

                class SubCollection(self.__class__):
                    content_path = None
                    content_items = subcollection
                    title = attr
                    slug = slugify(attr)

                subcollections[_subcollection].append(SubCollection())

        return subcollections

    def register_feed(self, feed, collection) -> None:
        """Create a Page object that is an RSS feed and add it to self.routes

        Parameters
        ----------
        feed: RSSFeedEngine
            the type of feed to generate
        collection: Collection
            the collection to

        Returns
        -------
        None
        """

        extension = self.rss_engine.extension
        _feed = feed
        _feed.slug = collection.slug
        _feed.title = f"{self.SITE_TITLE} - {_feed.title}"
        _feed.link = f"{self.SITE_URL}/{_feed.slug}{extension}"
        self.routes.append(_feed)

    def register_route(self, cls) -> None:
        route = cls()
        self.routes.append(route)

    def _remove_output_path(self):
        if self.output_path.exists():
            return shutil.rmtree(self.output_path)

    def _render_output(self, page):
        """Writes the page to a file"""
        engine = page.engine if page.engine else self.default_engine
        template_attrs = self.get_public_attributes(page)
        content = engine.render(page, **template_attrs)
        route = self.output_path.joinpath(page.routes[0].strip("/"))
        route.mkdir(exist_ok=True)
        filename = Path(page.slug).with_suffix(engine.extension)
        filepath = route.joinpath(filename)
        filepath.write_text(content)
        route_count = len(page.routes)

        if route_count > 1:

            # create a directory and path for each alternate route
            for new_route in page.routes[1:]:
                new_route = self.output_path.joinpath(new_route.strip("/"))
                new_route.mkdir(exist_ok=True)
                new_filepath = new_route.joinpath(filename)
                shutil.copy(filepath, new_filepath)

    def _render_subcollections(self):
        """Generate subcollection pages to be added to routes"""
        for _, collection in self.collections.items():

            if collection.subcollections:

                for subcollection_group in collection.get_subcollections():
                    _subcollection_group = collection.get_subcollections()[
                        subcollection_group
                    ]
                    sorted_group = sorted(
                        _subcollection_group,
                        key=lambda x: (len(x.pages), x.title),
                        reverse=True,
                    )

                    for subcollection in sorted_group:

                        self.subcollections[subcollection_group] = sorted_group

                        for archive in subcollection.archive:
                            self.routes.append(archive)

    def render(self, dry_run: bool = False, strict: bool = False) -> None:
        # removes the output path is strict is set
        if self.strict or strict:
            self._remove_output_path

        # create an output_path if it doesn't exist
        self.output_path.mkdir(exist_ok=True)

        # copy a defined static path into output path
        if Path(self.static_path).is_dir():
            shutil.copytree(
                self.static_path,
                self.output_path.joinpath(self.static_path),
                dirs_exist_ok=True,
            )

        # render registered subcollections
        self._render_subcollections()
        page_count = len(self.routes)

        with Bar(
            f"Rendering {page_count} Pages",
            max=page_count,
            suffix="%(percent).1f%% - %(elapsed_td)s",
        ) as bar:

            for page in self.routes:
                suffix = "%(percent).1f%% - %(elapsed_td)s"
                bar.suffix = suffix + f" ({page.title})"

                self._render_output(page)

                bar.next()

        if self.search:
            search_fields = {
                "title": {
                    "type": "text",
                },
                "content": {
                    "type": "text",
                },
                "slug": {
                    "type": "text",
                },
                "date_published": {
                    "type": "date",
                },
                "date_modified": {
                    "type": "date",
                },
                "tags": {
                    "type": "text",
                    "default": [""],
                },
                "category": {
                    "type": "keyword",
                },
            }
            self.search_params["id_fields"] = ["slug", "date_created"]
            self.search_params["fields"] = search_fields
            self.search_params['site_url'] = self.SITE_URL
            filtered_routes = itertools.filterfalse(lambda x: x.no_index, self.routes)
            self.search(
                search_client=self.search_client,
                pages=filtered_routes,
                **self.search_params,
            )


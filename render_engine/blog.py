import os
import logging
import typing
from typing import List

import pendulum
import more_itertools

from .collection import Collection
from .feeds import RSSFeed, RSSFeedEngine, RSSFeedItem
from .page import Page


class BlogPost(Page):
    """
    Page Like object with slight modifications to work with BlogPosts.

    Attributes:
        template : str
            the default template that the site will look for
        rss_feed_item : RSSFeedItem
            the content in an rss format
        date : pendulum.datetime
            date parsed in datetime format. usesul for sorting and things
        date_published : str
            date formated for `RSSFeed`
        date_friendly : str
            an easy to read string version of the date

    """

    template = "blog_post.html"
    list_attrs = ["tags"]

    def __init__(self, **kwargs):
        """
        checks published options and accepts the first that is listed

        Attributes:
            date : pendulum.datetime
                date parsed in datetime format. usesul for sorting and things
            date_published : str
                date formated for `RSSFeed`
            date_friendly : str
                an easy to read string version of the date
        """

        super().__init__(**kwargs)


        date_published = more_itertools.first_true(
            (
                getattr(self, "date_published", None),
                getattr(self, "publish_date", None),
                getattr(self, "date", None),
            )
        )

        self.date_published = pendulum.parse(date_published, strict=False).set(
            tz=pendulum.local_timezone()
        )

        date_modified = more_itertools.first_true(
            (
                getattr(self, "date_modified", None),
                getattr(self, "modified_date", None),
            ),
            default=None,
        )

        if not date_modified:
            self.date_modified = self.date_published

        else:
            self.date_modified = pendulum.parse(date_modified, strict=False).set(
                tz=pendulum.local_timezone()
            )

        self.date_friendly = self.date_modified.format("MMM DD, YYYY HH:mm A")

    @property
    def rss_feed_item(self):
        return RSSFeedItem(self)


class Blog(Collection):
    """
    Custom Collection Class with Archiving Enabled and the RSS Feed

    Todos:
        - Add Support for JSON Feeds
        - Rename the archive items so they are not private
    """

    content_type: typing.Type[BlogPost] = BlogPost
    archive_reverse: bool = True
    has_archive: bool = True
    archive_sort = "date_published"

    @property
    def feeds(self):
        return [RSSFeed(collection=self, title=self.title)]

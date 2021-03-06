from pathlib import Path
import pytest
from render_engine import Page

@pytest.fixture()
def content():
   return """title: Test Title
custom: 1, 2, 3

# Test Header
Test Paragraph"""

@pytest.fixture()
def base_page():
    """Tests can a simple Page be created given no Parameters"""
    return Page()

@pytest.fixture()
def base_collection():
    return Collection


@pytest.fixture()
def page_with_content_path(mocker, content):
    mocker.patch('pathlib.Path.read_text', lambda _:content)
    return Page.from_content_path('fake_path.md')

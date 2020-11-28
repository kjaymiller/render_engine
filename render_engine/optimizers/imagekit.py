from urllib.parse import urlparse

def add_optimization(img_url, transform):
    """Given a url inject transforms"""
    url = urlparse(img_url)
    modded_url = url._replace(path=f"{transform}{url.path}")
    return modded_url.geturl()


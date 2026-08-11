"""
Which sites the agents work on.

Adding another site is a matter of adding an entry here - none of the agent
code is site-specific.
"""

SITES = [
    {
        "name": "softclipper.pro",
        # exact property string as Search Console knows it
        "gsc_property": "sc-domain:softclipper.pro",
        "origin": "https://softclipper.pro",
        "sitemap": "https://softclipper.pro/sitemap-index.xml",
        # Deliberately kept out of the index. Google will never crawl these,
        # so without this list they would sit in the report as a permanent
        # "never crawled" warning that is not a problem and cannot be fixed.
        "noindex_urls": ["https://softclipper.pro/checkout/"],
        "enabled": True,
    },
    {
        "name": "aisofttechsolution.com",
        "gsc_property": "sc-domain:aisofttechsolution.com",
        "origin": "https://aisofttechsolution.com",
        # NOT sitemap-index.xml — that path does not exist on this site and,
        # because the server answers 200 with the app shell for any unknown
        # path, asking for it looks like it worked and yields zero URLs.
        "sitemap": "https://aisofttechsolution.com/sitemap.xml",
        "noindex_urls": [],
        "enabled": True,
    },
]


def enabled_sites():
    return [s for s in SITES if s.get("enabled")]

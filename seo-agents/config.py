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
        # Cold start: what to write about before the site has search history.
        # Seeds are the words a buyer would actually type - not the product
        # name, which nobody searches for yet.
        "coldstart": {
            "seeds": [
                "ai video clipper",
                "turn long videos into shorts",
                "repurpose podcast into clips",
                "auto reframe video",
                "add captions to video",
                "highlight reel from long video",
            ],
            # Competitors we compare against on /compare/, plus the two other
            # tools that own this search space.
            "competitors": [
                "https://www.opus.pro",
                "https://klap.app",
                "https://vizard.ai",
                "https://www.submagic.co",
                "https://2short.ai",
            ],
        },
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
        # No cold-start seeds yet: this site's positioning is not settled, and
        # guessing seeds produces a confident list of the wrong topics. Add
        # them here and the agent starts on the next run.
        "coldstart": {"seeds": [], "competitors": []},
        "enabled": True,
    },
]


def enabled_sites():
    return [s for s in SITES if s.get("enabled")]

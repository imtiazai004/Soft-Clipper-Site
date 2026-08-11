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
        "enabled": True,
    },
]


def enabled_sites():
    return [s for s in SITES if s.get("enabled")]

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
        "sitemap": "https://aisofttechsolution.com/sitemap-index.xml",
        # off until softclipper.pro is proven end to end
        "enabled": False,
    },
]


def enabled_sites():
    return [s for s in SITES if s.get("enabled")]

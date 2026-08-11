"""
Google Search Console API client.

Credentials are read from environment variables first (that is how this runs
in GitHub Actions, via repository Secrets), falling back to a local
credentials JSON file for development on a laptop.

Environment variables expected in CI:
    GSC_CLIENT_ID
    GSC_CLIENT_SECRET
    GSC_REFRESH_TOKEN

Access tokens last ~1 hour and are fetched fresh on each run, so nothing
needs to be persisted between runs.

NOTE on refresh token lifetime: while the Google Cloud OAuth app is in
"Testing" publishing status (unverified), Google issues refresh tokens valid
for only ~7 days. Once the app is verified/published this stops being an
issue. If you see "invalid_grant" here, the refresh token has expired and the
browser authorization flow needs to be redone.
"""

import json
import os
import time

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
WEBMASTERS_BASE = "https://www.googleapis.com/webmasters/v3"
URL_INSPECTION_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"

# only used when running locally, outside CI
LOCAL_CREDS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "credentials", "gsc_oauth.json"
)


def _load_credentials():
    """Environment variables win; a local JSON file is the dev fallback."""
    client_id = os.environ.get("GSC_CLIENT_ID")
    client_secret = os.environ.get("GSC_CLIENT_SECRET")
    refresh_token = os.environ.get("GSC_REFRESH_TOKEN")

    if client_id and client_secret and refresh_token:
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }

    if os.path.exists(LOCAL_CREDS_PATH):
        with open(LOCAL_CREDS_PATH) as f:
            return json.load(f)

    raise RuntimeError(
        "No Search Console credentials found. Set GSC_CLIENT_ID, GSC_CLIENT_SECRET "
        "and GSC_REFRESH_TOKEN (repository Secrets in CI), or provide "
        f"{LOCAL_CREDS_PATH} for local runs."
    )


class GSCClient:
    def __init__(self, creds: dict = None):
        self.creds = creds or _load_credentials()
        self._access_token = None
        self._token_fetched_at = 0

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def _refresh_access_token(self):
        resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": self.creds["client_id"],
                "client_secret": self.creds["client_secret"],
                "refresh_token": self.creds["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to refresh GSC access token ({resp.status_code}): {resp.text}\n"
                "If this says invalid_grant, the refresh token has expired "
                "(7-day limit while the Google Cloud app is unverified) - redo the "
                "browser authorization flow and update the GSC_REFRESH_TOKEN secret."
            )
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_fetched_at = time.time()
        return self._access_token

    def _headers(self):
        if not self._access_token or (time.time() - self._token_fetched_at) > 50 * 60:
            self._refresh_access_token()
        return {"Authorization": f"Bearer {self._access_token}"}

    def _request(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())
        resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        if resp.status_code == 401:
            self._refresh_access_token()
            headers.update(self._headers())
            resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        if resp.status_code >= 400:
            raise RuntimeError(f"{method} {url} -> {resp.status_code}: {resp.text}")
        return resp.json()

    # ------------------------------------------------------------------
    # Search Analytics
    # ------------------------------------------------------------------
    def search_analytics_query(
        self,
        site_url: str,
        start_date: str,
        end_date: str,
        dimensions=None,
        row_limit: int = 5000,
        start_row: int = 0,
        search_type: str = "web",
    ):
        """Returns the raw list of rows from the Search Analytics API.

        site_url must be the exact property string GSC uses, e.g.
        'sc-domain:softclipper.pro'.
        """
        dimensions = dimensions or ["query", "page"]
        url = f"{WEBMASTERS_BASE}/sites/{requests.utils.quote(site_url, safe='')}/searchAnalytics/query"
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "startRow": start_row,
            "type": search_type,
        }
        data = self._request("POST", url, json=body)
        return data.get("rows", [])

    # ------------------------------------------------------------------
    # Sitemaps
    # ------------------------------------------------------------------
    def list_sitemaps(self, site_url: str):
        url = f"{WEBMASTERS_BASE}/sites/{requests.utils.quote(site_url, safe='')}/sitemaps"
        data = self._request("GET", url)
        return data.get("sitemap", [])

    # ------------------------------------------------------------------
    # URL Inspection
    # ------------------------------------------------------------------
    def inspect_url(self, site_url: str, inspection_url: str):
        body = {"inspectionUrl": inspection_url, "siteUrl": site_url}
        return self._request("POST", URL_INSPECTION_URL, json=body)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def list_sites(self):
        data = self._request("GET", f"{WEBMASTERS_BASE}/sites")
        return data.get("siteEntry", [])

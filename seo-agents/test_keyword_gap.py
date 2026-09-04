"""
Offline tests for keyword_gap_agent.py - no live network calls.

Covers the three fixes made after reviewing every "Worth fixing" item the
dashboard had flagged (2026-09-04): a minimum-impressions floor before a
query counts as cannibalized at all, folding http:// / https:// copies of
the same URL into one page instead of counting them as two competing
pages, and a dominant-page-share check so one clear winner plus a single
stray impression elsewhere does not read as a contested query.
"""

import keyword_gap_agent as kga


def test_canonical_page_folds_http_and_https():
    assert kga._canonical_page("http://softclipper.pro/") == kga._canonical_page(
        "https://softclipper.pro/"
    )


def test_canonical_page_keeps_path_and_query():
    a = kga._canonical_page("http://softclipper.pro/help/?ref=x")
    b = kga._canonical_page("https://softclipper.pro/help/?ref=x")
    assert a == b
    assert a.startswith("https://softclipper.pro/help/")


class FakeGSCClient:
    """Stands in for GSCClient; returns whatever rows the test hands it."""

    def __init__(self, rows):
        self._rows = rows

    def __call__(self):
        return self

    def search_analytics_query(self, **kwargs):
        return self._rows


def _row(query, page, impressions, position=50, clicks=0, ctr=0.0):
    return {
        "keys": [query, page],
        "impressions": impressions,
        "position": position,
        "clicks": clicks,
        "ctr": ctr,
    }


def _run_with(monkeypatch, rows):
    fake = FakeGSCClient(rows)
    monkeypatch.setattr(kga, "GSCClient", fake)
    return kga.run("sc-domain:example.com")


def test_low_impression_split_is_not_flagged(monkeypatch):
    # the exact "clip soft" shape: 3 pages, 2 impressions total, deep position
    rows = [
        _row("clip soft", "https://example.com/download/", 1, position=61),
        _row("clip soft", "https://example.com/help/", 1, position=70),
    ]
    result = _run_with(monkeypatch, rows)
    assert result["cannibalization_flags"] == []


def test_http_https_pair_is_not_a_second_page(monkeypatch):
    # home and /download/ are close enough (7 vs 6) that this is a genuine
    # split, not a dominant page - isolates the http/https folding behaviour
    # from the dominance check tested separately below
    rows = [
        _row("softclipper", "https://example.com/", 6, position=6),
        _row("softclipper", "http://example.com/", 1, position=6),
        _row("softclipper", "https://example.com/download/", 6, position=6),
    ]
    result = _run_with(monkeypatch, rows)
    flags = result["cannibalization_flags"]
    assert len(flags) == 1
    assert flags[0]["query"] == "softclipper"
    assert flags[0]["pages"] == [
        "https://example.com/",
        "https://example.com/download/",
    ]
    assert flags[0]["impressions"] == 13


def test_dominant_page_with_stray_impression_is_not_flagged(monkeypatch):
    # the actual softclipper.pro numbers: homepage clearly owns this query
    # (11 https + 1 http = 12 of 13 impressions, 92%); /download/'s 1
    # impression is not a second page competing for it
    rows = [
        _row("softclipper", "https://example.com/", 11, position=6),
        _row("softclipper", "http://example.com/", 1, position=6),
        _row("softclipper", "https://example.com/download/", 1, position=6),
    ]
    result = _run_with(monkeypatch, rows)
    assert result["cannibalization_flags"] == []


def test_borderline_split_without_a_clear_winner_is_flagged(monkeypatch):
    # the actual softclip.pro numbers: 3/2/1 across three pages - nobody
    # has run away with it, so this stays a real (if low-value) split
    rows = [
        _row("softclip", "https://example.com/help/", 3, position=80),
        _row("softclip", "https://example.com/compare/opus/", 2, position=80),
        _row("softclip", "https://example.com/", 1, position=80),
    ]
    result = _run_with(monkeypatch, rows)
    flags = result["cannibalization_flags"]
    assert len(flags) == 1
    assert flags[0]["impressions"] == 6


def test_real_cannibalization_still_flagged_above_the_floor(monkeypatch):
    rows = [
        _row("ai video clipper", "https://example.com/", 20, position=9),
        _row("ai video clipper", "https://example.com/compare/", 8, position=14),
    ]
    result = _run_with(monkeypatch, rows)
    flags = result["cannibalization_flags"]
    assert len(flags) == 1
    assert flags[0]["impressions"] == 28


def test_flags_sort_worst_first(monkeypatch):
    rows = [
        _row("small overlap", "https://example.com/a/", 3, position=40),
        _row("small overlap", "https://example.com/b/", 3, position=45),
        _row("big overlap", "https://example.com/c/", 30, position=10),
        _row("big overlap", "https://example.com/d/", 20, position=12),
    ]
    result = _run_with(monkeypatch, rows)
    flags = result["cannibalization_flags"]
    assert [f["query"] for f in flags] == ["big overlap", "small overlap"]


if __name__ == "__main__":
    import sys
    import types

    # tiny stand-in for pytest's monkeypatch fixture so this file also runs
    # with a plain `python test_keyword_gap.py`
    class _Monkeypatch:
        def __init__(self):
            self._sets = []

        def setattr(self, obj, name, value):
            self._sets.append((obj, name, getattr(obj, name)))
            setattr(obj, name, value)

        def undo(self):
            for obj, name, old in reversed(self._sets):
                setattr(obj, name, old)

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        mp = _Monkeypatch()
        try:
            if "monkeypatch" in t.__code__.co_varnames:
                t(mp)
            else:
                t()
            print(f"ok    {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        finally:
            mp.undo()

    print()
    if failed:
        print(f"{failed} failed")
        sys.exit(1)
    print("all passed")

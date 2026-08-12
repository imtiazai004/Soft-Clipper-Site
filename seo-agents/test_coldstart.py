"""Offline tests - the sandbox cannot reach Google, so every network call is
replaced by a fixture. What is being tested is the parsing and ranking, which
is where the bugs would be."""
import sys
sys.path.insert(0, "/root/seo-automation/Soft-Clipper-Site/seo-agents")
import coldstart_agent as cs

fails = []
def check(name, got, want):
    if got != want:
        fails.append(f"{name}: got {got!r}, want {want!r}")

# --- suggest parsing -------------------------------------------------------
check("firefox shape", cs._parse_suggest(
    '["how to make shorts",["how to make shorts from long videos",'
    '"how to make shorts on youtube"]]'),
    ["how to make shorts from long videos", "how to make shorts on youtube"])
check("empty suggestions", cs._parse_suggest('["x",[]]'), [])
check("garbage is not a crash", cs._parse_suggest("<html>429</html>"), [])
check("truncated array", cs._parse_suggest('["x"]'), [])
check("non-string entries dropped", cs._parse_suggest('["x",["ok",5,null]]'), ["ok"])
check("whitespace + case normalised", cs._parse_suggest('["x",["  Foo Bar  "]]'), ["foo bar"])

# --- query building --------------------------------------------------------
q = cs.build_queries(["ai video clipper"])
check("bare seed first", q[0], "ai video clipper")
check("no duplicates", len(q), len(set(q)))
assert "how to ai video clipper" in q and "ai video clipper vs" in q, "prefix/suffix missing"
assert "ai video clipper a" in q, "letter expansion missing"

# --- slug words ------------------------------------------------------------
check("slug words", cs.slug_words("https://x.com/blog/how-to-repurpose-a-podcast/"),
      {"repurpose", "podcast"})
check("stopwords + short words dropped",
      cs.slug_words("https://x.com/blog/the-best-ai-for-you"), set())

# --- coverage matching -----------------------------------------------------
sets = [cs.slug_words("https://opus.pro/blog/repurpose-long-videos-into-shorts")]
check("2-word overlap counts", cs.covered_by("repurpose long videos", sets), True)
check("1-word overlap does not", cs.covered_by("videos everywhere", sets), False)
check("single meaningful word never matches", cs.covered_by("videos", sets), False)

# --- scoring ---------------------------------------------------------------
e = {"hits": 3, "best_position": 0}
check("score = 3*2 + (10-0) + 2*3", cs.score(e, 2), 22)
check("worse position scores lower", cs.score({"hits": 3, "best_position": 9}, 2), 13)
check("no competitor coverage", cs.score(e, 0), 16)

# --- ranking + gap filtering ----------------------------------------------
harvested = {"phrases": {
    "how to turn long videos into shorts": {"phrase": "how to turn long videos into shorts",
        "hits": 4, "best_position": 0, "from": ["a"]},
    "ai clip generator free": {"phrase": "ai clip generator free",
        "hits": 1, "best_position": 7, "from": ["b"]},
    "shorts": {"phrase": "shorts", "hits": 9, "best_position": 0, "from": ["c"]},
}}
comp = {"https://opus.pro": [cs.slug_words("https://opus.pro/blog/turn-long-videos-into-shorts")]}
ours = [cs.slug_words("https://softclipper.pro/blog/turn-long-videos-into-shorts")]
gaps, everything = cs.rank_topics(harvested, comp, ours)
check("single-word head term excluded", any(t["phrase"] == "shorts" for t in everything), False)
check("our existing post is not proposed again",
      any("turn long videos into shorts" in t["phrase"] for t in gaps), False)
check("the uncovered one survives", [t["phrase"] for t in gaps], ["ai clip generator free"])
check("covered count", cs.rank_topics(harvested, comp, ours)[1][0]["we_cover_it"], True)

# --- sitemap parsing -------------------------------------------------------
check("locs", cs._urls_from_xml(
    "<urlset><url><loc>https://a.com/blog/x</loc></url>"
    "<url><loc> https://a.com/pricing </loc></url></urlset>"),
    ["https://a.com/blog/x", "https://a.com/pricing"])

# --- harvest with a stubbed endpoint ---------------------------------------
class FakeSession:
    def __init__(self): self.calls = []
    def get(self, url, **kw):
        self.calls.append(url)
        class R:
            status_code = 200
            text = '["q",["turn long videos into shorts","ai clip generator"]]'
        return R()

fs = FakeSession()
h = cs.harvest(["ai clipper"], fs, max_requests=5, delay=0)
check("request cap respected", h["requests_made"], 5)
check("hits accumulate across prefixes",
      h["phrases"]["ai clip generator"]["hits"], 5)
check("best position tracked", h["phrases"]["ai clip generator"]["best_position"], 1)
check("`from` list capped at 5", len(h["phrases"]["ai clip generator"]["from"]), 5)

class BoomSession:
    def get(self, url, **kw): raise RuntimeError("network down")
h2 = cs.harvest(["x"], BoomSession(), max_requests=3, delay=0)
check("network failure is recorded, not raised", len(h2["errors"]), 3)
check("still returns a result", h2["phrases"], {})

print("\n".join(fails) if fails else f"all tests passed")
sys.exit(1 if fails else 0)

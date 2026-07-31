/**
 * Runs the real ReferralTag script against stubs.
 *
 *     npm test
 *
 * It exists because a broken attribution chain does not throw. The page renders,
 * the button works, the sale completes — and the affiliate is simply never
 * credited. Nobody notices until someone asks where their commission went, by
 * which point the sale is weeks old and there is no way to prove it happened.
 *
 * The script is read out of the .astro file rather than copied here, so this
 * cannot drift into testing a version of the logic that no longer ships.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const src = readFileSync(
	fileURLToPath(new URL("../src/components/ReferralTag.astro", import.meta.url)),
	"utf8",
);
const body = src.split("<script is:inline>")[1].split("</script>")[0];

function run(search, storeSeed, buyHref = "https://buy.stripe.com/abc123") {
  const store = new Map(storeSeed ? [["sc-ref", storeSeed]] : []);
  const link = { href: buyHref };
  const beacons = [];
  const g = {
    localStorage: {
      getItem: (k) => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(k, v),
      removeItem: (k) => store.delete(k),
    },
    location: { search },
    document: { querySelectorAll: () => [link] },
    // The click counter. Stubbed rather than left undefined so the script is
    // exercised on the path a real browser takes — the version of this that only
    // stubbed what the attribution needed would have passed while the beacon
    // threw on every page load.
    navigator: { sendBeacon: (url) => beacons.push(url) },
    URL, URLSearchParams, Date, JSON,
  };
  new Function(...Object.keys(g), body)(...Object.values(g));
  return { href: link.href, stored: store.get("sc-ref"), beacons };
}

const ref = (h) => new URL(h).searchParams.get("client_reference_id");
let fails = 0;
const check = (name, got, want) => {
  const ok = got === want;
  if (!ok) fails++;
  console.log(`${ok ? "ok  " : "FAIL"}  ${name}${ok ? "" : `\n        got ${JSON.stringify(got)} want ${JSON.stringify(want)}`}`);
};

// 1. Lands with ?ref= and buys on that page.
check("tag from the URL reaches the checkout", ref(run("?ref=ali").href), "ali");

// 2. Lands on a blog post with ?ref=, buys later from a clean URL. This is the
//    case that matters most and the one a URL-only implementation loses.
const seeded = run("?ref=ali").stored;
check("tag survives to a later page with no query", ref(run("", seeded).href), "ali");

// 3. Expired tag is not used.
const stale = JSON.stringify({ code: "ali", until: Date.now() - 1000 });
check("an expired tag is dropped", ref(run("", stale).href), null);

// 4. Last link wins.
const first = run("?ref=ali").stored;
check("a newer link overrides the older one", ref(run("?ref=sara", first).href), "sara");

// 5. Normalisation matches the server's.
check("upper case and spaces are normalised", ref(run("?ref=%20ALI-ONE%20").href), "ali-one");
check("junk is stripped", ref(run("?ref=a<script>b").href), "ascriptb");
check("a too-short code is ignored", ref(run("?ref=ab").href), null);

// 6. No ref at all -> untouched link.
check("no referral leaves the link alone", run("").href, "https://buy.stripe.com/abc123");

// 7. A hand-built link that already carries a tag is not overwritten.
check(
  "an explicit tag is not overwritten",
  ref(run("?ref=ali", null, "https://buy.stripe.com/abc?client_reference_id=fixed").href),
  "fixed",
);

// 8. The click counter. Only a link that was actually followed counts — a tag
//    read back out of storage is the same visitor still browsing, and counting
//    it on every page would turn one click into a dozen and make every
//    affiliate's conversion rate a fiction.
check(
  "following a link counts one click",
  run("?ref=ali").beacons[0],
  "https://api.softclipper.pro/api/partner/visit?code=ali",
);
check("a later page with no query counts nothing", run("", seeded).beacons.length, 0);
check("a too-short code counts nothing", run("?ref=ab").beacons.length, 0);
check("the counted code is the normalised one", run("?ref=%20ALI-ONE%20").beacons[0],
  "https://api.softclipper.pro/api/partner/visit?code=ali-one");

console.log(fails ? `\n${fails} FAILED` : "\nall passed");
process.exit(fails ? 1 : 0);

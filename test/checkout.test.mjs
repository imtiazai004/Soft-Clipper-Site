import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const checkout = readFileSync(join(root, "dist", "checkout", "index.html"), "utf8");
const pricing = readFileSync(join(root, "dist", "pricing", "index.html"), "utf8");

function test(name, fn) {
	try {
		fn();
		console.log("ok   ", name);
	} catch (error) {
		console.error("FAIL ", name);
		throw error;
	}
}

test("buy buttons now lead to the shared checkout", () => {
	assert.match(pricing, /href="\/checkout\/"/);
});

test("checkout keeps Stripe and adds the bank transfer/wallet path", () => {
	assert.match(checkout, /id="cardCheckout"[^>]+buy\.stripe\.com/);
	assert.match(checkout, /id="bankTab"[^>]*>[\s\S]*?Bank Transfer\/Wallet/);
	assert.match(checkout, /\/api\/checkout\/bank\/orders/);
	assert.doesNotMatch(checkout, /Pakistani|Pakistan bank/i);
});

test("customer-visible HTML does not bake personal receiving details into every build", () => {
	assert.doesNotMatch(checkout, /20300981005116011|PK76BAHL2030098100511601|03005863032/);
});

test("the supplied Bank Al-Habib QR is published with the checkout", () => {
	assert.equal(existsSync(join(root, "dist", "payments", "bank-al-habib-qr.jpeg")), true);
});

test("the QR opens full size, and can be closed without a mouse", () => {
	assert.match(checkout, /id="qrZoom"[^>]*aria-haspopup="dialog"/);
	assert.match(checkout, /id="qrModal"[^>]*role="dialog"[^>]*aria-modal="true"/);
	assert.match(checkout, /id="qrModal"[^>]*hidden/);
	assert.match(checkout, /"Escape"/);
});

test("a display rule never outranks the hidden attribute", () => {
	// Both the QR button and the dialog set `display`, which beats the browser's
	// own `[hidden] { display: none }`. JazzCash hides the QR this way, and the
	// dialog starts hidden — without these rules both are permanently visible.
	// Astro extracts <style> to a stylesheet, so this has to read the built CSS.
	const hrefs = [...checkout.matchAll(/<link rel="stylesheet" href="([^"]+\.css)"/g)].map((m) => m[1]);
	assert.ok(hrefs.length > 0, "the checkout page loads no stylesheet");
	const css = hrefs.map((href) => readFileSync(join(root, "dist", href), "utf8")).join("\n");
	for (const selector of [".bank-qr", ".qr-modal"]) {
		// Astro appends its own [data-astro-cid-…] scope attribute to every selector.
		assert.match(css, new RegExp(`\\${selector}(\\[[^\\]]+\\])*\\[hidden\\]\\s*\\{\\s*display:\\s*none`));
	}
});

console.log("\nall passed");

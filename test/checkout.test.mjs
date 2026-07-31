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

test("checkout keeps Stripe and adds the Pakistani payment path", () => {
	assert.match(checkout, /id="cardCheckout"[^>]+buy\.stripe\.com/);
	assert.match(checkout, /id="bankTab"/);
	assert.match(checkout, /\/api\/checkout\/bank\/orders/);
});

test("customer-visible HTML does not bake personal receiving details into every build", () => {
	assert.doesNotMatch(checkout, /20300981005116011|03005863032/);
});

test("the supplied Bank Al-Habib QR is published with the checkout", () => {
	assert.equal(existsSync(join(root, "dist", "payments", "bank-al-habib-qr.jpeg")), true);
});

console.log("\nall passed");

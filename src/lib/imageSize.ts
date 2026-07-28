/**
 * Pixel dimensions of a JPEG or PNG, read straight from the file header.
 *
 * This exists so every <img> can carry real width and height attributes. Without
 * them a lazily loaded image reserves no space until it arrives, the page jumps
 * as each one lands, and the layout shift counts against the site in Core Web
 * Vitals. Two file formats and a few header bytes each is much less machinery
 * than an image library for the job.
 */
import fs from "node:fs";

export interface Size {
	width: number;
	height: number;
}

/** Reads `public/<path>`. Returns null if the file is missing or unreadable. */
export function imageSize(publicPath: string): Size | null {
	const file = `public/${publicPath.replace(/^\//, "")}`;
	let buf: Buffer;
	try {
		buf = fs.readFileSync(file);
	} catch {
		return null;
	}

	// PNG: an 8-byte signature, then the IHDR chunk with width and height.
	if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) {
		return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
	}

	// JPEG: walk the marker segments to the start-of-frame, which is the only
	// one that states the image's size.
	if (buf.length > 4 && buf.readUInt16BE(0) === 0xffd8) {
		let i = 2;
		while (i + 9 < buf.length) {
			if (buf[i] !== 0xff) {
				i++;
				continue;
			}
			const marker = buf[i + 1];
			// C0–CF are start-of-frame markers, except C4 (Huffman table), C8
			// (reserved) and CC (arithmetic coding conditioning).
			if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
				return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7) };
			}
			i += 2 + buf.readUInt16BE(i + 2);
		}
	}

	return null;
}

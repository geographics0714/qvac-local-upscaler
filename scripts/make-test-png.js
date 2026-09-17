// One-off helper to generate a tiny valid PNG for smoke-testing the upscaler,
// so the repo doesn't need to ship a binary sample image.
import fs from "node:fs";
import zlib from "node:zlib";

function crc32(buf) {
  let c;
  const table = crc32.table || (crc32.table = (() => {
    const t = [];
    for (let n = 0; n < 256; n++) {
      c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c;
    }
    return t;
  })());
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) crc = table[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const typeBuf = Buffer.from(type, "ascii");
  const lenBuf = Buffer.alloc(4);
  lenBuf.writeUInt32BE(data.length, 0);
  const crcBuf = Buffer.alloc(4);
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([lenBuf, typeBuf, data, crcBuf]);
}

const width = 32;
const height = 32;
const raw = Buffer.alloc((width * 3 + 1) * height);
for (let y = 0; y < height; y++) {
  const rowStart = y * (width * 3 + 1);
  raw[rowStart] = 0; // filter type: none
  for (let x = 0; x < width; x++) {
    const off = rowStart + 1 + x * 3;
    raw[off] = Math.floor((x / width) * 255);
    raw[off + 1] = Math.floor((y / height) * 255);
    raw[off + 2] = 128;
  }
}

const ihdr = Buffer.alloc(13);
ihdr.writeUInt32BE(width, 0);
ihdr.writeUInt32BE(height, 4);
ihdr[8] = 8; // bit depth
ihdr[9] = 2; // color type: RGB
ihdr[10] = 0;
ihdr[11] = 0;
ihdr[12] = 0;

const idat = zlib.deflateSync(raw);
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const png = Buffer.concat([
  signature,
  chunk("IHDR", ihdr),
  chunk("IDAT", idat),
  chunk("IEND", Buffer.alloc(0)),
]);

fs.mkdirSync("samples", { recursive: true });
fs.writeFileSync("samples/test-gradient.png", png);
console.log("Wrote samples/test-gradient.png", png.length, "bytes");

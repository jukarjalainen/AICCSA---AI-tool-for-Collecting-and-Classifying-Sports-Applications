import store from "app-store-scraper";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// 1. Read a CSV file (fixed name in this folder)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const inputPath = path.join(__dirname, "AppStoreAppsCSV.csv");
const outputPath = path.join(__dirname, "appleStoreAppsNewDescriptions.csv");

// Optional: --limit N to process only first N data rows (for testing)
function getLimitArg() {
  const args = process.argv.slice(2);
  let val = 0;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--limit" && i + 1 < args.length) {
      val = parseInt(args[i + 1], 10) || 0;
      break;
    }
    const m = a.match(/^--limit=(\d+)$/);
    if (m) {
      val = parseInt(m[1], 10) || 0;
      break;
    }
  }
  return val > 0 ? val : 0;
}

function detectDelimiter(sample) {
  const semi = (sample.match(/;/g) || []).length;
  const comma = (sample.match(/,/g) || []).length;
  return semi >= comma ? ";" : ",";
}

function parseCSV(content, delimiter) {
  const rows = [];
  const len = content.length;
  let i = 0;
  let field = "";
  let row = [];
  let inQuotes = false;
  while (i < len) {
    const ch = content[i];
    if (inQuotes) {
      if (ch === '"') {
        const next = content[i + 1];
        if (next === '"') {
          field += '"';
          i += 2;
          continue;
        } else {
          inQuotes = false;
          i += 1;
          continue;
        }
      } else {
        field += ch;
        i += 1;
        continue;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
        i += 1;
        continue;
      }
      if (ch === delimiter) {
        row.push(field);
        field = "";
        i += 1;
        continue;
      }
      if (ch === "\n") {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
        i += 1;
        continue;
      }
      if (ch === "\r") {
        // handle CRLF
        i += 1;
        continue;
      }
      field += ch;
      i += 1;
    }
  }
  // flush last field/row
  row.push(field);
  rows.push(row);
  if (rows.length === 1 && rows[0].length === 1 && rows[0][0] === "") return [];
  return rows;
}

function stringifyCSV(rows, delimiter) {
  function esc(val) {
    const s = String(val ?? "");
    if (s.includes('"')) {
      return '"' + s.replaceAll('"', '""') + '"';
    }
    if (s.includes(delimiter) || s.includes("\n") || s.includes("\r")) {
      return '"' + s + '"';
    }
    return s;
  }
  const out = [];
  for (const r of rows) {
    out.push(r.map(esc).join(delimiter));
  }
  return out.join("\r\n");
}

function digitsOnly(v) {
  const m = String(v ?? "").match(/\d+/g);
  return m ? m.join("") : "";
}

const csvContent = fs.readFileSync(inputPath, "utf-8");
const delimiter = detectDelimiter(csvContent.slice(0, 4096));
const parsed = parseCSV(csvContent, delimiter);
if (!parsed || parsed.length === 0) {
  fs.writeFileSync(outputPath, "", "utf-8");
} else {
  // 2. for every row, get the "id" (from header)
  const header = parsed[0];
  const rows = parsed.slice(1);
  const idIdx = header.indexOf("id");
  const descIdx =
    header.indexOf("description") !== -1
      ? header.indexOf("description")
      : header.indexOf("Description");
  // if description column missing, do nothing special; we keep the row as-is

  // Prepare streaming writer to avoid building huge strings in memory
  const ws = fs.createWriteStream(outputPath, { encoding: "utf-8" });
  ws.write(stringifyCSV([header], delimiter) + "\r\n");

  // 3..6 Iterate rows, fetch and replace description and write each row immediately
  const limit = getLimitArg();
  const max = limit > 0 ? Math.min(rows.length, limit) : rows.length;
  for (let r = 0; r < max; r++) {
    const row = rows[r];
    const idRaw = idIdx >= 0 ? row[idIdx] : "";
    const id = digitsOnly(idRaw);
    if (id) {
      try {
        const app = await store.app({ id });
        const newDesc = app && app.description ? String(app.description) : null;
        if (newDesc && descIdx >= 0) {
          row[descIdx] = newDesc;
        }
      } catch (_) {
        // ignore errors, keep existing description
      }
    }
    ws.write(stringifyCSV([row], delimiter) + "\r\n");
    // release row reference
    rows[r] = null;
  }
  ws.end();
}

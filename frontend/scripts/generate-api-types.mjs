import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import openapiTS from "openapi-typescript";
import ts from "typescript";

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const workspace = resolve(frontend, "..");
const output = join(frontend, "src/lib/api/generated/openapi.ts");
const python =
  process.env.CYBERCASE_PYTHON ??
  join(workspace, "env_mitre", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");

async function exportSchema() {
  const temporary = await mkdtemp(join(tmpdir(), "cybercase-openapi-"));
  try {
    const schemaPath = join(temporary, "openapi.json");
    execFileSync(python, [join(workspace, "backend/scripts/export_openapi.py"), schemaPath], {
      cwd: workspace,
      stdio: "inherit",
    });
    return JSON.parse(await readFile(schemaPath, "utf8"));
  } finally {
    await rm(temporary, { recursive: true, force: true });
  }
}

function render(nodes) {
  const printer = ts.createPrinter({ removeComments: true });
  const source = ts.createSourceFile("openapi.ts", "", ts.ScriptTarget.Latest);
  return `${nodes.map((node) => printer.printNode(ts.EmitHint.Unspecified, node, source)).join("\n")}\n`;
}

const generated = render(await openapiTS(await exportSchema()));

if (process.argv.includes("--check")) {
  const current = await readFile(output, "utf8").catch(() => "");
  if (current.replace(/\r\n/g, "\n") !== generated) {
    console.error("src/lib/api/generated/openapi.ts is stale. Run npm run generate:api-types.");
    process.exitCode = 1;
  }
} else {
  await writeFile(output, generated);
}

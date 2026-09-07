import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import openapiTS from "openapi-typescript";
import ts from "typescript";

const frontend = fileURLToPath(new URL("..", import.meta.url));
const workspace = resolve(frontend, "..");
const python = process.env.CYBERCASE_PYTHON ?? join(workspace, "env_mitre", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const temporary = await mkdtemp(join(tmpdir(), "cybercase-openapi-"));
try {
  const schemaPath = join(temporary, "openapi.json");
  execFileSync(python, [join(workspace, "backend/scripts/export_openapi.py"), schemaPath], { cwd: workspace, stdio: "inherit" });
  const schema = JSON.parse(await readFile(schemaPath, "utf8"));
  const nodes = await openapiTS(schema);
  const components = nodes.find((node) => node.name?.text === "components");
  const schemas = components.members.find((member) => member.name?.text === "schemas").type.members;
  const byName = new Map(schemas.map((member) => [member.name.text, member.type]));
  const printer = ts.createPrinter({ removeComments: true });
  const source = ts.createSourceFile("generated.ts", "", ts.ScriptTarget.Latest);
  const pending = ["ChatThreadRead", "ChatThreadDetail", "ChatMessageRead", "ChatRunRead", "ChatMessageAccepted", "ChatMessageCreate", "CaseNarrativeDocumentSource", "CaseNarrativeDocumentPageSpan"];
  const generated = new Map();
  while (pending.length) {
    const name = pending.pop();
    if (generated.has(name)) continue;
    const type = byName.get(name);
    if (!type) throw new Error(`Missing OpenAPI schema: ${name}`);
    const dependencies = new Set();
    const body = printer.printNode(ts.EmitHint.Unspecified, type, source).replace(/components\["schemas"\]\["([^"]+)"\]/g, (_, dependency) => {
      if (dependency !== name) dependencies.add(dependency);
      return dependency;
    });
    const imports = [...dependencies].sort().map((dependency) => `import type { ${dependency} } from "./${dependency}";`).join("\n");
    const content = `${imports}${imports ? "\n\n" : ""}export type ${name} = ${body};\n`;
    if (content.split("\n").length > 300) throw new Error(`Generated schema exceeds 300 lines: ${name}`);
    generated.set(name, content);
    pending.push(...dependencies);
  }
  const output = join(frontend, "src/lib/generated");
  await mkdir(output, { recursive: true });
  for (const [name, content] of generated) {
    const path = join(output, `${name}.ts`);
    if (process.argv.includes("--check")) {
      if (await readFile(path, "utf8") !== content) throw new Error(`Generated schema is stale: ${name}`);
    } else {
      await writeFile(path, content);
    }
  }
} finally {
  await rm(temporary, { recursive: true, force: true });
}

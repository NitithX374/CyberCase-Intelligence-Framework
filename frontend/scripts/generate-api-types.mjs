import { execFileSync } from "node:child_process";
import {
  mkdtemp,
  mkdir,
  readFile,
  readdir,
  rm,
  unlink,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import openapiTS from "openapi-typescript";
import ts from "typescript";

const modulePath = import.meta.url.startsWith("file:")
  ? fileURLToPath(import.meta.url)
  : null;
const frontend = modulePath
  ? resolve(dirname(modulePath), "..")
  : resolve(process.cwd());
const workspace = resolve(frontend, "..");

export const SCHEMA_GROUPS = Object.freeze({
  caseTypes: [
    "CaseDocumentRead",
    "CaseNarrativeDocumentPageSpan",
    "CaseNarrativeDocumentSource",
    "CaseRead",
    "DocumentExtractionRead",
    "DocumentSourceMetadata",
  ],
  evidenceTypes: [
    "CaseEvidenceCreate",
    "CaseEvidenceSnapshotRead",
    "EvidenceRevisionRead",
    "EvidenceSourceRead",
  ],
  runTypes: [
    "AdmitExtractionRequest",
    "CaseAnalysisAccepted",
    "CaseAnalysisCreate",
    "CaseAnalysisResultRead",
    "CaseChatMessageAccepted",
    "CaseClarificationAccepted",
    "CaseClarificationAnswer",
    "CaseClarificationRead",
    "CaseRunRead",
  ],
  chatTypes: [
    "ChatActionMetadata",
    "ChatCaseLinkRead",
    "ChatMessageAccepted",
    "ChatMessageCreate",
    "ChatMessageRead",
    "ChatReportRead",
    "ChatRetryRequest",
    "ChatRunRead",
    "ChatThreadDetail",
    "ChatThreadRead",
    "FollowUpMetadata",
    "MessageMetadata",
    "RagAttemptMetadata",
  ],
  reportTypes: [
    "CaseReportCreate",
    "ReportClaim",
    "ReportSection",
    "StructuredReport",
  ],
});

export const LEGACY_GENERATED_FILES = Object.freeze([
  "AdmitExtractionRequest.ts",
  "CaseAnalysisAccepted.ts",
  "CaseAnalysisCreate.ts",
  "CaseAnalysisResultRead.ts",
  "CaseChatMessageAccepted.ts",
  "CaseClarificationAccepted.ts",
  "CaseClarificationAnswer.ts",
  "CaseClarificationRead.ts",
  "CaseDocumentRead.ts",
  "CaseEvidenceCreate.ts",
  "CaseEvidenceSnapshotRead.ts",
  "CaseNarrativeDocumentPageSpan.ts",
  "CaseNarrativeDocumentSource.ts",
  "CaseRead.ts",
  "CaseReportCreate.ts",
  "CaseRunRead.ts",
  "ChatActionMetadata.ts",
  "ChatCaseLinkRead.ts",
  "ChatMessageAccepted.ts",
  "ChatMessageCreate.ts",
  "ChatMessageRead.ts",
  "ChatReportRead.ts",
  "ChatRetryRequest.ts",
  "ChatRunRead.ts",
  "ChatThreadDetail.ts",
  "ChatThreadRead.ts",
  "DocumentExtractionRead.ts",
  "DocumentSourceMetadata.ts",
  "EvidenceRevisionRead.ts",
  "EvidenceSourceRead.ts",
  "FollowUpMetadata.ts",
  "MessageMetadata.ts",
  "RagAttemptMetadata.ts",
  "ReportClaim.ts",
  "ReportSection.ts",
  "StructuredReport.ts",
]);

function createSchemaOwners() {
  const owners = new Map();

  for (const [domain, names] of Object.entries(SCHEMA_GROUPS)) {
    for (const name of names) {
      if (owners.has(name)) {
        throw new Error(
          `Schema has duplicate ownership: ${name} (${owners.get(name)} and ${domain})`,
        );
      }

      owners.set(name, domain);
    }
  }

  return owners;
}

function getOpenApiSchemaTypes(nodes) {
  const components = nodes.find((node) => node.name?.text === "components");
  const schemas = components?.members.find(
    (member) => member.name?.text === "schemas",
  );

  if (!schemas) {
    throw new Error("OpenAPI schema components are missing");
  }

  return new Map(schemas.type.members.map((member) => [member.name.text, member.type]));
}

function renderSchemaType(name, type, printer, source, owners) {
  const dependencies = new Set();
  const body = printer
    .printNode(ts.EmitHint.Unspecified, type, source)
    .replace(
      /components\["schemas"\]\["([^"]+)"\]/g,
      (_, dependency) => {
        if (dependency !== name) {
          dependencies.add(dependency);
        }

        if (!owners.has(dependency)) {
          throw new Error(
            `Schema dependency has no domain owner: ${name} -> ${dependency}`,
          );
        }

        return dependency;
      },
    );

  return { body, dependencies };
}

function renderDomainFile(domain, names, renderedTypes, owners) {
  const importsByDomain = new Map();

  for (const name of names) {
    for (const dependency of renderedTypes.get(name).dependencies) {
      const dependencyDomain = owners.get(dependency);

      if (dependencyDomain === domain) {
        continue;
      }

      const domainImports = importsByDomain.get(dependencyDomain) ?? new Set();
      domainImports.add(dependency);
      importsByDomain.set(dependencyDomain, domainImports);
    }
  }

  const imports = [...importsByDomain.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([dependencyDomain, dependencies]) => {
      const names = [...dependencies].sort().join(", ");
      return `import type { ${names} } from "./${dependencyDomain}";`;
    });
  const definitions = [...names]
    .sort()
    .map((name) => {
      const { body } = renderedTypes.get(name);
      return `export type ${name} = ${body};`;
    })
    .join("\n\n");

  return `${imports.join("\n")}${imports.length ? "\n\n" : ""}${definitions}\n`;
}

export async function buildGeneratedFiles(schema) {
  const nodes = await openapiTS(schema);
  const schemaTypes = getOpenApiSchemaTypes(nodes);
  const owners = createSchemaOwners();
  const printer = ts.createPrinter({ removeComments: true });
  const source = ts.createSourceFile("generated.ts", "", ts.ScriptTarget.Latest);
  const renderedTypes = new Map();

  for (const names of Object.values(SCHEMA_GROUPS)) {
    for (const name of names) {
      const type = schemaTypes.get(name);

      if (!type) {
        throw new Error(`Missing OpenAPI schema: ${name}`);
      }

      renderedTypes.set(
        name,
        renderSchemaType(name, type, printer, source, owners),
      );
    }
  }

  return new Map(
    Object.entries(SCHEMA_GROUPS)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([domain, names]) => [
        `${domain}.ts`,
        renderDomainFile(domain, names, renderedTypes, owners),
      ]),
  );
}

async function getOutputEntries(output) {
  try {
    return await readdir(output, { withFileTypes: true });
  } catch (error) {
    if (error.code === "ENOENT") {
      return [];
    }

    throw error;
  }
}

async function assertGeneratedFile(path, name, expected) {
  let actual;

  try {
    actual = await readFile(path, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") {
      throw new Error(`Generated output is missing: ${name}`);
    }

    throw error;
  }

  if (actual !== expected) {
    throw new Error(`Generated output is stale: ${name}`);
  }
}

export async function syncGeneratedFiles(output, generated, { check = false } = {}) {
  const entries = await getOutputEntries(output);
  const expectedNames = new Set(generated.keys());
  const staleEntries = entries.filter((entry) => !expectedNames.has(entry.name));

  if (staleEntries.some((entry) => !LEGACY_GENERATED_FILES.includes(entry.name))) {
    const names = staleEntries.map((entry) => entry.name).sort().join(", ");
    throw new Error(`Unexpected generated output in owned directory: ${names}`);
  }

  if (check) {
    for (const [name, content] of generated) {
      await assertGeneratedFile(join(output, name), name, content);
    }

    if (staleEntries.length) {
      const names = staleEntries.map((entry) => entry.name).sort().join(", ");
      throw new Error(`Generated output is obsolete: ${names}`);
    }

    return;
  }

  await mkdir(output, { recursive: true });

  for (const entry of staleEntries) {
    if (!entry.isFile()) {
      throw new Error(`Cannot remove non-file generated output: ${entry.name}`);
    }

    await unlink(join(output, entry.name));
  }

  for (const [name, content] of generated) {
    await writeFile(join(output, name), content);
  }
}

export async function generateApiTypes({
  check = false,
  python = process.env.CYBERCASE_PYTHON ??
    join(
      workspace,
      "env_mitre",
      process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
    ),
  } = {}) {
  const temporary = await mkdtemp(join(tmpdir(), "cybercase-openapi-"));

  try {
    const schemaPath = join(temporary, "openapi.json");
    execFileSync(
      python,
      [join(workspace, "backend/scripts/export_openapi.py"), schemaPath],
      { cwd: workspace, stdio: "inherit" },
    );
    const schema = JSON.parse(await readFile(schemaPath, "utf8"));
    const generated = await buildGeneratedFiles(schema);
    const output = join(frontend, "src/lib/generated");

    await syncGeneratedFiles(output, generated, { check });
  } finally {
    await rm(temporary, { recursive: true, force: true });
  }
}

const isMainModule =
  modulePath &&
  process.argv[1] &&
  resolve(process.argv[1]) === resolve(modulePath);

if (isMainModule) {
  await generateApiTypes({ check: process.argv.includes("--check") });
}

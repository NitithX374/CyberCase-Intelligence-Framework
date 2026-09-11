import assert from "node:assert/strict";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import {
  LEGACY_GENERATED_FILES,
  SCHEMA_GROUPS,
  buildGeneratedFiles,
  syncGeneratedFiles,
} from "./generate-api-types.mjs";

function createSchemaFixture() {
  const names = Object.values(SCHEMA_GROUPS).flat();
  const schemas = Object.fromEntries(
    names.map((name) => [name, { type: "object", properties: {} }]),
  );

  return {
    openapi: "3.0.0",
    info: { title: "Generator fixture", version: "1.0.0" },
    paths: {},
    components: { schemas },
  };
}

async function createOutputDirectory() {
  return mkdtemp(join(tmpdir(), "cybercase-generator-test-"));
}

test("schema groups have unique ownership and stable output names", async () => {
  const names = Object.values(SCHEMA_GROUPS).flat();
  assert.equal(new Set(names).size, names.length);

  const first = await buildGeneratedFiles(createSchemaFixture());
  const second = await buildGeneratedFiles(createSchemaFixture());

  assert.deepEqual([...first], [...second]);
  assert.deepEqual([...first.keys()], [
    "caseTypes.ts",
    "chatTypes.ts",
    "evidenceTypes.ts",
    "reportTypes.ts",
    "runTypes.ts",
  ]);
});

test("check mode rejects obsolete legacy generated files", async () => {
  const output = await createOutputDirectory();
  const generated = new Map([["caseTypes.ts", "export type Case = {};\n"]]);

  try {
    await writeFile(join(output, "caseTypes.ts"), generated.get("caseTypes.ts"));
    await writeFile(join(output, LEGACY_GENERATED_FILES[0]), "");

    await assert.rejects(
      syncGeneratedFiles(output, generated, { check: true }),
      /Generated output is obsolete/,
    );
  } finally {
    await rm(output, { recursive: true, force: true });
  }
});

test("generation removes only known legacy files and rejects unknown files", async () => {
  const output = await createOutputDirectory();
  const generated = new Map([["caseTypes.ts", "export type Case = {};\n"]]);

  try {
    await writeFile(join(output, LEGACY_GENERATED_FILES[0]), "");
    await syncGeneratedFiles(output, generated);
    assert.deepEqual(await readdir(output), ["caseTypes.ts"]);
    assert.equal(
      await readFile(join(output, "caseTypes.ts"), "utf8"),
      generated.get("caseTypes.ts"),
    );

    await writeFile(join(output, "unexpected.ts"), "");
    await assert.rejects(
      syncGeneratedFiles(output, generated),
      /Unexpected generated output/,
    );
  } finally {
    await rm(output, { recursive: true, force: true });
  }
});

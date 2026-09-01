import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import ts from "../../frontend/node_modules/typescript/lib/typescript.js";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const requestedFiles = JSON.parse(fs.readFileSync(0, "utf8"));

function clean(text) {
  return text.replace(/\s+/g, " ").trim().slice(0, 220);
}

function lineOf(sourceFile, node) {
  return sourceFile.getLineAndCharacterOfPosition(node.getStart(sourceFile)).line + 1;
}

function declarationName(node, fallback) {
  if (node.name && ts.isIdentifier(node.name)) return node.name.text;
  if (node.name) return clean(node.name.getText());
  return fallback;
}

function parameters(node, sourceFile) {
  if (!node.parameters) return "";
  return node.parameters.map((parameter) => clean(parameter.getText(sourceFile))).join(", ");
}

function returnType(node, sourceFile) {
  return node.type ? `: ${clean(node.type.getText(sourceFile))}` : "";
}

function addSymbol(symbols, sourceFile, node, kind, name, signature, parent = "") {
  symbols.push({
    kind,
    name,
    qualified_name: parent ? `${parent}.${name}` : name,
    line: lineOf(sourceFile, node),
    signature: clean(signature),
  });
}

function walk(sourceFile) {
  const symbols = [];

  function visit(node, parentName = "") {
    if (ts.isFunctionDeclaration(node)) {
      const name = declarationName(node, "default");
      addSymbol(
        symbols,
        sourceFile,
        node,
        "function",
        name,
        `function ${name}(${parameters(node, sourceFile)})${returnType(node, sourceFile)}`,
        parentName,
      );
    } else if (ts.isClassDeclaration(node)) {
      const name = declarationName(node, "default class");
      addSymbol(symbols, sourceFile, node, "class", name, `class ${name}`, parentName);
      node.members.forEach((member) => visit(member, parentName ? `${parentName}.${name}` : name));
      return;
    } else if (ts.isMethodDeclaration(node)) {
      const name = declarationName(node, "method");
      addSymbol(
        symbols,
        sourceFile,
        node,
        "method",
        name,
        `${name}(${parameters(node, sourceFile)})${returnType(node, sourceFile)}`,
        parentName,
      );
    } else if (ts.isConstructorDeclaration(node)) {
      addSymbol(
        symbols,
        sourceFile,
        node,
        "constructor",
        "constructor",
        `constructor(${parameters(node, sourceFile)})`,
        parentName,
      );
    } else if (ts.isVariableDeclaration(node) && node.initializer) {
      const name = declarationName(node, "variable");
      if (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer)) {
        addSymbol(
          symbols,
          sourceFile,
          node,
          "function",
          name,
          `${name}(${parameters(node.initializer, sourceFile)})${returnType(node.initializer, sourceFile)}`,
          parentName,
        );
      }
    } else if (ts.isInterfaceDeclaration(node)) {
      const name = declarationName(node, "interface");
      addSymbol(symbols, sourceFile, node, "interface", name, `interface ${name}`, parentName);
    } else if (ts.isTypeAliasDeclaration(node)) {
      const name = declarationName(node, "type");
      addSymbol(symbols, sourceFile, node, "type", name, `type ${name}`, parentName);
    } else if (ts.isEnumDeclaration(node)) {
      const name = declarationName(node, "enum");
      addSymbol(symbols, sourceFile, node, "enum", name, `enum ${name}`, parentName);
    }

    ts.forEachChild(node, (child) => visit(child, parentName));
  }

  visit(sourceFile);
  return symbols.sort((left, right) => left.line - right.line || left.qualified_name.localeCompare(right.qualified_name));
}

const result = requestedFiles.map((relativePath) => {
  const absolutePath = path.join(projectRoot, relativePath);
  const sourceText = fs.readFileSync(absolutePath, "utf8");
  const scriptKind = relativePath.endsWith(".tsx")
    ? ts.ScriptKind.TSX
    : relativePath.endsWith(".jsx")
      ? ts.ScriptKind.JSX
      : relativePath.endsWith(".js") || relativePath.endsWith(".mjs")
        ? ts.ScriptKind.JS
        : ts.ScriptKind.TS;
  const sourceFile = ts.createSourceFile(relativePath, sourceText, ts.ScriptTarget.Latest, true, scriptKind);
  return { path: relativePath.replaceAll("\\", "/"), symbols: walk(sourceFile) };
});

process.stdout.write(JSON.stringify(result));

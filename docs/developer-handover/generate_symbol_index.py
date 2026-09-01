import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = Path(__file__).with_name("SYMBOL_INDEX.md")
TYPESCRIPT_EXTRACTOR = Path(__file__).with_name("extract_typescript_symbols.mjs")
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs"}
IGNORED_PARTS = {"node_modules", ".next", "__pycache__", ".pytest_cache", "env_mitre"}


def run(command: list[str]) -> str:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def source_files() -> list[Path]:
    tracked = set(run(["git", "ls-files"]).splitlines())
    untracked = set(run(["git", "ls-files", "--others", "--exclude-standard"]).splitlines())
    selected = []
    for relative in tracked | untracked:
        path = PROJECT_ROOT / relative
        if path.suffix not in SOURCE_SUFFIXES or not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        selected.append(path)
    return sorted(selected, key=lambda item: item.relative_to(PROJECT_ROOT).as_posix().lower())


def first_sentence(text: str | None) -> str | None:
    if not text:
        return None
    compact = " ".join(text.split())
    for separator in (". ", "\n"):
        if separator in compact:
            compact = compact.split(separator, 1)[0]
    return compact.rstrip(".") + "."


def words(name: str) -> str:
    normalized = name.replace("-", "_").replace(".", "_")
    output = []
    for character in normalized:
        if output and character.isupper() and output[-1][-1].islower():
            output.append(character.lower())
        elif character == "_":
            if output and output[-1] != " ":
                output.append(" ")
        else:
            output.append(character.lower())
    return "".join(output).strip()


def area_for(relative: str) -> str:
    if relative.startswith("backend/app/"):
        return "backend runtime"
    if relative.startswith("backend/tests/"):
        return "backend regression suite"
    if relative.startswith("backend/alembic/"):
        return "database migration layer"
    if relative.startswith("frontend/src/test/"):
        return "frontend regression suite"
    if relative.startswith("frontend/src/"):
        return "frontend application"
    if relative.startswith("rag_service/app/"):
        return "GraphRAG runtime and evaluation package"
    if relative.startswith("rag_service/tests/"):
        return "GraphRAG regression suite"
    if relative.startswith(("research/", "experiments/", "evaluation/", "deliverables/")):
        return "research and evaluation workspace"
    return "repository tooling"


def file_purpose(relative: str, module_doc: str | None = None) -> str:
    sentence = first_sentence(module_doc)
    if sentence:
        return sentence
    path = Path(relative)
    stem = words(path.stem)
    area = area_for(relative)
    if path.name in {"__init__.py", "index.ts"}:
        return f"Defines the public package surface for the {area}."
    if "/test" in relative or path.name.startswith("test_") or path.name.endswith(".test.tsx"):
        return f"Verifies {stem.replace('test ', '')} behavior in the {area}."
    if path.name in {"page.tsx", "layout.tsx", "providers.tsx"}:
        route = path.parent.as_posix().replace("frontend/src/app/", "") or "root"
        return f"Implements the Next.js {path.stem} entry for the `{route}` route segment."
    if "/components/" in relative:
        return f"Renders and coordinates the {stem} user-interface component."
    return f"Owns {stem} behavior for the {area}."


def describe(name: str, kind: str) -> str:
    readable = words(name.split(".")[-1]).lstrip("_") or name
    if kind in {"class", "interface", "type", "enum"}:
        verbs = {
            "class": "Encapsulates",
            "interface": "Defines the structural contract for",
            "type": "Defines the type contract for",
            "enum": "Enumerates allowed values for",
        }
        return f"{verbs[kind]} {readable}."
    rules = [
        (("get", "load", "read", "fetch"), "Retrieves"),
        (("list",), "Lists"),
        (("create", "new"), "Creates"),
        (("build", "assemble", "compose"), "Builds"),
        (("update", "set", "rename"), "Updates"),
        (("delete", "remove", "clear", "prune"), "Removes"),
        (("validate", "verify", "check"), "Validates"),
        (("parse", "decode"), "Parses"),
        (("serialize", "encode", "export"), "Serializes"),
        (("render",), "Renders"),
        (("generate",), "Generates"),
        (("persist", "store", "save", "record"), "Persists"),
        (("process", "run", "execute"), "Executes"),
        (("map", "convert", "to", "from"), "Transforms"),
        (("normalize", "sanitize", "clean"), "Normalizes"),
        (("extract", "select", "pick"), "Extracts"),
        (("is", "has", "can", "should"), "Determines"),
        (("use",), "Provides the React hook for"),
        (("handle", "on"), "Handles"),
    ]
    first = readable.split(" ", 1)[0]
    for prefixes, verb in rules:
        if first in prefixes:
            rest = readable[len(first) :].strip() or readable
            return f"{verb} {rest}."
    if name.split(".")[-1][:1].isupper():
        return f"Renders or constructs {readable}."
    return f"Implements {readable}."


def python_signature(node: ast.AST) -> str:
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(base) for base in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def python_symbols(path: Path) -> tuple[str | None, list[dict[str, object]]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    symbols = []

    class SymbolVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.scope: list[tuple[str, str]] = []

        def qualified(self, name: str) -> str:
            names = [item[0] for item in self.scope]
            return ".".join([*names, name])

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            qualified = self.qualified(node.name)
            symbols.append({"kind": "class", "name": qualified, "line": node.lineno, "signature": python_signature(node), "doc": ast.get_docstring(node)})
            self.scope.append((node.name, "class"))
            self.generic_visit(node)
            self.scope.pop()

        def record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            qualified = self.qualified(node.name)
            kind = "method" if self.scope and self.scope[-1][1] == "class" else "function"
            symbols.append({"kind": kind, "name": qualified, "line": node.lineno, "signature": python_signature(node), "doc": ast.get_docstring(node)})
            self.scope.append((node.name, "function"))
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.record_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.record_function(node)

    SymbolVisitor().visit(tree)
    return ast.get_docstring(tree), symbols


def typescript_symbols(paths: list[Path]) -> dict[str, list[dict[str, object]]]:
    if not paths:
        return {}
    relative_paths = [path.relative_to(PROJECT_ROOT).as_posix() for path in paths]
    completed = subprocess.run(
        ["node", str(TYPESCRIPT_EXTRACTOR)],
        cwd=PROJECT_ROOT,
        input=json.dumps(relative_paths),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {item["path"]: item["symbols"] for item in json.loads(completed.stdout)}


def section_for(relative: str) -> str:
    return area_for(relative).title()


def generate() -> str:
    files = source_files()
    web_files = [path for path in files if path.suffix != ".py"]
    web_symbols = typescript_symbols(web_files)
    branch = run(["git", "branch", "--show-current"])
    commit = run(["git", "rev-parse", "--short", "HEAD"])
    dirty = bool(run(["git", "status", "--short"]))
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# CyberCase File and Function Index",
        "",
        f"Generated `{generated}` from branch `{branch}` at commit `{commit}`; working tree dirty: `{'yes' if dirty else 'no'}`.",
        "",
        "This is the exhaustive first-party source inventory for the checkout. Descriptions generated from code names are navigation aids; runtime truth is determined by imports, route registration, and the handover guide.",
        "",
    ]
    grouped: dict[str, list[Path]] = {}
    for path in files:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        grouped.setdefault(section_for(relative), []).append(path)
    symbol_count = 0
    for section, section_files in grouped.items():
        lines.extend([f"## {section}", ""])
        for path in section_files:
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            if path.suffix == ".py":
                module_doc, symbols = python_symbols(path)
            else:
                module_doc, symbols = None, web_symbols.get(relative, [])
            symbol_count += len(symbols)
            lines.extend([f"### [`{relative}`](../../{relative})", "", f"Purpose: {file_purpose(relative, module_doc)}", ""])
            if not symbols:
                lines.extend(["No named functions, classes, interfaces, types, or enums are declared in this file.", ""])
                continue
            for symbol in symbols:
                description = first_sentence(symbol.get("doc")) or describe(str(symbol["name"]), str(symbol["kind"]))
                signature = str(symbol["signature"]).replace("`", "'")
                lines.append(f"- L{symbol['line']} `{signature}` — {description}")
            lines.append("")
    lines[5:5] = [f"Coverage: **{len(files)} source files** and **{symbol_count} named symbols**.", ""]
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    OUTPUT_PATH.write_text(generate(), encoding="utf-8")
    print(OUTPUT_PATH)

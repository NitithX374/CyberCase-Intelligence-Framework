import { describe, expect, it, vi } from "vitest";
import { backendDirectory, backendEnvironment, migrateThenServe } from "../../e2e/backend.mjs";

type Spawn = (command: string, args: string[], options: { cwd: string; env: object }) => unknown;

describe("the backend the end-to-end tests start", () => {
  it("brings its database to the current schema before it serves, with the same settings", () => {
    const server = { pid: 1 };
    const run = vi.fn<Spawn>(() => ({ status: 0 }));
    const start = vi.fn<Spawn>(() => server);

    const outcome = migrateThenServe({ run, start });

    const [python, migrationArgs, migrationOptions] = run.mock.calls[0];
    const [serverPython, serverArgs, serverOptions] = start.mock.calls[0];
    expect(migrationArgs).toEqual(["-m", "alembic", "upgrade", "head"]);
    expect(serverArgs.slice(0, 3)).toEqual(["-m", "uvicorn", "app.main:app"]);
    expect(run.mock.invocationCallOrder[0]).toBeLessThan(start.mock.invocationCallOrder[0]);
    expect(serverPython).toBe(python);
    expect(migrationOptions).toMatchObject({ cwd: backendDirectory, env: backendEnvironment });
    expect(serverOptions).toBe(migrationOptions);
    expect(outcome).toEqual({ exitCode: 0, server });
  });

  it("does not serve a database it could not migrate", () => {
    const start = vi.fn<Spawn>();

    const outcome = migrateThenServe({ run: () => ({ status: 2 }), start });

    expect(start).not.toHaveBeenCalled();
    expect(outcome).toEqual({ exitCode: 2, server: null });
  });

  it("fails when the migration could not run at all", () => {
    const start = vi.fn<Spawn>();

    const outcome = migrateThenServe({ run: () => ({ status: null }), start });

    expect(start).not.toHaveBeenCalled();
    expect(outcome).toEqual({ exitCode: 1, server: null });
  });
});

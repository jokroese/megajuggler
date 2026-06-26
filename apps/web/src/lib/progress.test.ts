import { describe, expect, test } from "vitest";
import { createProgressExport, parseProgressImport, serialiseProgress } from "./progress";

describe("progress import/export", () => {
  test("creates a stable versioned progress export", () => {
    const exported = createProgressExport(
      new Set(["reverse-cascade", "cascade"]),
      new Date("2026-06-26T12:00:00.000Z"),
    );
    expect(exported).toEqual({
      version: 1,
      exportedAt: "2026-06-26T12:00:00.000Z",
      knownTrickIds: ["cascade", "reverse-cascade"],
    });
  });

  test("serialises progress as formatted JSON", () => {
    const serialised = serialiseProgress(
      new Set(["cascade"]),
      new Date("2026-06-26T12:00:00.000Z"),
    );
    expect(serialised).toBe(
      '{\n  "version": 1,\n  "exportedAt": "2026-06-26T12:00:00.000Z",\n  "knownTrickIds": [\n    "cascade"\n  ]\n}\n',
    );
  });

  test("imports versioned progress", () => {
    const imported = parseProgressImport(
      JSON.stringify({
        version: 1,
        exportedAt: "2026-06-26T12:00:00.000Z",
        knownTrickIds: ["cascade", "reverse-cascade"],
      }),
    );
    expect([...imported]).toEqual(["cascade", "reverse-cascade"]);
  });

  test("imports legacy progress arrays", () => {
    const imported = parseProgressImport(JSON.stringify(["cascade", "reverse-cascade", 123]));
    expect([...imported]).toEqual(["cascade", "reverse-cascade"]);
  });

  test("rejects invalid progress", () => {
    expect(() => parseProgressImport(JSON.stringify({ nope: true }))).toThrow(
      "Progress file must contain a Megajuggler progress export.",
    );
  });
});

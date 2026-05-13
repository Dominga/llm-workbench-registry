# Registry format reference

The Workbench app fetches one JSON file from each subscribed registry
source. This document pins the schema so authors and tooling stay in
sync.

## `index.json` schema

```json
{
  "schema_version": 1,
  "updated_at": "2026-05-13T12:34:56Z",
  "artifacts": [
    {
      "type": "mode" | "family",
      "id": "worldbuilder",
      "version": "1.2.0",
      "sha256": "<hex of concatenated file contents in declared order>",
      "files": [
        { "path": "worldbuilder.toml", "url": "https://raw.../worldbuilder.toml" },
        { "path": "worldbuilder.system.md", "url": "https://raw.../worldbuilder.system.md" }
      ],
      "description": "Narrative worldbuilding helper.",
      "tags": ["narrative", "rpg"],
      "recommended_for": ["qwen3", "qwen3.5"],
      "author": "<name or handle>",
      "preview": "First ~500 chars of the system prompt..."
    }
  ]
}
```

### Field rules

- `schema_version` — integer; bump only on breaking changes.
- `type` — `"mode"` or `"family"`. Other types reserved for future use
  (`"script"`, `"tool"` etc.).
- `id` — `[a-z0-9][a-z0-9._-]{0,63}`. Used as the destination filename
  basename, so it must be filesystem-safe.
- `version` — free-form, but [semver](https://semver.org/) is strongly
  recommended so update-notification logic can compare correctly.
- `sha256` — optional but recommended. Hex of the SHA-256 over each
  file's content concatenated in `files[]` order. The Workbench app
  refuses to install if the computed hash doesn't match.
- `files[].path` — destination basename only (no slashes); the
  Workbench app rejects anything else as a safety measure.
- `files[].url` — fully qualified URL. `raw.githubusercontent.com`
  links are the easy default.
- `tags` — free-form, but try to reuse existing ones so filtering
  stays useful.
- `recommended_for` — list of family IDs (see the Workbench's
  `families/` directory for canonical names). Advisory only — the
  picker shows a soft warning when the active profile family isn't
  listed.
- `preview` — short snippet shown in the registry browser before the
  user installs. ~500 chars max; longer strings are truncated.
- `default_install` — optional bool. When `true`, the Workbench
  auto-installs the artifact the first time it subscribes to the
  source (only if the destination files don't already exist on disk,
  so upgrades from a previous app version are never clobbered). The
  official `agent` / `auto-edit` / `research` modes set this so new
  users get a working set out of the box.

## Mode files

A mode bundle is two files:

- `<id>.toml` — definition (see the
  [Workbench mode docs](https://github.com/Dominga/LLM-Worckbench/blob/main/llm-workbench/docs/prompt-variables.md)
  for `recommended_for` semantics).
- `<id>.system.md` — default prompt template. Supports `{{...}}`
  placeholders (see `prompt-variables.md`).
- Optional `<id>.<family>.system.md` (and `<id>.<family>.<version>.system.md`)
  — family-tuned variants. The Workbench resolver picks the most
  specific match for the active profile.

Each variant referenced by the mode must be listed in `files[]`. The
build CI verifies this.

## Family files

Single file: `<id>.toml`. See the Workbench's bundled families
(`llm-workbench/families/`) for the schema (id, name, description,
chat_template_hint, reasoning_token, sampling_defaults, notes).

## Versioning

- Bump `version` on every meaningful change to the artifact's content.
- The Workbench compares installed-vs-latest by string equality —
  semver-shaped strings sort naturally most of the time, but exact
  match is what drives the "update available" badge.

## Tags taxonomy (informal)

These are the tags currently used. Reuse rather than coin new ones
unless your category is genuinely new:

- `narrative`, `rpg`, `worldbuilding`, `gamedesign`
- `coding`, `refactor`, `review`
- `research`, `summarisation`
- `experimental` (use freely)

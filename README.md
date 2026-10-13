# cjm-vad-adapter-interface

<!-- generated from the context graph by `cjm-context-graph readme` — do not edit by hand; edit the graph (the urge to hand-edit = move it on-graph) -->

_No purpose recorded on-graph yet — author it with_ `assert b841c358-3bb8-50cb-b461-fc4567b4f538 purpose "…"` _(or by the repo's entity key)._

## Modules

- **`cjm_vad_adapter_interface.__init__`**
- **`cjm_vad_adapter_interface.adapter`** — The typed voice-activity-detection task contract — the VADAdapter ABC + the VADToolProtocol structural contract (capability-unit Option C, pass-2 Thread 3).
- **`cjm_vad_adapter_interface.generic`** — The generic (tool-agnostic) VAD adapter — cache-check, invoke the bound tool's pure-compute detect_speech, persist; reused across every tool capability satisfying VADToolProtocol.
- **`cjm_vad_adapter_interface.storage`** — Standardized SQLite storage for voice-activity-detection results with content hashing — the cache/persistence bookend GenericVADAdapter wraps around the pure-compute VAD tool.

## API

### `cjm_vad_adapter_interface.adapter`

- `VADAdapter` _class_ — Typed voice-activity-detection task adapter: model-ready audio in,
- `VADToolProtocol` _class_ — Structural contract for voice-activity-detection tool capabilities

### `cjm_vad_adapter_interface.generic`

- `GenericVADAdapter` _class_ — Generic VAD adapter: cache-check -> pure-compute tool -> persist.

### `cjm_vad_adapter_interface.storage`

- `VADRow` _class_ — A single row from the vad_results table.
- `VADStorage` _class_ — Standardized SQLite storage for voice-activity-detection results.

## Dependencies

**Depends on:** `cjm-capability-primitives`, `cjm-substrate`

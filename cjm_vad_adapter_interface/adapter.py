"""The typed voice-activity-detection task contract — the VADAdapter ABC + the VADToolProtocol structural contract (capability-unit Option C, pass-2 Thread 3).

Surface-based compatibility (stage 4) gates auto-binding: only tools whose
RECORDED structural surface carries `detect_speech` + `get_current_config`
match — a fused-era execute-shaped tool does not satisfy the protocol. The
caller guarantees MODEL-READY audio (resample / mono / decode upstream via
ffmpeg `convert`; silero-vad's librosa load+resample retired on migration —
the tool reads ready audio via soundfile). Canonical data-noun home (stage 8 /
PILLAR 1c): `VADResult` lives in cjm-capability-primitives, so the
pure-compute tool depends on it, never on this adapter machinery."""

from abc import abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Dict, Protocol, runtime_checkable, Union

from cjm_capability_primitives.vad import VADResult
from cjm_substrate.core.adapter import TaskAdapter


@runtime_checkable
class VADToolProtocol(Protocol):
    """Structural contract for voice-activity-detection tool capabilities
    (born-final at stage 8 — derived from the native tool surface).

    Pure compute: `detect_speech` reads the model-ready audio + runs inference +
    builds the typed result. `get_current_config` supplies the effective config
    the generic adapter hashes for its cache key. Persistence is NOT here — the
    adapter owns it (the native-surface seam)."""

    def detect_speech(self, audio: Union[str, Path], **kwargs) -> VADResult: ...
    def get_current_config(self) -> Dict[str, Any]: ...


class VADAdapter(TaskAdapter):
    """Typed voice-activity-detection task adapter: model-ready audio in,
    `VADResult` out.

    Input contract: the caller guarantees MODEL-READY audio — format /
    sample-rate / channel handling happens upstream (ffmpeg `convert`), never
    in the adapter or tool.

    Native-surface model (stage 8 / PILLAR 1c): the TOOL is pure compute; the
    ADAPTER owns the cache + persistence bookends (see `GenericVADAdapter`) +
    the per-call `force` control. Storage resolves from the substrate-injected
    `CAPABILITY_DATA_DIR`; `db_path` is not on the tool protocol.

    Implementations run in-worker beside their tool capability and are
    constructed with the bound tool instance: `AdapterClass(tool)` (mirrors
    `GraphStorageAdapter`). The result DTO is wire-registered ("vad.result"):
    returned values cross the worker boundary typed.
    """

    task_name: ClassVar[str] = "vad"
    required_tool_protocol: ClassVar[type] = VADToolProtocol

    def __init__(
        self,
        tool: VADToolProtocol,  # The bound tool capability instance (worker-side binding)
    ):
        self.tool = tool

    @abstractmethod
    def detect_speech(
        self,
        audio: Union[str, Path],  # Path to MODEL-READY audio (converted upstream)
        **kwargs,                 # Provenance + tool options
    ) -> VADResult:               # Typed VAD output
        """Detect speech segments in model-ready audio."""
        ...

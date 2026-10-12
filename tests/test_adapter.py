"""Shape tests for the VAD task contract (projected from nbs/adapter.ipynb at
the golden-reference flip): abstract gate + ClassVars + __init__(tool) + a
concrete impl returning the typed DTO + the protocol structurally matching a
migrated tool surface (detect_speech + get_current_config) and rejecting a
fused-era execute tool."""

import pytest
from cjm_capability_primitives.vad import TimeRange, VADResult
from cjm_vad_adapter_interface.adapter import VADAdapter, VADToolProtocol


class _FakeTool:  # structural match, no inheritance
    def detect_speech(self, audio, **kwargs) -> VADResult:
        return VADResult(ranges=[TimeRange(start=0.0, end=1.0)], metadata={"src": audio})

    def get_current_config(self):
        return {"threshold": 0.5}


class _FakeVADAdapter(VADAdapter):
    def detect_speech(self, audio, **kwargs) -> VADResult:
        return self.tool.detect_speech(audio, **kwargs)


class _FusedEraTool:
    def execute(self, media_path, **kwargs):
        return {"ranges": []}


def test_abstract_gate_refuses_instantiation():
    with pytest.raises(TypeError):
        VADAdapter(_FakeTool())  # type: ignore[abstract]


def test_concrete_impl_returns_typed_dto_and_classvars_hold():
    impl = _FakeVADAdapter(_FakeTool())
    out = impl.detect_speech("a.wav")
    assert isinstance(out, VADResult) and out.ranges[0].end == 1.0
    assert VADAdapter.task_name == "vad"
    assert VADAdapter.required_tool_protocol is VADToolProtocol


def test_protocol_matches_native_surface_not_fused_era():
    assert isinstance(_FakeTool(), VADToolProtocol)
    # the fused-era execute-shaped tool does NOT satisfy the real protocol
    assert not isinstance(_FusedEraTool(), VADToolProtocol)

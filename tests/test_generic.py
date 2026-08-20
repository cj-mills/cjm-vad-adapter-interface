"""Cache-bookends tests for GenericVADAdapter (projected from nbs/generic.ipynb
at the golden-reference flip): miss -> compute + persist; hit -> NO recompute
(ranges re-type to TimeRange); force via CallEnvelope.control -> bypass +
recompute."""

from cjm_capability_primitives.vad import TimeRange, VADResult
from cjm_substrate.core.wire import CallEnvelope, reset_call_envelope, set_call_envelope
from cjm_vad_adapter_interface.generic import GenericVADAdapter


class _FakeTool:
    def __init__(self):
        self.calls = 0

    def get_current_config(self):
        return {"threshold": 0.5}

    def detect_speech(self, audio, **kwargs) -> VADResult:
        self.calls += 1
        return VADResult(ranges=[TimeRange(start=0.0, end=float(self.calls))],
                         metadata={"calls": self.calls})


def test_cache_bookends_miss_hit_force(tmp_path, monkeypatch):
    monkeypatch.setenv("CAPABILITY_DATA_DIR", str(tmp_path))
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"audiobytes")

    tool = _FakeTool()
    ad = GenericVADAdapter(tool)

    # 1. cache MISS -> compute (calls=1) + persist
    r1 = ad.detect_speech(str(audio))
    assert tool.calls == 1 and r1.ranges[0].end == 1.0

    # 2. cache HIT -> no recompute; ranges re-typed to TimeRange (NOT dicts)
    r2 = ad.detect_speech(str(audio))
    assert tool.calls == 1, f"expected cache hit, calls={tool.calls}"
    assert isinstance(r2.ranges[0], TimeRange) and r2.ranges[0].end == 1.0

    # 3. force via CallEnvelope.control -> bypass cache, recompute (calls=2)
    tok = set_call_envelope(CallEnvelope(job_id="j3", control={"force": True}))
    try:
        ad.detect_speech(str(audio))
    finally:
        reset_call_envelope(tok)
    assert tool.calls == 2, f"force should bypass cache, calls={tool.calls}"

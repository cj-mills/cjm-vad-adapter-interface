"""VADStorage tests (projected from nbs/storage.ipynb at the golden-reference
flip): content-correct get_cached hit/miss + INSERT OR REPLACE upsert on
(file_path, config_hash), and save_with_logging's success + swallowed-failure
paths."""

import logging

from cjm_vad_adapter_interface.storage import VADStorage

FH = "sha256:" + "a" * 64
CFG = "sha256:" + "c" * 64


def _storage(tmp_path):
    return VADStorage(str(tmp_path / "vad.db"))


def test_get_cached_hit_miss_and_upsert(tmp_path):
    storage = _storage(tmp_path)
    storage.save(file_path="/tmp/a.wav", file_hash=FH, config_hash=CFG,
                 ranges=[{"start": 0.0, "end": 2.5, "label": "speech",
                          "confidence": 1.0, "payload": {}}],
                 metadata={"duration": 6.0, "sample_rate": 16000})

    hit = storage.get_cached("/tmp/a.wav", FH, CFG)
    assert hit is not None and hit.ranges[0]["end"] == 2.5
    # changed content -> miss; different config -> miss
    assert storage.get_cached("/tmp/a.wav", "sha256:" + "9" * 64, CFG) is None
    assert storage.get_cached("/tmp/a.wav", FH, "sha256:" + "0" * 64) is None

    # same (file_path, config), changed content -> replaces the stale row
    # (one row, no orphan)
    storage.save(file_path="/tmp/a.wav", file_hash="sha256:" + "b" * 64,
                 config_hash=CFG, ranges=[], metadata={})
    rows = storage.list_jobs()
    assert len(rows) == 1 and rows[0].file_hash == "sha256:" + "b" * 64


def test_save_with_logging_success_and_swallowed_failure(tmp_path, monkeypatch):
    storage = _storage(tmp_path)
    logger = logging.getLogger("vad_storage_test")

    ok = storage.save_with_logging(file_path="/tmp/b.wav",
                                   file_hash="sha256:" + "d" * 64,
                                   config_hash=CFG, ranges=[], metadata={},
                                   logger=logger)
    assert ok is True
    assert storage.get_cached("/tmp/b.wav", "sha256:" + "d" * 64, CFG) is not None

    def _boom(**kwargs):
        raise RuntimeError("simulated DB failure")

    monkeypatch.setattr(storage, "save", _boom)
    ok_fail = storage.save_with_logging(file_path="/tmp/x.wav",
                                        file_hash="sha256:" + "e" * 64,
                                        config_hash=CFG, ranges=[], metadata={},
                                        logger=logger)
    assert ok_fail is False

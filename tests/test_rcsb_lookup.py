"""Tests for rcsb_lookup.py.

fetch_pdb_metadata hits the real RCSB Data API (data.rcsb.org) - one live
lookup is exercised here (matching this project's existing convention for
network-backed modules, see test_receptor_atlas.py), plus offline tests for
the malformed/unknown-response handling using a stubbed requests.get.
"""
import rcsb_lookup
from rcsb_lookup import fetch_pdb_metadata


def test_fetch_pdb_metadata_known_structure():
    # 6CM4: dopamine D2 receptor structure - real, stable, public PDB entry.
    fetch_pdb_metadata.clear()
    meta = fetch_pdb_metadata("6cm4")
    assert meta is not None
    assert meta.pdb_id == "6CM4"
    assert meta.gene == "DRD2"


def test_fetch_pdb_metadata_empty_id_returns_none():
    assert fetch_pdb_metadata("") is None
    assert fetch_pdb_metadata("   ") is None


def test_fetch_pdb_metadata_network_error_returns_none(monkeypatch):
    import requests

    def _raise(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(rcsb_lookup.requests, "get", _raise)
    fetch_pdb_metadata.clear()
    assert fetch_pdb_metadata("6CM4") is None


def test_fetch_pdb_metadata_non_json_response_returns_none(monkeypatch):
    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr(rcsb_lookup.requests, "get", lambda *a, **k: _FakeResponse())
    fetch_pdb_metadata.clear()
    assert fetch_pdb_metadata("6CM4") is None


def test_fetch_pdb_metadata_empty_entry_returns_none(monkeypatch):
    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    monkeypatch.setattr(rcsb_lookup.requests, "get", lambda *a, **k: _FakeResponse())
    fetch_pdb_metadata.clear()
    assert fetch_pdb_metadata("0000") is None

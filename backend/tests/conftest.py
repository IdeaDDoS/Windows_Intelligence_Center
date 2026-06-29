"""Fixtures compartilhadas dos testes.

Isola cada teste do banco de runtime: aponta ``db_path`` para um arquivo temporário
(schema aplicado do ``database/schema.sql`` real) e desliga o sampler — nenhum teste
escreve no ``wic.db`` de verdade nem dispara coleta em background.
"""

from __future__ import annotations

import pytest

from config import settings
from storage.db import init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """DB temporário e sampler desligado para todos os testes."""
    monkeypatch.setattr(settings, "db_path", tmp_path / "wic_test.db")
    monkeypatch.setattr(settings, "sampler_enabled", False)
    init_db()
    yield

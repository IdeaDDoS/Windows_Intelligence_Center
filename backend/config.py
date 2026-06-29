"""Configurações da aplicação, carregadas de variáveis de ambiente / arquivo .env.

Todas as variáveis usam o prefixo ``WIC_`` (ex.: ``WIC_APP_PORT``). Os caminhos
são resolvidos a partir da raiz do projeto, de modo que o backend funciona
independentemente do diretório de trabalho em que o uvicorn é iniciado.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do repositório (pai de backend/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Configurações centrais do Windows Intelligence Center."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WIC_",
        extra="ignore",
    )

    # Porta do backend FastAPI.
    app_port: int = 8000
    # Intervalo do sampler de métricas (usado a partir da Fatia 3).
    sample_interval_seconds: int = 5
    # Liga o sampler em background no lifespan (desligado nos testes).
    sampler_enabled: bool = True
    # Arquivo SQLite local (runtime, fora do versionamento).
    db_path: Path = PROJECT_ROOT / "database" / "wic.db"
    # Chave da API Anthropic — opcional; o painel funciona sem ela.
    anthropic_api_key: str | None = None
    # Origens permitidas no CORS (frontend Vite em dev).
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()

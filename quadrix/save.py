"""Persistência de progresso (conquistas e recordes)."""

import json

from .config import PROGRESSO_SAVE_FILE


def salvar_progresso(jogo):
    """Salva conquistas e recordes em arquivo JSON unificado."""
    dados = {
        "conquistas": {cid: c["desbloqueada"] for cid, c in jogo.conquistas.items()},
        "recordes": jogo.recordes,
    }
    try:
        with open(PROGRESSO_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # Se não conseguir salvar, continua sem salvar


def carregar_progresso(jogo):
    """Carrega conquistas e recordes do arquivo JSON unificado, se existir."""
    try:
        with open(PROGRESSO_SAVE_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
        for cid, desbloqueada in dados.get("conquistas", {}).items():
            if cid in jogo.conquistas:
                jogo.conquistas[cid]["desbloqueada"] = desbloqueada
        for modo, recorde in dados.get("recordes", {}).items():
            if modo in jogo.recordes:
                jogo.recordes[modo] = recorde
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass  # Sem arquivo salvo ou corrompido - mantém valores padrão

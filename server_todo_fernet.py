#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor/Script exemplo com gestão de chave Fernet num só ficheiro.

Funcionalidades:
- Carrega ou cria automaticamente a chave 'key.fernet' ao lado deste script.
- Helpers para cifrar/decifrar strings.
- API Flask opcional com:
    * GET  /health
    * POST /encrypt   (eco cifrado)
    * POST /decrypt   (eco decifrado)
    * POST /add       (adiciona tarefa à lista - cifrada em ficheiro)
    * GET  /list      (lista tarefas decifradas)

Requisitos:
    pip install cryptography
    # (Opcional para HTTP)
    pip install flask
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List
import os
import sys
import tempfile
import threading

# === 1) Gestão de chave Fernet (robusta e independente do CWD) =================
from cryptography.fernet import Fernet, InvalidToken

BASE_DIR = Path(__file__).resolve().parent
KEY_PATH = BASE_DIR / "key.fernet"          # chave ao lado do script
TODO_PATH = BASE_DIR / "todo_list.fernet"    # ficheiro com tarefas cifradas (1 token/linha)

# Lock simples para proteger leitura/escrita concorrente (mesmo processo)
_FILE_LOCK = threading.Lock()

def get_or_create_fernet_key(path: Path) -> bytes:
    """
    Lê a chave Fernet de 'path' ou cria uma nova se não existir.
    AVISO: se gerar nova chave, dados cifrados com a chave anterior deixam
    de poder ser desencriptados.
    """
    if path.exists():
        key = path.read_bytes()
        # Validação: tentar instanciar Fernet (confirma formato/base64)
        try:
            Fernet(key)
        except Exception as e:
            raise RuntimeError(
                f"A chave existente em {path} é inválida/corrompida. "
                f"Apague-a e gere nova, ou substitua pela chave correta. Detalhe: {e}"
            )
        return key

    key = Fernet.generate_key()  # 32 bytes, Base64 urlsafe
    path.write_bytes(key)
    print(f"[INFO] Nova chave Fernet criada em: {path}")
    return key

try:
    FERNET_KEY: bytes = get_or_create_fernet_key(KEY_PATH)
    fernet = Fernet(FERNET_KEY)
    print(f"[OK] Chave Fernet carregada de: {KEY_PATH}")
except Exception as e:
    raise SystemExit(f"[ERRO] Não foi possível obter a chave Fernet: {e}")

# === 2) Helpers de cifra/decifra ===============================================

def cifrar_texto(plaintext: str, *, encoding: str = "utf-8") -> bytes:
    """Cifra texto para token (bytes) usando a chave Fernet global."""
    if not isinstance(plaintext, str):
        raise TypeError("plaintext deve ser str.")
    return fernet.encrypt(plaintext.encode(encoding))

def decifrar_texto(token: bytes, *, encoding: str = "utf-8") -> str:
    """Decifra token (bytes) para texto (str)."""
    if not isinstance(token, (bytes, bytearray)):
        raise TypeError("token deve ser bytes.")
    try:
        return fernet.decrypt(bytes(token)).decode(encoding)
    except InvalidToken as e:
        raise ValueError("Token inválido ou chave incorreta.") from e

# === 3) Persistência da TODO list (cifrada uma tarefa por linha) ===============

def _ler_todos() -> List[str]:
    """Lê e decifra todo_list.fernet. Linhas inválidas são ignoradas com aviso."""
    if not TODO_PATH.exists():
        return []

    todos: List[str] = []
    with _FILE_LOCK:
        with TODO_PATH.open("rb") as f:
            for i, line in enumerate(f, start=1):
                token = line.strip()
                if not token:
                    continue
                try:
                    texto = decifrar_texto(token)
                except ValueError:
                    # Linha inválida – pode estar corrompida; ignora mas avisa
                    print(f"[AVISO] Linha {i} em {TODO_PATH} não pôde ser decifrada. Ignorada.", file=sys.stderr)
                    continue
                todos.append(texto)
    return todos

def _escrever_todos(todos: List[str]) -> None:
    """
    Escreve a lista completa de tarefas:
      - cifra cada item (UTF-8) e grava um token por linha
      - escrita atómica: escreve para ficheiro temporário e faz replace
    """
    with _FILE_LOCK:
        tmp_fd, tmp_name = tempfile.mkstemp(prefix="todo_", suffix=".fernet.tmp", dir=str(BASE_DIR))
        try:
            with os.fdopen(tmp_fd, "wb") as tmp:
                for item in todos:
                    token = cifrar_texto(item)
                    tmp.write(token + b"\n")
            os.replace(tmp_name, TODO_PATH)  # atómico (Windows/Unix)
        finally:
            # Se algo correu mal antes do replace, tenta limpar o temp
            try:
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)
            except OSError:
                pass

def adicionar_todo(task: str) -> List[str]:
    """Adiciona tarefa (validada) e persiste tudo cifrado. Devolve a lista atualizada."""
    task = (task or "").strip()
    if not task:
        raise ValueError("A tarefa (task) não pode ser vazia.")
    todos = _ler_todos()
    todos.append(task)
    _escrever_todos(todos)
    return todos

# === 4) (Opcional) Mini API Flask para testar via HTTP ==========================
# Pode comentar esta secção se não pretender expor HTTP.

try:
    from flask import Flask, jsonify, request
    FLASK_DISPONIVEL = True
except Exception:
    FLASK_DISPONIVEL = False

app: Optional["Flask"] = None
if FLASK_DISPONIVEL:
    app = Flask(__name__)

    # ----- rotas utilitárias de teste/diagnóstico -----
    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/encrypt")
    def api_encrypt():
        """
        Exemplo:
            curl -X POST http://127.0.0.1:5000/encrypt -H "Content-Type: application/json" -d "{\"text\":\"segredo\"}"
        """
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        if not isinstance(text, str):
            return jsonify(error="Campo 'text' (string) é obrigatório."), 400
        token = cifrar_texto(text)   # bytes
        # devolver em base64 (string) para transporte JSON
        return jsonify(token=token.decode("utf-8"))

    @app.post("/decrypt")
    def api_decrypt():
        """
        Exemplo:
            curl -X POST http://127.0.0.1:5000/decrypt -H "Content-Type: application/json" -d "{\"token\":\"<token>\"}"
        """
        data = request.get_json(silent=True) or {}
        token_b64 = data.get("token")
        if not isinstance(token_b64, str):
            return jsonify(error="Campo 'token' (string base64) é obrigatório."), 400
        try:
            texto = decifrar_texto(token_b64.encode("utf-8"))
        except ValueError as e:
            return jsonify(error=str(e)), 400
        return jsonify(text=texto)

    # ----- rotas da TODO list (compatíveis com o cliente) -----
    @app.post("/add")
    def api_add():
        """
        POST /add
        body: {"task": "<texto>"}
        """
        data = request.get_json(silent=True) or {}
        task = data.get("task", "")
        try:
            todos = adicionar_todo(task)
            return jsonify({"status": "ok", "todos": todos})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.get("/list")
    def api_list():
        """
        GET /list
        """
        todos = _ler_todos()
        return jsonify(todos)

# === 5) Execução direta (CLI de demonstração) ==================================

def demo_cli():
    """
    Demonstração rápida em linha de comando:
        python server_todo_fernet.py --demo
    """
    msg = "exemplo de mensagem secreta"
    token = cifrar_texto(msg)
    claro = decifrar_texto(token)
    print("\n[DEMO] Mensagem original :", msg)
    print("[DEMO] Token (base64)    :", token.decode("utf-8"))
    print("[DEMO] Decifrada         :", claro, "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Servidor/Script com Fernet num só ficheiro.")
    parser.add_argument("--demo", action="store_true", help="Executa demonstração de cifra/decifra.")
    parser.add_argument("--no-http", action="store_true", help="Não iniciar o servidor HTTP (Flask).")
    parser.add_argument("--host", default="127.0.0.1", help="Host HTTP (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=5000, help="Porta HTTP (default: 5000).")
    parser.add_argument("--todo-file", default=str(TODO_PATH), help="Caminho para o ficheiro de tarefas cifradas.")
    parser.add_argument("--key-file", default=str(KEY_PATH), help="Caminho para a chave Fernet.")
    args = parser.parse_args()

    # Reatribuição direta (sem 'global'): estamos no nível do módulo
    TODO_PATH = Path(args.todo_file).resolve()
    KEY_PATH = Path(args.key_file).resolve()

    # Se o utilizador apontou para outra chave, recarrega o Fernet.
    if KEY_PATH != (BASE_DIR / "key.fernet"):
        FERNET_KEY = get_or_create_fernet_key(KEY_PATH)
        fernet = Fernet(FERNET_KEY)

    if args.demo:
        demo_cli()

    iniciar_http = (not args.no_http) and FLASK_DISPONIVEL
    if iniciar_http:
        assert app is not None
        print("URL Map:", app.url_map)
        print(f"[INFO] HTTP em http://{args.host}:{args.port}  (Ctrl+C para parar)")
        app.run(host=args.host, port=args.port, debug=True)
    elif not FLASK_DISPONIVEL and not args.no_http:
        print("[AVISO] Flask não está instalado. Instale com 'pip install flask' ou use --no-http.")
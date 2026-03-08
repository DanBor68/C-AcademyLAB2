#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor TODO com persistência cifrada (Fernet).
- Usa apenas biblioteca padrão + cryptography.fernet
- Grava SEMPRE a lista cifrada em 'todo_list.fernet'
- Corrige bug comum: ao arrancar, respeitar o campo 'completed' gravado (não forçar False)

Execução:
  python server_todo_fernet.py --key fernet.key --data todo_list.fernet --host 127.0.0.1 --port 8080

Rotas:
  GET    /todos
  POST   /todos              body: {"title": "comprar leite"}
  PATCH  /todos/{id}         body: {"completed": true} (ou "title": "novo título")
  DELETE /todos/{id}
"""

from __future__ import annotations

import json
import re
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fernet_utils import encrypt_json_to_file, decrypt_json_from_file

# ---------------- Config ----------------

DEFAULT_KEY = "fernet.key"
DEFAULT_DATA = "todo_list.fernet"

# ---------------- Modelo ----------------

class TodoStore:
    """
    Armazena tarefas na memória e faz persistência cifrada.
    Estrutura do ficheiro (após decifrar): {"next_id": int, "items": [ {id, title, completed}, ... ]}
    """
    def __init__(self, key_file: str, data_file: str):
        self.key_file = key_file
        self.data_file = data_file
        self._lock = threading.RLock()
        self._state: Dict[str, Any] = {"next_id": 1, "items": []}
        self._load_if_exists()

    def _load_if_exists(self):
        """Carrega e decifra o ficheiro (se existir), preservando 'completed' conforme gravado. (Bug fix)."""
        p = Path(self.data_file)
        if not p.is_file():
            return
        try:
            data = decrypt_json_from_file(p, self.key_file)
            # Validação básica e normalização SEM sobrescrever 'completed'
            next_id = int(data.get("next_id", 1))
            items_in = data.get("items", [])
            items_out: List[Dict[str, Any]] = []
            for it in items_in:
                # Não definir defaults agressivos que apaguem 'completed' (bug original típico)
                item = {
                    "id": int(it["id"]),
                    "title": str(it.get("title", "")),
                    # FIX: usa o valor gravado; se faltar, assume False apenas nesse caso
                    "completed": bool(it.get("completed", False)),
                }
                items_out.append(item)
            self._state = {"next_id": max(next_id, 1), "items": items_out}
        except Exception as e:
            # Em caso de erro de decifra/JSON, arranca com estado vazio
            print(f"[WARN] Falha a carregar {p}: {e}. Arrancando com lista vazia.")
            self._state = {"next_id": 1, "items": []}

    def _persist(self):
        """Grava o estado cifrado de forma atómica."""
        encrypt_json_to_file(self._state, self.data_file, self.key_file)

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._state["items"])

    def create(self, title: str) -> Dict[str, Any]:
        with self._lock:
            new = {"id": self._state["next_id"], "title": title, "completed": False}
            self._state["items"].append(new)
            self._state["next_id"] += 1
            self._persist()
            return new

    def update(self, item_id: int, patch: Dict[str, Any]) -> Dict[str, Any] | None:
        with self._lock:
            for it in self._state["items"]:
                if it["id"] == item_id:
                    # Atualiza apenas campos fornecidos (sem apagar 'completed' indevidamente)
                    if "title" in patch:
                        it["title"] = str(patch["title"])
                    if "completed" in patch:
                        it["completed"] = bool(patch["completed"])
                    self._persist()
                    return dict(it)
        return None

    def delete(self, item_id: int) -> bool:
        with self._lock:
            n0 = len(self._state["items"])
            self._state["items"] = [it for it in self._state["items"] if it["id"] != item_id]
            if len(self._state["items"]) != n0:
                self._persist()
                return True
            return False

# ------------- HTTP Handler -------------

class TodoHandler(BaseHTTPRequestHandler):
    # ligado pelo main()
    store: TodoStore = None  # type: ignore

    _re_item = re.compile(r"^/todos/(\d+)$")

    def _send(self, code: int, payload: Any = None):
        body = b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if payload is not None:
            js = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            body = js
            self.send_header("Content-Length", str(len(body)))
        else:
            self.send_header("Content-Length", "0")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _parse_json(self) -> Tuple[bool, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return False, {"error": "Content-Length inválido"}
        data = self.rfile.read(length) if length > 0 else b""
        if not data:
            return True, {}
        try:
            return True, json.loads(data.decode("utf-8"))
        except Exception:
            return False, {"error": "JSON inválido"}

    # ----------- Métodos HTTP -----------

    def do_GET(self):
        if self.path == "/todos":
            todos = self.store.list()
            self._send(HTTPStatus.OK, todos)
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "rota não encontrada"})

    def do_POST(self):
        if self.path == "/todos":
            ok, obj = self._parse_json()
            if not ok or "title" not in obj or not str(obj["title"]).strip():
                self._send(HTTPStatus.BAD_REQUEST, {"error": "body deve conter {'title': '...'}"})
                return
            new_item = self.store.create(str(obj["title"]).strip())
            self._send(HTTPStatus.CREATED, new_item)
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "rota não encontrada"})

    def do_PATCH(self):
        m = self._re_item.match(self.path)
        if not m:
            self._send(HTTPStatus.NOT_FOUND, {"error": "rota não encontrada"})
            return
        item_id = int(m.group(1))
        ok, obj = self._parse_json()
        if not ok:
            self._send(HTTPStatus.BAD_REQUEST, obj)
            return
        patch = {}
        if "title" in obj:
            patch["title"] = obj["title"]
        if "completed" in obj:
            patch["completed"] = obj["completed"]
        if not patch:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "body deve conter 'title' e/ou 'completed'"})
            return
        updated = self.store.update(item_id, patch)
        if updated is None:
            self._send(HTTPStatus.NOT_FOUND, {"error": "id não encontrado"})
        else:
            self._send(HTTPStatus.OK, updated)

    def do_DELETE(self):
        m = self._re_item.match(self.path)
        if not m:
            self._send(HTTPStatus.NOT_FOUND, {"error": "rota não encontrada"})
            return
        item_id = int(m.group(1))
        ok = self.store.delete(item_id)
        if ok:
            self._send(HTTPStatus.NO_CONTENT, None)
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "id não encontrado"})

    # Evitar log barulhento
    def log_message(self, fmt, *args):
        return  # silencia logs padrão; comenta para ver

# --------------- Bootstrap ---------------

def run_server(host: str, port: int, key_file: str, data_file: str):
    store = TodoStore(key_file=key_file, data_file=data_file)
    TodoHandler.store = store
    httpd = HTTPServer((host, port), TodoHandler)
    print(f"✅ Servidor TODO cifrado a correr em http://{host}:{port}")
    print(f"   Chave: {Path(key_file).resolve()}")
    print(f"   Dados cifrados: {Path(data_file).resolve()}")
    httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Servidor TODO com persistência cifrada (Fernet).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--key", default=DEFAULT_KEY, help="Ficheiro da chave Fernet (gerado previamente).")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Ficheiro de dados cifrados.")
    args = parser.parse_args()
    run_server(args.host, args.port, args.key, args.data)
# server_todo.py
import socket
import threading

HOST = "127.0.0.1"   # altera se quiseres aceitar fora da máquina local
PORT = 5555          # Escolhe uma porta livre e usa a mesma no cliente

# Estrutura simples em memória; persistência não é pedida na alínea 1
tasks = []  # cada item: {"id": int, "text": str, "done": bool}
_next_id = 1
lock = threading.Lock()

HELP = (
    "Comandos:\n"
    "  ADD <texto da tarefa>\n"
    "  LIST\n"
    "  DONE <id>\n"
    "  COUNT            (total de itens)\n"
    "  COUNT_OPEN       (itens não concluídos)\n"
    "  CLEAR            (apaga TODAS as tarefas)\n"
    "  QUIT\n"
)

def handle_cmd(cmdline: str) -> str:
    global _next_id

    parts = cmdline.strip().split(" ", 1)
    if not parts or not parts[0]:
        return "ERR comando vazio\n"

    cmd = parts[0].upper()
    arg = parts[1].strip() if len(parts) > 1 else ""

    # ADD
    if cmd == "ADD":
        if not arg:
            return "ERR uso: ADD <texto>\n"
        with lock:
            tid = _next_id
            _next_id += 1
            tasks.append({"id": tid, "text": arg, "done": False})
        return f"OK added id={tid}\n"

    # LIST
    if cmd == "LIST":
        with lock:
            if not tasks:
                return "OK (vazio)\n"
            lines = [
                f"[{'✓' if t['done'] else ' '}] {t['id']}: {t['text']}"
                for t in tasks
            ]
        return "OK\n" + "\n".join(lines) + "\n"

    # DONE
    if cmd == "DONE":
        if not arg.isdigit():
            return "ERR uso: DONE <id>\n"
        tid = int(arg)
        with lock:
            for t in tasks:
                if t["id"] == tid:
                    t["done"] = True
                    return f"OK done id={tid}\n"
        return "ERR id não encontrado\n"

    # COUNT
    if cmd == "COUNT":
        with lock:
            return f"OK total={len(tasks)}\n"

    # COUNT_OPEN
    if cmd == "COUNT_OPEN":
        with lock:
            open_count = sum(1 for t in tasks if not t["done"])
            return f"OK abertas={open_count}\n"

    # CLEAR
    if cmd == "CLEAR":
        with lock:
            tasks.clear()
        return "OK cleared\n"

    # HELP
    if cmd in ("HELP", "?"):
        return HELP

    # QUIT
    if cmd == "QUIT":
        return "BYE\n"

    return "ERR comando desconhecido. Use HELP\n"


def client_thread(conn: socket.socket, addr):
    with conn:
        conn.sendall(b"TodoServer pronto. Use HELP\n")
        while True:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(4096)
                if not chunk:
                    return
                data += chunk

            resp = handle_cmd(data.decode("utf-8", errors="ignore"))
            conn.sendall(resp.encode("utf-8"))

            if resp.startswith("BYE"):
                return


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Servidor a escutar em {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            print("Cliente ligado:", addr)
            threading.Thread(
                target=client_thread,
                args=(conn, addr),
                daemon=True
            ).start()


if __name__ == "__main__":
    main()

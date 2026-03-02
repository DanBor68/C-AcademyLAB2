HOST = "127.0.0.1"
PORT = 8888

tasks = [
    {"title": "Comprar pão", "done": False},
    {"title": "Estudar Python", "done": True},
    {"title": "Enviar email", "done": False}
]

incomplete = sum(1 for task in tasks if not task["done"])

print("Tarefas incompletas:", incomplete)

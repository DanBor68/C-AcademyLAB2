# C‑AcademyLAB2  
Projeto LAB2 – Comunicação Cliente‑Servidor com Criptografia Fernet

---

## 📌 Descrição Geral

Este projeto foi desenvolvido no âmbito do **LAB2 da C‑Academy** e implementa um sistema de **comunicação Cliente‑Servidor**, enriquecido com:

- 🔐 **Criptografia simétrica autenticada (Fernet)**  
- 🌐 **API HTTP com Flask**  
- 🧪 **Cliente de teste automático (requests)**  
- 📁 **Persistência cifrada** (um token por linha)

O objetivo é demonstrar conceitos fundamentais de:

- Programação em rede  
- Comunicação Cliente‑Servidor  
- Troca estruturada de mensagens  
- Segurança e cifragem de dados  
- Gestão de ficheiros cifrados  
- Desenvolvimento de APIs simples  

---

## 🧩 Objetivos do Projeto

1. Criar um servidor capaz de aceitar múltiplas comunicações de clientes.  
2. Implementar uma API para envio e receção de dados.  
3. Garantir que todos os dados persistidos são **cifrados com Fernet**.  
4. Permitir que os clientes enviem pedidos de forma estruturada (JSON).  
5. Implementar um encerramento seguro e tratamento de erros.  
6. Demonstrar cifragem/decifragem com `cryptography.Fernet`.

---

## 🏗️ Arquitetura do Sistema

O sistema segue o modelo **Cliente ↔ Servidor**:

### 🖥️ Servidor
- Carrega ou cria automaticamente a chave `key.fernet`
- Expõe endpoints HTTP:
  - `POST /add` → adiciona tarefa cifrada  
  - `GET /list` → devolve lista decifrada  
  - `POST /encrypt` / `POST /decrypt` → utilidades para testes  
  - `GET /health` → estado do servidor  
- Mantém a persistência segura no ficheiro `todo_list.fernet`
- Garante escrita atómica e proteção contra corrupção de dados

### 💻 Clientes
- Enviam pedidos HTTP ao servidor
- Podem:
  - Adicionar tarefas
  - Listar tarefas
  - Testar cifragem/descifragem
- Implementados em Python (módulo `requests`)

---

## 🚀 Como Executar

### 1️⃣ Instalar dependências
```bash
pip install cryptography flask requests
```

### 2️⃣ Executar o Servidor
```bash
python server_todo_fernet.py
```

Deverá ver algo como:
```
[OK] Chave Fernet carregada de: .../key.fernet
URL Map: Map([... '/add', '/list', '/encrypt', '/decrypt', '/health' ...])
[INFO] HTTP em http://127.0.0.1:5000
```

### 3️⃣ Executar o Cliente de Teste
```bash
python -u client_test.py
```

Pode abrir vários clientes em janelas diferentes para testar comunicação.

---

## 🌐 Endpoints da API

| Método | Rota        | Descrição |
|--------|-------------|-----------|
| GET    | `/health`   | Verifica estado do servidor |
| POST   | `/add`      | Adiciona tarefa (cifrada e persistida) |
| GET    | `/list`     | Lista tarefas decifradas |
| POST   | `/encrypt`  | Cifra texto e devolve token Base64 |
| POST   | `/decrypt`  | Decifra token Base64 e devolve texto |

---

## 🛠️ Exemplos de Utilização com `curl`

Adicionar tarefa:
```bash
curl -X POST http://127.0.0.1:5000/add \
     -H "Content-Type: application/json" \
     -d "{\"task\":\"Comprar pão\"}"
```

Listar tarefas:
```bash
curl http://127.0.0.1:5000/list
```

---

## 📂 Estrutura do Repositório

```
/C-AcademyLAB2
 ├── server_todo_fernet.py      # Servidor + API + gestão de chave
 ├── client_test.py             # Cliente de testes com requests
 ├── key.fernet                 # (gerado automaticamente) chave Fernet
 ├── todo_list.fernet           # (gerado automaticamente) tarefas cifradas
 ├── README.md                  # Documentação do projeto
 └── docs/
      └── Lab2-enunciado.pdf    # Enunciado oficial do laboratório
```

---

## 🔐 Detalhes da Criptografia

- Utiliza **Fernet (AES‑128 + HMAC‑SHA256)**  
- Cada tarefa é cifrada individualmente  
- O ficheiro `todo_list.fernet` contém **um token por linha**  
- Se apagar a chave `key.fernet`, **perde acesso aos dados cifrados**  
- Escrita é feita através de ficheiro temporário (**escrita atómica**)  

---

## 👥 Autores

1. António Soares Martins  
2. Danielle Alvarinho  
3. Marina Ferreiro  

---

## 🎓 Orientação

Professor **Hugo AgoGa**

---

## 📝 Notas Finais

- Este projeto foi desenvolvido no âmbito da formação **C‑Academy**.  
- O documento **docs/Lab2‑enunciado.pdf** contém instruções detalhadas.  
- Possíveis extensões:
  - Autenticação JWT
  - Logs de auditoria
  - UI gráfica para cliente
  - Exportação/importação segura de tarefas
  - Dockerização do servidor


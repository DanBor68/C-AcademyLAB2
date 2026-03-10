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

## 🔐 Detalhes da Criptografia
📘 C‑Academy LAB2 — Sistema Cliente‑Servidor com Criptografia Fernet
📌 Descrição Geral
Este projeto foi desenvolvido no âmbito do LAB2 da C‑Academy e implementa um sistema completo de comunicação Cliente‑Servidor, incluindo:

🔐 Criptografia simétrica autenticada (Fernet, AES‑128 + HMAC‑SHA256)
🌐 API HTTP com Flask
💾 Persistência segura num ficheiro cifrado
🧪 Clientes de teste (automático e interativo)
📁 Manipulação de ficheiros binários
🛠️ Scripts auxiliares para estudo de criptografia

O sistema demonstra conceitos fundamentais de:

Programação em rede
Comunicação Cliente‑Servidor
Troca estruturada de mensagens (JSON)
Criptografia e segurança de dados
Escrita atómica para proteção da persistência
Desenvolvimento de APIs simples

🧩 Objetivos do Projeto
✔️ Criar um servidor capaz de receber pedidos HTTP
✔️ Cifrar e persistir dados usando Fernet
✔️ Permitir múltiplos clientes simultâneos
✔️ Expor endpoints REST para adicionar/listar tarefas
✔️ Demonstrar cifragem/decifragem através da API
✔️ Incluir clientes de teste automáticos e manuais
✔️ Realizar exercícios de I/O binário e criptografia

🏗️ Arquitetura do Sistema
Cliente ↔ Servidor (HTTP + JSON)
🖥️ Servidor (server_todo_fernet.py)

Carrega ou cria automaticamente key.fernet
Expõe endpoints:

POST /add — adiciona tarefa cifrada
GET /list — devolve lista descifrada
POST /encrypt / POST /decrypt — utilitários
GET /health — estado do servidor

Persistência segura em todo_list.fernet
Escrita atómica para evitar corrupção
Validação e tratamento de erros

💻 Clientes

Usam a API HTTP via requests
Tipos de cliente disponíveis:

Cliente automático (client_test.py)
Cliente interativo (client_todo_shell.py)
Cliente para versão alternativa (client_tudo.py)

🚀 Como Executar
1️⃣ Instalar dependências
pip install cryptography flask requests

2️⃣ Iniciar o Servidor
python server_todo_fernet.py

Exemplo de output:
[OK] Chave Fernet carregada de: .../key.fernet
URL Map: Map([... '/add', '/list', '/encrypt', '/decrypt', '/health' ...])
[INFO] HTTP em http://127.0.0.1:5000

3️⃣ Executar o Cliente de Teste
python -u client_test.py

🌐 Endpoints da API
Método | Rota | Descrição
GET | /health | Verifica estado do servidor
POST | /add | Adiciona tarefa cifrada ao ficheiro
GET | /list | Lista todas as tarefas descifradas
POST | /encrypt | Cifra texto e devolve token Base64
POST | /decrypt | Descifra token Base64 e devolve texto

🛠️ Exemplos com curl
Adicionar tarefa:
curl -X POST http://127.0.0.1:5000/add -H "Content-Type: application/json" -d "{"task":"Comprar pão"}"

Listar tarefas:
curl http://127.0.0.1:5000/list

📂 Estrutura Completa do Repositório
/C-AcademyLAB2
├── server_todo_fernet.py
├── server_tudo.py
├── client_test.py
├── client_todo_shell.py
├── client_tudo.py
├── crypto_tools.py
├── fernet_utils.py
├── fernet_keygen.py
├── fernet-sym-cypher.py
├── test_crypto_tools.py
├── key.fernet
├── fernet.key
├── todo_list.fernet
├── abc.txt
├── myfile.txt
├── random.bin
├── empty.bin
├── copy-file-bytes.py
├── c-academy.bmp
├── c-academy-original.bmp
├── body/
├── commons-crypto-1.2.0-src.zip
├── README.md
└── docs/Lab2-enunciado.pdf

🔐 Detalhes da Criptografia
Fernet = AES‑128 em modo CBC + HMAC‑SHA256
Garante confidencialidade, integridade e autenticidade.
Cada tarefa é cifrada individualmente.
O ficheiro todo_list.fernet armazena um token por linha.
Se perder a chave key.fernet, todos os dados ficam irrecuperáveis.
Escrita atómica para garantir durabilidade.

👥 Autores
António Soares Martins
Danielle Alvarinho
Marina Ferreiro

🎓 Orientação
Professor Hugo AgoGa

📝 Notas Finais
Este projeto integra vários temas do módulo LAB2 e pode ser facilmente estendido:
- Autenticação JWT
- Dockerização do servidor
- UI gráfica para cliente
- Logs de auditoria
- Exportação/importação segura de tarefas

Documentação oficial: docs/Lab2-enunciado.pdf

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


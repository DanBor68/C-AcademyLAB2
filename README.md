C‑AcademyLAB2
Projeto LAB2 – Comunicação Cliente‑Servidor

📌 Descrição Geral
  	Este projeto faz parte do LAB2 da C‑Academy e tem como objetivo implementar um sistema de comunicação entre um servidor e múltiplos clientes, permitindo a troca de mensagens e informação em tempo real.
    A aplicação demonstra conceitos fundamentais de programação em rede, comunicação TCP/UDP, gestão de múltiplas ligações e tratamento de mensagens.

🧩 Objetivos do Projeto
    1. Criar um servidor capaz de aceitar vários clientes em simultâneo.
    2. Permitir que os clientes enviem e recebam mensagens através do servidor.
    3. Gerir conexões ativas, mensagens recebidas e difusão de dados.
    4. Implementar um encerramento seguro das ligações.

🏗️ Arquitetura do Sistema
  O sistema segue o modelo Cliente ↔ Servidor, onde:
  Servidor
    1. Aguarda ligações
    2. Mantém a lista de clientes conectados
    3. Processa e encaminha mensagens
  Clientes
  1. Estabelecem ligação ao servidor
  2. Enviam dados
  3. Recebem respostas ou mensagens de outros clientes
     
🚀 Como Executar
1. Executar o Servidor
   python server.py
2. Executar um Cliente
   python client.py
Podes abrir vários clientes em janelas diferentes para testar comunicação simultânea.

📂 Estrutura do Repositório
Code
/C-AcademyLAB2
 ├── server.py
 ├── client.py
 ├── README.md
 └── docs/
      └── Lab2-enunciado.pdf
      
👥 Autores
    1. António Soares Martins
    2. Danielle Alvarinho
    3. Marina Ferreiro

🎓 Orientação
Professor Hugo AgoGa

📝 Notas
Este projeto foi desenvolvido no âmbito da formação C‑Academy.
O documento Lab2-enunciado.pdf contém todos os detalhes técnicos.
O projeto pode ser expandido com autenticação, logs, interface gráfica, entre outras funcionalidades.

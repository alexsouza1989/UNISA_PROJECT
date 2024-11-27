Sistema de Gestão Hospitalar
Descrição do Projeto
O Sistema de Gestão Hospitalar é uma aplicação desktop desenvolvida em Python, utilizando a biblioteca Tkinter para interface gráfica. Ele permite o gerenciamento básico de pacientes, médicos e consultas. A aplicação é alimentada por um banco de dados SQLite para armazenar informações de maneira local.

Funcionalidades
Gerenciamento de Pacientes:

Cadastro de pacientes com informações como nome, CPF, idade, endereço e contato.
Visualização da lista de pacientes cadastrados.
Busca de pacientes pelo nome.
Edição e exclusão de dados dos pacientes.
Gerenciamento de Médicos:

Cadastro de médicos com informações como nome, especialidade e horário de trabalho.
Visualização da lista de médicos cadastrados.
Edição e exclusão de médicos.
Gerenciamento de Consultas:

Agendamento de consultas, associando pacientes e médicos.
Visualização de consultas agendadas.
Exportação da lista de consultas para um arquivo CSV.
Backup e Restauração:

Backup do banco de dados SQLite.
Restauração do banco de dados a partir de backups existentes.
Requisitos
Python: Versão 3.6 ou superior.
Bibliotecas Python:
sqlite3
Tkinter (incluído no Python padrão)
shutil
csv
re
Instalação
Passo 1: Clone o Repositório
Clone este repositório em sua máquina local:

bash
Copiar código
git clone https://github.com/seu-repositorio/sistema-hospitalar.git
Passo 2: Instale o Python
Certifique-se de ter o Python 3.6 ou superior instalado em sua máquina.

Passo 3: Execute o Script
Entre na pasta do projeto e execute o arquivo programa_hospital.py:

bash
Copiar código
cd sistema-hospitalar
python programa_hospital.py
Como Criar um Executável
Se você deseja criar um executável para Windows:

Instale o PyInstaller:

bash
Copiar código
pip install pyinstaller
Gere o executável:

bash
Copiar código
pyinstaller --onefile --windowed programa_hospital.py
O executável será gerado na pasta dist.

Estrutura do Banco de Dados
O sistema utiliza um banco de dados SQLite com as seguintes tabelas:

Tabela patients:

id: Identificador único do paciente.
name: Nome do paciente.
age: Idade do paciente.
address: Endereço do paciente.
contact: Contato do paciente.
Tabela doctors:

id: Identificador único do médico.
name: Nome do médico.
specialty: Especialidade do médico.
schedule: Horário de trabalho do médico.
Tabela appointments:

id: Identificador único da consulta.
patient_id: ID do paciente (chave estrangeira).
doctor_id: ID do médico (chave estrangeira).
date: Data da consulta.
time: Hora da consulta.
Tabela users (opcional):

id: Identificador único do usuário.
username: Nome de usuário.
password: Senha do usuário.
Funcionalidades Futuras
Integração com sistemas em nuvem.
Relatórios avançados e gráficos.
Módulo de autenticação com múltiplos usuários.
Contribuição
Contribuições são bem-vindas! Siga estas etapas para contribuir:

Faça um fork deste repositório.
Crie uma branch para sua feature ou correção de bug: git checkout -b minha-feature.
Faça commit das suas alterações: git commit -m 'Adicionei uma nova funcionalidade'.
Envie para o branch principal: git push origin minha-feature.
Crie um Pull Request.
Suporte
Para dúvidas ou problemas, abra uma Issue no repositório do projeto ou entre em contato pelo e-mail seu-email@provedor.com.

Desenvolvido com ❤️ por Alex F. de Souza.

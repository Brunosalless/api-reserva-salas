# API de Reservas de salas 

Uma api para reservas de sala, pode ser usada pra gerenciar quem pode usar cada sala e em qual horario pode ser usada e muito boa para professores em universidades 

## Tecnologias

- Python 3.11.9
- FastAPI
- uvicorne app.main:app
- SQLite (arquivo local) - biblioteca que se comunica com o phyton e a SQLAlchemy==2.1.8 e a configura~
ao ainda ira ser emplementada 

## Como rodar o projeto

1. Clone o repositório e entre na pasta:

```
git clone <url do repositório>
cd <nome da pasta>
```

2. Crie e ative o ambiente virtual (no PowerShell):

```
"caminho da sua pasta\venv\Scripts\Activate.ps1"
```

3. Instale as dependências:

```
pip install -r requirements.txt
```

4. Copie o `.env.example` para `.env` e preencha os valores. O .env nao pode ir de jeito nenhum para o git porque e onde entra as credenciais mais importantes do projeto com o token e a senha do banco de dados que sao as informações mais importantes do projeto

5. Suba o servidor:

```
uvicorn app.main:app
```

6. Abra `<endereço>/docs` para ver a documentação automática. Voce vera o Sweeguer basicamente onde voce ve as rotas e requisissoes HTTP funcionando 

## Estrutura de pastas

| Pasta / arquivo | Para que serve |
| --- | --- |
| `app/` | E onde fica o codigo principal do projeto  |
| `app/main.py` | E o arquivo principal onde fica responsavel por iniciar o FastAPI e para registrar oss routers  |
| `app/database.py` | Responsavel para a configuração do banco de dados e para as configurações necessarias para acessar o banco  |
| `app/models/` | onde ficam os modelos que serao introduzidos no banco de dados  |
| `app/schemas/` | serve para validar os dados recebidos pelos schemas e definir o formato de resposta da api |
| `app/routers/` | Onde ficam as rotas da api organizadas por funcionalidade |
| `app/core/` | COnfigurações principais entram aqui, como variaveis de ambiente e configurações de segurança e de autenticação |
| `tests/` | Testes para rodarem na aplicação para ver se as funcionalidades do projeto estao funcionando corretamente |
| `requirements.txt` | Lista de bibliotecas necessario para gerar o projeto e instalar em qualquer maquin  |
| `.env.example` | E necessario para mostrar os nomes das variaveis de ambiente para configurar a aplicação |

## Equipe

- Bruno Candido Salles ([@Brunosalless](https://github.com/Brunosalless))
- Pedro Henrique Carneiro da Silva ([@PedroCarneiro-sheep](https://github.com/PedroCarneiro-sheep))
- Thyago Barbosa Afonso ([@Thyago-afonso](https://github.com/Thyago-afonso))
- João Victor Costa Silva ([@jv-cos](https://github.com/jv-cos))


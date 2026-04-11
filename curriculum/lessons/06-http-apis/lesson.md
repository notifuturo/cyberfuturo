# HTTP e APIs públicas

Até agora a gente só tocou em arquivos locais. Essa lição é onde tudo isso se conecta com
a internet real. Você vai usar `curl` pra fazer uma requisição HTTP para uma API pública,
ver a resposta JSON, e escrever um pequeno script Python que lê essa resposta e extrai
um campo.

Esse é o padrão que está em todos os apps modernos: seu programa manda uma requisição,
a API responde com JSON, seu programa faz alguma coisa com os dados. Slack, Uber,
Instagram, tudo — é o mesmo ciclo.

## A API que a gente vai usar

[JSONPlaceholder](https://jsonplaceholder.typicode.com/) é uma API pública, gratuita,
sem autenticação, criada especialmente para testes e aprendizado. A gente vai bater em
um endpoint dela que devolve uma tarefa (a "todo"):

```
https://jsonplaceholder.typicode.com/todos/1
```

A resposta é um JSON parecido com isso:

```json
{
  "userId": 1,
  "id": 1,
  "title": "delectus aut autem",
  "completed": false
}
```

## Sua tarefa

Duas partes, as duas dentro de `curriculum/`:

1. Usando `curl`, baixe a resposta do endpoint acima e salve em um arquivo chamado
   `todo.json`.
2. Escreva um script Python chamado `ler_todo.py` que:
   - lê o arquivo `todo.json`
   - extrai o campo `title`
   - imprime uma linha: `Título: <o valor do title>`

## Comandos que você vai usar

```
curl https://jsonplaceholder.typicode.com/todos/1
    ← imprime a resposta na tela

curl -s https://jsonplaceholder.typicode.com/todos/1 > todo.json
    ← salva a resposta em um arquivo (-s para "silencioso", sem barra de progresso)

python3 -m json.tool todo.json
    ← imprime o JSON de forma legível (utilitário embutido do Python)
```

E para o script Python, você vai precisar do módulo `json` da biblioteca padrão:

```python
import json
from pathlib import Path

data = json.loads(Path("todo.json").read_text())
print(f"Título: {data['title']}")
```

## Os passos, um por um

### 1. Faça a requisição e salve o JSON

```
cd ~/curriculum
curl -s https://jsonplaceholder.typicode.com/todos/1 > todo.json
```

### 2. Veja o que chegou

```
cat todo.json
python3 -m json.tool todo.json
```

Você deve ver um objeto JSON com os campos `userId`, `id`, `title`, `completed`.

### 3. Crie o script ler_todo.py

Abra `ler_todo.py` no seu editor e escreva:

```python
import json
from pathlib import Path

data = json.loads(Path("todo.json").read_text())
print(f"Título: {data['title']}")
```

### 4. Rode o script

```
python3 ler_todo.py
```

Você deve ver algo como:

```
Título: delectus aut autem
```

### 5. Valide

```
./cf check
```

## Se algo der errado

- **`curl: (6) Could not resolve host`** — não tem internet. Num Codespace isso é raro.
  Verifique com `curl -I https://google.com`.
- **`json.decoder.JSONDecodeError`** no Python — o `todo.json` provavelmente está vazio
  ou tem algum texto que não é JSON. Refaça o `curl`.
- **`KeyError: 'title'`** — o JSON está certo mas você extraiu uma chave errada. Confira
  com `python3 -m json.tool todo.json`.

## O que você acabou de aprender

- **curl** — fazer requisições HTTP direto do terminal
- **JSON** — o formato padrão pra trocar dados entre programas e APIs
- **python3 -m json.tool** — um jeito rápido de imprimir JSON legível
- **import json** em Python — ler JSON de um arquivo e acessar seus campos como um
  dicionário
- A anatomia de uma integração real: **requisição HTTP → resposta JSON → extrair um
  campo → fazer alguma coisa com ele**

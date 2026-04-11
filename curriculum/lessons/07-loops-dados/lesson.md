# Loops com dados reais

Na lição anterior você bateu em uma API pública e leu UMA tarefa. Essa é a parte
que muda tudo: a mesma API devolve uma LISTA com 200 tarefas se você tirar o
`/1` do final. Uma requisição, duzentos registros. Agora você escreve um loop de
três linhas em Python e de repente tem um mini-pipeline de dados.

Esse é o padrão que todo analista, todo engenheiro de backend, todo cientista de
dados usa o dia inteiro: pega uma lista vinda de algum lugar, passa por ela uma
vez, conta ou filtra, imprime o resumo. Você vai fazer exatamente isso.

## A API (mesma de ontem, endpoint diferente)

```
https://jsonplaceholder.typicode.com/todos
```

Sem o `/1`. A resposta é uma lista JSON com 200 objetos, cada um no mesmo formato
que você já viu:

```json
[
  { "userId": 1, "id": 1, "title": "delectus aut autem", "completed": false },
  { "userId": 1, "id": 2, "title": "quis ut nam facilis...", "completed": false },
  ...
]
```

## Sua tarefa

Duas partes, as duas dentro de `curriculum/`:

1. Usando `curl`, baixe a lista inteira e salve em um arquivo chamado
   `todos.json`.
2. Escreva um script Python chamado `contar_todos.py` que:
   - lê o arquivo `todos.json`
   - conta quantas tarefas tem no total
   - conta quantas estão `completed: true`
   - conta quantas estão `completed: false`
   - imprime exatamente três linhas, nessa ordem:
     ```
     Total: 200
     Concluídas: <n>
     Pendentes: <n>
     ```

Os números de concluídas e pendentes têm que somar 200. Se não somar, tem bug.

## Comandos que você vai usar

```
curl -s https://jsonplaceholder.typicode.com/todos > todos.json
    ← salva a lista inteira no arquivo

python3 contar_todos.py
    ← roda seu script
```

## Dica de Python (se travar)

O padrão de contar coisas em uma lista é esse aqui:

```python
import json

with open("todos.json") as f:
    todos = json.load(f)

total = len(todos)
concluidas = 0
for t in todos:
    if t["completed"]:
        concluidas += 1
pendentes = total - concluidas

print(f"Total: {total}")
print(f"Concluídas: {concluidas}")
print(f"Pendentes: {pendentes}")
```

Leia antes de copiar. Cada linha tem um motivo. `len()` conta, o `for` passa por
cada item, o `if` decide se soma, e no final a matemática fecha sozinha.

## Quando estiver pronto

```
./cf check
```

Se passar:

```
./cf next
```

## Por que essa lição importa

Um loop com `if` dentro é um dos conceitos mais antigos da computação e ainda é
a ferramenta mais usada pra tirar sentido de dados. SQL GROUP BY, pandas, Excel
pivot, Spark, tudo isso é uma versão sofisticada do que você acabou de fazer em
cinco linhas. Se você entender esse loop de verdade, o resto é só vocabulário.

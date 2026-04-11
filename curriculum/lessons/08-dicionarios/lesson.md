# Dicionários e agrupamento

Na lição 07 você escreveu um loop que passou pela lista inteira e contou
uma coisa: quantas estavam concluídas. Três números no final. Agora vem
a pergunta que todo produto do mundo faz do jeito que você acabou de fazer:
*quantas por usuário?*

A resposta é uma estrutura de dados nova pra você: o **dicionário**. Em
Python se escreve `{}`. Em JavaScript você já viu com outro nome: é o
objeto JSON que saiu da API. Em SQL é uma tabela com chave primária. Em
Excel é uma tabela dinâmica (pivot). É literalmente o mesmo conceito em
quatro sotaques diferentes: "pra cada chave, guarda um valor".

## A pergunta

Usando o mesmo arquivo `todos.json` da lição anterior (sim, aquele mesmo,
se você apagou baixa de novo), responda:

> Quantas tarefas cada usuário tem, e quantas dessas estão concluídas?

A resposta final tem que imprimir uma linha por usuário, do `userId` 1
até o 10, exatamente nesse formato:

```
Usuário 1: 20 tarefas, 11 concluídas
Usuário 2: 20 tarefas, 8 concluídas
...
Usuário 10: 20 tarefas, 12 concluídas
```

(Os números de concluídas por usuário você descobre rodando o script —
não copia da lição.)

## Sua tarefa

1. Se você não tem mais o `todos.json`, rode de novo:
   ```
   curl -s https://jsonplaceholder.typicode.com/todos > todos.json
   ```
2. Escreva um script Python chamado `por_usuario.py` que:
   - lê `todos.json`
   - monta um dicionário onde a chave é o `userId` e o valor são dois
     contadores: total e concluídas
   - imprime uma linha por usuário, do 1 até o 10, no formato acima

## A ideia do dicionário

O pulo do gato é esse: em vez de contadores soltos (`concluidas = 0`
como na lição 07), você guarda um contador POR CHAVE:

```python
contagem = {}   # começa vazio
contagem[1] = {"total": 0, "concluidas": 0}
contagem[1]["total"] += 1
```

E o padrão clássico pra "adicionar um item que pode ainda não existir no
dicionário" é `dict.setdefault`:

```python
for t in todos:
    u = t["userId"]
    contagem.setdefault(u, {"total": 0, "concluidas": 0})
    contagem[u]["total"] += 1
    if t["completed"]:
        contagem[u]["concluidas"] += 1
```

Depois você passa pelas chaves em ordem e imprime:

```python
for u in sorted(contagem):
    c = contagem[u]
    print(f"Usuário {u}: {c['total']} tarefas, {c['concluidas']} concluídas")
```

Leia, não copie. O `setdefault` é o que garante que a chave existe antes
de você mexer nela — sem isso você toma `KeyError` na primeira iteração.

## Rodar

```
python3 por_usuario.py
./cf check
```

## Por que isso importa

Você acabou de escrever um `GROUP BY`. De verdade. A query SQL
`SELECT userId, COUNT(*), SUM(completed) FROM todos GROUP BY userId`
faz EXATAMENTE isso, só que o banco de dados escreve o loop por você.
pandas, Spark, MapReduce, Power BI — todas essas ferramentas existem
pra não ter que escrever esse loop na mão quando a lista tem bilhão
de itens em vez de duzentos. O conceito é o mesmo. A partir de agora,
quando alguém te falar "agrupa por X", você sabe o que tá acontecendo
debaixo do capô.

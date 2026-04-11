# Sua primeira consulta SQL

Banco de dados é onde dados **de verdade** moram. Quando você abre um app, clica em um
botão, e vê uma lista de alguma coisa, provavelmente teve um `SELECT` rodando em algum
banco de dados no meio do caminho.

SQL é a linguagem universal para falar com bancos de dados relacionais. É velha (dos
anos 70), simples (seis comandos principais), e está em todo lugar. Aprender SQL uma vez
serve para o resto da sua carreira.

Nessa lição você vai criar um banco de dados SQLite do zero, criar uma tabela, inserir
alguns livros, e rodar uma consulta que filtra por um critério.

O legal do **SQLite**: o banco de dados inteiro cabe em um único arquivo `.db`. Sem
servidor, sem daemon, sem configuração. É perfeito para aprender e para muitas aplicações
reais.

## Sua tarefa

Dentro de `curriculum/` você vai criar um banco SQLite chamado `biblioteca.db` com:

1. Uma tabela chamada `livros` com as colunas: `id` (integer primary key), `titulo`
   (text), `autor` (text), `ano` (integer)
2. Pelo menos **3 livros inseridos**, e pelo menos **2 deles com `ano >= 2000`**
3. Rodar uma consulta que seleciona apenas os livros com `ano >= 2000` e salvar o
   resultado em `curriculum/consulta.txt`

## Comandos que você vai usar

```
sqlite3 biblioteca.db            ← abre (ou cria) o banco de dados em modo interativo
.tables                          ← lista as tabelas (comando especial, começa com ponto)
.schema                          ← mostra o SQL de criação das tabelas
.quit                            ← sai do sqlite3

# SQL de verdade (termina cada comando com ; ):
CREATE TABLE livros (id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, ano INTEGER);
INSERT INTO livros (titulo, autor, ano) VALUES ('O Alquimista', 'Paulo Coelho', 1988);
INSERT INTO livros (titulo, autor, ano) VALUES ('Cidade de Deus', 'Paulo Lins', 1997);
SELECT * FROM livros WHERE ano >= 2000;
```

## Dicas

- Você pode rodar SQL direto da linha de comando sem entrar no modo interativo:
  ```
  sqlite3 biblioteca.db "SELECT * FROM livros WHERE ano >= 2000"
  ```
- Para salvar a saída de uma consulta em um arquivo, use o redirecionamento de shell:
  ```
  sqlite3 biblioteca.db "SELECT titulo FROM livros WHERE ano >= 2000" > consulta.txt
  ```
- Aspas simples `'` dentro do SQL, aspas duplas `"` do lado de fora pro shell. Se
  confundir, entre no modo interativo com `sqlite3 biblioteca.db` e digite lá dentro.
- Livros podem ter aspas simples no título (`"L'Etranger"`). No SQL você escapa com
  duas aspas simples: `'L''Etranger'`.

## Os passos, um por um

### 1. Criar o banco e a tabela

```
cd ~/curriculum
sqlite3 biblioteca.db
```

Isso abre o prompt do sqlite3. No prompt, rode:

```
CREATE TABLE livros (id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, ano INTEGER);
```

### 2. Inserir pelo menos 3 livros

Ainda no mesmo prompt:

```
INSERT INTO livros (titulo, autor, ano) VALUES ('Dom Casmurro', 'Machado de Assis', 1899);
INSERT INTO livros (titulo, autor, ano) VALUES ('Cidade de Deus', 'Paulo Lins', 1997);
INSERT INTO livros (titulo, autor, ano) VALUES ('Torto Arado', 'Itamar Vieira Junior', 2019);
INSERT INTO livros (titulo, autor, ano) VALUES ('Ponciá Vicêncio', 'Conceição Evaristo', 2003);
```

Pelo menos 2 livros precisam ter `ano >= 2000`.

### 3. Verificar que tudo está lá

```
SELECT * FROM livros;
```

Você deve ver seus livros listados.

### 4. Sair do prompt

```
.quit
```

### 5. Rodar a consulta final e salvar em consulta.txt

De volta no shell normal (fora do sqlite3):

```
sqlite3 biblioteca.db "SELECT titulo FROM livros WHERE ano >= 2000" > consulta.txt
cat consulta.txt
```

Você deve ver os títulos dos livros de 2000 pra cima, um por linha.

### 6. Rode o check

```
./cf check
```

## O que você acabou de aprender

- **sqlite3 arquivo.db** — abrir ou criar um banco SQLite
- **CREATE TABLE / INSERT INTO / SELECT** — os três comandos SQL mais usados no mundo
- **WHERE** — filtrar linhas por um critério
- **Redirecionamento do shell** para guardar a saída de uma consulta em um arquivo
- Como um banco de dados relacional pensa: tabelas, linhas, colunas, tipos

# Navegar o sistema de arquivos

Agora que você já sabe criar um arquivo, vamos aprender a se mover. Um sistema de arquivos
é uma estrutura em forma de árvore: diretórios dentro de diretórios, com arquivos nas
folhas. Os comandos para se mover e olhar são os que você vai usar **todos os dias** da
sua carreira.

## Sua tarefa

Dentro de `curriculum/lessons/01-terminal/workspace/` tem um diretório chamado
`labirinto/`. Em algum lugar desse labirinto tem um arquivo escondido chamado `.premio`.
Sua tarefa é **encontrar ele** e escrever o conteúdo dele em um arquivo novo chamado
`premio.txt` no diretório `curriculum/` (não dentro do workspace, diretamente em
`curriculum/`).

## Comandos que você vai usar

```
cd <caminho>           ← mudar de diretório
cd ..                  ← subir um nível
cd                     ← voltar pro home
ls                     ← listar arquivos
ls -a                  ← listar TODOS os arquivos (incluindo os ocultos: os que começam com .)
ls -la                 ← lista detalhada
find . -name .premio   ← buscar um arquivo por nome a partir daqui pra baixo
cat <arquivo>          ← ler o conteúdo
pwd                    ← onde estou agora
```

## Dicas

- Arquivos que começam com `.` são **arquivos ocultos**. `ls` normal não mostra eles;
  você precisa usar `ls -a`.
- O comando `find` é seu amigo. `find . -name .premio` vai procurar a partir do
  diretório atual pra baixo e imprimir o caminho do arquivo se achar.
- Você pode usar `cat <caminho-completo>` para ler o arquivo sem precisar fazer `cd`
  antes.
- Para escrever o conteúdo de um arquivo em outro: `cat <origem> > <destino>`.

## Os passos, um por um

1. `cd curriculum/lessons/01-terminal/workspace/labirinto`
2. Use `ls -la` e `find` para explorar a estrutura. Você vai ver alguns diretórios aninhados.
3. Encontre `.premio` com `find . -name .premio`. O comando te dá o caminho.
4. Leia com `cat <caminho>`. Confira o conteúdo.
5. Volte com `cd ~/curriculum` (ou `cd` até chegar no diretório `curriculum/`).
6. Escreva o conteúdo em `premio.txt` com `cat <caminho-do-.premio> > premio.txt`.
7. Rode `./cf check`.

## O que você acabou de aprender

- **cd** — se mover entre diretórios
- **ls -la** — ver arquivos ocultos e detalhes
- **find** — buscar arquivos por nome
- **cat origem > destino** — copiar conteúdo de um arquivo para outro
- O que são arquivos ocultos (os que começam com `.`)

# Seu primeiro commit em Git

Git é o sistema de controle de versão que 95% do mundo do software usa. Ele faz uma
coisa: guarda instantâneas do seu código ao longo do tempo. Cada instantânea se chama um
**commit**. Um commit tem uma mensagem curta que explica o que mudou. Todo o seu trabalho
vai ficar registrado como uma lista de commits que você pode ver com `git log`.

Nessa lição você vai criar um miniprojeto, inicializar como um repositório Git, e fazer
seu primeiro commit de verdade.

## Sua tarefa

Dentro de `curriculum/` você vai criar um diretório chamado `meu-projeto/` que contém:

1. Um arquivo `README.md` com exatamente essa linha: `# meu-projeto`
2. Um arquivo `notas.txt` com qualquer texto que você quiser (qualquer coisa, com pelo
   menos 3 caracteres)
3. O diretório precisa ser um repositório Git com **pelo menos um commit** que inclui os
   dois arquivos

## Comandos que você vai usar

```
mkdir meu-projeto              ← criar o diretório
cd meu-projeto                 ← entrar no diretório
echo "# meu-projeto" > README.md
echo "oi" > notas.txt

git init                       ← inicializar um repositório git aqui
git status                     ← ver quais arquivos estão e qual é o estado deles
git add .                      ← adicionar todos os arquivos à "área de staging"
git commit -m "mensagem"       ← criar um commit com essa mensagem
git log                        ← ver o histórico de commits
```

## Dicas

- Se você nunca usou Git, a primeira vez ele pode pedir um nome e um email. Se isso
  acontecer, rode:
  ```
  git config --global user.email "voce@email.com"
  git config --global user.name "Seu Nome"
  ```
- `git status` é o comando mais importante. Use ele **muito**. Depois de cada passo,
  pra ver o que o Git está vendo.
- Quando você rodar `git add .`, nada visível acontece. Isso é normal. O Git prepara
  os arquivos pro commit, mas ainda não guarda. `git status` vai te mostrar os arquivos
  "staged".
- A mensagem de commit precisa ser significativa. Não coloque `"asdf"`. Coloque algo
  como `"início do projeto"` ou `"primeiro commit"`. Uma mensagem decente faz parte
  da tarefa.

## Os passos, um por um

1. `cd ~/curriculum`
2. `mkdir meu-projeto && cd meu-projeto`
3. `echo "# meu-projeto" > README.md`
4. `echo "essa é minha primeira nota" > notas.txt`
5. `git init`
6. `git status`  ← olhe a saída. Os arquivos aparecem em vermelho, "untracked".
7. `git add .`
8. `git status`  ← agora aparecem em verde, "Changes to be committed".
9. `git commit -m "início do projeto"`
10. `git log`  ← você vai ver seu commit com um hash, seu nome, e a data.
11. `cd ..` para voltar a `curriculum/`, e depois `./cf check`.

## O que você acabou de aprender

- **git init** — transformar um diretório em um repositório Git
- **git status** — ver o que mudou e o que está pronto pra commit
- **git add** — preparar arquivos para serem commitados
- **git commit -m "mensagem"** — criar uma instantânea com uma mensagem
- **git log** — ver o histórico de commits
- O que é "staging" (a área intermediária entre seu código e o histórico)

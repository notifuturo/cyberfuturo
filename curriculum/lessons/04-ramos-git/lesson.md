# Ramos e fusões em Git

Na lição 02 você aprendeu a fazer um commit. Um commit é uma foto do seu código. Agora
vamos aprender a ter **várias fotos em paralelo** — que é o que um ramo (branch) faz.

Um ramo é uma linha independente de commits. Você pode trabalhar em uma ideia nova em um
ramo separado sem bagunçar o ramo principal. Quando a ideia estiver pronta, você **funde**
(merge) ela de volta no ramo principal, e os commits aparecem no histórico.

Essa é a forma mais comum de trabalhar em qualquer projeto real: `main` é a linha estável,
os ramos são onde você experimenta, e o merge é como o experimento volta pro projeto.

## Sua tarefa

Dentro de `curriculum/` você vai criar um novo projetinho chamado `meu-blog/`:

1. Inicializar como repo Git
2. Fazer um commit inicial com um `README.md` que contenha `# meu-blog`
3. Criar um ramo chamado `adicionar-licenca`
4. Nesse ramo, adicionar um arquivo `LICENSE` com pelo menos o texto `MIT` dentro
5. Fazer um commit com a licença
6. Voltar pro ramo principal e fazer o merge do ramo `adicionar-licenca`
7. O resultado final: no seu ramo principal, `git log` mostra **pelo menos dois
   commits**, o `LICENSE` existe e está versionado, e `meu-blog/` é um repositório
   Git válido

## Comandos que você vai usar

```
git init                          ← cria um repositório
git add <arquivo>                 ← prepara arquivos pra commit
git commit -m "mensagem"          ← cria um commit
git branch                        ← lista os ramos
git branch <nome>                 ← cria um ramo com esse nome (não muda pra ele)
git switch <nome>                 ← muda pro ramo (comando moderno, recomendado)
git switch -c <nome>              ← cria E muda pro ramo em um passo só
git checkout <nome>               ← jeito antigo de mudar de ramo, ainda funciona
git merge <nome>                  ← funde o ramo na branch atual
git log --oneline --graph         ← vê o histórico com uma pequena ilustração
```

## Dicas

- A primeira vez que você roda `git init`, o ramo padrão pode ser `main` ou `master`
  dependendo da sua configuração. Os dois funcionam pra essa tarefa. Para forçar
  `main`: `git init -b main`.
- `git switch -c adicionar-licenca` é **equivalente** a `git branch adicionar-licenca`
  seguido de `git switch adicionar-licenca`. Os dois caminhos levam ao mesmo lugar.
- Antes de fazer merge, você precisa estar **no ramo de destino**. Ou seja: volte pro
  `main` primeiro, e depois rode `git merge adicionar-licenca`.
- Se o merge for "fast-forward" (nenhum commit no main além do ponto de origem do
  ramo), o Git só vai mover o ponteiro. Sem conflito. Isso é normal.

## Os passos, um por um

```
cd ~/curriculum
mkdir meu-blog && cd meu-blog
git init -b main

echo "# meu-blog" > README.md
git add README.md
git commit -m "primeiro commit"

git switch -c adicionar-licenca
echo "MIT" > LICENSE
git add LICENSE
git commit -m "adicionar licenca MIT"

git switch main
git merge adicionar-licenca

git log --oneline --graph
```

Você deve ver duas linhas no log: o primeiro commit e o commit da licença.

Depois disso, `cd ~/curriculum` e rode `./cf check`.

## O que você acabou de aprender

- **git branch / git switch** — criar e navegar entre ramos
- **git merge** — juntar um ramo dentro de outro
- **git log --graph** — ver a história como um gráfico de commits
- Por que trabalhar em ramos: manter o ramo principal estável enquanto você experimenta
- O ciclo básico do Git em equipe: ramo → commits → merge de volta pro main

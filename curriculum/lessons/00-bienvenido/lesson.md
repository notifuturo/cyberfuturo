# Boas-vindas — seu primeiro arquivo

Você está em uma máquina virtual, no navegador. Não instalou nada. Aquela janela embaixo
com o cursor piscando é um **terminal**, e a partir de agora ele é sua ferramenta principal.

O terminal é um programa que aceita comandos digitados e executa. Cada comando é uma
palavra (às vezes com argumentos). No fim do comando, você aperta Enter, o programa faz
alguma coisa, e devolve o controle pra você.

## Sua tarefa

Dentro do diretório atual você vai criar um arquivo. Ele se chama `ola.txt` e seu conteúdo
é exatamente o texto **olá mundo** seguido de uma quebra de linha.

## Comandos que você vai precisar

```
pwd                          ← imprime "print working directory"
ls                           ← lista os arquivos do diretório atual
echo "olá mundo" > ola.txt   ← cria um arquivo com o texto dado
cat ola.txt                  ← imprime o conteúdo do arquivo
```

## Os passos, um por um

1. Rode `pwd`. Isso mostra onde você está no sistema de arquivos.
2. Rode `ls`. Isso mostra quais arquivos tem aqui. Você ainda não deve ver `ola.txt`.
3. Rode `echo "olá mundo" > ola.txt`. O símbolo `>` redireciona a saída do comando
   para um arquivo. Você está criando `ola.txt` com esse conteúdo em uma única linha.
4. Rode `cat ola.txt`. Deve imprimir `olá mundo` na tela.
5. Quando estiver pronto, rode `./cf check` para validar.

## Se algo der errado

- Se o arquivo ficar com aspas dentro do texto, você provavelmente escreveu
  `echo ola mundo` sem as aspas ou usou aspas curvas. Delete o arquivo com
  `rm ola.txt` e tente de novo.
- Se o conteúdo terminar sem quebra de linha, o teste vai te avisar com uma dica.
- Se você se perdeu e está no diretório errado, volte com `cd ~/curriculum` e
  confirme com `pwd`.

## O que você acabou de aprender

- **pwd** — onde você está
- **ls** — o que tem aqui
- **echo** — imprimir texto na tela (ou redirecionar para um arquivo)
- **cat** — ler um arquivo
- **>** — redirecionar a saída para um arquivo

# CyberFuturo — o curso

> **Aprenda tecnologia de trás para frente.** GUI → Terminal → Git → SQL → Python.
> Tudo no seu navegador, sem instalar nada.

Este diretório contém o curso completo. Se você está lendo isso dentro de um Codespace,
já tem tudo o que precisa pra começar. Se chegou aqui pelo GitHub, clique no botão verde
**Code → Open in Codespaces**.

## Começar

```bash
cd curriculum
./cf start
```

Isso abre a primeira lição que você ainda não concluiu.

## Idiomas

As lições são escritas em **português brasileiro** por padrão. Se você preferir outro
idioma, defina a variável de ambiente `CF_LANG` antes de começar:

```bash
export CF_LANG=es    # espanhol (arquivo: lesson.es.md)
export CF_LANG=pt    # português (padrão, arquivo: lesson.md)
```

O runner carrega automaticamente a versão do idioma escolhido quando ela existe. Se não
houver uma tradução, ele usa o português canônico como fallback. As traduções disponíveis
hoje:

| Idioma | Status |
|---|---|
| Português (pt) | ✅ canônico |
| Espanhol (es) | ✅ arquivo em todas as lições |
| Inglês (en) | ⏳ em desenvolvimento |
| Francês (fr) | ⏳ em desenvolvimento |

## Comandos do runner

| Comando | O que faz |
|---|---|
| `./cf list` | Lista todas as lições com seu status |
| `./cf start [n]` | Começa a lição `n` (ou a próxima não concluída) |
| `./cf show` | Reimprime as instruções da lição atual |
| `./cf check` | Valida a lição atual |
| `./cf next` | Avança pra próxima lição (depois de passar o check) |
| `./cf progress` | Mostra seu progresso geral |
| `./cf reset` | Reinicia seu progresso |
| `./cf help` | Ajuda |

## Como as lições estão organizadas

Cada lição vive em `lessons/NN-slug/` e contém:

- `lesson.md` — as instruções em português (padrão)
- `lesson.es.md` — versão em espanhol (opcional)
- `test.py` — o validador automático da lição

Seu progresso é salvo em `.progress.json` (esse arquivo está no `.gitignore` pra cada
estudante ter seu próprio progresso no seu fork).

## Lições disponíveis (v0.1)

| # | Nome | Tempo |
|---|---|---|
| 00 | Boas-vindas — seu primeiro arquivo | ~15 min |
| 01 | Navegar o sistema de arquivos | ~25 min |
| 02 | Seu primeiro commit em Git | ~30 min |
| 03 | Seu primeiro script em Python | ~30 min |
| 04 | Ramos e fusões em Git | ~30 min |
| 05 | Sua primeira consulta SQL | ~35 min |
| 06 | HTTP e APIs públicas | ~30 min |
| 07 | Loops com dados reais | ~30 min |
| 08 | Dicionários e agrupamento | ~30 min |

Total atual: **9 lições · ~4h 15min** de tarefas práticas com validação automática.

## Filosofia

- **As lições são tarefas reais**, não quizzes nem múltipla escolha.
- **Os testes verificam o estado real** dos seus arquivos, do seu repositório Git, ou
  da saída dos seus programas — eles não comparam texto com uma resposta pré-escrita.
- **O runner é Python stdlib puro**, 0 dependências. Se algo quebrar, você pode ler o
  código você mesmo e consertar.
- **Progresso = commits**. Cada lição concluída é uma nova entrada no seu histórico do
  Git. No final do curso você tem um repo com 30+ commits reais pra colocar no seu CV.

## Se algo não funcionar

1. Leia com atenção a mensagem de erro que o `./cf check` te deu. Os testes tentam
   te dar uma dica específica.
2. Rode `./cf show` pra reler as instruções da lição atual.
3. Olha o arquivo `test.py` da lição atual — é Python legível, você pode ver
   exatamente o que ele está procurando.
4. Abra uma issue no repositório do GitHub.

## Licença

MIT sobre o código. CC-BY-4.0 sobre o conteúdo das lições. Use, modifique, traduza,
ensine. Só atribua.

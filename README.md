# Nuvem de Palavras (Flask) — Deploy na Vercel

Este projeto é um gerador de nuvem de palavras com frontend estático em `web/` e backend Flask.

## Como o deploy na Vercel funciona

- A Vercel executa o backend como **Python Serverless Function** em `api/index.py`.
- O Flask também serve os arquivos estáticos do frontend (`web/`).
- A geração da imagem acontece em disco temporário (`/tmp`) e a rota `POST /generate` retorna o **PNG diretamente**.

## Deploy (via Dashboard)

1. Suba este repositório para o GitHub.
2. No painel da Vercel: **Add New → Project → Import**.
3. Framework preset: pode deixar “Other”.
4. Deploy.

Depois do deploy, abra a URL do projeto e teste a geração.

## Deploy (via Vercel CLI)

> Opcional. Útil pra iterar rápido.

```zsh
npm i -g vercel
vercel login
vercel
```

## Estrutura relevante

- `api/index.py`: entrypoint da Vercel (expõe o `app` do Flask)
- `server.py`: rotas `/` e `/generate`
- `web/`: frontend
- `vercel.json`: regras de build/rotas

## Observações importantes (serverless)

- O filesystem da Vercel é **somente leitura**, exceto `/tmp`. Por isso uploads/outputs vão pra `/tmp`.
- A rota `GET /results/<filename>` existe por compatibilidade, mas não é garantido que o arquivo exista entre invocações.
- Se a fonte padrão não estiver disponível, envie uma fonte `.ttf/.otf` pelo formulário.

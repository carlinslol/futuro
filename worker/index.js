/**
 * Finanças do Casal - o servidor.
 *
 * Faz duas coisas, e só:
 *   1. entrega o app (o financas.html, embutido no Worker na publicação);
 *   2. guarda e devolve o "cofre" de cada casal.
 *
 * O cofre chega aqui JÁ CIFRADO. A senha do casal nunca sai do celular: lá
 * ela vira a chave AES e o id do cofre (PBKDF2). Este Worker só vê um id de
 * 64 hex e um texto embaralhado - quem tiver acesso ao banco, inclusive você
 * pelo painel da Cloudflare, não consegue ler gasto nenhum.
 *
 * Conflito: cada gravação diz em qual versão se baseou. Se o outro celular
 * gravou no meio, a resposta é 409 com a versão atual; o app junta as duas
 * (mesclar() no financas.html) e tenta de novo. Ninguém perde edição.
 *
 * Não tem login: quem não sabe a senha do casal não chega a cofre nenhum,
 * e mesmo quem chegasse só veria texto cifrado.
 */
import pagina from "../financas.html";

// Um cofre cifrado e comprimido de um ano de dois cartões e duas contas fica
// na casa de 150 KB. O teto é o limite de linha do D1 (2 MB) com folga.
const TAMANHO_MAX = 1_900_000;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
};

const SEGURANCA = {
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...CORS },
  });
}

async function lerCofre(env, id) {
  return env.DB.prepare("SELECT versao, dados, atualizado FROM cofres WHERE id = ?").bind(id).first();
}

async function gravarCofre(req, env, id) {
  let corpo;
  try {
    corpo = await req.json();
  } catch {
    return json({ erro: "corpo não é JSON" }, 400);
  }
  const anterior = Number(corpo && corpo.versaoAnterior);
  const dados = corpo && corpo.dados;
  if (!Number.isInteger(anterior) || anterior < 0 || typeof dados !== "string" || !dados)
    return json({ erro: "faltam versaoAnterior e dados" }, 400);
  if (dados.length > TAMANHO_MAX) return json({ erro: "cofre grande demais" }, 413);

  const agora = new Date().toISOString();
  let r;
  if (anterior === 0) {
    // Cofre novo. Teto de cofres para ninguém usar o seu Worker de depósito.
    const max = Number(env.MAX_COFRES || 5);
    const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM cofres").first();
    const existe = await lerCofre(env, id);
    if (!existe && n && n.n >= max)
      return json({ erro: "limite de cofres deste servidor atingido (MAX_COFRES)" }, 403);
    r = await env.DB.prepare(
      "INSERT INTO cofres (id, versao, dados, atualizado) VALUES (?, 1, ?, ?) ON CONFLICT(id) DO NOTHING"
    ).bind(id, dados, agora).run();
  } else {
    r = await env.DB.prepare(
      "UPDATE cofres SET dados = ?, versao = versao + 1, atualizado = ? WHERE id = ? AND versao = ?"
    ).bind(dados, agora, id, anterior).run();
  }
  if (!r.meta || !r.meta.changes) {
    const atual = await lerCofre(env, id);
    return json({ erro: "conflito", versao: atual ? atual.versao : 0, dados: atual ? atual.dados : null }, 409);
  }
  return json({ versao: anterior + 1, atualizado: agora });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    const m = /^\/api\/cofre\/([0-9a-f]{64})$/.exec(url.pathname);
    if (m) {
      const id = m[1];
      if (req.method === "GET") {
        const c = await lerCofre(env, id);
        if (!c) return json({ versao: 0 }, 404);
        // O app manda a versão que já tem: se for a mesma, não precisa baixar tudo de novo.
        if (url.searchParams.get("versao") === String(c.versao))
          return json({ versao: c.versao, atualizado: c.atualizado, igual: true });
        return json(c);
      }
      if (req.method === "PUT") return gravarCofre(req, env, id);
      return json({ erro: "método não permitido" }, 405);
    }

    if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/index.html" || url.pathname === "/financas.html")) {
      return new Response(pagina, {
        headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-cache", ...SEGURANCA },
      });
    }
    // O app procura este arquivo (gerado pelo financas_pluggy.py) ao abrir.
    // Online ele não existe: responde vazio em vez de 404 para não sujar o console.
    if (url.pathname === "/financas-dados.js")
      return new Response("", { headers: { "Content-Type": "text/javascript", "Cache-Control": "no-store" } });

    return new Response("não encontrado", { status: 404 });
  },
};

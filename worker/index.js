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
    "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
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
    // Ícone da tela de início (a Clo), para "Adicionar à tela de início".
    if (url.pathname === "/icone-180.png")
      return new Response(Uint8Array.from(atob(ICONE_180), (c) => c.charCodeAt(0)), {
        headers: { "Content-Type": "image/png", "Cache-Control": "public, max-age=86400" },
      });
    // O app procura este arquivo (gerado pelo financas_pluggy.py) ao abrir.
    // Online ele não existe: responde vazio em vez de 404 para não sujar o console.
    if (url.pathname === "/financas-dados.js")
      return new Response("", { headers: { "Content-Type": "text/javascript", "Cache-Control": "no-store" } });

    return new Response("não encontrado", { status: 404 });
  },
};

/* A cabeça da Clo em PNG 180x180: o mesmo desenho do símbolo "clo-cabeca" do
   financas.html, renderizado sobre fundo branco (o iPhone não aceita SVG como
   ícone da tela de início). */
const ICONE_180 =
  "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";

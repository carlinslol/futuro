// O Worker (o cofre do casal), rodado aqui com um D1 de mentira
// em cima do SQLite do próprio Node.
//
// O que ele não pode errar: dois celulares gravando ao mesmo tempo - um ganha,
// o outro recebe 409 com a versão atual para juntar e tentar de novo. Errar
// isso é perder gasto lançado sem ninguém perceber.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { DatabaseSync } from "node:sqlite";

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PASTA = path.join(RAIZ, "worker");

const falhas = [];
function ok(c, msg, x) {
  console.log((c ? "  [ok]   " : "  [FALHA] ") + msg + (x !== undefined ? "  -> " + x : ""));
  if (!c) falhas.push(msg);
}

/* D1 mínimo: prepare().bind().first()/run(), como o Worker usa. */
export function d1(arquivo = ":memory:") {
  const db = new DatabaseSync(arquivo);
  db.exec(fs.readFileSync(path.join(PASTA, "schema.sql"), "utf8"));
  return {
    prepare(sql) {
      let args = [];
      const st = {
        bind(...a) { args = a; return st; },
        async first() { return db.prepare(sql).get(...args) ?? null; },
        async run() { const r = db.prepare(sql).run(...args); return { meta: { changes: Number(r.changes) } }; },
      };
      return st;
    },
  };
}

/* O Worker importa o financas.html como texto (regra do wrangler). Aqui
   troco a linha do import pelo conteúdo, e carrego como módulo. */
export async function carregarWorker() {
  const html = fs.readFileSync(path.join(RAIZ, "financas.html"), "utf8");
  const fonte = fs.readFileSync(path.join(PASTA, "index.js"), "utf8")
    .replace(/^import pagina from "\.\.\/financas\.html";$/m, () => "const pagina = " + JSON.stringify(html) + ";");
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "financas-worker-")), "index.mjs");
  fs.writeFileSync(tmp, fonte);
  return (await import(pathToFileURL(tmp).href)).default;
}

async function principal() {
  const W = await carregarWorker();
  const env = { DB: d1(), MAX_COFRES: "2" };
  const pedir = (caminho, init) => W.fetch(new Request("https://f.test" + caminho, init), env);
  const put = (id, versaoAnterior, dados) => pedir("/api/cofre/" + id, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ versaoAnterior, dados }),
  });
  const A = "a".repeat(64), B = "b".repeat(64), C = "c".repeat(64);

  console.log("\n=== página ===");
  let r = await pedir("/");
  const html = await r.text();
  ok(r.status === 200 && html.includes('<script id="nucleo">'), "entrega o financas.html em /");
  ok(/connect-src 'self'/.test(r.headers.get("Content-Security-Policy") || ""), "com CSP");
  r = await pedir("/financas-dados.js");
  ok(r.status === 200 && (await r.text()) === "", "financas-dados.js vazio online");
  ok((await pedir("/qualquer")).status === 404, "o resto é 404");

  console.log("\n=== cofre ===");
  r = await pedir("/api/cofre/" + A);
  ok(r.status === 404 && (await r.json()).versao === 0, "cofre que não existe: 404, versão 0");
  ok((await pedir("/api/cofre/xyz")).status === 404, "id inválido nem chega no banco");
  r = await put(A, 0, "cifrado-1");
  ok(r.status === 200 && (await r.json()).versao === 1, "cria na versão 1");
  r = await pedir("/api/cofre/" + A);
  let j = await r.json();
  ok(j.versao === 1 && j.dados === "cifrado-1", "lê de volta");
  r = await pedir("/api/cofre/" + A + "?versao=1");
  j = await r.json();
  ok(j.igual === true && j.dados === undefined, "mesma versão: não manda os dados de novo");

  console.log("\n=== os dois gravando ao mesmo tempo ===");
  const [ele, ela] = await Promise.all([put(A, 1, "dele"), put(A, 1, "dela")]);
  const st = [ele.status, ela.status].sort();
  ok(st[0] === 200 && st[1] === 409, "um ganha, o outro recebe 409", st.join(","));
  const perdedor = ele.status === 409 ? ele : ela;
  j = await perdedor.json();
  ok(j.versao === 2 && (j.dados === "dele" || j.dados === "dela"), "o 409 traz a versão atual para juntar");
  r = await put(A, 2, "juntado");
  ok(r.status === 200 && (await r.json()).versao === 3, "depois de juntar, grava");
  ok((await put(A, 0, "recriar")).status === 409, "não recria por cima de cofre existente");

  console.log("\n=== limites ===");
  ok((await put(B, 0, "x")).status === 200, "segundo cofre ok");
  r = await put(C, 0, "x");
  ok(r.status === 403, "terceiro passa do MAX_COFRES", r.status);
  ok((await put(A, 3, "x".repeat(1_900_001))).status === 413, "cofre grande demais");
  ok((await put(A, -1, "x")).status === 400, "versão inválida");
  r = await pedir("/api/cofre/" + A, { method: "PUT", body: "não é json" });
  ok(r.status === 400, "corpo inválido");
  ok((await pedir("/api/cofre/" + A, { method: "DELETE" })).status === 405, "não dá para apagar pela API");
  r = await pedir("/api/cofre/" + A, { method: "OPTIONS" });
  ok(r.status === 204 && r.headers.get("Access-Control-Allow-Origin") === "*", "CORS para o app aberto do computador");

  console.log("\n" + (falhas.length ? falhas.length + " FALHA(S)" : "tudo certo"));
  process.exit(falhas.length ? 1 : 0);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) principal();

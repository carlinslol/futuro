// subir_cofre.mjs: as transações do Pluggy indo direto para o cofre, sem
// navegador, contra o Worker de verdade (o mesmo index.js, num D1 de SQLite).
//
// O que não pode errar: senha errada nunca cria cofre novo; o que já está no
// cofre (regras, edições, a outra pessoa) nunca se perde; e se o celular
// gravar no meio, junta e grava de novo.
import http from "node:http";
import { carregarWorker, d1 } from "./financas_worker.mjs";
import { carregarNucleo, subir, lerConfig, lerDados, Erro } from "../subir_cofre.mjs";

const falhas = [];
function ok(c, msg, x) {
  console.log((c ? "  [ok]   " : "  [FALHA] ") + msg + (x !== undefined ? "  -> " + x : ""));
  if (!c) falhas.push(msg);
}
const calado = () => {};

const W = await carregarWorker();
const env = { DB: d1(), MAX_COFRES: "2" };
const srv = http.createServer(async (req, res) => {
  const corpo = await new Promise((r) => { const b = []; req.on("data", (c) => b.push(c)); req.on("end", () => r(Buffer.concat(b))); });
  const resp = await W.fetch(new Request("http://x" + req.url, {
    method: req.method, headers: req.headers, body: ["GET", "HEAD"].includes(req.method) ? undefined : corpo,
  }), env);
  res.writeHead(resp.status, Object.fromEntries(resp.headers));
  res.end(Buffer.from(await resp.arrayBuffer()));
});
await new Promise((r) => srv.listen(0, "127.0.0.1", r));
const SERVIDOR = "http://127.0.0.1:" + srv.address().port;

const N = carregarNucleo();
const SENHA = "abcd-efgh-jkmn-pqrs";
const { id, chave } = await N.derivarCofre(SENHA);
const URL_COFRE = SERVIDOR + "/api/cofre/" + id;
async function lerCofre() {
  const j = await (await fetch(URL_COFRE)).json();
  return { versao: j.versao, estado: await N.decifrar(chave, j.dados) };
}

// O cofre como o celular deixou: nomes, uma regra própria e uma transação dela.
const celular = N.estadoPadrao();
celular.pessoas.p1.nome = "Brenno"; celular.pessoas.p2.nome = "Ana";
// como a tela do app faz: a regra nova substitui a que já existia com o mesmo termo
celular.regras = celular.regras.filter((r) => r.termo !== "padaria");
celular.regras.push({ termo: "padaria", categoria: "lazer", divisao: "casal" });
celular.configAlterada = Date.now();
N.importar(celular, "p2-cartao", [{ data: "2026-10-03", descricao: "Farmácia dela", valor: 40 }], "nubank-cartao");
await fetch(URL_COFRE, { method: "PUT", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ versaoAnterior: 0, dados: await N.cifrar(chave, celular) }) });

const DADOS = { geradoEm: "2026-10-09T10:00:00-03:00", transacoes: [
  { id: "t1", pessoa: "p1", tipo: "conta", data: "2026-10-01", descricao: "Compra no débito - PADARIA REAL", valor: 12.5, categoriaPluggy: "Bakery" },
  { id: "t2", pessoa: "p1", tipo: "conta", data: "2026-10-02", descricao: "Transferência recebida - SALARIO", valor: -5000, categoriaPluggy: "Salary" },
] };

console.log("\n=== subir ===");
let r = await subir({ N, servidor: SERVIDOR + "/", senha: SENHA, dados: DADOS, avisar: calado });
ok(r.novas === 2, "as duas transações sobem", JSON.stringify(r));
let { versao, estado } = await lerCofre();
const padaria = estado.transacoes.find((t) => t.id === "pg-t1");
ok(padaria && padaria.categoria === "lazer" && padaria.divisao === "casal", "usa as regras que estão no cofre", padaria && padaria.categoria);
ok(estado.transacoes.find((t) => t.id === "pg-t2").categoria === "entradas", "salário vira entrada");
ok(estado.transacoes.some((t) => t.descricao === "Farmácia dela") && estado.pessoas.p2.nome === "Ana",
   "o que já estava no cofre continua lá");

console.log("\n=== de novo, nada novo ===");
r = await subir({ N, servidor: SERVIDOR, senha: SENHA, dados: DADOS, avisar: calado });
ok(r.novas === 0 && (await lerCofre()).versao === versao, "não regrava o cofre à toa");

console.log("\n=== o celular apagou uma; o script não ressuscita ===");
N.apagar(estado, "pg-t1");
await fetch(URL_COFRE, { method: "PUT", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ versaoAnterior: versao, dados: await N.cifrar(chave, estado) }) });
r = await subir({ N, servidor: SERVIDOR, senha: SENHA, dados: DADOS, avisar: calado });
ok(r.novas === 0 && !(await lerCofre()).estado.transacoes.some((t) => t.id === "pg-t1"), "apagada no app continua apagada");

console.log("\n=== senha errada ===");
const contar = async () => (await env.DB.prepare("SELECT COUNT(*) AS n FROM cofres").first()).n;
const antes = await contar();
let erro = null;
try { await subir({ N, servidor: SERVIDOR, senha: "outra-senha-qualquer", dados: DADOS, avisar: calado }); } catch (e) { erro = e; }
ok(erro instanceof Erro && /Não existe cofre/.test(erro.message), "avisa que não existe cofre", erro && erro.message.split("\n")[0]);
ok((await contar()) === antes, "e não cria cofre nenhum");
erro = null;
try { await subir({ N, servidor: SERVIDOR, senha: "", dados: DADOS, avisar: calado }); } catch (e) { erro = e; }
ok(erro && /cofre_senha/.test(erro.message), "sem senha no config: diz qual linha preencher");
erro = null;
try { await subir({ N, servidor: "http://127.0.0.1:1", senha: SENHA, dados: DADOS, avisar: calado }); } catch (e) { erro = e; }
ok(erro instanceof Erro && /Não consegui falar/.test(erro.message), "site fora do ar: mensagem clara");

console.log("\n=== o celular grava no meio ===");
const DADOS2 = { geradoEm: "2026-10-10T10:00:00-03:00", transacoes: [
  { id: "t3", pessoa: "p1", tipo: "cartao", data: "2026-10-05", descricao: "IFOOD", valor: 60, categoriaPluggy: "" }] };
let atrapalhou = false;
const buscar = async (url, opts) => {
  if (opts && opts.method === "PUT" && !atrapalhou) {
    atrapalhou = true;   // antes do PUT do script, o celular grava uma edição
    const c = await lerCofre();
    c.estado.pessoas.p1.nome = "Brenno C."; c.estado.configAlterada = Date.now();
    await fetch(URL_COFRE, { method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ versaoAnterior: c.versao, dados: await N.cifrar(chave, c.estado) }) });
  }
  return fetch(url, opts);
};
const avisos = [];
r = await subir({ N, servidor: SERVIDOR, senha: SENHA, dados: DADOS2, buscar, avisar: (m) => avisos.push(m) });
({ estado } = await lerCofre());
ok(r.novas === 1 && avisos.some((m) => /gravou no meio/.test(m)), "recebe 409 e refaz");
ok(estado.pessoas.p1.nome === "Brenno C." && estado.transacoes.some((t) => t.id === "pg-t3"),
   "a edição do celular e a transação nova ficam as duas");

console.log("\n=== arquivos ===");
const cfg = lerConfig('﻿# x\ncofre_servidor = "https://a.b"\ncofre_senha = <abc-def>\nvazio =\n');
ok(cfg.cofre_servidor === "https://a.b" && cfg.cofre_senha === "abc-def" && cfg.vazio === "", "config com aspas e <>");
ok(lerDados("// Gerado\nwindow.FINANCAS_PLUGGY = " + JSON.stringify(DADOS) + ";\n").transacoes.length === 2, "lê o financas-dados.js");

srv.close();
console.log("\n" + (falhas.length ? falhas.length + " FALHA(S)" : "tudo certo"));
process.exit(falhas.length ? 1 : 0);

// Finanças do casal - leva as transações baixadas pelo financas_pluggy.py
// direto para o cofre do casal, sem abrir navegador.
//
//   node subir_cofre.mjs
//
// Lê o financas-dados.js, abre o cofre com a senha do casal (a mesma do
// celular), importa o que for novo com as MESMAS regras do app e grava de
// volta. Usa o próprio núcleo do financas.html - a categorização, a divisão
// e a mesclagem são exatamente as do app, não uma cópia.
//
// Nunca cria cofre: se a senha não abrir um cofre que já existe, ele para e
// avisa. (Senha errada criando um cofre novo, separado do de vocês, é o
// tipo de erro que ninguém percebe por semanas.)
//
// Precisa do Node 18 ou mais novo (o mesmo que roda o wrangler).
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath, pathToFileURL } from "node:url";

const PASTA = path.dirname(fileURLToPath(import.meta.url));

export class Erro extends Error {}

/* O núcleo do app, tirado do <script id="nucleo"> do financas.html. */
export function carregarNucleo(html = fs.readFileSync(path.join(PASTA, "financas.html"), "utf8")) {
  const m = /<script id="nucleo">([\s\S]*?)<\/script>/.exec(html);
  if (!m) throw new Erro("Não achei o núcleo dentro do financas.html.");
  const ctx = {
    module: { exports: {} }, crypto: globalThis.crypto, TextEncoder, TextDecoder,
    CompressionStream, DecompressionStream, Blob, Response, btoa, atob,
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(m[1], ctx);
  return ctx.module.exports;
}

/* financas_config.txt: "chave = valor", # comenta, aspas e <> em volta
   são tiradas (mesmas regras do financas_pluggy.py). */
export function lerConfig(texto) {
  const cfg = {};
  for (let linha of texto.replace(/^﻿/, "").split(/\r?\n/)) {
    linha = linha.trim();
    if (!linha || linha.startsWith("#") || !linha.includes("=")) continue;
    const i = linha.indexOf("=");
    let v = linha.slice(i + 1).trim();
    while (v.length >= 2 && ['""', "''", "<>"].includes(v[0] + v[v.length - 1])) v = v.slice(1, -1).trim();
    cfg[linha.slice(0, i).trim().toLowerCase()] = v;
  }
  return cfg;
}

function lerTexto(arquivo) {
  const b = fs.readFileSync(arquivo);
  if (b[0] === 0xff && b[1] === 0xfe) return b.subarray(2).toString("utf16le");
  return b.toString("utf8");
}

export function lerDados(texto) {
  const i = texto.indexOf("window.FINANCAS_PLUGGY = ");
  if (i < 0) throw new Erro("O financas-dados.js não tem o formato esperado. Rode o financas_pluggy.py de novo.");
  return JSON.parse(texto.slice(i + "window.FINANCAS_PLUGGY = ".length).trim().replace(/;\s*$/, ""));
}

/* Abre o cofre, importa e grava. Se o celular gravar no meio, o servidor
   responde 409: baixa de novo e refaz (até 5 vezes). */
export async function subir({ N, servidor, senha, dados, buscar = fetch, avisar = console.log }) {
  if (!senha || N.limparSenha(senha).length < 12)
    throw new Erro("Falta a senha do casal (cofre_senha no financas_config.txt), a mesma do celular.");
  if (!/^https?:\/\//.test(servidor || ""))
    throw new Erro("Falta o endereço do site (cofre_servidor no financas_config.txt).");
  const base = servidor.replace(/\/+$/, "");
  const { id, chave } = await N.derivarCofre(senha);
  const url = base + "/api/cofre/" + id;

  for (let tentativa = 1; tentativa <= 5; tentativa++) {
    let r;
    try {
      r = await buscar(url, { cache: "no-store" });
    } catch (e) {
      throw new Erro("Não consegui falar com " + base + " (" + (e.cause?.code || e.message) + ").");
    }
    if (r.status === 404)
      throw new Erro("Não existe cofre com essa senha em " + base + ".\n" +
        "Confira se cofre_senha é exatamente a mesma senha que vocês usam no celular.\n" +
        "(Este script nunca cria cofre: quem cria é o app, no celular.)");
    if (!r.ok) throw new Erro("O site respondeu " + r.status + " ao abrir o cofre.");
    const j = await r.json();
    let estado;
    try {
      estado = N.completar(await N.decifrar(chave, j.dados));
    } catch (e) {
      throw new Erro("Achei o cofre, mas não consegui abrir os dados. A senha está certa?");
    }

    const antes = estado.transacoes.length;
    const res = N.importarPluggy(estado, dados);
    if (!res.novas) {
      avisar("Nada novo para subir: as " + dados.transacoes.length + " transações baixadas já estão no cofre.");
      return { novas: 0, versao: j.versao, total: antes };
    }
    const cifrado = await N.cifrar(chave, estado);
    const p = await buscar(url, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ versaoAnterior: j.versao, dados: cifrado }),
    });
    if (p.status === 409) { avisar("O outro aparelho gravou no meio; juntando de novo..."); continue; }
    if (!p.ok) {
      const e = await p.json().catch(() => ({}));
      throw new Erro("O site recusou a gravação (" + p.status + "): " + (e.erro || "sem detalhe"));
    }
    const v = await p.json();
    avisar(res.novas + " transações novas subiram para o cofre (agora são " + estado.transacoes.length + ").");
    return { novas: res.novas, versao: v.versao, total: estado.transacoes.length };
  }
  throw new Erro("O cofre mudou 5 vezes seguidas enquanto eu gravava. Tente de novo daqui a pouco.");
}

async function principal() {
  const arqConfig = path.join(PASTA, "financas_config.txt");
  const arqDados = path.join(PASTA, "financas-dados.js");
  if (!fs.existsSync(arqConfig)) throw new Erro("Não achei o financas_config.txt. Rode antes: python financas_pluggy.py");
  if (!fs.existsSync(arqDados)) throw new Erro("Não achei o financas-dados.js. Rode antes: python financas_pluggy.py");
  const cfg = lerConfig(lerTexto(arqConfig));
  const N = carregarNucleo();
  await subir({ N, servidor: cfg.cofre_servidor, senha: cfg.cofre_senha, dados: lerDados(lerTexto(arqDados)) });
  console.log("Pronto: abra o site no celular para ver.");
}

if (process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url) {
  principal().catch((e) => {
    console.error("\n" + (e instanceof Erro ? e.message : (e && e.stack) || e));
    process.exit(1);
  });
}

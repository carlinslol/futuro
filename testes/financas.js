// Finanças do casal: o núcleo do financas.html.
//
// O que importa acertar aqui é dinheiro: o sinal de cada formato do Nubank
// (fatura e extrato vêm com sinais opostos), não duplicar quando o mesmo
// arquivo é importado de novo, e o acerto entre os dois - que não pode contar
// o mesmo Pix duas vezes quando os dois extratos estão importados.
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RAIZ = path.resolve(__dirname, "..");
const PASTA = RAIZ;
const html = fs.readFileSync(path.join(PASTA, "financas.html"), "utf8");
const m = /<script id="nucleo">([\s\S]*?)<\/script>/.exec(html);
const ctx = { module: { exports: {} }, crypto: globalThis.crypto, TextEncoder, TextDecoder,
  CompressionStream, DecompressionStream, Blob, Response, btoa, atob };
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(m[1], ctx);
const N = ctx.module.exports;

let falhas = [];
function ok(c, msg, x) {
  console.log((c ? "  [ok]   " : "  [FALHA] ") + msg + (x !== undefined ? "  -> " + x : ""));
  if (!c) falhas.push(msg);
}
const exemplo = (n) => fs.readFileSync(path.join(PASTA, "exemplos", n), "utf8");
const perto = (a, b) => Math.abs(a - b) < 0.011;  // meio centavo arredonda para um lado ou outro

console.log("\n=== leitura de valores e datas ===");
ok(N.lerValor("1.234,56") === 1234.56, "1.234,56");
ok(N.lerValor("-45.90") === -45.9, "-45.90");
ok(N.lerValor("R$ 12,00") === 12, "R$ 12,00");
ok(N.lerValor("1,234.56") === 1234.56, "1,234.56");
ok(N.lerData("15/01/2024") === "2024-01-15", "dd/mm/aaaa");
ok(N.lerData("2024-01-15") === "2024-01-15", "aaaa-mm-dd");
ok(N.lerData("20240115120000[-3:BRT]") === "2024-01-15", "data OFX");

console.log("\n=== formatos do Nubank ===");
const c1 = N.lerArquivo(exemplo("cartao-pessoa1-2026-09.csv"));
ok(c1.formato === "nubank-cartao" && c1.tipo === "cartao", "fatura CSV reconhecida como cartão");
ok(c1.itens.find((i) => i.descricao === "Carrefour Hiper").valor === 312.48, "compra no cartão fica positiva");
ok(c1.itens.find((i) => i.descricao === "Pagamento recebido").valor === -1840.33, "pagamento da fatura fica negativo");

const e1 = N.lerArquivo(exemplo("extrato-pessoa1-2026-09.csv"));
ok(e1.formato === "nubank-conta" && e1.tipo === "conta", "extrato CSV reconhecido como conta");
ok(e1.itens.find((i) => /ENEL/.test(i.descricao)).valor === 189.9, "saída da conta vira gasto positivo");
ok(e1.itens.find((i) => /EMPRESA EXEMPLO/.test(i.descricao)).valor === -5200, "salário vira negativo");
ok(e1.itens.every((i) => i.idExterno), "extrato usa o Identificador do Nubank");

const c2 = N.lerArquivo(exemplo("cartao-pessoa2-2026-09.csv"));
ok(c2.itens.some((i) => i.descricao === 'Estorno de "Shein"' && i.valor === -43.9), "aspas escapadas no CSV", JSON.stringify(c2.itens.slice(-1)));

const ofx = `OFXHEADER:100
DATA:OFXSGML
<OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST>
<STMTTRN><TRNTYPE>DEBIT<DTPOSTED>20260903000000[-3:BRT]<TRNAMT>-58.70<FITID>abc-1<MEMO>Compra no débito - PADARIA REAL</STMTTRN>
<STMTTRN><TRNTYPE>CREDIT<DTPOSTED>20260905000000[-3:BRT]<TRNAMT>1000.00<FITID>abc-2<MEMO>Transferência recebida</STMTTRN>
</BANKTRANLIST></STMTRS></STMTTRNRS></BANKMSGSRSV1></OFX>`;
const o = N.lerArquivo(ofx);
ok(o.formato === "ofx" && o.tipo === "conta" && o.itens.length === 2, "OFX da conta", o.itens.length);
ok(o.itens[0].valor === 58.7 && o.itens[0].data === "2026-09-03" && o.itens[0].idExterno === "abc-1", "OFX: débito vira gasto positivo");
ok(N.lerArquivo(ofx.replace("<BANKMSGSRSV1>", "<CREDITCARDMSGSRSV1>")).tipo === "cartao", "OFX de cartão reconhecido");

let erro = null;
try { N.lerArquivo("qualquer,coisa\n1,2"); } catch (x) { erro = x; }
ok(erro && /não reconhecido/.test(erro.message), "arquivo estranho dá erro claro");

console.log("\n=== categorias ===");
const e = N.estadoPadrao();
e.pessoas.p1 = { nome: "Bruno", nomeBanco: "Bruno Costa" };
e.pessoas.p2 = { nome: "Ana", nomeBanco: "Ana Pereira" };
const cat = (d, v, conta) => N.categorizar(e, d, v === undefined ? 10 : v, conta || "p1-cartao").categoria;
ok(cat("Ifd*Ifood Restaurante") === "restaurante", "iFood");
ok(cat("Uber Eats") === "restaurante" && cat("Uber *Trip") === "transporte", "termo mais longo vence (uber eats x uber)");
ok(cat("Mercado Dia") === "mercado" && cat("Diaria hotel") !== "mercado", "palavra inteira: 'dia' não pega 'diaria'");
ok(cat("Pagamento de fatura", 100, "p1-conta") === "fora", "pagamento de fatura não é gasto");
ok(cat("Pagamento recebido", -100) === "fora", "pagamento recebido no cartão não é gasto");
ok(cat("Transferência recebida pelo Pix - EMPRESA", -5000, "p1-conta") === "entradas", "dinheiro que entra sem regra = entrada");
ok(cat("Estorno de qualquer loja xyz", -20, "p1-cartao") === "outros", "estorno no cartão não vira entrada");
ok(cat("Transferência enviada pelo Pix - ANA PEREIRA - 123", 300, "p1-conta") === "entre", "Pix para a outra pessoa = entre vocês");
ok(cat("Transferência enviada pelo Pix - ANA PEREIRA - 123", 300, "p2-conta") !== "entre", "Pix para si mesma não é 'entre vocês'");
ok(N.categorizar(e, "Carrefour", 100, "p1-cartao").divisao === "casal", "mercado é do casal por padrão");
ok(N.categorizar(e, "Netflix", 40, "p1-cartao").divisao === "pessoal", "assinatura é pessoal por padrão");
ok(N.categorizar(e, "algo novo", 40, "p1-conta", "Food delivery").categoria === "restaurante", "dica do Pluggy quando não há regra");
ok(N.descricaoCurta("Transferência enviada pelo Pix - ANA PEREIRA - •••.123.456-•• - NU PAGAMENTOS - IP") === "Pix para ANA PEREIRA", "descrição curta do Pix");
ok(N.descricaoCurta("Amazon Marketplace - Parcela 2/5") === "Amazon Marketplace - Parcela 2/5", "descrição curta não corta parcela");
ok(N.sugerirTermo("Compra no débito - PADARIA REAL 123") === "padaria real", "termo sugerido", N.sugerirTermo("Compra no débito - PADARIA REAL 123"));

console.log("\n=== importar sem duplicar ===");
let r = N.importar(e, "p1-cartao", c1.itens, "nubank-cartao");
ok(r.novas === c1.itens.length && r.repetidas === 0, "primeira importação", JSON.stringify(r));
const padarias = e.transacoes.filter((t) => t.descricao === "Padaria Pao Quente");
ok(padarias.length === 2 && padarias[0].id !== padarias[1].id, "duas compras iguais no mesmo dia continuam duas");
r = N.importar(e, "p1-cartao", N.lerArquivo(exemplo("cartao-pessoa1-2026-09.csv")).itens, "nubank-cartao");
ok(r.novas === 0 && r.repetidas === c1.itens.length, "reimportar o mesmo arquivo não duplica", JSON.stringify(r));
r = N.importar(e, "p2-cartao", c1.itens, "nubank-cartao");
ok(r.novas === c1.itens.length, "mesmo arquivo em outra pessoa conta separado");
e.transacoes = e.transacoes.filter((t) => t.conta !== "p2-cartao");

console.log("\n=== acerto entre os dois ===");
const a = N.estadoPadrao();
a.pessoas.p1.nomeBanco = "Bruno Costa";
a.pessoas.p2.nomeBanco = "Ana Pereira";
N.importar(a, "p1-cartao", N.lerArquivo(exemplo("cartao-pessoa1-2026-09.csv")).itens, "x");
N.importar(a, "p2-cartao", N.lerArquivo(exemplo("cartao-pessoa2-2026-09.csv")).itens, "x");
N.importar(a, "p1-conta", N.lerArquivo(exemplo("extrato-pessoa1-2026-09.csv")).itens, "x");
// Casal em setembro, pago por p1: Carrefour 312.48 é de agosto; Assai 264.90; ENEL 189.90;
// Claro 109.90; imobiliária (aluguel) 1800.  p2: Hortifruti 96.30, Mercado Dia 81.25.
const casalP1 = 264.90 + 189.90 + 109.90 + 1800;
const casalP2 = 96.30 + 81.25;
let ac = N.acerto(a, "2026-09");
ok(perto(ac.pagoPor.p1, casalP1), "despesas do casal pagas por p1", ac.pagoPor.p1);
ok(perto(ac.pagoPor.p2, casalP2), "despesas do casal pagas por p2", ac.pagoPor.p2);
// p2 recebeu de p1? Não: p1 RECEBEU 300 de p2 (só o extrato de p1 está importado).
ok(perto(ac.transferencias.p2, 300), "Pix recebido conta quando a saída não foi importada", JSON.stringify(ac.transferencias));
const esperado = casalP1 / 2 - casalP2 / 2 - 300;
ok(perto(ac.saldo, esperado), "saldo: metade do que p1 pagou - metade do de p2 - Pix", ac.saldo + " x " + esperado.toFixed(2));

N.importar(a, "p2-conta", N.lerArquivo(exemplo("extrato-pessoa2-2026-09.csv")).itens, "x");
ac = N.acerto(a, "2026-09");
const casalP2b = casalP2 + 220; // condomínio pago pela p2
ok(perto(ac.transferencias.p2, 300), "com os dois extratos o mesmo Pix conta UMA vez", JSON.stringify(ac.transferencias));
ok(perto(ac.saldo, casalP1 / 2 - casalP2b / 2 - 300), "saldo com os dois extratos", ac.saldo);

a.divisao.p1 = 70;
ac = N.acerto(a, "2026-09");
ok(perto(ac.saldo, casalP1 * 0.3 - casalP2b * 0.7 - 300), "divisão 70/30", ac.saldo);
a.divisao.p1 = 50;

console.log("\n=== resumo do mês ===");
const rs = N.resumoMes(a, "2026-09");
const soma = (o) => o.p1 + o.p2;
ok(perto(soma(rs.pagou), rs.total), "pagou p1 + p2 = total");
ok(perto(soma(rs.custo), rs.total), "custo p1 + p2 = total");
ok(!rs.categorias.some((c) => N.ESPECIAIS[c.id]), "entradas/fora/entre não aparecem como gasto");
ok(!a.transacoes.some((t) => /Pagamento de fatura/.test(t.descricao) && N.ehGasto(t)), "fatura não conta duas vezes");
ok(perto(rs.entradas.p1, 5200) && perto(rs.entradas.p2, 3900), "entradas de cada um", JSON.stringify(rs.entradas));
const mercado = rs.categorias.find((c) => c.id === "mercado");
ok(perto(mercado.total, 264.90 + 96.30 + 81.25), "mercado no mês", mercado.total);
const serie = N.serieMeses(a, "2026-09", 6);
ok(serie.length === 6 && serie[5].mes === "2026-09" && serie[4].mes === "2026-08", "série de 6 meses");
ok(N.somarMes("2026-01", -1) === "2025-12" && N.somarMes("2026-12", 1) === "2027-01", "virada de ano");

console.log("\n=== Pluggy, regras e backup ===");
const pg = N.estadoPadrao();
const dados = { geradoEm: "2026-10-09T10:00:00Z", transacoes: [
  { id: "t1", pessoa: "p1", tipo: "cartao", data: "2026-10-01", descricao: "IFOOD", valor: 50, categoriaPluggy: "Food delivery" },
  { id: "t2", pessoa: "p2", tipo: "conta", data: "2026-10-02", descricao: "Loja nova", valor: 30, categoriaPluggy: "Pharmacy" },
  { id: "t3", pessoa: "p9", tipo: "conta", data: "2026-10-02", descricao: "pessoa inválida", valor: 30 }
]};
r = N.importarPluggy(pg, dados);
ok(r.novas === 2, "Pluggy: importa e ignora pessoa desconhecida", JSON.stringify(r));
ok(pg.transacoes.find((t) => t.id === "pg-t2").categoria === "saude", "Pluggy: dica de categoria usada");
ok(N.importarPluggy(pg, dados).novas === 0, "Pluggy: abrir de novo não duplica");

const t = pg.transacoes.find((x) => x.id === "pg-t1");
t.categoria = "lazer"; t.manual = true;
pg.regras.push({ termo: "loja nova", categoria: "compras", divisao: "casal" });
N.reaplicarRegras(pg);
ok(t.categoria === "lazer", "reaplicar regras não mexe no que foi editado à mão");
const t2 = pg.transacoes.find((x) => x.id === "pg-t2");
ok(t2.categoria === "compras" && t2.divisao === "casal", "nova regra com divisão fixa");

const outro = JSON.parse(JSON.stringify(a));
outro.transacoes.push({ id: "zzz", conta: "p2-outro", data: "2026-09-30", descricao: "feira", valor: 20, categoria: "mercado", divisao: "casal" });
const antes = a.transacoes.length;
const nm = N.mesclar(a, outro);
ok(nm === 1 && a.transacoes.length === antes + 1, "juntar backup só traz o que falta", nm);

const vazio = N.completar({ transacoes: [] });
ok(vazio.categorias.some((c) => c.id === "fora") && vazio.pessoas.p2, "backup incompleto é completado");

console.log("\n=== os dois aparelhos ===");
// Dois celulares partindo do mesmo cofre, cada um mexendo numa coisa.
const base = N.estadoPadrao();
N.importar(base, "p1-cartao", N.lerArquivo(exemplo("cartao-pessoa1-2026-09.csv")).itens, "x");
const dele = JSON.parse(JSON.stringify(base)), dela = JSON.parse(JSON.stringify(base));
const ifood = (e) => e.transacoes.find((t) => /Ifood/.test(t.descricao));
const netflix = (e) => e.transacoes.find((t) => /Netflix/.test(t.descricao));
Object.assign(ifood(dele), { categoria: "lazer", manual: true, alterado: Date.now() + 10 });
Object.assign(ifood(dela), { categoria: "mercado", manual: true, alterado: Date.now() + 20 });
N.apagar(dele, netflix(dele).id);
dela.pessoas.p2.nome = "Ana"; dela.configAlterada = Date.now() + 5;
N.importar(dela, "p2-cartao", N.lerArquivo(exemplo("cartao-pessoa2-2026-09.csv")).itens, "x");

const a1 = JSON.parse(JSON.stringify(dele)), a2 = JSON.parse(JSON.stringify(dela));
N.mesclar(a1, dela);
N.mesclar(a2, dele);
ok(N.canonico(a1) === N.canonico(a2), "juntar nos dois sentidos dá o mesmo estado");
ok(ifood(a1).categoria === "mercado", "na mesma transação vale a edição mais recente");
ok(!netflix(a1) && !netflix(a2), "apagada num aparelho some nos dois");
ok(a1.pessoas.p2.nome === "Ana", "configuração mais recente vale");
ok(a1.transacoes.some((t) => t.conta === "p2-cartao"), "o que ela importou chega para ele");
const vol = N.importar(a1, "p1-cartao", N.lerArquivo(exemplo("cartao-pessoa1-2026-09.csv")).itens, "x");
ok(vol.novas === 0 && !netflix(a1), "reimportar não ressuscita a apagada", JSON.stringify(vol));
const regra = JSON.parse(JSON.stringify(a1));
regra.regras.push({ termo: "netflix", categoria: "lazer", divisao: "" }); regra.configAlterada = Date.now() + 99;
N.mesclar(a1, regra);
ok(a1.regras.some((r) => r.termo === "netflix" && r.categoria === "lazer"), "regra nova chega pelo bloco de configuração");
const ordem = { b: 1, a: { d: [1, { y: 2, x: 1 }], c: null } };
ok(N.canonico(ordem) === N.canonico({ a: { c: null, d: [1, { x: 1, y: 2 }] }, b: 1 }), "canonico ignora ordem das chaves");

console.log("\n=== cofre cifrado ===");
(async () => {
  const c1 = await N.derivarCofre("  minha-senha-do-casal ");
  const c2 = await N.derivarCofre("minha-senha-do-casal");
  const c3 = await N.derivarCofre("minha-senha-do-casaL");
  ok(c1.id === c2.id && c1.chave === c2.chave, "mesma senha, mesmo cofre (espaços nas pontas não importam)");
  ok(c1.id !== c3.id && /^[0-9a-f]{64}$/.test(c1.id), "senha diferente, outro cofre");
  ok(!c1.chave.includes(c1.id.slice(0, 10)), "id e chave são coisas diferentes");
  const texto = await N.cifrar(c1.chave, a1);
  ok(!/Ifood|Carrefour|Ana/.test(texto), "nada legível no que vai para o servidor");
  const volta = await N.decifrar(c1.chave, texto);
  ok(N.canonico(volta) === N.canonico(a1), "decifra igual ao original");
  ok(texto.length < JSON.stringify(a1).length, "vai comprimido", texto.length + " < " + JSON.stringify(a1).length);
  let falhou = false;
  try { await N.decifrar(c3.chave, texto); } catch (x) { falhou = true; }
  ok(falhou, "senha errada não abre");
  const s1 = N.gerarSenha(), s2 = N.gerarSenha();
  ok(/^[a-z2-9]{4}(-[a-z2-9]{4}){3}$/.test(s1) && s1 !== s2, "senha gerada", s1);

  console.log("\n" + (falhas.length ? falhas.length + " FALHA(S)" : "tudo certo"));
  process.exit(falhas.length ? 1 : 0);
})();

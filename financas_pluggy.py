# -*- coding: utf-8 -*-
"""
Finanças do casal - baixa as transações do Nubank dos dois pelo Open Finance.

O Nubank não tem API aberta para pessoa física. O caminho oficial é o Open
Finance, e para um app caseiro o jeito prático de chegar nele é um agregador:
aqui, o Pluggy (https://pluggy.ai). Cada um de vocês autoriza a própria conta
uma vez, o Pluggy devolve um "itemId", e este script usa os dois itemIds para
baixar cartão e conta de cada um.

O resultado vai para financas-dados.js, ao lado do financas.html. O HTML lê
esse arquivo por <script src> ao abrir e importa o que for novo - o mesmo
arranjo do resto do projeto: o Python grava um .js, o HTML funciona offline.

Uso:
    python financas_pluggy.py              baixa o que é novo
    python financas_pluggy.py --dias 365   baixa o último ano inteiro
    python financas_pluggy.py --testar     só confere credenciais e lista as contas
    python financas_pluggy.py --atualizar  pede ao Pluggy para buscar no banco antes
    python financas_pluggy.py --conectar pessoa1
                                           conecta o MeuPluggy e grava o itemId no config

Só usa a biblioteca padrão do Python: nada para instalar.
"""
import argparse
import datetime as dt
import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PASTA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(PASTA, "financas_config.txt")
SAIDA = os.path.join(PASTA, "financas-dados.js")
PREFIXO = "window.FINANCAS_PLUGGY = "
UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
API = os.environ.get("PLUGGY_URL", "https://api.pluggy.ai").rstrip("/")

MODELO_CONFIG = """\
# Finanças do casal - configuração da conexão automática (Pluggy / Open Finance)
#
# ESTE ARQUIVO TEM SEGREDO. Ele está no .gitignore: não mande para ninguém.
#
# Caminho gratuito (Meu Pluggy, uso pessoal): CADA UM tem a própria conta no
# Meu Pluggy e a própria aplicação no dashboard.pluggy.ai - o plano grátis é
# de um titular (CPF) só. Por isso cada pessoa tem as suas credenciais aqui.
# Passo a passo no LEIA-ME.md.
#
# pessoa1 é a "Pessoa 1" do app (cor azul); pessoa2, a "Pessoa 2" (laranja).
# Pode deixar uma pessoa em branco: assim cada um roda o script no próprio
# computador só com os próprios dados, e o cofre junta os dois.
#
# pessoa1 / pessoa2 = o itemId (NÃO o nome), um código assim:
#   1a2b3c4d-1111-2222-3333-444455556666
# Não precisa achar à mão: preencha o client_id e o client_secret e rode
#   python financas_pluggy.py --conectar pessoa1      (ou pessoa2)
# Ele abre a janela do Pluggy, você entra no MeuPluggy e o itemId vem para cá.
pessoa1 =
pessoa1_client_id =
pessoa1_client_secret =

pessoa2 =
pessoa2_client_id =
pessoa2_client_secret =

# Plano pago do Pluggy (uma aplicação para os dois): preencha só estas duas
# linhas e deixe as de cada pessoa em branco.
client_id =
client_secret =

# Cofre do casal: o sincronizar.bat sobe as transações direto para o site.
# A senha é a MESMA que vocês usam no celular (o script nunca cria cofre).
cofre_servidor = https://financas-casal.contatocarlinslol.workers.dev
cofre_senha =
"""


class Erro(Exception):
    pass


# ------------------------------------------------------------------ config

def ler_texto(caminho):
    """Lê o config no encoding em que o editor tiver salvo. O Bloco de Notas
    do Windows grava "Unicode" (UTF-16) ou ANSI se a pessoa escolher."""
    with open(caminho, "rb") as f:
        bruto = f.read()
    if bruto.startswith((b"\xff\xfe", b"\xfe\xff")):
        return bruto.decode("utf-16")
    try:
        return bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        return bruto.decode("cp1252")


def limpar_valor(v):
    """'  "abc"  ' -> 'abc'. Aspas e <> em volta do valor são o erro mais
    comum ao colar: viravam parte da credencial e o Pluggy recusava."""
    v = v.strip()
    while len(v) >= 2 and (v[0], v[-1]) in (('"', '"'), ("'", "'"), ("<", ">")):
        v = v[1:-1].strip()
    return v


def ler_chaves():
    """O financas_config.txt como dicionário (cria o modelo na primeira vez)."""
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            f.write(MODELO_CONFIG)
        raise Erro("Criei o %s. Preencha o Client ID e o Client Secret e rode de novo."
                   % os.path.basename(CONFIG))
    cfg = {}
    for linha in ler_texto(CONFIG).splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        k, v = linha.split("=", 1)
        cfg[k.strip().lower()] = limpar_valor(v)
    return cfg


def credenciais(cfg, p):
    """As credenciais da própria pessoa (Meu Pluggy, uma por titular); se não
    houver, as gerais (plano pago, uma aplicação para os dois)."""
    cred = (cfg.get(p + "_client_id", ""), cfg.get(p + "_client_secret", ""))
    if not all(cred):
        cred = (os.environ.get("PLUGGY_CLIENT_ID") or cfg.get("client_id", ""),
                os.environ.get("PLUGGY_CLIENT_SECRET") or cfg.get("client_secret", ""))
    if not all(cred):
        raise Erro("Faltam %s_client_id e %s_client_secret no %s."
                   % (p, p, os.path.basename(CONFIG)))
    return cred


def ler_config():
    cfg = ler_chaves()
    itens = {}   # itemId -> (pessoa, (client_id, client_secret))
    for p in ("pessoa1", "pessoa2"):
        ids = [x.strip() for x in cfg.get(p, "").split(",") if x.strip()]
        if not ids:
            continue
        cred = credenciais(cfg, p)
        for i in ids:
            if not UUID.match(i):
                raise Erro(
                    "Em %s = %s: isso não é um itemId.\n"
                    "O itemId é um código no formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.\n"
                    "O nome da pessoa não vai aqui. Para o script descobrir e gravar o itemId\n"
                    "sozinho, rode:  python financas_pluggy.py --conectar %s"
                    % (p, i, p))
            itens[i] = ("p1" if p == "pessoa1" else "p2", cred)
    if not itens:
        raise Erro("Nenhum itemId em pessoa1/pessoa2 no %s.\n"
                   "Para o script descobrir e gravar o seu, rode:\n"
                   "  python financas_pluggy.py --conectar pessoa1   (ou pessoa2)"
                   % os.path.basename(CONFIG))
    cfg["itens"] = itens
    return cfg


# --------------------------------------------------------------------- API

class Pluggy:
    def __init__(self, client_id, client_secret):
        r = self._pedir("POST", "/auth", {"clientId": client_id, "clientSecret": client_secret})
        self.chave = r.get("apiKey")
        if not self.chave:
            raise Erro("O Pluggy não devolveu a apiKey. Confira client_id e client_secret.")

    def _pedir(self, metodo, caminho, corpo=None, consulta=None):
        url = API + caminho
        if consulta:
            url += "?" + urllib.parse.urlencode(consulta)
        dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
        req = urllib.request.Request(url, data=dados, method=metodo)
        req.add_header("Accept", "application/json")
        if dados is not None:
            req.add_header("Content-Type", "application/json")
        if getattr(self, "chave", None):
            req.add_header("X-API-KEY", self.chave)
        for tentativa in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode("utf-8") or "{}")
            except urllib.error.HTTPError as e:
                texto = e.read().decode("utf-8", "replace")[:300]
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 ** tentativa)
                    continue
                if e.code in (401, 403):
                    raise Erro("O Pluggy recusou o acesso (%d). Confira as credenciais "
                               "e se o itemId é desta aplicação. %s" % (e.code, texto))
                raise Erro("Erro %d em %s: %s" % (e.code, caminho, texto))
            except urllib.error.URLError as e:
                if tentativa == 3:
                    raise Erro("Sem conexão com %s: %s" % (API, e.reason))
                time.sleep(2 ** tentativa)
        raise Erro("O Pluggy não respondeu em %s depois de 4 tentativas." % caminho)

    def connect_token(self, cliente):
        r = self._pedir("POST", "/connect_token", {"options": {"clientUserId": cliente}})
        token = r.get("accessToken")
        if not token:
            raise Erro("O Pluggy não devolveu o connect token.")
        return token

    def faturas(self, conta_id):
        """Faturas fechadas do cartão (GET /bills)."""
        r = self._pedir("GET", "/bills", consulta={"accountId": conta_id, "pageSize": 50})
        return r.get("results") or []

    def item(self, item_id):
        return self._pedir("GET", "/items/" + item_id)

    def atualizar_item(self, item_id, espera=180):
        """Pede ao Pluggy para buscar dados novos no banco e espera terminar."""
        self._pedir("PATCH", "/items/" + item_id, {})
        fim = time.time() + espera
        while time.time() < fim:
            st = self.item(item_id).get("status")
            if st not in ("UPDATING", "CREATING", None):
                return st
            time.sleep(5)
        return "UPDATING"

    def contas(self, item_id):
        return self._pedir("GET", "/accounts", consulta={"itemId": item_id}).get("results", [])

    def transacoes(self, conta_id, desde, ate):
        """GET /v2/transactions, página a página pelo cursor. (O /transactions
        por página foi desativado pelo Pluggy: responde 410.)"""
        todas, after, vistos = [], None, set()
        while True:
            consulta = {"accountId": conta_id, "dateFrom": desde, "dateTo": ate}
            if after:
                consulta["after"] = after
            r = self._pedir("GET", "/v2/transactions", consulta=consulta)
            todas.extend(r.get("results") or [])
            after = cursor_seguinte(r.get("next"))
            if not after or after in vistos:
                return todas
            vistos.add(after)


def cursor_seguinte(proximo):
    """O cursor da próxima página, a partir do campo "next" do /v2/transactions.

    O "next" vem como link ("/v2/transactions?accountId=...&after=CURSOR"),
    às vezes só a parte depois do "?", e há relato de vir o cursor puro. O
    cursor é base64 e pode ter "+", "/" e "=": aqui ele é tirado SEM tratar
    "+" como espaço (o erro que já quebrou o SDK oficial do Pluggy), e na
    próxima chamada o urlencode manda o "+" como %2B."""
    if not proximo:
        return None
    proximo = str(proximo)
    consulta = urllib.parse.urlsplit(proximo).query if "?" in proximo else ""
    if not consulta and "=" in proximo and "after" in proximo.split("=", 1)[0]:
        consulta = proximo
    if consulta:
        for parte in consulta.split("&"):
            if "=" in parte:
                k, v = parte.split("=", 1)
                if k == "after":
                    return urllib.parse.unquote(v) or None
        return None
    return proximo   # o cursor puro


# ----------------------------------------------------------- transformação

def valor_de(t):
    """Valor no sinal do app (positivo = gasto). O sinal vem do campo type, não
    do amount: no Pluggy o sinal do amount muda entre conta e cartão, e o type
    (DEBIT = saiu, CREDIT = entrou) não."""
    valor = t.get("amountInAccountCurrency")
    if valor is None:
        valor = t.get("amount")
    if valor is None:
        return None
    valor = abs(float(valor))
    return round(-valor if (t.get("type") or "").upper() == "CREDIT" else valor, 2)


def data10(v):
    v = str(v or "")[:10]
    return v if re.match(r"^\d{4}-\d{2}-\d{2}$", v) else None


def campos_cartao(t):
    """Do creditCardMetadata: parcela 3 de 10, a fatura prevista (AAAA-MM) e o
    id da fatura no banco."""
    m = t.get("creditCardMetadata") or {}
    x = {}
    try:
        k, n = int(m.get("installmentNumber") or 0), int(m.get("totalInstallments") or 0)
        if n > 1 and 1 <= k <= n:
            x["parcela"], x["parcelas"] = k, n
    except (TypeError, ValueError):
        pass
    prev = str(m.get("billForecastDate") or "")[:7]
    if re.match(r"^\d{4}-\d{2}$", prev):
        x["fatura"] = prev
    if m.get("billId"):
        x["billId"] = str(m["billId"])
    return x


def converter(t, pessoa, tipo):
    """Transação do Pluggy -> formato do app."""
    if (t.get("status") or "POSTED").upper() == "PENDING":
        return None  # compra ainda não fechada: o id pode mudar quando fechar
    valor = valor_de(t)
    data = data10(t.get("date"))
    if valor is None or not data:
        return None
    x = {
        "id": t["id"],
        "pessoa": pessoa,
        "tipo": tipo,
        "data": data,
        "descricao": t.get("description") or t.get("descriptionRaw") or "(sem descrição)",
        "valor": valor,
        "categoriaPluggy": t.get("category") or "",
    }
    if tipo == "cartao":
        x.update(campos_cartao(t))
    return x


def prevista(t):
    """Compra do cartão ainda pendente (ou parcela futura): não vira transação
    - o id muda quando ela fecha -, mas entra na previsão das faturas."""
    valor = valor_de(t)
    if valor is None:
        return None
    x = {"descricao": t.get("description") or "(sem descrição)", "valor": valor, "data": data10(t.get("date"))}
    x.update(campos_cartao(t))
    return x


def dados_do_cartao(api, c, pessoa, pendentes):
    cd = c.get("creditData") or {}
    faturas = []
    try:
        for b in api.faturas(c["id"]):
            faturas.append({"id": b.get("id"), "vencimento": data10(b.get("dueDate")),
                            "fechamento": data10(b.get("billClosingDate")),
                            "total": b.get("totalAmount"), "minimo": b.get("minimumPaymentAmount")})
    except Erro as e:
        print("           (faturas fechadas não vieram: %s)" % str(e)[:80])
    faturas.sort(key=lambda b: b["vencimento"] or "", reverse=True)
    return {
        "conta": c["id"], "pessoa": pessoa,
        "nome": c.get("marketingName") or c.get("name") or "Cartão",
        "bandeira": cd.get("brand") or "",
        "limite": cd.get("creditLimit"), "disponivel": cd.get("availableCreditLimit"),
        "saldo": c.get("balance"), "minimo": cd.get("minimumPayment"),
        "fechamento": data10(cd.get("balanceCloseDate")), "vencimento": data10(cd.get("balanceDueDate")),
        "faturas": faturas[:24],
        "previstas": [x for x in (prevista(t) for t in pendentes) if x],
        "atualizadoEm": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def reais(v):
    if v is None:
        return "?"
    return "R$ " + ("%.2f" % float(v)).replace(".", ",")


def ler_saida():
    if not os.path.exists(SAIDA):
        return {"transacoes": []}
    with open(SAIDA, encoding="utf-8") as f:
        texto = f.read().strip()
    i = texto.find(PREFIXO)
    if i == -1:
        return {"transacoes": []}
    texto = texto[i + len(PREFIXO):].rstrip(";")
    try:
        return json.loads(texto)
    except ValueError:
        return {"transacoes": []}


def gravar_saida(dados):
    tmp = SAIDA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("// Gerado pelo financas_pluggy.py - NAO publique, tem seus dados bancarios.\n")
        f.write(PREFIXO + json.dumps(dados, ensure_ascii=False) + ";\n")
    os.replace(tmp, SAIDA)


# -------------------------------------------------------------------- main

# ---------------------------------------------------------------- conectar
#
# A API do Pluggy não lista os itens de uma aplicação: o itemId só existe no
# fim de uma conexão. Então o script faz a conexão: pede um connect token com
# as suas credenciais, abre no navegador a janela oficial do Pluggy (Pluggy
# Connect), você escolhe o MeuPluggy, e o itemId que a janela devolve vai
# direto para o financas_config.txt.

PLUGGY_CONNECT_JS = "https://cdn.pluggy.ai/pluggy-connect/v2.14.2/pluggy-connect.js"
PLUGGY_CONNECT_JS_RESERVA = "https://cdn.pluggy.ai/pluggy-connect/latest/pluggy-connect.js"

PAGINA_CONECTAR = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conectar ao Meu Pluggy</title>
<style>
 body { font: 16px/1.5 system-ui, sans-serif; max-width: 560px; margin: 40px auto; padding: 0 16px; color: #1b1b1b; background: #fafaf8; }
 h1 { font-size: 22px; } .caixa { background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 16px 20px; }
 button { font: inherit; padding: 8px 16px; border-radius: 8px; border: 0; background: #6d1fb8; color: #fff; cursor: pointer; }
 .ok { color: #006300; font-weight: 600; } .erro { color: #b42d2d; font-weight: 600; }
</style></head><body>
<h1>Conectar ao Meu Pluggy &mdash; __NOME__</h1>
<div class="caixa">
 <ol>
  <li>Na janela do Pluggy, aceite os termos e procure <strong>MeuPluggy</strong> na lista.</li>
  <li>Entre com a sua conta do <strong>Meu Pluggy</strong> (a de meu.pluggy.ai, onde o Nubank já está conectado).</li>
  <li>Quando terminar, esta página avisa e o itemId vai sozinho para o financas_config.txt.</li>
 </ol>
 <p id="estado">Abrindo a janela do Pluggy&hellip;</p>
 <p><button id="abrir" hidden>Abrir de novo</button></p>
</div>
<script>
var TOKEN = __TOKEN__, SEGREDO = __SEGREDO__;
var estado = document.getElementById("estado"), abrir = document.getElementById("abrir");
function avisar(caminho, dados) {
  return fetch("/" + SEGREDO + "/" + caminho, { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados) });
}
function classe() { return window.PluggyConnect && (window.PluggyConnect.PluggyConnect || window.PluggyConnect); }
function iniciar() {
  var C = classe();
  if (!C) { estado.className = "erro"; estado.textContent = "Não consegui carregar a janela do Pluggy (sem internet ou bloqueador de anúncios?)."; return; }
  abrir.hidden = true;
  new C({
    connectToken: TOKEN,
    includeSandbox: false,
    onSuccess: function (dados) {
      var item = (dados && dados.item) || dados || {};
      estado.className = "ok";
      estado.textContent = "Conectado! Gravando o itemId " + item.id + "… pode fechar esta aba.";
      avisar("pronto", { itemId: item.id, conector: item.connector && item.connector.name, status: item.status });
    },
    onError: function (erro) {
      estado.className = "erro";
      estado.textContent = "O Pluggy avisou: " + ((erro && erro.message) || "erro desconhecido") + ". Tente de novo.";
      abrir.hidden = false;
      avisar("erro", { mensagem: erro && erro.message });
    },
    onClose: function () { if (!estado.className) { estado.textContent = "A janela foi fechada antes de terminar."; abrir.hidden = false; } }
  }).init().catch(function (e) { estado.className = "erro"; estado.textContent = "Erro ao abrir: " + e; abrir.hidden = false; });
}
abrir.onclick = function () { estado.className = ""; estado.textContent = "Abrindo…"; iniciar(); };
var s = document.createElement("script");
s.src = __JS__;
s.onload = iniciar;
s.onerror = function () {
  var r = document.createElement("script");
  r.src = __JS_RESERVA__; r.onload = iniciar;
  r.onerror = function () { estado.className = "erro"; estado.textContent = "Não consegui baixar a janela do Pluggy (cdn.pluggy.ai)."; };
  document.head.appendChild(r);
};
document.head.appendChild(s);
</script></body></html>
"""


def gravar_item_no_config(p, item_id):
    """Põe o itemId na linha pessoaN do config. Valor que não é itemId (um
    nome, por exemplo) é trocado; itemId que já estava fica, e o novo entra
    depois de uma vírgula (mais de um banco por pessoa)."""
    linhas = ler_texto(CONFIG).splitlines()
    padrao = re.compile(r"^\s*" + p + r"\s*=", re.I)
    for n, linha in enumerate(linhas):
        if padrao.match(linha):
            atuais = [x.strip() for x in limpar_valor(linha.split("=", 1)[1]).split(",")]
            atuais = [x for x in atuais if UUID.match(x) and x != item_id]
            linhas[n] = "%s = %s" % (p, ", ".join(atuais + [item_id]))
            break
    else:
        linhas.append("%s = %s" % (p, item_id))
    with open(CONFIG, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def conectar(p, abrir=webbrowser.open, espera=900):
    cfg = ler_chaves()
    api = Pluggy(*credenciais(cfg, p))
    token = api.connect_token(p)
    segredo = secrets.token_urlsafe(16)   # só a página que eu abri sabe o caminho
    resultado = {}
    terminou = threading.Event()
    nome = "Pessoa 1 (azul)" if p == "pessoa1" else "Pessoa 2 (laranja)"
    pagina = (PAGINA_CONECTAR.replace("__NOME__", nome)
              .replace("__TOKEN__", json.dumps(token)).replace("__SEGREDO__", json.dumps(segredo))
              .replace("__JS_RESERVA__", json.dumps(PLUGGY_CONNECT_JS_RESERVA))
              .replace("__JS__", json.dumps(PLUGGY_CONNECT_JS))).encode("utf-8")

    class Pagina(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _responder(self, codigo, corpo=b"", tipo="text/plain; charset=utf-8"):
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            if self.path == "/" + segredo:
                return self._responder(200, pagina, "text/html; charset=utf-8")
            self._responder(404)

        def do_POST(self):
            if self.path not in ("/%s/pronto" % segredo, "/%s/erro" % segredo):
                return self._responder(404)
            try:
                dados = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            except ValueError:
                return self._responder(400)
            if self.path.endswith("/pronto"):
                resultado.update(dados)
                terminou.set()
            else:
                print("  O Pluggy avisou: %s" % (dados.get("mensagem") or "erro"))
            self._responder(200, b"ok")

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Pagina)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/%s" % (srv.server_port, segredo)
    print("Abrindo o navegador para conectar a %s." % nome)
    print("Se não abrir sozinho, copie este endereço no navegador:\n  %s\n" % url)
    print("Na janela do Pluggy: escolha MeuPluggy e entre com a sua conta do Meu Pluggy.")
    print("Esperando (até %d minutos; Ctrl+C cancela)..." % (espera // 60))
    abrir(url)
    try:
        if not terminou.wait(espera):
            raise Erro("Passou o tempo e a conexão não terminou. Rode de novo quando quiser.")
    finally:
        srv.shutdown()

    item_id = str(resultado.get("itemId") or "")
    if not UUID.match(item_id):
        raise Erro("A janela do Pluggy terminou sem um itemId válido (%r)." % item_id)
    gravar_item_no_config(p, item_id)
    print("\nConectado: %s (%s)." % (resultado.get("conector") or "conexão", item_id))
    print("itemId gravado em %s = ... no %s." % (p, os.path.basename(CONFIG)))
    print("Agora confira com:  python financas_pluggy.py --testar")
    return item_id


def principal(argv=None):
    ap = argparse.ArgumentParser(description="Baixa as transações das duas contas pelo Pluggy.")
    ap.add_argument("--dias", type=int, default=0,
                    help="quantos dias para trás buscar (padrão: desde a última vez, ou 365)")
    ap.add_argument("--testar", action="store_true", help="só lista as contas encontradas")
    ap.add_argument("--conectar", choices=("pessoa1", "pessoa2"),
                    help="abre a janela do Pluggy, conecta o MeuPluggy e grava o itemId no config")
    ap.add_argument("--atualizar", action="store_true",
                    help="pede ao Pluggy para buscar dados novos no banco antes de baixar")
    a = ap.parse_args(argv)

    if a.conectar:
        conectar(a.conectar)
        return 0

    cfg = ler_config()
    apis = {}    # uma sessão por par de credenciais
    anterior = ler_saida()
    por_id = {t["id"]: t for t in anterior.get("transacoes", [])}

    hoje = dt.date.today()
    if a.dias:
        desde = hoje - dt.timedelta(days=a.dias)
    elif any(t["data"] <= hoje.isoformat() for t in por_id.values()):
        # volta 10 dias além da última transação: o banco ainda ajusta as
        # recentes. Só conta até hoje - parcela futura do cartão não vale.
        ultima = max(t["data"] for t in por_id.values() if t["data"] <= hoje.isoformat())
        desde = dt.date.fromisoformat(ultima) - dt.timedelta(days=10)
    else:
        desde = hoje - dt.timedelta(days=365)

    novas = 0
    cartoes = {c["conta"]: c for c in anterior.get("cartoes", []) if c.get("conta")}
    for item_id, (pessoa, cred) in cfg["itens"].items():
        nome = "Pessoa 1" if pessoa == "p1" else "Pessoa 2"
        if cred not in apis:
            apis[cred] = Pluggy(*cred)
        api = apis[cred]
        if a.atualizar:
            print("  %s: pedindo atualização ao banco..." % nome)
            try:
                st = api.atualizar_item(item_id)
            except Erro as e:
                # O conector MeuPluggy não aceita atualizar pela API: quem
                # atualiza é o próprio Meu Pluggy. Segue com o que já existe.
                st = "não aceito (%s)" % str(e)[:80]
            if st not in ("UPDATED",):
                print("    status: %s (sigo com o que já existe)" % st)
        it = api.item(item_id)
        banco = (it.get("connector") or {}).get("name", "?")
        status = it.get("status", "?")
        print("%s - %s (status %s)" % (nome, banco, status))
        if status in ("LOGIN_ERROR", "OUTDATED", "WAITING_USER_INPUT"):
            print("    ! A conexão pede atenção no Pluggy (reautorizar o Open Finance).")
        for c in api.contas(item_id):
            tipo = "cartao" if (c.get("type") or "").upper() == "CREDIT" else "conta"
            print("    %-6s %s" % ("cartão" if tipo == "cartao" else "conta", c.get("name") or c.get("number") or c.get("id")))
            if tipo == "cartao":
                cd = c.get("creditData") or {}
                print("           limite %s, disponível %s, fatura vence %s"
                      % (reais(cd.get("creditLimit")), reais(cd.get("availableCreditLimit")),
                         data10(cd.get("balanceDueDate")) or "?"))
            if a.testar:
                continue
            # no cartão, até um ano para a frente: parcelas futuras que o banco já informa
            ate = hoje + dt.timedelta(days=400) if tipo == "cartao" else hoje
            lista = api.transacoes(c["id"], desde.isoformat(), ate.isoformat())
            n, pendentes = 0, []
            for t in lista:
                if tipo == "cartao" and (t.get("status") or "").upper() == "PENDING":
                    pendentes.append(t)
                x = converter(t, pessoa, tipo)
                if not x:
                    continue
                if x["id"] not in por_id:
                    n += 1
                por_id[x["id"]] = x
            novas += n
            print("           %d transações no período, %d novas" % (len(lista), n))
            if tipo == "cartao":
                cartoes[c["id"]] = dados_do_cartao(api, c, pessoa, pendentes)
                print("           %d faturas fechadas, %d lançamentos previstos"
                      % (len(cartoes[c["id"]]["faturas"]), len(cartoes[c["id"]]["previstas"])))

    if a.testar:
        print("\nCredenciais e conexões OK.")
        return 0
    todas = sorted(por_id.values(), key=lambda t: t["data"], reverse=True)
    gravar_saida({
        "geradoEm": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "transacoes": todas,
        "cartoes": list(cartoes.values()),
    })
    print("\n%d novas. %s tem %d transações%s."
          % (novas, os.path.basename(SAIDA), len(todas),
             " e os dados de %d cartão(ões)" % len(cartoes) if cartoes else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except Erro as e:
        print("\n" + str(e))
        sys.exit(1)

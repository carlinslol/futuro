# -*- coding: utf-8 -*-
"""
financas_pluggy.py contra um Pluggy falso, rodando aqui mesmo.

O que precisa dar certo: o sinal (DEBIT é gasto, CREDIT é entrada, nos dois
tipos de conta), a paginação, compra pendente ficar de fora, e rodar duas
vezes não duplicar nem perder o que já estava no financas-dados.js.
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from urllib.parse import urlparse, parse_qs

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import financas_pluggy as F

falhas = []


def ok(c, nome, extra=""):
    print("  [%s] %-58s %s" % ("ok" if c else "FALHA", nome, extra))
    if not c:
        falhas.append(nome)


CONTAS = {
    "aaaaaaaa-0000-4000-8000-00000000000a": [{"id": "ca", "type": "CREDIT", "name": "Nubank cartão"},
               {"id": "ba", "type": "BANK", "name": "Nubank conta"}],
    "bbbbbbbb-0000-4000-8000-00000000000b": [{"id": "cb", "type": "CREDIT", "name": "Nubank cartão"}],
}
TRANS = {
    # cartão: 3 páginas de 1 para testar a paginação
    "ca": [
        {"id": "t1", "date": "2026-10-01T12:00:00.000Z", "description": "IFOOD", "amount": 50.0, "type": "DEBIT", "category": "Food delivery"},
        {"id": "t2", "date": "2026-10-02T12:00:00.000Z", "description": "Pagamento recebido", "amount": -900.0, "type": "CREDIT"},
        {"id": "t3", "date": "2026-10-03T12:00:00.000Z", "description": "Compra pendente", "amount": 10.0, "type": "DEBIT", "status": "PENDING"},
    ],
    "ba": [
        {"id": "t4", "date": "2026-10-04T00:00:00.000Z", "description": "Salário", "amount": 5000.0, "type": "CREDIT"},
        {"id": "t5", "date": "2026-10-05T00:00:00.000Z", "description": "Pix aluguel", "amount": -1800.0, "type": "DEBIT"},
    ],
    "cb": [
        {"id": "t6", "date": "2026-10-06T00:00:00.000Z", "description": "Compra USD", "amount": 10.0,
         "amountInAccountCurrency": 55.3, "type": "DEBIT"},
    ],
}
pedidos = []
# Como no plano grátis (Meu Pluggy): cada titular tem a própria aplicação, e
# cada aplicação só enxerga os itens do próprio titular.
APPS = {("id-a", "segredo-a"): "chave-a", ("id-b", "segredo-b"): "chave-b"}
DONO = {"aaaaaaaa-0000-4000-8000-00000000000a": "chave-a", "bbbbbbbb-0000-4000-8000-00000000000b": "chave-b", "ca": "chave-a", "ba": "chave-a", "cb": "chave-b"}


class Falso(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, codigo, obj):
        b = json.dumps(obj).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/connect_token":
            if self.headers.get("X-API-KEY") not in APPS.values():
                return self._json(403, {"message": "sem chave"})
            pedidos.append(("/connect_token", corpo))
            return self._json(200, {"accessToken": "token-de-conexao-" + self.headers["X-API-KEY"]})
        chave = APPS.get((corpo.get("clientId"), corpo.get("clientSecret")))
        if self.path == "/auth" and chave:
            return self._json(200, {"apiKey": chave})
        self._json(401, {"message": "credenciais"})

    def do_PATCH(self):
        # o conector MeuPluggy não deixa atualizar pela API
        self._json(400, {"message": "MeuPluggy items cannot be updated"})

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        alvo = u.path[7:] if u.path.startswith("/items/") else q.get("itemId") or q.get("accountId")
        if self.headers.get("X-API-KEY") not in APPS.values() or DONO.get(alvo) != self.headers.get("X-API-KEY"):
            return self._json(403, {"message": "item de outro titular"})
        pedidos.append((u.path, q))
        if u.path.startswith("/items/"):
            return self._json(200, {"id": u.path[7:], "status": "UPDATED", "connector": {"name": "Nubank"}})
        if u.path == "/accounts":
            return self._json(200, {"results": CONTAS.get(q["itemId"], [])})
        if u.path == "/transactions":   # como o Pluggy de verdade hoje
            return self._json(410, {"message": "This endpoint is deprecated. Use GET /v2/transactions "
                                               "with cursor pagination instead.", "code": 410})
        if u.path == "/v2/transactions":
            lista = TRANS[q["accountId"]]
            if q["accountId"] == "ca":
                # uma por página, e o "next" de cada página num formato diferente:
                # link completo, só a query, e os cursores com + / = (base64)
                cursores = [None, "pag+2/aa==", "pag+3/bb=="]
                p = cursores.index(q.get("after")) if q.get("after") in cursores else -1
                if p < 0:
                    return self._json(400, {"message": "cursor inválido: %r" % q.get("after")})
                prox = None
                if p == 0:
                    prox = "/v2/transactions?accountId=ca&after=" + urllib.parse.quote(cursores[1], safe="")
                elif p == 1:
                    prox = "?accountId=ca&after=" + urllib.parse.quote(cursores[2], safe="")
                return self._json(200, {"results": lista[p:p + 1], "next": prox})
            if q["accountId"] == "ba" and len(lista) > 1:
                # o cursor puro, sem link nenhum
                if q.get("after") == "cru+1/=":
                    return self._json(200, {"results": lista[1:], "next": None})
                return self._json(200, {"results": lista[:1], "next": "cru+1/="})
            return self._json(200, {"results": lista, "next": None})
        self._json(404, {})


srv = HTTPServer(("127.0.0.1", 0), Falso)
threading.Thread(target=srv.serve_forever, daemon=True).start()
F.API = "http://127.0.0.1:%d" % srv.server_port
for k in ("PLUGGY_CLIENT_ID", "PLUGGY_CLIENT_SECRET", "HTTP_PROXY", "http_proxy"):
    os.environ.pop(k, None)
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1"

tmp = tempfile.mkdtemp()
F.CONFIG = os.path.join(tmp, "financas_config.txt")
F.SAIDA = os.path.join(tmp, "financas-dados.js")


def rodar(*args):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        try:
            cod = F.principal(list(args))
        except F.Erro as e:
            print(e)
            cod = 1
    return cod, saida.getvalue()


print("\n=== configuração ===")
cod, txt = rodar()
ok(cod == 1 and os.path.exists(F.CONFIG), "primeira vez cria o financas_config.txt")
cod, txt = rodar()
ok(cod == 1 and "itemId" in txt, "config vazio dá mensagem clara", txt.strip()[:60])
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("pessoa1 = aaaaaaaa-0000-4000-8000-00000000000a\npessoa1_client_id = id-a\npessoa1_client_secret = errado\n")
cod, txt = rodar()
ok(cod == 1 and "recusou" in txt, "credencial errada é explicada", txt.strip()[:60])
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("pessoa1 = aaaaaaaa-0000-4000-8000-00000000000a\npessoa1_client_id = id-a\npessoa1_client_secret = segredo-a\npessoa2 = bbbbbbbb-0000-4000-8000-00000000000b\n")
cod, txt = rodar()
ok(cod == 1 and "pessoa2_client_id" in txt, "pessoa sem credencial é apontada", txt.strip()[:60])
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("pessoa1 = Brenno\npessoa1_client_id = id-a\npessoa1_client_secret = segredo-a\n")
pedidos.clear()
cod, txt = rodar()
ok(cod == 1 and "não é um itemId" in txt and not pedidos, "nome no lugar do itemId: avisa sem chamar o Pluggy", txt.strip().splitlines()[0])
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("# comentário\n"
            "pessoa1 = aaaaaaaa-0000-4000-8000-00000000000a\npessoa1_client_id = id-a\npessoa1_client_secret = segredo-a\n"
            "pessoa2 = bbbbbbbb-0000-4000-8000-00000000000b\npessoa2_client_id = id-b\npessoa2_client_secret = segredo-b\n")

print("\n=== config escrito do jeito que der ===")
texto = ('pessoa1 = "aaaaaaaa-0000-4000-8000-00000000000a"\npessoa1_client_id = "id-a"\npessoa1_client_secret = <segredo-a>\n'
         "pessoa2 = 'bbbbbbbb-0000-4000-8000-00000000000b'\npessoa2_client_id = id-b\npessoa2_client_secret =   segredo-b   \n")
for nome, dados in (("aspas e <> em volta", texto.encode("utf-8")),
                    ("Bloco de Notas 'Unicode' (UTF-16)", texto.encode("utf-16")),
                    ("UTF-8 com BOM", b"\xef\xbb\xbf" + texto.encode("utf-8")),
                    ("ANSI com acento no comentário", ("# configuração\n" + texto).encode("cp1252"))):
    with open(F.CONFIG, "wb") as f:
        f.write(dados)
    cod, txt = rodar("--testar")
    ok(cod == 0 and "OK" in txt, "config lido: " + nome, txt.strip().splitlines()[-1][:50])
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("# comentário\n"
            "pessoa1 = aaaaaaaa-0000-4000-8000-00000000000a\npessoa1_client_id = id-a\npessoa1_client_secret = segredo-a\n"
            "pessoa2 = bbbbbbbb-0000-4000-8000-00000000000b\npessoa2_client_id = id-b\npessoa2_client_secret = segredo-b\n")

print("\n=== --testar e --atualizar ===")
cod, txt = rodar("--testar")
ok(cod == 0 and "OK" in txt and not os.path.exists(F.SAIDA), "--testar não grava nada")
ok(txt.count("Nubank") >= 2, "dois titulares, cada um com a própria aplicação")
cod, txt = rodar("--testar", "--atualizar")
ok(cod == 0 and "sigo com o que já existe" in txt, "MeuPluggy recusando atualizar não derruba o script", txt.count("sigo"))

print("\n=== sincronizar ===")
cod, txt = rodar("--dias", "30")
ok(cod == 0 and os.path.exists(F.SAIDA), "grava o financas-dados.js", txt.strip().splitlines()[-1])
texto = open(F.SAIDA, encoding="utf-8").read()
ok(F.PREFIXO in texto, "arquivo é um .js que o HTML lê por <script src>")
dados = F.ler_saida()
por = {t["id"]: t for t in dados["transacoes"]}
ok(set(por) == {"t1", "t2", "t4", "t5", "t6"}, "paginação ok e pendente fica de fora", sorted(por))
ok(por["t1"]["valor"] == 50 and por["t1"]["tipo"] == "cartao" and por["t1"]["pessoa"] == "p1", "compra no cartão = gasto positivo")
ok(por["t2"]["valor"] == -900, "pagamento recebido no cartão = negativo")
ok(por["t4"]["valor"] == -5000 and por["t4"]["tipo"] == "conta", "salário na conta = negativo")
ok(por["t5"]["valor"] == 1800, "saída da conta = gasto positivo (amount negativo no Pluggy)")
ok(por["t6"]["valor"] == 55.3 and por["t6"]["pessoa"] == "p2", "compra em dólar usa o valor em reais")
ok(por["t1"]["data"] == "2026-10-01" and por["t1"]["categoriaPluggy"] == "Food delivery", "data e categoria")

print("\n=== cursor do /v2/transactions ===")
for entrada, esperado in (
        ("/v2/transactions?accountId=x&after=a%2Bb%2Fc%3D%3D", "a+b/c=="),
        ("https://api.pluggy.ai/v2/transactions?after=a+b/c==&accountId=x", "a+b/c=="),
        ("?accountId=x&after=abc", "abc"),
        ("after=abc&accountId=x", "abc"),
        ("abc+/=", "abc+/="),
        (None, None), ("", None), ("/v2/transactions?accountId=x", None)):
    ok(F.cursor_seguinte(entrada) == esperado, "next %r -> %r" % (entrada, esperado), F.cursor_seguinte(entrada))
v2 = [q for p, q in pedidos if p == "/v2/transactions"]
ok(v2 and all("dateFrom" in q and "dateTo" in q for q in v2), "pede com dateFrom/dateTo")
ok(not any(p == "/transactions" for p, q in pedidos), "não usa mais o /transactions antigo (410)")

print("\n=== rodar de novo ===")
TRANS["ba"].append({"id": "t7", "date": "2026-10-08T00:00:00.000Z", "description": "Padaria", "amount": -12.0, "type": "DEBIT"})
TRANS["cb"] = []          # o período novo não traz mais a t6...
pedidos.clear()
cod, txt = rodar()
dados = F.ler_saida()
ids = [t["id"] for t in dados["transacoes"]]
ok(len(ids) == len(set(ids)) == 6, "não duplica e não perde o que já tinha", ids)
ok("1 novas" in txt, "conta só as novas", txt.strip().splitlines()[-1])
desde = [q["dateFrom"] for p, q in pedidos if p == "/v2/transactions"][0]
ok(desde == "2026-09-26", "incremental: 10 dias antes da última transação", desde)

print("\n=== só uma pessoa neste computador ===")
with open(F.CONFIG, "w", encoding="utf-8") as f:
    f.write("pessoa1 =\npessoa2 = bbbbbbbb-0000-4000-8000-00000000000b\npessoa2_client_id = id-b\npessoa2_client_secret = segredo-b\n")
TRANS["cb"] = [{"id": "t8", "date": "2026-10-09T00:00:00.000Z", "description": "Farmácia", "amount": 30.0, "type": "DEBIT"}]
cod, txt = rodar()
dados = F.ler_saida()
ok(cod == 0 and any(t["id"] == "t8" and t["pessoa"] == "p2" for t in dados["transacoes"]),
   "cada um pode rodar só com os próprios dados", txt.strip().splitlines()[-1])

print("\n=== --conectar ===")
import urllib.request as U
NOVO = "cccccccc-0000-4000-8000-00000000000c"
with open(F.CONFIG, "w", encoding="utf-16") as f:   # salvo como "Unicode" pelo Bloco de Notas
    f.write("# meu config\npessoa1 = Brenno\npessoa1_client_id = id-a\npessoa1_client_secret = segredo-a\n"
            "pessoa2 =\n")
visto = {}


def navegador(url, item=NOVO):
    # faz o papel do navegador: abre a página e, como a janela do Pluggy faria, avisa o itemId
    def ir():
        pagina = U.urlopen(url).read().decode("utf-8")
        visto["pagina"] = pagina
        U.urlopen(U.Request(url + "/pronto", data=json.dumps({"itemId": item, "conector": "MeuPluggy"}).encode(),
                            headers={"Content-Type": "application/json"}, method="POST")).read()
    threading.Thread(target=ir).start()
    return True


pedidos.clear()
saida = io.StringIO()
with contextlib.redirect_stdout(saida):
    got = F.conectar("pessoa1", abrir=navegador, espera=10)
ok(got == NOVO, "--conectar devolve o itemId da janela do Pluggy")
ok("token-de-conexao-chave-a" in visto.get("pagina", ""), "a página leva o connect token da aplicação da pessoa")
ok(("/connect_token", {"options": {"clientUserId": "pessoa1"}}) in pedidos, "connect token pedido à API")
cfg = F.ler_chaves()
ok(cfg["pessoa1"] == NOVO and cfg["pessoa1_client_id"] == "id-a" and "# meu config" in F.ler_texto(F.CONFIG),
   "nome trocado pelo itemId, resto do config intacto", cfg["pessoa1"])
NOVO2 = "dddddddd-0000-4000-8000-00000000000d"
with contextlib.redirect_stdout(io.StringIO()):
    F.conectar("pessoa1", abrir=lambda u: navegador(u, NOVO2), espera=10)
ok(F.ler_chaves()["pessoa1"] == NOVO + ", " + NOVO2, "segundo banco entra depois de vírgula")
cod = None
try:
    with contextlib.redirect_stdout(io.StringIO()):
        F.conectar("pessoa2", abrir=lambda u: True, espera=1)
except F.Erro as e:
    cod = str(e)
ok(cod and "Faltam pessoa2_client_id" in cod, "sem credencial da pessoa: erro claro antes de abrir nada", cod)
url_ruim = {}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        F.conectar("pessoa1", abrir=lambda u: url_ruim.setdefault("u", u) and False, espera=1)
except F.Erro as e:
    cod = str(e)
ok("tempo" in cod, "ninguém conectou: desiste com aviso", cod[:40])
r404 = None
try:
    U.urlopen(url_ruim["u"].rsplit("/", 1)[0] + "/outro-caminho")
except Exception as e:
    r404 = str(e)
ok(r404 is not None, "servidor local fechado depois")

srv.shutdown()
print("\n" + ("%d FALHA(S)" % len(falhas) if falhas else "tudo certo"))
sys.exit(1 if falhas else 0)

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

Só usa a biblioteca padrão do Python: nada para instalar.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PASTA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(PASTA, "financas_config.txt")
SAIDA = os.path.join(PASTA, "financas-dados.js")
PREFIXO = "window.FINANCAS_PLUGGY = "
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
# itemId: o da conexão MeuPluggy (ou de cada banco). Vários: separe por vírgula.
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
"""


class Erro(Exception):
    pass


# ------------------------------------------------------------------ config

def ler_config():
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            f.write(MODELO_CONFIG)
        raise Erro("Criei o %s. Preencha as credenciais do Pluggy e os itemIds "
                   "e rode de novo." % os.path.basename(CONFIG))
    cfg = {}
    with open(CONFIG, encoding="utf-8-sig") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            cfg[k.strip().lower()] = v.strip()
    geral = (os.environ.get("PLUGGY_CLIENT_ID") or cfg.get("client_id", ""),
             os.environ.get("PLUGGY_CLIENT_SECRET") or cfg.get("client_secret", ""))
    itens = {}   # itemId -> (pessoa, (client_id, client_secret))
    for p in ("pessoa1", "pessoa2"):
        ids = [x.strip() for x in cfg.get(p, "").split(",") if x.strip()]
        if not ids:
            continue
        # As credenciais da própria pessoa (Meu Pluggy, uma por titular); se
        # não houver, as gerais (plano pago, uma aplicação para os dois).
        cred = (cfg.get(p + "_client_id", ""), cfg.get(p + "_client_secret", ""))
        if not all(cred):
            cred = geral
        if not all(cred):
            raise Erro("Faltam %s_client_id e %s_client_secret no %s."
                       % (p, p, os.path.basename(CONFIG)))
        for i in ids:
            itens[i] = ("p1" if p == "pessoa1" else "p2", cred)
    if not itens:
        raise Erro("Nenhum itemId em pessoa1/pessoa2 no %s." % os.path.basename(CONFIG))
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
        pagina, todas = 1, []
        while True:
            r = self._pedir("GET", "/transactions", consulta={
                "accountId": conta_id, "from": desde, "to": ate,
                "pageSize": 500, "page": pagina})
            todas.extend(r.get("results", []))
            if pagina >= int(r.get("totalPages") or 1):
                return todas
            pagina += 1


# ----------------------------------------------------------- transformação

def converter(t, pessoa, tipo):
    """Transação do Pluggy -> formato do app (valor positivo = gasto).

    O sinal vem do campo type, não do amount: no Pluggy o sinal do amount
    muda entre conta e cartão, e o type (DEBIT = saiu, CREDIT = entrou) não."""
    if (t.get("status") or "POSTED").upper() == "PENDING":
        return None  # compra ainda não fechada: o id pode mudar quando fechar
    valor = t.get("amountInAccountCurrency")
    if valor is None:
        valor = t.get("amount")
    if valor is None:
        return None
    valor = abs(float(valor))
    if (t.get("type") or "").upper() == "CREDIT":
        valor = -valor
    data = str(t.get("date") or "")[:10]
    if len(data) != 10:
        return None
    desc = t.get("description") or t.get("descriptionRaw") or "(sem descrição)"
    return {
        "id": t["id"],
        "pessoa": pessoa,
        "tipo": tipo,
        "data": data,
        "descricao": desc,
        "valor": round(valor, 2),
        "categoriaPluggy": t.get("category") or "",
    }


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

def principal(argv=None):
    ap = argparse.ArgumentParser(description="Baixa as transações das duas contas pelo Pluggy.")
    ap.add_argument("--dias", type=int, default=0,
                    help="quantos dias para trás buscar (padrão: desde a última vez, ou 365)")
    ap.add_argument("--testar", action="store_true", help="só lista as contas encontradas")
    ap.add_argument("--atualizar", action="store_true",
                    help="pede ao Pluggy para buscar dados novos no banco antes de baixar")
    a = ap.parse_args(argv)

    cfg = ler_config()
    apis = {}    # uma sessão por par de credenciais
    anterior = ler_saida()
    por_id = {t["id"]: t for t in anterior.get("transacoes", [])}

    hoje = dt.date.today()
    if a.dias:
        desde = hoje - dt.timedelta(days=a.dias)
    elif por_id:
        # volta 10 dias além da última transação: o banco ainda ajusta as recentes
        ultima = max(t["data"] for t in por_id.values())
        desde = dt.date.fromisoformat(ultima) - dt.timedelta(days=10)
    else:
        desde = hoje - dt.timedelta(days=365)

    novas = 0
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
            if a.testar:
                continue
            lista = api.transacoes(c["id"], desde.isoformat(), hoje.isoformat())
            n = 0
            for t in lista:
                x = converter(t, pessoa, tipo)
                if not x:
                    continue
                if x["id"] not in por_id:
                    n += 1
                por_id[x["id"]] = x
            novas += n
            print("           %d transações no período, %d novas" % (len(lista), n))

    if a.testar:
        print("\nCredenciais e conexões OK.")
        return 0
    todas = sorted(por_id.values(), key=lambda t: t["data"], reverse=True)
    gravar_saida({
        "geradoEm": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "transacoes": todas,
    })
    print("\n%d novas. %s tem %d transações. Abra o financas.html."
          % (novas, os.path.basename(SAIDA), len(todas)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except Erro as e:
        print("\n" + str(e))
        sys.exit(1)

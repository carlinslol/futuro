# Finanças do Casal

Controle de gastos para duas pessoas com Nubank que **não moram juntas**: cada
um usa no próprio celular, os dois veem e editam os mesmos dados. O app junta
o **cartão** e a **conta** de cada um, separa o que é pessoal do que é do
casal e diz **quem deve quanto para quem**.

```
 celular dele ─┐                                   ┌─ celular dela
   (cifra)     ├──►  Worker na sua Cloudflare  ◄───┤   (cifra)
               │     guarda só texto embaralhado   │
```

Os dados são **criptografados no celular** com a *senha do casal* antes de
sair do aparelho (AES-GCM, chave derivada da senha por PBKDF2). O servidor
guarda um texto embaralhado e nunca vê a senha: nem você, pelo painel da
Cloudflare, consegue ler um gasto lá.

---

## Montar (uma vez, uns 10 minutos)

Precisa de uma conta Cloudflare (o plano grátis
basta) e do `wrangler` (`npm install -g wrangler`).

1. Dê duplo clique em **`publicar.bat`**. Na primeira vez ele
   cria o banco, a tabela e publica. No fim ele mostra o endereço, algo como
   `https://financas-casal.SUA-CONTA.workers.dev`.
2. Abra esse endereço no seu celular → **Configurar** → *Cada um no seu
   celular* → **Gerar** → **Conectar**.
3. **Guarde a senha** (num gerenciador de senhas, por exemplo). Sem ela não
   dá para abrir o cofre num aparelho novo, e ninguém consegue recuperar.
4. Toque em **Copiar link de convite** e mande para ela por mensagem direta.
   Ela só abre o link: o celular dela conecta sozinho no mesmo cofre.
5. Nos dois celulares: menu do navegador → **Adicionar à tela de início**.
   Vira um ícone como de app.

Pronto. A partir daí, tudo que um faz aparece para o outro em segundos
(quando o app está aberto) — ou na próxima vez que abrir.

Mudou o `financas.html`? Rode o `publicar.bat` de novo: o app vai embutido
no Worker.

---

## Como os dados entram

O Nubank **não tem API aberta para pessoa física**: a API de Open Finance
dele só atende instituições autorizadas. Sobram dois caminhos, os dois
gratuitos, e dá para usar os dois:

| Caminho | Como é | Custo |
|---|---|---|
| **Arquivo exportado** (padrão) | Cada um exporta a fatura (CSV) e o extrato (CSV ou OFX) no app do Nubank e importa no app, **do próprio celular** | Grátis |
| **Open Finance pelo Meu Pluggy** (opcional) | Cada um autoriza o próprio Nubank uma vez; um script baixa as transações e o app sobe para o cofre | Grátis para uso pessoal |

### 1. Arquivo exportado

1. Em **Configurar**, ponham o nome de vocês dois e o **nome completo como
   aparece no Pix**. É assim que o app reconhece um Pix entre vocês: ele não
   conta como gasto e entra no acerto. (Basta um fazer: sincroniza.)
2. No app do Nubank, exporte:
   - **Fatura do cartão**: Cartão de crédito → fatura do mês → *Exportar fatura* → CSV;
   - **Extrato da conta**: Conta → extrato → *Pedir extrato* → CSV (ou OFX).

   Os nomes dos menus mudam de vez em quando; se não achar, procure
   “exportar” na ajuda do app.
3. Na aba **Importar**, escolha de quem é o arquivo (o app lembra da escolha
   em cada celular) e escolha o arquivo. Ele descobre sozinho se é fatura ou
   extrato.

Reimportar o mesmo arquivo não duplica nada, nem se cada um importar o mesmo
arquivo no próprio celular. Só não misture CSV e OFX **da mesma conta**.

### 2. Open Finance pelo Meu Pluggy (opcional, grátis)

O [Meu Pluggy](https://www.pluggy.ai/meu-pluggy) é o portal gratuito do Pluggy
para uma pessoa ler os **próprios** dados bancários por API, via Open Finance
(o mesmo consentimento oficial que um banco pede a outro). Duas regras moldam
o jeito de usar com um casal:

- **É por titular.** O grátis cobre os dados de um CPF. Então **cada um** de
  vocês faz a própria conta no Meu Pluggy **e** a própria aplicação no
  dashboard do Pluggy. Não junte as duas pessoas numa aplicação só.
- **É uso pessoal, não comercial.** Um app de vocês dois, para vocês dois, é
  exatamente isso. Se um dia virar produto para outras pessoas, aí é a API paga.

Passo a passo — **cada um faz o seu**:

1. Crie a conta em <https://meu.pluggy.ai> e conecte o seu Nubank (é o fluxo
   de Open Finance: o app do Nubank abre e pede para autorizar).
2. Crie a conta em <https://dashboard.pluggy.ai>. Ela já vem com uma
   aplicação; anote o **Client ID** e o **Client Secret** dela. (O dashboard
   avisa de um teste grátis de 15 dias: é da API paga, pode ignorar.)
3. No dashboard, em *Conectar conta*, escolha o conector **MeuPluggy** e entre
   com a sua conta do Meu Pluggy. Isso gera um **itemId**: anote.
4. Mande as três coisas para quem vai rodar o script — ou rode você mesmo no
   seu computador (veja abaixo).

Depois:

5. Rode `python financas_pluggy.py` uma vez. Ele cria o `financas_config.txt`:

   ```
   pessoa1 = itemId da Pessoa 1 (cor azul no app)
   pessoa1_client_id = ...
   pessoa1_client_secret = ...

   pessoa2 = itemId da Pessoa 2 (cor laranja)
   pessoa2_client_id = ...
   pessoa2_client_secret = ...
   ```

6. Confira com `python financas_pluggy.py --testar` (lista as contas sem baixar).
7. Abra o `financas.html` **direto do computador** uma vez e conecte ao cofre
   (aberto do computador, o app pede também o endereço do Worker).
8. Daí em diante: **`sincronizar.bat`**. Ele baixa o que é novo, abre o app,
   o app importa e sobe para o cofre — e chega no celular dos dois.

**Cada um no seu computador:** como vocês não moram juntos, dá para cada um
rodar o script no próprio computador, preenchendo só a própria pessoa no
config (a outra fica em branco). Cada um sobe as próprias transações para o
cofre, e ninguém precisa entregar o Client Secret para o outro. É o jeito
mais limpo.

Opções: `--dias 365` busca o ano inteiro; `--atualizar` pede ao Pluggy para
buscar no banco antes de baixar (no conector MeuPluggy quem atualiza é o
próprio Meu Pluggy; se ele recusar, o script segue com o que já tem).

O `financas.html` aberto **pelo endereço do Worker** não lê o
`financas-dados.js`: esse arquivo tem dado bancário em claro e nunca sobe
para servidor nenhum. Quem leva os dados para o cofre é o app aberto direto
do computador onde o script rodou.

Condições e limites do Pluggy mudam: confira a
[página de preços](https://www.pluggy.ai/precos) antes. Se o grátis acabar, o
caminho 1 (arquivo exportado) continua funcionando igual.

**`financas_config.txt` e `financas-dados.js` estão no `.gitignore`.** Um tem
o segredo do Pluggy, o outro o extrato de vocês.

---

## O que o app faz

**Resumo do mês**
- quanto vocês gastaram, comparado ao mês anterior;
- o **custo real** de cada um: o que é pessoal mais a sua parte das despesas do casal;
- gastos por categoria, com **orçamento** (passou do limite, fica vermelho);
- os últimos 6 meses e os maiores gastos;
- o **acerto**: quem deve quanto para quem, já descontados os Pix entre vocês.

**Transações**: troque categoria e divisão (pessoal ou do casal) de qualquer
uma. Ao mudar a categoria, o app oferece criar uma regra para as próximas.
Dá para lançar gastos em dinheiro à mão.

**Configurar**: o cofre, nomes, divisão do casal (50/50, 60/40...),
categorias com orçamento e quais são do casal por padrão, regras e backup.

### O que não conta como gasto

- **pagamento de fatura** no extrato (as compras já estão na fatura);
- **pagamento recebido** na fatura;
- **caixinhas e RDB** (aplicação e resgate);
- **Pix entre vocês**: vão para o acerto, não para os gastos;
- **entradas** (salário, Pix recebido) aparecem separadas.

Estorno no cartão abate da categoria.

### Quando os dois mexem ao mesmo tempo

- Cada transação guarda quando foi editada: vale a edição **mais recente**.
- Apagou num celular, **some nos dois** — e não volta nem reimportando o arquivo.
- Nomes, categorias, regras e divisão andam juntos: vale o bloco mexido por último.
- Sem internet, o app funciona normal; as mudanças sobem quando a conexão voltar.

---

## Segurança, em uma lista

- A senha do casal **nunca sai do celular**. Ela gera a chave e o id do
  cofre; o servidor recebe só o id e o texto cifrado.
- O link de convite tem a senha depois do `#`, parte que o navegador não
  manda ao servidor. O app apaga a senha da barra de endereço ao abrir.
  Mesmo assim: **mande o link só para ela**.
- Senha gerada pelo app: 16 caracteres aleatórios (~79 bits). Se escolherem
  uma própria, o mínimo é 12 caracteres — e quanto mais, melhor.
- O Worker aceita no máximo `MAX_COFRES` cofres (2, no `wrangler.toml`): quem
  descobrir o endereço não consegue usar o seu Worker de depósito.
- Cada celular guarda a chave para não pedir a senha toda vez. Perdeu o
  celular? No outro aparelho: **Desconectar**, gerar senha nova, **Conectar**
  (os dados vêm junto, pela cópia local) e convidar de novo. Depois apague o
  cofre antigo, o de `atualizado` mais velho:

  ```
  wrangler d1 execute financas-casal --remote --command "SELECT id, atualizado FROM cofres"
  wrangler d1 execute financas-casal --remote --command "DELETE FROM cofres WHERE id = 'ID-DO-ANTIGO'"
  ```

---

## Arquivos

| Arquivo | O que é |
|---|---|
| `financas.html` | o app (funciona também direto do computador) |
| `publicar.bat` / `publicar.ps1` | publica o Worker (cria o banco na primeira vez) |
| `worker/` | o servidor: `index.js`, `wrangler.toml`, `schema.sql` |
| `financas_pluggy.py` | baixa as transações pelo Meu Pluggy / Pluggy (opcional) |
| `sincronizar.bat` | roda o script e abre o app |
| `exemplos/` | faturas e extratos **fictícios** para testar sem dado real |
| `financas_config.txt` | criado pelo script; **segredo** |
| `financas-dados.js` | gerado pelo script; **dados bancários** |

Testes (o `rodar_testes.bat` roda todos):

```
node testes/financas.js            leitura dos arquivos, contas, mesclagem, criptografia
node testes/financas_worker.mjs    o servidor, inclusive dois gravando ao mesmo tempo
python testes/financas_pluggy.py   o script do Pluggy contra um Pluggy falso
```

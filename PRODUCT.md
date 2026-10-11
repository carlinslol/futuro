# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Duas pessoas, um casal que **não mora junto**, ambas com Nubank (cartão e
conta). Cada uma usa o app no próprio celular, instalado como ícone na tela de
início; as duas veem e editam os mesmos dados. O app é só delas: não há outros
usuários previstos, nem agora nem depois.

O uso tem dois ritmos, e os dois importam:

- **Conferida rápida**, cada um sozinho, de passagem: quanto já foi no mês, se
  alguma categoria estourou, quanto está a fatura.
- **Revisão juntos**, de tempos em tempos, com calma (lado a lado ou à
  distância, cada um no seu celular): olhar o mês, acertar categorias e regras.

Quem mantém a parte técnica (Cloudflare, script do Pluggy, `publicar.bat`) é
uma pessoa só; a outra apenas abre o link de convite e usa o app.

## Product Purpose

Controle de gastos do casal num lugar só, juntando cartão e conta das duas
pessoas e separando o que é pessoal do que é do casal. O que mais precisa
funcionar bem, em ordem de importância igual:

1. **Orçamento do mês**: quanto já foi gasto, comparado ao mês anterior, e quais
   categorias passaram do limite, a tempo de segurar.
2. **Cartão e faturas**: fatura atual (fechamento, vencimento, mínimo),
   próximas faturas, parcelamentos em andamento e limite, sem abrir o app do
   banco.
3. **Organizar transações**: trocar categoria e divisão (pessoal ou do casal),
   criar regras a partir de uma correção, lançar gasto em dinheiro à mão.

A divisão do casal (custo real de cada um, 50/50, 60/40...) existe e continua
correta, mas não foi apontada como o trabalho principal.

Sucesso: abrir o app e entender o mês em segundos, confiar nos números sem
conferir no banco, e gastar pouco tempo arrumando transações.

## Positioning

É um app feito para estas duas pessoas e só para elas, com privacidade de
verdade: os dados são cifrados no celular com a senha do casal (AES-GCM, chave
por PBKDF2) antes de sair do aparelho, e o servidor (um Worker na Cloudflare
delas) guarda só texto embaralhado. Não depende de serviço pago nem de
terceiros lendo o extrato.

## Operating Context

- Os dados entram por **arquivo exportado do Nubank** (fatura em CSV, extrato
  em CSV ou OFX), importado do próprio celular, ou pelo **Meu Pluggy** (Open
  Finance), com um script no computador que sobe direto para o cofre, rodando
  sozinho às 08:00 e às 20:00 no Windows.
- O dado do Pluggy pode estar atrasado: o Pluggy decide quando busca no banco.
  O app mostra "dados do banco até ..." por pessoa, e transações ainda não
  fechadas aparecem como **pendente** (somam, mas só se editam depois).
- Funciona sem internet; as mudanças sobem quando a conexão volta. Edições dos
  dois ao mesmo tempo se resolvem pela mais recente.
- Abas: Resumo, Transações, Cartão, Importar, Configurar.

## Capabilities and Constraints

- Um único arquivo, `financas.html` (HTML, CSS e JS sem framework nem build),
  que também roda direto do computador e vai embutido no Worker ao publicar.
  O servidor fica em `worker/`.
- Uso principal no celular; precisa funcionar bem em tela estreita e com
  tema claro e escuro (automático pelo sistema).
- Faturas levam o nome do mês do vencimento.
- Não contam como gasto: pagamento de fatura, pagamento recebido, caixinhas e
  RDB, Pix entre os dois, entradas. Estorno abate da categoria.
- Apagar uma transação apaga nos dois celulares e ela não volta reimportando.
- O Worker aceita no máximo 2 cofres.
- Termos do app: *cofre*, *senha do casal*, *Pessoa 1* / *Pessoa 2*, *do
  casal* / *pessoal*, *custo real*, *pendente*, *fatura atual*, *próximas
  faturas*, *parcelamentos*.

## Brand Commitments

- Nome: **Clo** (também na tela de início). Antes se chamava "Finanças do Casal";
  o Worker continua com o nome técnico `financas-casal`, para o endereço não mudar.
- Mascote: **Clo**, uma calopsita desenhada a partir da calopsita de verdade do
  casal (corpo cinza, rosto e topete amarelos, bochecha laranja, faixa branca na
  asa). Ela é a marca (logo e ícone) e aparece só em momentos certos: telas
  vazias, avisos e no orçamento do mês, com o topete deitado dentro do ritmo e
  em pé quando passa. As cores dela ficam só no desenho, nunca nas cores do app.
  Nada de infantil ou gamificado: ela acompanha, os números mandam.
- Idioma: português do Brasil, em texto direto e coloquial, falando com as
  duas pessoas ("vocês").
- Cada pessoa tem uma cor fixa (Pessoa 1 azul, Pessoa 2 laranja) e a cor nunca
  aparece sozinha: todo número leva o nome ao lado.

## Evidence on Hand

- Faturas e extratos **fictícios** para testar sem dado real: `exemplos/`.
- Testes automatizados em `testes/` (leitura dos arquivos, contas, mesclagem,
  criptografia, Worker, upload, script do Pluggy).
- Dados reais das duas pessoas nunca entram no repositório
  (`financas-dados.js`, `financas_config.txt` e backups estão no `.gitignore`)
  e não devem aparecer em telas de exemplo, capturas ou textos.

## Product Principles

1. **O número tem que ser confiável.** Melhor mostrar menos do que mostrar
   algo errado; quando o dado é estimado, atrasado ou pendente, dizer isso.
2. **Entender o mês em segundos.** A conferida rápida no celular é o uso mais
   frequente: o essencial aparece primeiro, sem precisar procurar.
3. **Arrumar uma vez, valer para sempre.** Cada correção deve poder virar
   regra, para que organizar transações dê cada vez menos trabalho.
4. **Feito para estas duas pessoas.** Pode assumir Nubank, o casal e o fluxo
   delas; não precisa de onboarding genérico nem de recursos para terceiros.
5. **Privacidade não se negocia.** Nada que exponha dado em claro fora dos
   celulares e do computador de quem sincroniza.

## Accessibility & Inclusion

As cores das duas pessoas foram escolhidas para passar no teste de daltonismo
nos dois temas, e a cor nunca é a única pista (sempre há o nome ao lado).

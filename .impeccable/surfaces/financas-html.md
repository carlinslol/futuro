---
version: 1
slug: "financas-html"
primary_target: "financas.html"
related_targets: []
---

# Surface brief: financas.html (o app inteiro)

## Scope and mode

Todas as abas do app (Resumo, Transações, Cartão, Importar, Configurar), celular primeiro, desktop junto. Modo: Operate.

## Audience, job, constraints

As duas pessoas do casal, cada uma no seu celular: conferida rápida de passagem e revisão juntos de vez em quando. O Resumo abre pelo mês contra o orçamento. Nada infantil ou gamificado. O roxo pode sair; azul (Pessoa 1) e laranja (Pessoa 2) ficam, sempre com o nome ao lado. Um arquivo só, sem build, embutido no Worker; tema claro e escuro automáticos; comportamento, textos de ajuda e testes intactos.

## Direction contract

THESIS: O mês é uma folha de folhinha de parede: dá para ver de relance quanto já foi e em quais dias o dinheiro saiu do ritmo. Recusa o painel de cartões arredondados com sombra e números soltos em blocos iguais.

OWN-WORLD: Papel branco frio (não creme), tinta preta e o vermelho da folhinha, que aqui só marca o que passou do limite: dia acima do ritmo, categoria estourada, fatura vencida. Algarismos grandes em Sofia Sans Extra Condensed 800 (mês, valores principais, números dos dias); o resto em fonte do sistema com algarismos tabulares. Cantos retos, separação por fios de 1px e uma segunda camada cinza-jornal, sem sombras de cartão. Botão principal preto. Ícones em SVG de traço único.

STORY: Abrir, ler "R$ X de R$ Y, sobram Z para N dias", ver na folha os dias vermelhos, tocar num dia e ver o que saiu nele; descer para categorias, o custo de cada um e o cartão.

FIRST VIEWPORT: Topo com o nome do mês enorme em condensada (OUTUBRO 2026) e ‹ › ao lado. Logo abaixo, a frase do orçamento em algarismos grandes e a linha do ritmo ("no dia 11, o ritmo seria R$ 798"). Em seguida a folha do mês: grade de 7 colunas D S T Q Q S S, cada casa com o número do dia e o gasto do dia; hoje emoldurado, dias futuros apagados, dias acima do ritmo com o número em vermelho. No celular, barra de abas fixa embaixo; no desktop, abas no topo e a folha à esquerda com categorias e pessoas à direita.

FORM: Folhinha de parede (candidato 1 de 7 da lista ordenada; escolha do usuário sobre o sorteio, que designou o 4). Seed key 72c7fd6c. Gesto principal: o mês como folha de calendário com o gasto em cada dia, tocar no dia lista as transações dele; em Transações, os grupos por data levam cabeçalho de folhinha (número grande + dia da semana).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Unresolved

- Sem orçamento cadastrado, a folha mostra o gasto por dia sem dias vermelhos e o topo compara com o mês anterior.

## Extension: Clo (pedido do usuário, 11/10)

O app passa a se chamar **Clo** e ganha uma mascote: a calopsita Clo, chapada e de frente (rosto amarelo redondo, olhos pretos, bochechas laranja da calopsita do casal, bico triangular, topete), no estilo da referência que o usuário mandou. Inteira, ela tem corpo cinza, asas cinza-escuras com a faixa branca e pés. A cabeça é a marca (topo, favicon, ícone da tela de início). Inteira, ela aparece só em momentos certos: de pé na barra do orçamento, onde o gasto chegou (topete pequeno dentro do ritmo, alto quando passou), nas telas vazias e nos avisos. As cores dela ficam só no desenho; o mundo da folhinha não muda. Junto: escolha de tema claro/escuro/automático (botão no topo e Aparência em Configurar), salva por aparelho.

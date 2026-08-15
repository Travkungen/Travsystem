# Phoenix 15 — Reduktionscheckpoint 2026-08-15

## Grundprincip

Phoenix ska först rangordna och välja **Top 7** i varje lopp. Därefter ska en **separat reduktionsmotor** lära sig vilka hästar som kan kastas. Målet är inte maximal reduktion utan **att kasta rätt hästar**.

## Historiskt facit — speloddsrank

Verifierat historiskt experiment:

- Starter med giltigt odds: 245,976
- Lopp med giltigt odds + vinnare: 28,458
- Speloddsrank 1–3: **25,481 vinnare = 89.41 %**
- Rank 1: 61.14 %
- Rank 2: 19.35 %
- Rank 3: 8.92 %
- Rank 4–6: 8.65 %
- Rank 7: 0.89 %
- Rank 7+: 1.93 %
- Rank 8+: 1.05 %

## Phoenix Top 7

Historiskt experiment på 45,428 matchade lopp:

- Phoenix Top 1: 9,865 vinnare / 21.72 % av loppen
- Phoenix Top 3: 17,477 vinnare / 38.47 % av loppen
- Phoenix Top 5: 20,252 vinnare / 44.58 % av loppen
- Phoenix Top 7: 21,239 vinnare / 46.75 % av loppen

Tidigare backtester/utvärdering har visat att Phoenix Top 7 ska betraktas som ett mycket brett säkerhetslager; målet är att fånga omkring **98 % av relevanta vinnare** innan reduktionen.

## Värdeområdet

Phoenix 4–7 ska inte automatiskt kastas. Det är vårt primära område för att hitta värde efter att Top 7 har skapats.

I den genomförda korsanalysen för Phoenix 4–7:

- Speloddsrank 1–3: 69.35 % av Phoenix 4–7-vinnarna
- Speloddsrank 4–6: 24.40 %
- Speloddsrank 7: 2.71 %
- Speloddsrank 8+: 3.54 %
- Phoenix 4–7 + spelodds 4–7: **1,020 vinnare av 3,762 = 27.11 %**

## Reduktionsregel — arbetsversion

1. **Phoenix Top 3 = skyddszon.** Var mycket försiktig med att kasta dessa.
2. **Phoenix Top 3 + speloddsrank 1–3 = extra skydd.** Dessa ska i princip inte reduceras bort utan stark evidens.
3. **Phoenix 4–7 = värdezon.** Här ska reduktionsmotorn arbeta aktivt.
4. **Phoenix 4–7 + speloddsrank 4–7 = särskilt intressant värdeområde.**
5. **Phoenix 4–7 + speloddsrank 8+ = hårdare reduktion möjlig**, men inte automatiskt.
6. Reduktionsmotorn ska väga ihop **Phoenix-rank + speloddsrank** och lära sig vilka kombinationer som historiskt är säkra att kasta.

## Aktuellt systemexperiment 2026-08-15

Våra åtta aktuella system hade följande Phoenix Top 3-täckning:

- Phoenix Top 3 totalt: 24 hästar
- Täckta i systemen: 11
- Saknade: 13
- Täckning: **45.8 %**

Saknade Phoenix Top 3:

- V85-1: nr 7 (Phoenix #1)
- V85-2: nr 9 (Phoenix #1), nr 10 (Phoenix #3)
- V85-3: nr 10 (Phoenix #2), nr 7 (Phoenix #3)
- V85-4: nr 8 (Phoenix #2)
- V85-5: nr 4 (Phoenix #3)
- V85-6: nr 8 (Phoenix #1), nr 7 (Phoenix #2)
- V85-7: nr 2 (Phoenix #1), nr 10 (Phoenix #2)
- V85-8: nr 1 (Phoenix #1), nr 2 (Phoenix #2)

Detta visar att den aktuella reduktionen kan vara för aggressiv. Framför allt är det en varningssignal när Phoenix #1–3 kastas bort.

## Viktig lärdom

Vi ska **inte försöka göra Phoenix mer aggressiv**. Phoenix ska ge Top 7. Den separata reduktionsmotorn ska lära sig **vilka hästar som är rätt att kasta**.

Målet är därför:

> **98 %-säkerhet i Phoenix Top 7 → intelligent reduktion → behålla starka Phoenix Top 3 och marknadsstarka hästar → leta värde främst i Phoenix 4–7.**

## Nästa steg

Innan reduktionsregler ändras ska kombinationerna Phoenix-rank × speloddsrank analyseras korrekt på hela historiska materialet och därefter backtestas på out-of-sample-data. Aktuella lopp ska inte användas för att lära historiska regler.

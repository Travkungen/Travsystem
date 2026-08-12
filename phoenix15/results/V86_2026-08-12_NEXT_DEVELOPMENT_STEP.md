# Phoenix 15 — nästa utvecklingssteg efter V86 2026-08-12

## Status
V86-resultatet från Örebro 2026-08-12 är sammanställt och verifierat mot den manuellt sparade resultatlistan. Denna fil är en utvecklingscheckpoint och ändrar inte Phoenix-databasen.

## Benchmark
- Top 1: 2/8 = 25.0%
- Top 3: 4/8 = 50.0%
- Top 5: 6/8 = 75.0%
- Top 7: 8/8 = 100.0%
- Phoenix-system: 3/8 = 37.5%

## Viktig observation
Alla 8 vinnare fanns inom Phoenix Top 7. Problemet ligger därför inte primärt i Phoenix rankingens kandidatfält utan i steget där Top 7 reduceras till det faktiska V86-systemet.

Systemmissar där vinnaren låg i Top 7:
- V86-3: vinnare #6, Phoenix rank #5, system [2, 5]
- V86-4: vinnare #2, Phoenix rank #6, system [4, 7, 3]
- V86-5: vinnare #4, Phoenix rank #6, system [5, 1, 10, 2, 12]
- V86-7: vinnare #4, Phoenix rank #3, system [5, 7, 12]
- V86-8: vinnare #15, Phoenix rank #5, system [8, 14, 1, 6]

## Nästa utvecklingssteg
Bygg och testa en separat **Phoenix 15 System Selection / Protection Layer v1** ovanpå den befintliga rankingen.

Princip:
1. Låt Phoenix ranking vara oförändrad.
2. Använd Top 7 som kandidatuniversum.
3. Analysera varför rank 4–7 ibland faller bort från systemet trots att de senare vinner.
4. Inför en separat skyddslogik som kan återföra starka Top-7-kandidater till systemet när systemreduceringen annars skapar uppenbar risk.
5. Testa mot V86 2026-08-12 först som diagnostiskt fall.
6. Därefter backtestas logiken på tidigare sparade V86-resultat innan den får påverka live-system.

## Viktig spärr
Ingen ändring av Phoenix Score, Feature Engine, rankingmotorn eller den frysta baseline-koden i detta steg. Först ska System Selection / Protection Layer valideras separat.

## Mål
Förbättra systemträffsäkerheten utan att förstöra styrkan i nuvarande ranking. V86 2026-08-12 visar att Phoenix redan hade vinnaren inom Top 7 i 8/8 lopp; nästa steg är därför att göra systemkonstruktionen bättre på att behålla rätt hästar.

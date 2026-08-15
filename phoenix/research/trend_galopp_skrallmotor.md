# Phoenix research note: trend, galopp och skrällmotor

Status: RESEARCH ONLY. Ingen modelländring.

## Observation
V85-analysen visade att korrigerad Phoenix Top 7 fångade 6 av 8 vinnare och 7 av 8 andraplatser. De sju fångade tvåorna låg på rank 2, 2, 3, 3, 3, 4 och 5. Hybrid Phoenix 3000 fångade också 7 av 8 tvåor.

Slutsats: kandidatmotorn ser lovande ut. Grundmodellen ska inte byggas om på basis av en enda omgång.

## Skrällmotor
Behåll grundrankingen och Top 7 separata. Skapa en separat outsiderpool för hästar rankade 8+.

En outsider kan få extra signal från odds, trend, galopprisk, kusk/häst-form och extern AI som ATG Elli. Outsiders ska inte automatiskt flyttas upp i grundrankingen.

## Trend
Undersök senaste 3 starter mot tidigare 5, placeringstrend, prestation relativt motstånd och kusk/häst-form. Testa som separat signal innan den eventuellt blir en del av grundmodellen.

## Galopp
Undersök senaste galopp, galopp senaste 3/5/10 starter, galoppfrekvens och eventuell bana-/distansspecifik risk. Behandla främst som riskfaktor i reduktionen.

## Value Gap
Testa Phoenix sannolikhet mot marknadens sannolikhet från odds. Positiv skillnad ska identifiera hästar som inte bör reduceras bort för lätt.

## ATG Elli
Använd Elli som extern benchmark, inte som input i Phoenix ännu. Spara Phoenix grundrank, odds, vår slutrad, Elli-förslag och resultat separat.

## Arkitektur
FROZEN WAREHOUSE -> Trend/Galopp research -> Phoenix grundranking -> Odds/Market -> Value/Outsider -> Hybrid -> Reduction -> Final coupon -> Resultat/erfarenhetsbank.

## Databas
Den frysta Phoenix Warehouse-grunden är SQLite-databasen /content/drive/MyDrive/PhoenixTrav/phoenix_trav.db. Den ska öppnas READ ONLY för att inventera om galopp, trend, placering, distans, bana och kusk/tränardata redan finns. Ingen ombyggnad innan detta är kontrollerat.

## Nästa test
1. Inventera SQLite-schemat READ ONLY.
2. Identifiera galopp- och resultatfält.
3. Bygg trend/galopp i separat forskningslager.
4. Backtesta varje signal separat.
5. Testa outsiderpool rank 8+ mot odds och resultat.
6. Testa därefter hur reduktionen ska använda signalerna.

Regel: nya faktorer testas en i taget och behålls endast om historiska data visar mätbart värde.

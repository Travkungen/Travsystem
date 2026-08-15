# PHOENIX 15 — 10-TIMMARS ARBETSPIPLINE

## Syfte
Återställa en stabil Phoenix 15-arbetsmiljö utan att bygga om kärnan efter varje V85/V86-omgång. V85/V86 ska löpande sparas som erfarenhetsbank så att motorerna kan utvärderas över tid.

## Grundprincip
**Colab kör Phoenix. GitHub är teknisk backup/versionering. Drive lagrar arbetsdata/checkpoints. Historiska resultat är erfarenhetsbanken.**

En paus eller ny Colab-runtime får aldrig innebära att Phoenix börjar om.

## Arbetsflöde

1. **STARTUP** — en officiell startup-cell återställer miljön, hittar rätt databas/moduler/modell och verifierar versioner.
2. **LIVE IMPORT** — en cell hämtar dagens V85/V86 automatiskt och sparar lopp, starter, odds, streck och övriga startdata.
3. **ANALYS** — en cell kör de godkända Phoenix-motorerna och producerar gemensam ranking.
4. **TOP 7 + REDUCERING** — Top 7 tas fram och flera systempaket produceras.
5. **FACIT** — när resultatet kommer importeras det och hela omgången jämförs mot Phoenix, odds, streck, värde och systemen.
6. **ERFARENHETSBANK** — varje omgång sparas för framtida backtest och motorutvärdering.

## 10-timmars prioritering

### Pass 1 — Återställning & inventering
- Kontrollera GitHub, Phoenix 15-struktur, senaste verifierade checkpoint, databas, modeller och motorer.
- Klassificera: fungerande / behöver testas / trasigt / ska inte röras.
- Ingen modelländring.

### Pass 2 — Colab startup
- Bygg/verifiera en enda officiell startup-cell.
- Kontrollera Drive, databas, kodversion, modell, feature-set och databasanslutning.
- Runtime ska kunna startas om utan manuella gamla variabler.

### Pass 3 — Automatisk V85/V86-import
- En cell för dagens omgång.
- Säker ID-kedja mellan livedata och historiska data.
- Kontroll av lopp, starter, bana, distans, startmetod, odds och streck.

### Pass 4 — Analyspipeline
- Kör befintliga godkända motorer.
- Gemensam analys per häst.
- Phoenix Score och Phoenix Rank 1–7 som central produkt.

### Pass 5 — Bananalys
Testa historiskt, separat och read-only:
- bana
- distans
- startmetod
- spår/startposition
- banprofil
- bana × distans × startmetod
- relevanta kusk-/hästeffekter

### Pass 6 — Safe-2 / Safe-3
Testa historiskt:
- Phoenix Top 1/2/3
- Phoenix + spelodds
- Phoenix + streck
- Phoenix + värde
- kombinationer som kan ge bästa säkra 2–3-hästskydd.

### Pass 7 — Reduktionsmotor
Input: Phoenix Top 7.
Output: flera systempaket med olika risknivå.
Reduktion ska prioritera vilka Phoenix 4–7 som kan kastas och skydda starka Top 1–3 där historiken stödjer det.

### Pass 8 — Erfarenhetsbank
Spara per omgång:
- omgång/lopp
- alla starter
- Phoenix-rank och score
- motorfeatures
- odds/speloddsrank
- streck
- värdesignaler
- systempaket
- slutresultat/placering

## Regler

- Ändra inte Phoenix-kärnan efter en enskild omgång.
- Testa nya features/motorer historiskt innan de får påverka live-system.
- Experiment ska vara read-only mot fryst data när det är möjligt.
- `race_id`, `atg_race_id` och oddsdefinitioner ska hanteras genom en tydlig standardiserad bridge.
- Använd `odds_sort` där den historiska tabellen definierar speloddsrank; blanda inte ihop detta med ett fiktivt `odds`-fält.
- NaN, stängda databaskopplingar och 0-matchningar ska stoppas av valideringsceller, inte lösas med manuella gissningar.
- Dagens V85/V86 är data/erfarenhet, inte anledning att bygga om Phoenix.

## Nästa milstolpe
Phoenix ska kunna gå från **ny Colab-runtime → startup → dagens lopp → alla godkända motorer → Top 7 → systempaket → sparad omgång → senare facit** med minimalt manuellt arbete.

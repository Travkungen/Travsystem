# Phoenix V85 checkpoint — 2026-08-15

## Purpose
Observation checkpoint from the V85 round. **No Phoenix model changes are authorized from this checkpoint alone.**

## Core finding
The raw/corrected Phoenix candidate material appears substantially stronger than the final played system suggests. The main question is therefore how to transform the Phoenix ranking into a betting system without destroying useful candidates.

## Corrected Phoenix Top 7 vs V85 results

Using ATG race 5–12 as V85-1–8:

| V85 | Winner | 2nd | Phoenix Top 7 | 2nd rank |
|---|---:|---:|---|---:|
| V85-1 | 3 | 6 | 11, 5, 10, **6**, 2, 14, 7 | 4 |
| V85-2 | 4 | 6 | 5, **6**, 4, 3, 2, 7, 1 | 2 |
| V85-3 | 12 | 9 | 2, 4, **9**, 10, 12, 3, 7 | 3 |
| V85-4 | 11 | 1 | 9, 12, **1**, 6, 5, 11, 7 | 3 |
| V85-5 | 6 | 12 | 6, **12**, 8, 11, 3, 10, 2 | 2 |
| V85-6 | 5 | 8 | 7, 5, 2, 1, **8**, 9, 3 | 5 |
| V85-7 | 4 | 8 | 1, 5, **8**, 9, 3, 7, 6 | 3 |
| V85-8 | 7 | 5 | 9, 10, 8, 1, 7, 4, 11 | outside Top 7 |

### Summary
- Winners in corrected Phoenix Top 7: **6/8**.
- Second-place horses in corrected Phoenix Top 7: **7/8 (87.5%)**.
- The seven captured second-place horses had Phoenix ranks: **2, 2, 3, 3, 3, 4, 5**.
- The only second-place miss from Top 7 was V85-8 nr 5.

## Hybrid comparison
The separate Hybrid Phoenix 3,000-row candidate list also captured **7/8 second-place horses**. Its only second-place miss in this check was V85-6 nr 8.

## Important examples
- **V85-1 nr 3** won at about 4%; Phoenix had it at rank 6, but it was removed from the played system. This is a candidate/reduction issue, not proof that Phoenix failed to see it.
- **V85-3 nr 12** won; Phoenix had it at rank 3, but it was removed from the played system.
- **V85-4 nr 11 Chaplin** won at about 2%; it was present in the Hybrid candidate list at rank 7 before the later selection/reduction stages.
- **V85-5 nr 6** won; the image showed the pre-odds Phoenix ranking with nr 12 #1 and nr 6 #2. This supports keeping raw Phoenix ranking separate from later odds integration for diagnostic purposes.

## Architecture hypothesis to test — do not implement yet
Keep these layers separate:

1. **Phoenix Grundranking** — pure Phoenix model, no odds, no public betting information.
2. **Market/odds layer** — odds/market can add information, but must not overwrite the raw ranking invisibly.
3. **Value layer** — compare Phoenix strength against market price.
4. **Candidate/Top 7 layer** — preserve a sufficiently broad candidate pool.
5. **Reduction/play engine** — decide which candidates survive under a fixed budget.

The key diagnostic is:
**Grundranking → odds effect → Hybrid → reduction → final coupon → result.**

## Next analysis
Before changing any model:
- Compare winners, second and third places against raw/corrected Phoenix ranks.
- Track exactly where each finishing horse disappears: Grundranking, Top 7, Hybrid, or final reduction.
- Test whether odds improve or damage the raw Phoenix ranking historically using the available historical race bank.
- Only then design a new reduction/value motor.

## Operational rule
For live V85 work: final submission closes **16:10** and first V85 start is **16:20**. The system is considered locked after 16:10.

# Phoenix Trav 15

## FINAL PRODUCT CHECKPOINT — 2026-08-18

Final product stage: **FINAL FAST PRODUCT ENGINE v6**. Product/rad generation is READ ONLY: no training, model write, or SQLite write.

### Verified final product
- Phoenix 3000: exactly 3,000 unique rows / 3,000 SEK
- Phoenix Core: 1,080 rows
- Smart value expansion
- Maximum 3 external candidates per leg
- Only verified start numbers
- Tangen Tom #9 protected by Phoenix Core
- Fast generation suitable for practical Colab use

### Phoenix pools
- V64-1: [3,5,7]
- V64-2: [1,2,6]
- V64-3: [9]
- V64-4: [1,2,5,7,8]
- V64-5: [1,2,3,4,6,7,8,9]
- V64-6: [1,7,8]

### Final fast product pools
- V64-1: [1,2,3,4,5,7]
- V64-2: [1,2,6,7,9,12]
- V64-3: [6,8,9,14]
- V64-4: [1,2,3,4,5,6,7,8]
- V64-5: [1,2,3,4,5,6,7,8,9,10]
- V64-6: [1,5,7,8,10,12]

### Product layers
- SAFE: 32 SEK
- BALANS: 96 SEK
- MAX/Core: 1,080 SEK raw Phoenix-space product
- PHOENIX 3000: exactly 3,000 unique rows / 3,000 SEK
- Shares: 100%=3,000 SEK; 50%=1,500; 25%=750; 10%=300

### Few-cell requirement
The complete Phoenix chain must be runnable from a few Google Colab cells after runtime restart, using reusable bootstrap/modules rather than large copied notebook cells. Required chain: bootstrap -> live/startlist load -> Phoenix scoring -> value/market -> spike/value profile -> SAFE/BALANS/OFFENSIV -> fast rad engine -> final 3,000-row/andel layer -> export rows/coupon/share basis -> post-race result import and evaluation.

### Hard constraints
- No training during live product generation
- No model write
- No SQLite write from product engines
- Preserve frozen Phoenix baselines
- Verify start numbers before row generation
- Never claim the full 3,000 rows unless they have actually been exported/read

Phoenix 15 historical architecture and READ ONLY verification remain the reference baseline. Google Drive PhoenixTrav live environment/backups remain the primary Colab-side recovery location.

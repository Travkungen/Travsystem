# PHOENIX 15 — FINAL ENGINE V1 INSTALL/RUNNER
# Paste into Colab after Drive is mounted.
# Does not modify Master/Frozen/Model.

from pathlib import Path
import importlib.util

ROOT = Path('/content/drive/MyDrive/PhoenixTrav/phoenix_15_live')
CANON = ROOT / 'canonical'

# Download/update canonical code from the already versioned Drive copy if present.
final_path = CANON / 'PHOENIX15_FINAL_ENGINE_V1.py'
engine_path = CANON / 'PHOENIX15_INTELLIGENT_ENGINE_V1.py'
skrall_path = CANON / 'PHOENIX15_MILLION_DOLLAR_SECRET_V1.py'

for p in [final_path, engine_path, skrall_path]:
    if not p.exists():
        raise FileNotFoundError(f'Saknas: {p}')

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

final = load(final_path, 'phoenix15_final_v1')
core = load(engine_path, 'phoenix15_core_v1')
mds = load(skrall_path, 'phoenix15_mds_v1')

ARCHIVE = ROOT / 'runs'
ARCHIVE.mkdir(parents=True, exist_ok=True)

# Expected input: core_df = prepared live dataframe with race_id, phoenix_score, odds,
# market_rank-compatible data and (for Million Dollar Secret) hd_win_percent.
# Example:
# result = final.run(core_df, core, mds, out_dir=ARCHIVE,
#                    metadata={'game':'V64','track':'Mantorp'})
# print(result['budget'])
# print(result['coupon'])

print('PHOENIX 15 FINAL ENGINE V1 LADDAD')
print('Pipeline: Phoenix -> 60/40 -> TOP7 -> Spik -> Million Dollar Secret -> Kupong -> Archive')
print('Master/Frozen/Model: READ ONLY')
print('Redo för end-to-end-körning.')

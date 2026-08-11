# Phoenix Trav — architecture foundation

## Target layers

1. **Raw ATG layer** — immutable source payloads and original program files.
2. **Ingestion layer** — validates and records source payloads without changing them.
3. **Normalized layer** — stable race/start/horse/person representations.
4. **Feature layer** — reproducible Phoenix features.
5. **Model layer** — training, validation and prediction.
6. **Application layer** — race-day analysis, ranking and system generation.

## Source of truth

Google Drive currently contains the historical Phoenix assets and the SQLite database. These remain outside GitHub and are treated as protected data assets.

GitHub stores source code, tests, configuration templates and documentation.

Colab remains useful for experiments, validation and controlled execution, but it is not the permanent home of the codebase.

## ATG principle

ATG source material must be archived before transformation. The system must be able to reproduce a run from an archived source payload without depending on a live ATG response.

## Safety principle

The foundation starts read-only. No database writes, migrations, ATG requests or model changes belong in the architecture bootstrap.

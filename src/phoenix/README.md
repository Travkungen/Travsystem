# Phoenix core

This package is the new application foundation for Phoenix Trav.

## Rules

- No live ATG calls in core modules.
- No database writes from exploratory code.
- Raw ATG payloads are treated as immutable source data.
- Historical data, normalized data, features and predictions are separate layers.
- Colab is an execution/notebook environment, not the system of record.
- Every data transformation should be reproducible and testable.

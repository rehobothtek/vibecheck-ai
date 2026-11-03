# Architecture

`ingest` validates source records and keeps source text separate. `provider` only makes HTTPS model calls. `classify` creates a bounded prompt and rejects any output that violates the classification contract. `cache` ties accepted output to source hash, model, and schema version. `report` computes all numeric aggregates deterministically in Python. `retrieve` chooses evidence locally, while `qa` permits citations only from that subset.

Model output is AI-derived inference, not fact. Reports contain only validated classifications and state coverage.

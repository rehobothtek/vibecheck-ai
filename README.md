# VibeCheck AI

An evidence-grounded Python CLI for synthetic festival feedback. It imports reviews, validates live AI classifications, caches only verified output, calculates reports in Python, and constrains AI Q&A to retrieved records.

## Run

Requires Python 3.10+ and no third-party dependencies.

```powershell
python -m unittest discover -v
python main.py
```

For a live demo, copy `.env.example` values into environment variables (do not commit a key):

```powershell
$env:AI_BASE_URL = 'https://provider.example/documented/path'
$env:AI_MODEL = 'approved-model'
$env:AI_API_KEY = 'secret'
```

The adapter expects an OpenAI-compatible chat-completions response. Verify the selected provider's current official documentation and adjust the adapter only with its approved request/response contract. Run menu option 3 for one or more live classifications and option 6 for grounded Q&A. The program does not claim live integration is complete until these demonstrations succeed.

## Trust boundaries and limitations

Reviews are synthetic and untrusted. AI-generated labels are retained only after strict schema, source-ID, topic, length, and exact-quote validation. Percentages and coverage are computed in Python from those verified labels. Q&A may cite only retrieved IDs; unsupported retrieval returns an abstention. Model output can still be wrong or biased, and voluntary comments are not a representative survey.

See `docs/architecture.md`, `docs/security-notes.md`, and `docs/gold-set-evaluation.md`.

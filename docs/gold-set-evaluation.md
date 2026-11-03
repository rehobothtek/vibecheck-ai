# Gold-set evaluation template

Use R001–R012 as the initial 12-record gold set. Record human labels before a live model run: R001 mixed, R002 negative, R003 positive, R004 positive, R005 positive, R006 mixed, R007 neutral, R008 mixed, R009 positive, R010 neutral, R011 positive, R012 negative.

After running a real provider, fill a table with model label, agreement, and disagreement rationale. Accuracy is `agreements / evaluated records`; it is a small-sample check, not an external performance claim. R010 deliberately tests that injection-like text remains data.

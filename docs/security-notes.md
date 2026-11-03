# Security and privacy notes

- API credentials are read only from environment variables and must never be committed or printed.
- The configured endpoint must be HTTPS with a hostname. Confirm the provider's current endpoint and body contract before a live run.
- Festival text is untrusted data, wrapped as data in prompts, and never allowed to alter policy.
- Only one review is sent for classification and at most five retrieved reviews are sent for Q&A.
- Responses are validated for IDs, enums, exact evidence, source hash, and citation scope. These mitigations reduce risk; they do not guarantee factual accuracy.

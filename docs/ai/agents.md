# AI Agent Architecture

Elevra runs specialized agents behind the AI Engine:

- Career Agent
- Learning Agent
- Resume Agent
- Exam Agent
- Scholarship Agent
- Interview Agent
- Recommendation Agent

## Production Rules

- Agent responses must include provenance when derived from retrieved content.
- Personally identifiable information is redacted before model evaluation.
- Recommendations must expose rank reasons to support user trust and auditability.
- Safety and quality evaluation samples run on a scheduled workflow before model promotion.

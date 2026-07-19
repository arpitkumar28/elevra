"""AI agent registry for Elevra's specialized student workflows."""

from pydantic import BaseModel


class AgentCapability(BaseModel):
    key: str
    name: str
    purpose: str
    tools: list[str]
    guardrails: list[str]


AGENTS = [
    AgentCapability(
        key="career",
        name="Career Agent",
        purpose="Maps interests, projects, internships, and applications into career plans.",
        tools=["profile_graph", "opportunity_search", "application_tracker"],
        guardrails=["no_unverified_claims", "student_safety_review"],
    ),
    AgentCapability(
        key="learning",
        name="Learning Agent",
        purpose="Creates adaptive study paths and explanations from course progress.",
        tools=["rag_retriever", "lesson_graph", "spaced_repetition"],
        guardrails=["age_appropriate_content", "source_attribution"],
    ),
    AgentCapability(
        key="resume",
        name="Resume Agent",
        purpose="Reviews student resumes, projects, and profile readiness.",
        tools=["ocr", "portfolio_parser", "rubric_evaluator"],
        guardrails=["privacy_redaction", "bias_check"],
    ),
    AgentCapability(
        key="exam",
        name="Exam Agent",
        purpose="Analyzes mock tests and generates revision plans.",
        tools=["mock_test_analytics", "weakness_detector", "planner"],
        guardrails=["no_medical_or_legal_advice"],
    ),
    AgentCapability(
        key="scholarship",
        name="Scholarship Agent",
        purpose="Matches eligibility and drafts application strategy.",
        tools=["eligibility_matcher", "essay_reviewer", "deadline_tracker"],
        guardrails=["no_fabrication", "source_attribution"],
    ),
    AgentCapability(
        key="interview",
        name="Interview Agent",
        purpose="Runs structured interview practice and feedback loops.",
        tools=["question_bank", "speech_feedback", "rubric_evaluator"],
        guardrails=["constructive_feedback_only"],
    ),
    AgentCapability(
        key="recommendation",
        name="Recommendation Agent",
        purpose="Ranks opportunities, lessons, and next actions for each student.",
        tools=["embedding_ranker", "collaborative_filtering", "freshness_boost"],
        guardrails=["explainable_ranking", "fairness_monitoring"],
    ),
]

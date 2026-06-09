"""Data models for the Policy Governance Catalyst Canvas module."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PolicyGovernanceItem:
    item: str
    policy_area: str
    description: str
    problem_clarity: float
    authority_clarity: float
    evidence_strength: float
    stakeholder_visibility: float
    implementation_detail: float
    accountability_coverage: float
    participation_clarity: float
    ambiguity: float
    claim_strength: float
    owner: str
    status: str
    review_date: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "PolicyGovernanceItem":
        numeric_fields = {
            key: float(row[key])
            for key in [
                "problem_clarity",
                "authority_clarity",
                "evidence_strength",
                "stakeholder_visibility",
                "implementation_detail",
                "accountability_coverage",
                "participation_clarity",
                "ambiguity",
                "claim_strength",
            ]
        }

        return cls(
            item=row["item"],
            policy_area=row["policy_area"],
            description=row["description"],
            owner=row["owner"],
            status=row["status"],
            review_date=row["review_date"],
            **numeric_fields,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    item: str
    policy_area: str
    description: str
    owner: str
    status: str
    review_date: str
    problem_clarity: float
    authority_clarity: float
    evidence_strength: float
    stakeholder_visibility: float
    implementation_detail: float
    accountability_coverage: float
    participation_clarity: float
    ambiguity: float
    claim_strength: float
    completeness_score: float
    evidence_gap: float
    governance_risk: float
    review_priority_score: float
    review_priority: str
    governance_reasons: str
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

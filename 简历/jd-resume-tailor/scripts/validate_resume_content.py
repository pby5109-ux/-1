#!/usr/bin/env python3
"""Validate an approved JD-tailored resume payload against the evidence bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = SKILL_DIR / "references" / "candidate-profile.json"
DEFAULT_PROJECTS = SKILL_DIR / "references" / "project-evidence.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def evidence_index(profile: dict[str, Any], projects: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in profile.get("skill_boundaries", []):
        result[item["id"]] = item
    for item in profile.get("evidence", []):
        result[item["id"]] = item
    for project in projects.get("projects", []):
        for claim in project.get("claims", []):
            result[claim["id"]] = claim
    return result


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WFA" else 1 for ch in text)


def all_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        output: list[str] = []
        for key, child in value.items():
            if key != "evidence_ids":
                output.extend(all_text(child))
        return output
    if isinstance(value, list):
        output = []
        for child in value:
            output.extend(all_text(child))
        return output
    return []


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(payload: dict[str, Any], profile: dict[str, Any], projects: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    index = evidence_index(profile, projects)

    require(payload.get("schema_version") == 1, "schema_version must be 1", errors)
    require(payload.get("approved") is True, "approved must be true after explicit user approval", errors)
    require(payload.get("template") in {"embedded", "general"}, "template must be embedded or general", errors)
    require(bool(payload.get("preview_id")), "preview_id is required", errors)
    require(bool(re.fullmatch(r"\d{8}", str(payload.get("date", "")))), "date must be YYYYMMDD", errors)
    require(bool(payload.get("company")), "company is required", errors)
    require(bool(payload.get("role")), "role is required", errors)

    skills = payload.get("skills", [])
    project_list = payload.get("projects", [])
    enterprise = payload.get("enterprise", {})
    campus = payload.get("campus", {})
    competitions = payload.get("competitions", [])
    self_evaluation = payload.get("self_evaluation", {})

    require(isinstance(skills, list) and len(skills) == 3, "skills must contain exactly 3 items", errors)
    require(isinstance(project_list, list) and len(project_list) == 3, "projects must contain exactly 3 items", errors)
    project_bullets = sum(len(project.get("bullets", [])) for project in project_list if isinstance(project, dict))
    require(project_bullets == 8, f"project bullets must total 8, found {project_bullets}", errors)
    require(len(enterprise.get("bullets", [])) == 2, "enterprise must contain exactly 2 bullets", errors)
    require(len(campus.get("bullets", [])) == 2, "campus must contain exactly 2 bullets", errors)
    require(isinstance(competitions, list) and len(competitions) == 4, "competitions must contain exactly 4 items", errors)
    require(bool(self_evaluation), "self_evaluation is required", errors)

    allowed_project_ids = {project["id"] for project in projects.get("projects", [])}
    for number, project in enumerate(project_list, start=1):
        project_id = project.get("id")
        require(project_id in allowed_project_ids, f"project {number} has unknown id: {project_id}", errors)
        require(bool(project.get("name")), f"project {number} name is required", errors)
        require(bool(project.get("role")), f"project {number} role is required", errors)
        require(bool(project.get("period")), f"project {number} period is required", errors)

    claim_items: list[tuple[str, dict[str, Any]]] = []
    for i, item in enumerate(skills, start=1):
        claim_items.append((f"skill {i}", item))
    for i, project in enumerate(project_list, start=1):
        for j, item in enumerate(project.get("bullets", []), start=1):
            claim_items.append((f"project {i} bullet {j}", item))
    for i, item in enumerate(enterprise.get("bullets", []), start=1):
        claim_items.append((f"enterprise bullet {i}", item))
    for i, item in enumerate(campus.get("bullets", []), start=1):
        claim_items.append((f"campus bullet {i}", item))
    for i, item in enumerate(competitions, start=1):
        claim_items.append((f"competition {i}", item))
    claim_items.append(("self evaluation", self_evaluation))

    for location, item in claim_items:
        label = str(item.get("label", "")).strip()
        text = str(item.get("text", "")).strip()
        evidence_ids = item.get("evidence_ids", [])
        require(bool(label), f"{location}: label is required", errors)
        require(bool(text), f"{location}: text is required", errors)
        require(isinstance(evidence_ids, list) and bool(evidence_ids), f"{location}: at least one evidence_id is required", errors)
        if display_width(label) > 12:
            warnings.append(f"{location}: label is wider than the established four-character pattern: {label}")
        for evidence_id in evidence_ids if isinstance(evidence_ids, list) else []:
            evidence = index.get(evidence_id)
            if evidence is None:
                errors.append(f"{location}: unknown evidence_id {evidence_id}")
                continue
            policy = evidence.get("resume_policy")
            if policy not in {"allowed", "allowed_with_qualifier", "prohibited"}:
                errors.append(f"{location}: unknown evidence policy for {evidence_id}")
            if policy == "prohibited" or evidence.get("status") in {"prohibited", "unresolved", "design_only"}:
                errors.append(f"{location}: prohibited evidence_id {evidence_id}")
            elif policy == "allowed_with_qualifier":
                warnings.append(f"{location}: {evidence_id} requires accurate qualification")
                terms = evidence.get("required_qualifier_terms", [])
                if terms and not any(term in text for term in terms):
                    errors.append(f"{location}: {evidence_id} requires a same-bullet validation qualifier")

    forbidden_patterns = {
        r"三角波": "current instrument source does not implement a true triangle wave",
        r"已解决波形撕裂": "waveform tearing is not fixed",
        r"LoRaWAN": "the project uses a custom serial LoRa protocol, not LoRaWAN",
        r"多节点组网": "multi-node networking has not been validated",
        r"(?:实测)?通信距离": "RF distance has not been measured",
        r"RSSI": "RSSI has not been measured",
        r"丢包率": "packet loss has not been measured",
        r"(?:μA|微安|实测功耗)": "whole-device power has not been measured",
        r"精通C(?:语言)?": "C proficiency must not be overstated",
        r"(?:C\+\+|嵌入式Linux|AUTOSAR|Bootloader|TCP/IP|CAN(?:总线)?)": "unsupported skill keyword"
    }
    # Scan candidate assertions, not JD metadata, company names or target titles.
    # A role titled Linux engineer is not proof the candidate claims Linux skills.
    assertions = [str(payload.get("header", {}).get("tags", ""))]
    assertions.extend(str(item.get("label", "")) + " " + str(item.get("text", ""))
                      for _, item in claim_items)
    assertions.extend(str(project.get("name", "")) + " " + str(project.get("role", ""))
                      for project in project_list)
    assertions.extend([str(enterprise.get("role", "")), str(campus.get("role", ""))])
    combined = "\n".join(assertions)
    for pattern, reason in forbidden_patterns.items():
        if re.search(pattern, combined, flags=re.IGNORECASE):
            errors.append(f"forbidden wording matched /{pattern}/: {reason}")

    widths: list[tuple[str, int]] = []
    for location, item in claim_items:
        widths.append((location, display_width(str(item.get("label", "")) + "：" + str(item.get("text", "")))))
    long_items = [(location, width) for location, width in widths if width > 275]
    for location, width in long_items:
        warnings.append(f"{location}: display width {width} is likely to threaten the one-page layout")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--projects", type=Path, default=DEFAULT_PROJECTS)
    args = parser.parse_args()

    try:
        payload = load_json(args.content)
        profile = load_json(args.profile)
        projects = load_json(args.projects)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(payload, profile, projects)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"OK: {args.content} passed evidence and structure validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

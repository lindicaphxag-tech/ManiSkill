from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnchorLifetimeAudit:
    classification: str
    has_chunk_in_flight: bool
    has_queue_binding: bool
    guarded_anchor_assignments: int
    unguarded_anchor_assignments: int
    reason: str


def _is_last_state_assignment(node: ast.AST) -> bool:
    if not isinstance(node, (ast.Assign, ast.AnnAssign)):
        return False
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    for target in targets:
        if isinstance(target, ast.Attribute) and target.attr == "_last_state":
            return True
    return False


def _mentions_chunk_guard(expr: ast.AST) -> bool:
    for node in ast.walk(expr):
        if isinstance(node, ast.Attribute) and node.attr == "_chunk_in_flight":
            return True
        if isinstance(node, ast.Name) and node.id == "_chunk_in_flight":
            return True
    return False


def audit_relative_anchor_source(source: str) -> AnchorLifetimeAudit:
    tree = ast.parse(source)
    cls = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "RelativeActionsProcessorStep"
        ),
        None,
    )
    if cls is None:
        raise ValueError("RelativeActionsProcessorStep not found")

    method_names = {
        node.name for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    call = next(
        (
            node
            for node in cls.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "__call__"
        ),
        None,
    )
    if call is None:
        raise ValueError("RelativeActionsProcessorStep.__call__ not found")

    guarded = 0
    unguarded = 0

    def visit_statements(statements: list[ast.stmt], guarded_by_chunk: bool = False) -> None:
        nonlocal guarded, unguarded
        for stmt in statements:
            if isinstance(stmt, ast.If):
                child_guard = guarded_by_chunk or _mentions_chunk_guard(stmt.test)
                visit_statements(stmt.body, child_guard)
                visit_statements(stmt.orelse, guarded_by_chunk)
                continue
            if _is_last_state_assignment(stmt):
                if guarded_by_chunk:
                    guarded += 1
                else:
                    unguarded += 1
            for field in ("body", "orelse", "finalbody"):
                child = getattr(stmt, field, None)
                if isinstance(child, list):
                    visit_statements(child, guarded_by_chunk)

    visit_statements(call.body)

    has_chunk = "_chunk_in_flight" in method_names
    has_binding = "bind_action_queue" in method_names

    if guarded > 0 and unguarded == 0 and has_chunk and has_binding:
        classification = "chunk_held_anchor"
        reason = (
            "anchor updates are guarded by queue/chunk lifetime and the processor "
            "exposes an explicit queue binding"
        )
    elif unguarded > 0 and guarded == 0:
        classification = "moving_anchor"
        reason = (
            "anchor state is refreshed without a chunk-lifetime guard, so queued "
            "actions can be re-anchored to later observations"
        )
    else:
        classification = "ambiguous"
        reason = "source structure does not match either frozen anchor-lifetime contract"

    return AnchorLifetimeAudit(
        classification=classification,
        has_chunk_in_flight=has_chunk,
        has_queue_binding=has_binding,
        guarded_anchor_assignments=guarded,
        unguarded_anchor_assignments=unguarded,
        reason=reason,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument(
        "--expect",
        choices=["moving_anchor", "chunk_held_anchor", "ambiguous"],
        required=True,
    )
    args = parser.parse_args()

    audit = audit_relative_anchor_source(args.file.read_text())
    print(
        "LEROBOT_ANCHOR_AUDIT",
        {
            "classification": audit.classification,
            "has_chunk_in_flight": audit.has_chunk_in_flight,
            "has_queue_binding": audit.has_queue_binding,
            "guarded_anchor_assignments": audit.guarded_anchor_assignments,
            "unguarded_anchor_assignments": audit.unguarded_anchor_assignments,
            "reason": audit.reason,
        },
    )
    if audit.classification != args.expect:
        raise SystemExit(
            f"expected {args.expect}, observed {audit.classification}: {audit.reason}"
        )


if __name__ == "__main__":
    main()

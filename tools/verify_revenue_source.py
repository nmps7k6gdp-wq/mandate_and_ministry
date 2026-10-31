"""Read-only Revenue source checks. This does not emulate CK3 or validate engine behavior."""
from __future__ import annotations

import hashlib
import json
import re
import runpy
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game")
TOKEN = re.compile(r'\s+|\#[^\n]*|"(?:\\.|[^"\\])*"|\?=|>=|<=|!=|[{}=<>]|[^\s{}=<>!?#"]+')


@dataclass
class Node:
    key: str
    value: str | None
    start: int
    end: int
    children: list["Node"] = field(default_factory=list)
    parent: "Node | None" = None

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


def parse(text: str) -> list[Node]:
    tokens = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text)
              if not m.group().isspace() and not m.group().startswith("#")]
    pos = 0

    def group(parent=None, closing=False):
        nonlocal pos
        result = []
        while pos < len(tokens):
            key, start, end = tokens[pos]
            if key == "}":
                assert closing, f"Unexpected closing brace at {start}"
                pos += 1
                return result, end
            assert key != "{", f"Unlabelled block at {start}"
            if pos + 1 < len(tokens) and tokens[pos + 1][0] in {"=", "?=", ">", "<", ">=", "<=", "!="}:
                pos += 2
                assert pos < len(tokens), f"Missing value for {key}"
                value, _, value_end = tokens[pos]
                pos += 1
                node = Node(key, None if value == "{" else value, start, value_end, parent=parent)
                if value == "{":
                    node.children, node.end = group(node, True)
                else:
                    assert value != "}", f"Missing value before closing brace for {key}"
                result.append(node)
            else:
                # Unkeyed list entries (traits, on_action names, etc.).
                pos += 1
        assert not closing, "Unclosed block"
        return result, len(text)

    return group()[0]


def main():
    paths = sorted(p for base in ("common", "events", "localization")
                   for p in (ROOT / base).rglob("*")
                   if p.is_file() and "revenue" in p.name.lower() and p.suffix in {".txt", ".yml"})
    sources = {}
    trees = {}
    loc = {}
    for path in paths:
        assert path.read_bytes().startswith(b"\xef\xbb\xbf"), f"Missing UTF-8 BOM: {path}"
        text = path.read_text(encoding="utf-8-sig")
        sources[path] = text
        if path.suffix == ".yml":
            assert text.startswith("l_english:\n")
            for line in text.splitlines()[1:]:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                match = re.fullmatch(r" ([\w.]+):0 (\".*\")", line)
                assert match, f"Malformed localization: {line}"
                assert match[1] not in loc, f"Duplicate localization: {match[1]}"
                loc[match[1]] = json.loads(match[2])
        else:
            trees[path] = parse(text)

    all_definitions = [(node.key, path, node) for path, nodes in trees.items() for node in nodes if node.value is None]
    module_names = [key for key, _, _ in all_definitions if key.startswith(("mam_revenue_", "mam_revenue."))]
    assert len(module_names) == len(set(module_names)), "Duplicate Revenue database definition"
    definitions = {key: (path, node) for key, path, node in all_definitions}
    custom = {key for key in definitions if key.startswith("mam_revenue_")}
    errors = []
    uses = 0
    trigger_contexts = {"limit", "trigger", "is_shown", "is_valid", "is_available", "is_valid_showing_failures_only",
                        "show_as_unavailable", "ai_potential", "auto_accept", "can_send", "starts_enabled"}
    macros = {key: set(re.findall(r"\$([A-Z_]+)\$", sources[path][node.start:node.end]))
              for key, (path, node) in definitions.items() if key.startswith("mam_revenue_")}
    for path, text in sources.items():
        if path.suffix == ".yml":
            continue
        for ref in re.findall(r"\bmam_revenue_[A-Za-z0-9_]+\b", re.sub(r"#[^\n]*", "", text)):
            if ref not in custom and ref not in loc:
                errors.append(f"Unresolved Revenue identifier {ref} in {path.name}")
        for ref in re.findall(r"\bmam_rv\.[A-Za-z0-9_]+\b", text):
            if ref not in loc:
                errors.append(f"Missing localization {ref} in {path.name}")
        for top in trees[path]:
            for node in top.walk():
                if node is top:
                    continue
                if node.key in macros and macros[node.key]:
                    supplied = {child.key for child in node.children}
                    if supplied != macros[node.key]:
                        errors.append(f"Parameters for {node.key}: {supplied}, expected {macros[node.key]}")
                if node.key.startswith("mam_revenue_"):
                    uses += 1
                if node.key.endswith("_effect") and node.key.startswith("mam_revenue_"):
                    parent = node.parent
                    while parent:
                        if parent.key in trigger_contexts:
                            errors.append(f"Effect {node.key} inside trigger {parent.key}: {path.name}")
                            break
                        parent = parent.parent

    event_ids = {key for key in definitions if re.fullmatch(r"mam_revenue\.\d+", key)}
    for path, text in sources.items():
        if path.suffix != ".yml":
            for ref in re.findall(r"\bmam_revenue\.\d+\b", text):
                if ref not in event_ids:
                    errors.append(f"Missing event {ref}: {path.name}")
    for value in loc.values():
        for ref in re.findall(r"Custom\('([^']+)'\)", value):
            if ref.startswith("MamRevenue") and ref not in definitions:
                errors.append(f"Missing contextual localization: {ref}")

    script_text = "\n".join(text for path, text in sources.items() if path.suffix == ".txt")
    bound_scopes = set(re.findall(r"save_(?:temporary_)?scope_as\s*=\s*(mam_rv_\w+)", script_text))
    bound_scopes.update(re.findall(r"save_scope_value_as\s*=\s*\{\s*name\s*=\s*(mam_rv_\w+)", script_text))
    used_scopes = set(re.findall(r"\bscope:(mam_rv_\w+)", script_text))
    errors.extend(f"Never-bound Revenue scope: {name}" for name in used_scopes - bound_scopes)

    manifest = json.loads((ROOT / "docs/REVENUE-NATIVE-BRIDGE.json").read_text(encoding="utf-8"))
    native_text = Path(manifest["native_source"]).read_text(encoding="utf-8-sig")
    original = next(node for node in parse(native_text) if node.key == manifest["native_definition"])
    original_text = native_text[original.start:original.end]
    assert hashlib.sha256(original_text.encode()).hexdigest() == manifest["native_definition_sha256"], "Native definition changed; bridge needs review"
    accept = next(child for child in original.children if child.key == "on_accept")
    opening = native_text.index("{", accept.start)
    body = native_text[opening + 1:accept.end - 1]
    assert hashlib.sha256(body.encode()).hexdigest() == manifest["native_acceptance_body_sha256"]
    bridge = (ROOT / manifest["overridden_file"]).read_text(encoding="utf-8-sig")
    assert body in bridge, "Unsupported native acceptance branch was changed"
    bridged = next(node for node in parse(bridge) if node.key == manifest["native_definition"])
    for key in ("cost", "cooldown", "is_available", "ai_targets", "ai_frequency_by_tier", "ai_will_do", "ai_accept", "on_decline"):
        before = [native_text[node.start:node.end] for node in original.children if node.key == key]
        after = [bridge[node.start:node.end] for node in bridged.children if node.key == key]
        assert before == after, f"Unsupported native behavior changed in {key}"

    # Native conquest definitions already contain title handoffs. Exempt only
    # exact source-pinned overrides, after verifying every permitted guard;
    # authored Revenue code keeps the prohibition on foreign-domain mutation.
    safety = runpy.run_path(str(ROOT / 'tools/revenue_safety_contracts.py'))
    registry = json.loads((ROOT / 'tools/templates/revenue_native_campaign_safety.json').read_text(encoding='utf-8'))
    safety_outputs = set()
    for record in registry['records']:
        expected = safety['compile_native_record'](record, parse)
        output = ROOT / record['output']
        actual = next(node for node in trees[output] if node.key == record['definition'])
        assert sources[output][actual.start:actual.end] == expected, 'Native safety override differs from reviewed guards'
        safety_outputs.add(output)
    for output in safety_outputs:
        expected_keys = {r['definition'] for r in registry['records'] if ROOT / r['output'] == output}
        assert {n.key for n in trees[output] if n.children} == expected_keys, 'Unexpected native safety definition'
    module_text = "\n".join(text for path, text in sources.items()
                            if path.suffix == ".txt" and path.name != "zz_mam_revenue_native_requests.txt"
                            and "great_projects" not in path.parts
                            and path not in safety_outputs
                            and path.name != "zz_mam_revenue_common_native_obligations.txt")
    for forbidden in ("change_title_holder", "change_liege", "add_gold", "remove_gold", "add_treasury", "remove_treasury",
                      "mam_personnel_", "mam_senior_", "mam_cj_record_"):
        assert not re.search(r"\b" + re.escape(forbidden), module_text), f"Revenue must not mutate foreign domain: {forbidden}"
    commit_path, commit = definitions["mam_revenue_commit_effect"]
    commit_text = sources[commit_path][commit.start:commit.end]
    assert commit_text.count("pay_short_term_treasury") == 1
    assert commit_text.index("name = mam_rv_pending value = 0") < commit_text.index("pay_short_term_treasury")
    assert "mam_revenue_payment_ready_trigger = yes" in commit_text
    assert "mam_rv_before_donor" in commit_text and "mam_rv_before_recipient" in commit_text

    # dev.46 regressions found in the first live transfer's engine logs.
    # `current_date` parses its RHS as a literal date; computed comparisons must
    # put a numeric variable on the left instead.
    assert not re.search(r"\bcurrent_date\s*[<>]=?\s*\{", script_text), "Computed RHS for literal-date trigger"
    for path, nodes in trees.items():
        for top in nodes:
            for node in top.walk():
                if node.key == "vassal_contract_obligation_level:celestial_ministry_budget":
                    assert node.value in {"0", "1", "2"}, "Budget query needs a numeric obligation index"
    native_contract = (NATIVE / "common/subject_contracts/contracts/celestial.txt").read_text(encoding="utf-8-sig")
    native_budget = next(node for node in parse(native_contract) if node.key == "celestial_ministry_budget")
    native_levels = next(node for node in native_budget.children if node.key == "obligation_levels")
    assert [node.key for node in native_levels.children] == [
        "celestial_ministry_budget_low", "celestial_ministry_budget_medium", "celestial_ministry_budget_high"]
    province_path, province = definitions["mam_revenue_province_trigger"]
    province_text = sources[province_path][province.start:province.end]
    assert "prev.primary_title" not in province_text, "Province iterator must use its named character scope"
    assert "save_temporary_scope_as = mam_rv_province_subject" in province_text
    ready_path, ready = definitions["mam_revenue_payment_ready_trigger"]
    ready_text = sources[ready_path][ready.start:ready.end]
    for snapshot in ("mam_rv_donor_snapshot", "mam_rv_recipient_snapshot"):
        assert ready_text.count("exists = var:" + snapshot) >= 2, "Snapshot lookup needs presence and evaluation guards"
    create_path, create = definitions["mam_revenue_create_file_effect"]
    for node in create.walk():
        if node.key == "scope:mam_rv_created":
            parent = node.parent
            guarded = False
            while parent is not None:
                if parent.key == "if":
                    limit = next((n for n in parent.children if n.key == "limit"), None)
                    guarded |= limit is not None and any(n.key == "exists" and n.value == "scope:mam_rv_created" for n in limit.children)
                parent = parent.parent
            assert guarded, "Story initialization must not inspect a nonexistent tooltip-only story"

    # Fiscal law, editable drafts and appeals must preserve the transaction boundary.
    for level, index in (("reserved", "0"), ("limited", "1"), ("expanded", "2")):
        key = "mam_revenue_authority_" + level
        _, law = definitions[key]
        assert next(n.value for n in law.children if n.key == "index") == index
        assert key + "_effects" in loc and key + "_desc" in loc
        icon = ROOT / "gfx/interface/icons/laws" / (key + ".dds")
        assert icon.read_bytes().startswith(b"DDS "), "Missing or invalid law icon"
        # The vanilla filenames are zero-based, but their artwork is numbered
        # 1..4. Using _1.._3 produced the user's incorrect 2..4 display.
        native_icon = NATIVE / "gfx/interface/icons/laws" / ("imperial_bureaucracy_" + index + ".dds")
        assert icon.read_bytes() == native_icon.read_bytes(), "Law artwork is offset from its displayed 1..3 level"
    _, authority_event = definitions["mam_revenue.8"]
    assert not any(n.key in {"mam_revenue_set_mandate_effect", "add_realm_law"} for n in authority_event.walk()), "Help event must not bypass the law panel"
    amount_path, amount_event = definitions["mam_revenue.11"]
    assert not any(n.key in {"pay_short_term_treasury", "mam_revenue_propose_payment_effect", "mam_revenue_commit_effect"} for n in amount_event.walk()), "Draft editor must not transfer funds"
    _, result_event = definitions["mam_revenue.20"]
    assert not any(n.key in {"pay_short_term_treasury", "mam_revenue_commit_effect", "vassal_contract_set_obligation_level"} for n in result_event.walk()), "Result acknowledgement must not repeat financial effects"
    # Char.Custom() does not carry the caller event's saved scopes into nested
    # localization. Event-dependent prose must use native scripted descriptions.
    for path, nodes in trees.items():
        if path.parent.name == "customizable_localization":
            assert "scope:mam_rv_" not in sources[path], "Event scopes cannot be read through character Custom localization"
    assert "MamRevenueOutcome" not in definitions and "MamRevenuePayer" not in definitions
    for receipt in ("mam_rv_after_donor", "mam_rv_after_recipient", "mam_rv_actual_debit", "mam_rv_actual_credit"):
        assert receipt in commit_text, "Missing actual account movement in payment verification"
    assert "var:mam_rv_actual_debit > 0" in commit_text and "var:mam_rv_actual_credit > 0" in commit_text

    # Evaluate only the native result-description selector's small trigger
    # subset. This is a source regression test, not a CK3 financial emulator.
    desc = next(n for n in result_event.children if n.key == "desc")
    choices = next(n for n in desc.children if n.key == "first_valid").children

    def match_notice(nodes, context):
        for node in nodes:
            if node.key == "limit":
                continue
            if node.key == "exists":
                passed = node.value in context
            elif node.key == "trigger_if":
                limit = next(n for n in node.children if n.key == "limit")
                passed = not match_notice(limit.children, context) or match_notice(node.children, context)
            elif node.key.startswith("scope:mam_rv_outcome_"):
                passed = context.get(node.key) == int(node.value)
            else:
                raise AssertionError("Unhandled notice predicate in source test: " + node.key)
            if not passed:
                return False
        return True

    def select_notice(context):
        for choice in choices:
            if choice.key == "desc":
                return choice.value
            trigger = next(n for n in choice.children if n.key == "trigger")
            if match_notice(trigger.children, context):
                return next(n.value for n in choice.children if n.key == "desc")
        raise AssertionError("No safe fallback notice")

    cases = [
        ({}, "mam_rv.outcome_desc"),
        ({"status": 7, "kind": 2}, "mam_rv.outcome_consent"),
        ({"status": 1, "kind": 2}, "mam_rv.outcome_desc"),
        ({"status": 1, "kind": 2, "payment_state": 0}, "mam_rv.outcome_desc"),
        ({"status": 1, "kind": 2, "payment_state": 2}, "mam_rv.outcome_paid"),
        ({"status": 2, "kind": 1}, "mam_rv.outcome_refused"),
        ({"status": 2, "kind": 4}, "mam_rv.outcome_budget_refused"),
        ({"status": 1, "kind": 4, "budget": 0}, "mam_rv.outcome_budget_changed_low"),
        ({"status": 1, "kind": 13, "budget": 2}, "mam_rv.outcome_appeal_upheld_high"),
        ({"status": 2, "kind": 13}, "mam_rv.outcome_appeal_rejected"),
        ({"status": 5, "kind": 2, "payment_state": 3}, "mam_rv.outcome_uncertain"),
        ({"status": 6, "kind": 2}, "mam_rv.outcome_returned"),
        ({"status": 8, "kind": 13}, "mam_rv.outcome_superseded"),
    ]
    for context, expected in cases:
        saved = {"scope:mam_rv_outcome_" + key: value for key, value in context.items()}
        assert select_notice(saved) == expected, (context, select_notice(saved), expected)
    _, appeal_gate = definitions["mam_revenue_can_appeal_trigger"]
    assert any(n.key == "has_variable" and n.value == "mam_rv_appeal_used" for n in appeal_gate.walk())
    assert any(n.key == "var:mam_rv_recipient_snapshot" for n in appeal_gate.walk())
    assert any(n.key == "mam_revenue_budget_level" for n in appeal_gate.walk())
    for event_id in event_ids:
        _, event = definitions[event_id]
        if any(n.key == "hidden" and n.value == "yes" for n in event.children):
            continue
        for option in (n for n in event.children if n.key == "option"):
            assert any(n.key == "custom_tooltip" or n.key.endswith("_preview_effect") for n in option.children), f"Unexplained option in {event_id}"
    assert not errors, "\n".join(sorted(set(errors)))
    print(f"PASS: {len(paths)} Revenue game/localization files parsed; {len(custom)} custom definitions; "
          f"{len(event_ids)} events; {len(loc)} localization keys; {uses} resolved uses.")
    print("PASS: parameters, trigger/effect placement, native bridge, payment guard, fiscal law, draft/result boundaries and appeal checks.")
    print(f"PASS: {len(cases)} result-description regressions, scope-safe localization, numbered artwork and actual debit/credit receipt fields.")
    print("NOT TESTED: CK3 engine commands, live event rendering, treasury buckets, observer AI balance or runtime regressions.")


if __name__ == "__main__":
    main()

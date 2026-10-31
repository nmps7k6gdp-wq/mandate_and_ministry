"""Build the isolated common-fund module. Native sources are read, never written.

Generated files are reviewed by verify_common_fund.py. Re-run deliberately only.
"""
from pathlib import Path
import hashlib
import json
import runpy
import os
import tempfile

ROOT = Path(__file__).resolve().parents[1]
# Keep CK3 hot reload useful: the multiversion generator runs off the watched
# tree. Publish only validated, complete, changed files rather than repeatedly
# exposing intermediate generated versions to a running game.
if __name__ == '__main__':
    if os.environ.get('MAM_COMMON_FUND_STAGING') == '1':
        staging_parent=Path(os.environ.get('MAM_BUILD_STAGING_DIR',tempfile.gettempdir())).resolve()
        if not (ROOT.parent.name.startswith('mam-cf-build-') and ROOT.parent.parent.resolve()==staging_parent):
            raise RuntimeError('Raw generation is restricted to the isolated staging directory. Use the normal builder without the staging environment flag.')
    else:
        runpy.run_path(str(ROOT/'tools/stage_common_fund.py'), run_name='__main__')
        raise SystemExit(0)
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game')
parse = runpy.run_path(str(ROOT / 'tools/verify_revenue_source.py'))['parse']
# Never silently rebuild compatibility overrides against an unreviewed game
# update. The manifest is an audit baseline, not permission to accept new data.
native_manifest = ROOT/'docs/COMMON-FUND-NATIVE-PROJECTS.json'
if native_manifest.exists():
    for native_path, expected in json.loads(native_manifest.read_text(encoding='utf-8-sig'))['native_files'].items():
        if hashlib.sha256(Path(native_path).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Native CK3 project source changed. Review compatibility and explicitly migrate the native baseline before rebuilding: '+native_path)
TITLES = ['e_minister_chancellor', 'e_minister_censor', 'e_minister_grand_marshal',
          'e_minister_of_personnel', 'e_minister_of_war', 'e_minister_of_rites',
          'e_minister_of_works', 'e_minister_of_revenue', 'e_minister_of_justice']

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + '\n', encoding='utf-8-sig' if p.suffix in {'.txt', '.yml'} else 'utf-8')

def roster(effect):
    return '\n'.join(f'title:{t} = {{ if = {{ limit = {{ exists = holder holder = {{ mam_revenue_ministry_trigger = yes }} }} {effect} }} }}' for t in TITLES)

write('common/script_values/mam_revenue_common_values.txt', r'''
# Character values; all actual currency remains native treasury.
mam_revenue_fund_observed_cost = {
 value = monthly_character_treasury_income subtract = monthly_character_treasury_balance min = 0
}
mam_revenue_fund_headroom = {
 value = 75
 if = { limit = { title:h_china = { var:mam_cf_programme = 1 } } value = 25 }
 if = { limit = { has_trait = generous } add = 25 }
 if = { limit = { has_trait = greedy } subtract = 20 }
 if = { limit = { has_trait = paranoid } subtract = 15 }
 if = { limit = { has_trait = trusting } add = 15 }
 if = { limit = { has_trait = diligent } add = 10 }
 min = 25 max = 150
}
mam_revenue_fund_military_advance = {
 value = major_treasury_value
 # Native proactive debt aid is AI-disabled at 1,000 treasury or less.
 if = { limit = { has_title = title:e_minister_of_war } min = 1200 }
}
# Title scope. Project cash is excluded from ordinary operations.
mam_revenue_fund_target = { value = var:mam_cf_cost multiply = 2 add = var:mam_cf_headroom add = var:mam_cf_special_target }
mam_revenue_fund_cash_target = { value = mam_revenue_fund_target add = var:mam_cf_project_cash }
mam_revenue_fund_available = {
 value = 0
 if = { limit = { exists = title:e_minister_of_revenue.holder title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes } }
  value = title:e_minister_of_revenue.holder.treasury
  subtract = title:e_minister_of_revenue.mam_revenue_fund_cash_target
  subtract = title:h_china.var:mam_cf_reserve subtract = title:h_china.var:mam_cf_unfunded
  min = 0
  if = { limit = { title:e_minister_of_revenue = { has_variable = mam_cf_payment_hold } } value = 0 }
 }
}
mam_revenue_fund_queue_score = {
 value = 1000000 subtract = var:mam_cf_serial
 if = { limit = { var:mam_cf_kind = 2 var:mam_cf_target.holder = { mam_revenue_has_recovery_need_trigger = yes } } add = 2000000 }
 if = { limit = { var:mam_cf_kind = 8 } add = 1000000 }
}
mam_revenue_fund_support_weight = {
 value = 80
 if = { limit = { has_trait = generous } add = 25 }
 if = { limit = { has_trait = trusting } add = 15 }
 if = { limit = { has_trait = greedy } subtract = 20 }
 if = { limit = { has_trait = paranoid } subtract = 20 }
 if = { limit = { has_trait = lazy } subtract = 20 }
 if = { limit = { has_trait = diligent } add = 15 }
 if = { limit = { scope:mam_cf_file = { var:mam_cf_kind = 2 } has_trait = compassionate } add = 60 }
 if = { limit = { has_trait = ambitious OR = {
  is_close_or_extended_family_of = scope:mam_cf_subject has_relation_friend = scope:mam_cf_subject
  is_in_same_movement_as = { TARGET = scope:mam_cf_subject }
 } } add = 25 }
 if = { limit = { has_trait = vengeful has_relation_rival = scope:mam_cf_subject } subtract = 50 }
 if = { limit = { has_trait = just } add = 15 }
 min = 10 max = 180
}
''')

write('common/scripted_triggers/mam_revenue_common_triggers.txt', r'''
mam_revenue_fund_enabled_trigger = {
 exists = title:h_china.holder title:h_china.holder = { mam_revenue_emperor_trigger = yes }
 title:h_china = { has_variable = mam_cf_active }
}
mam_revenue_fund_member_trigger = {
 mam_revenue_fund_enabled_trigger = yes has_treasury = yes top_liege = title:h_china.holder
 primary_title = { tgp_is_minister_title = yes holder = prev }
}
# Story identity includes the exact holder who requested/was reviewed.
mam_revenue_fund_case_trigger = {
 var:mam_cf_pending = 1 exists = var:mam_cf_target.holder exists = var:mam_cf_requester
 mam_revenue_fund_enabled_trigger = yes
 trigger_if = { limit = { var:mam_cf_kind < 10 } var:mam_cf_emperor = title:h_china.holder }
 save_temporary_scope_as = mam_cf_check
 var:mam_cf_target = { var:mam_cf_case_$KIND$ = scope:mam_cf_check }
 var:mam_cf_target.holder = var:mam_cf_snapshot
 trigger_if = { limit = { var:mam_cf_target != title:h_china }
  trigger_if = { limit = { var:mam_cf_kind < 10 }
   var:mam_cf_target.holder = { mam_revenue_recipient_trigger = yes primary_title = scope:mam_cf_check.var:mam_cf_target }
  }
  trigger_else = { var:mam_cf_target.holder = { has_treasury = yes top_liege = title:h_china.holder } }
 }
}
mam_revenue_fund_live_case_trigger = {
 exists = var:mam_cf_target.holder exists = var:mam_cf_requester
 var:mam_cf_pending = 1 mam_revenue_fund_enabled_trigger = yes
 trigger_if = { limit = { var:mam_cf_kind < 10 }
  var:mam_cf_emperor = title:h_china.holder var:mam_cf_target.holder = var:mam_cf_snapshot
 }
 trigger_if = { limit = { var:mam_cf_target != title:h_china }
  save_temporary_scope_as = mam_cf_check
  trigger_if = { limit = { var:mam_cf_kind < 10 }
   var:mam_cf_target.holder = { mam_revenue_recipient_trigger = yes primary_title = scope:mam_cf_check.var:mam_cf_target }
  }
  trigger_else = { var:mam_cf_target.holder = { has_treasury = yes top_liege = title:h_china.holder } }
 }
}
mam_revenue_fund_actor_trigger = {
 is_alive = yes is_imprisoned = no NOT = { has_trait = incapable }
 exists = scope:mam_cf_file exists = var:mam_cf_open
 var:mam_cf_open = scope:mam_cf_file
 scope:mam_cf_file = {
  mam_revenue_fund_live_case_trigger = yes var:mam_cf_actor = root
  var:mam_cf_generation = scope:mam_cf_generation
  var:mam_cf_stage = scope:mam_cf_stage
  trigger_if = { limit = { var:mam_cf_stage = 0 var:mam_cf_kind != 4 var:mam_cf_kind != 5 var:mam_cf_kind != 7 }
   var:mam_cf_actor = title:e_minister_of_revenue.holder
   var:mam_cf_actor = { mam_revenue_officer_trigger = yes }
  }
  trigger_if = { limit = { OR = { var:mam_cf_stage = 1 var:mam_cf_kind = 5 var:mam_cf_kind = 7 } }
   OR = { var:mam_cf_actor = title:h_china.holder
    AND = { mam_revenue_fund_imperial_trigger = no var:mam_cf_actor = title:e_minister_chancellor.holder
     var:mam_cf_actor = { mam_revenue_chancellor_trigger = yes } }
   }
  }
  trigger_if = { limit = { var:mam_cf_stage = 2 } var:mam_cf_actor = var:mam_cf_target.holder }
  trigger_if = { limit = { var:mam_cf_kind = 4 }
   OR = { var:mam_cf_actor = title:h_china.holder
    AND = { var:mam_cf_actor = title:e_minister_chancellor.holder var:mam_cf_actor = { mam_revenue_chancellor_trigger = yes } }
   }
  }
 }
}
# Story scope. Rechecked at commitment; the law changes control rights.
mam_revenue_fund_imperial_trigger = {
  OR = {
  var:mam_cf_kind = 5 var:mam_cf_target = title:e_minister_chancellor
  title:h_china.holder = { has_realm_law = mam_revenue_authority_reserved }
  AND = { var:mam_cf_target.holder = { mam_revenue_reserved_ministry_trigger = yes } var:mam_cf_kind != 8 }
  AND = { var:mam_cf_kind = 4 title:h_china = { has_variable = mam_cf_imperial_programme } }
  has_variable = mam_cf_explicit_imperial
 }
}
mam_revenue_fund_delegated_trigger = {
 title:h_china = { NOT = { has_variable = mam_cf_suspended } }
 title:h_china.holder = { has_realm_law = mam_revenue_authority_expanded }
 mam_revenue_fund_imperial_trigger = no
 var:mam_cf_kind != 4 var:mam_cf_kind != 7 var:mam_cf_kind != 8
 var:mam_cf_target != title:e_minister_of_revenue
 var:mam_cf_amount <= 500
 trigger_if = { limit = { OR = { var:mam_cf_kind = 3 var:mam_cf_kind = 9 } }
  title:h_china = { var:mam_cf_programme = 0 }
 }
 trigger_if = { limit = { var:mam_cf_kind = 6 }
  var:mam_cf_amount <= 200 var:mam_cf_target.holder = { mam_revenue_has_recovery_need_trigger = no }
 }
}
mam_revenue_fund_project_start_trigger = {
 primary_title = {
  NOT = { has_variable = mam_cf_payment_hold }
  has_variable = mam_cf_project_type var:mam_cf_project_type = $TYPE$
  has_variable = mam_cf_project_until var:mam_cf_project_until > current_date
  NOT = { has_variable = mam_cf_project_instance }
  var:mam_cf_project_cash >= $COST$
 }
}
mam_revenue_fund_project_location_trigger = {
 primary_title = {
  exists = var:mam_cf_project_target.holder
  save_temporary_scope_as = mam_cf_project_office
  scope:province.county.holder = {
   OR = { this = scope:mam_cf_project_office.var:mam_cf_project_target.holder
    is_vassal_or_below_of = scope:mam_cf_project_office.var:mam_cf_project_target.holder }
  }
 }
}
mam_revenue_fund_contribution_trigger = {
 exists = scope:great_project
 primary_title = {
  NOT = { has_variable = mam_cf_payment_hold }
  var:mam_cf_project_instance = scope:great_project
  var:mam_cf_project_until > current_date var:mam_cf_project_cash >= $COST$
 }
}
''')

write('common/story_cycles/mam_revenue_common_story.txt', r'''
mam_revenue_fund_story = {
 visible = no on_setup = { }
 on_owner_death = {
  title:h_china.holder ?= { if = { limit = { is_alive = yes } save_scope_as = mam_cf_heir } }
  if = { limit = { exists = scope:mam_cf_heir } make_story_owner = scope:mam_cf_heir }
 }
 effect_group = { days = 30 triggered_effect = {
  trigger = { always = yes }
  effect = {
   if = { limit = { var:mam_cf_pending = 1 }
    if = { limit = { OR = { mam_revenue_fund_live_case_trigger = no AND = { var:mam_cf_kind < 10 var:mam_cf_created <= { value = current_date subtract = 365 } } } }
     mam_revenue_fund_close_effect = { RESULT = 4 }
    }
    else = { title:h_china.holder ?= { mam_revenue_fund_wake_effect = yes } }
   }
   else_if = { limit = { var:mam_cf_closed <= { value = current_date subtract = 365 } } end_story = yes }
  }
 } }
}
''')

core = r'''
# Title scope. Identity and operating authorisations persist with the office.
mam_revenue_fund_init_office_effect = {
 if = { limit = { NOT = { has_variable = mam_cf_cost } }
  set_variable = { name = mam_cf_cost value = holder.mam_revenue_fund_observed_cost }
  set_variable = { name = mam_cf_headroom value = 75 }
  set_variable = { name = mam_cf_project_cash value = 0 }
  set_variable = { name = mam_cf_special_target value = 0 }
  set_variable = { name = mam_cf_period_end value = { value = current_date add = 90 } }
  set_variable = { name = mam_cf_remaining value = { value = var:mam_cf_cost multiply = 5 add = 150 } }
  set_variable = { name = mam_cf_issued value = 0 }
 }
 if = { limit = { var:mam_cf_period_end <= current_date }
  set_variable = { name = mam_cf_period_end value = { value = current_date add = 90 } }
  set_variable = { name = mam_cf_remaining value = { value = var:mam_cf_cost multiply = 3 add = var:mam_cf_headroom } }
  set_variable = { name = mam_cf_issued value = 0 }
 }
 # Retire individual recipient-rate settings. The overall native budget is intact.
 if = { limit = { has_variable = mam_cf_special_until var:mam_cf_special_until <= current_date }
  set_variable = { name = mam_cf_special_target value = 0 } remove_variable = mam_cf_special_until
 }
 if = { limit = { holder = { mam_revenue_budget_office_trigger = yes
  NOT = { vassal_contract_obligation_level:celestial_ministry_budget = 1 } } }
  holder = { vassal_contract_set_obligation_level = { type = celestial_ministry_budget level = 1 } }
 }
 # Unspent project advances expire after one year; cash is returned by the sweep.
 # An active native project is retained across succession until its grant expires.
 if = { limit = { has_variable = mam_cf_project_until var:mam_cf_project_until <= current_date }
  set_variable = { name = mam_cf_project_cash value = 0 }
  remove_variable = mam_cf_project_type remove_variable = mam_cf_project_target
  remove_variable = mam_cf_project_instance remove_variable = mam_cf_project_until
 }
}
mam_revenue_fund_start_effect = {
 if = { limit = { mam_revenue_emperor_trigger = yes }
  title:h_china = {
   if = { limit = { NOT = { has_variable = mam_cf_active } }
    set_variable = { name = mam_cf_active value = 1 }
    set_variable = { name = mam_cf_programme value = 0 }
    set_variable = { name = mam_cf_serial value = 0 }
    set_variable = { name = mam_cf_reserve value = 200 }
    set_variable = { name = mam_cf_unfunded value = 0 }
    set_variable = { name = mam_cf_total_cost value = 0 }
    set_variable = { name = mam_cf_receipt_count value = 0 }
    # Pending dev.48 proposals cannot spend under the superseded authority.
    every_in_list = { variable = mam_rv_files limit = { var:mam_rv_pending = 1 }
     set_variable = { name = mam_rv_result value = 4 } mam_revenue_close_effect = yes
    }
    if = { limit = { holder = { NOR = {
     has_realm_law = mam_revenue_authority_reserved has_realm_law = mam_revenue_authority_limited
     has_realm_law = mam_revenue_authority_expanded } } }
     holder = { add_realm_law_skip_effects = mam_revenue_authority_reserved }
    }
   }
  }
  @INIT@
  mam_revenue_fund_month_effect = yes
  mam_revenue_fund_wake_effect = yes
 }
}
# All module transfers use this single native payment boundary. Bind payer,
# payee, amount and protected floor first. Never transfer to oneself or retry an
# uncertain debit. Both readings remain on the imperial title for save inspection.
mam_revenue_fund_transfer_effect = {
 save_scope_value_as = { name = mam_cf_paid value = 0 }
 save_scope_value_as = { name = mam_cf_uncertain value = 0 }
 if = { limit = {
  exists = scope:mam_cf_payer exists = scope:mam_cf_payee scope:mam_cf_payer != scope:mam_cf_payee
  scope:mam_cf_amount > 0 scope:mam_cf_payer = { has_treasury = yes top_liege = title:h_china.holder
   treasury >= { value = scope:mam_cf_amount add = scope:mam_cf_floor }
   primary_title = { NOT = { has_variable = mam_cf_payment_hold } }
  }
  scope:mam_cf_payee = { has_treasury = yes top_liege = title:h_china.holder
   primary_title = { NOT = { has_variable = mam_cf_payment_hold } }
  }
 }
  title:h_china = {
   set_variable = { name = mam_cf_last_payer value = scope:mam_cf_payer }
   set_variable = { name = mam_cf_last_payee value = scope:mam_cf_payee }
   set_variable = { name = mam_cf_last_payer_title value = scope:mam_cf_payer.primary_title }
   set_variable = { name = mam_cf_last_payee_title value = scope:mam_cf_payee.primary_title }
   set_variable = { name = mam_cf_last_amount value = scope:mam_cf_amount }
   set_variable = { name = mam_cf_before_payer value = scope:mam_cf_payer.treasury }
   set_variable = { name = mam_cf_before_payee value = scope:mam_cf_payee.treasury }
   set_variable = { name = mam_cf_receipt_state value = 1 }
  }
  scope:mam_cf_payer = { pay_short_term_treasury = { target = scope:mam_cf_payee treasury = scope:mam_cf_amount } }
  title:h_china = {
   set_variable = { name = mam_cf_after_payer value = scope:mam_cf_payer.treasury }
   set_variable = { name = mam_cf_after_payee value = scope:mam_cf_payee.treasury }
   set_variable = { name = mam_cf_debit value = { value = var:mam_cf_before_payer subtract = var:mam_cf_after_payer } }
   set_variable = { name = mam_cf_credit value = { value = var:mam_cf_after_payee subtract = var:mam_cf_before_payee } }
   if = { limit = {
    var:mam_cf_debit > 0 var:mam_cf_credit > 0
    var:mam_cf_debit >= { value = scope:mam_cf_amount subtract = 0.01 }
    var:mam_cf_debit <= { value = scope:mam_cf_amount add = 0.01 }
    var:mam_cf_credit >= { value = scope:mam_cf_amount subtract = 0.01 }
    var:mam_cf_credit <= { value = scope:mam_cf_amount add = 0.01 }
   }
    set_variable = { name = mam_cf_receipt_state value = 2 }
    change_variable = { name = mam_cf_receipt_count add = 1 }
    save_scope_value_as = { name = mam_cf_paid value = scope:mam_cf_amount }
   }
   else = {
    set_variable = { name = mam_cf_receipt_state value = 3 }
    save_scope_value_as = { name = mam_cf_uncertain value = 1 }
    scope:mam_cf_payer.primary_title = { set_variable = { name = mam_cf_payment_hold value = 1 } }
    scope:mam_cf_payee.primary_title = { set_variable = { name = mam_cf_payment_hold value = 1 } }
    debug_log = "MAM_COMMON_FUND: uncertain native debit/credit; affected accounts held; no retry"
   }
  }
 }
}
# Title scope. Sweeps never include project earmarks or the operating target.
mam_revenue_fund_sweep_effect = {
 if = { limit = { this != title:e_minister_of_revenue holder.treasury > mam_revenue_fund_cash_target }
  holder = { save_scope_as = mam_cf_payer }
  title:e_minister_of_revenue.holder = { save_scope_as = mam_cf_payee }
  save_scope_value_as = { name = mam_cf_floor value = mam_revenue_fund_cash_target }
  save_scope_value_as = { name = mam_cf_amount value = { value = holder.treasury subtract = mam_revenue_fund_cash_target floor = yes min = 0 } }
  mam_revenue_fund_transfer_effect = yes
 }
}
mam_revenue_fund_count_effect = {
 title:h_china = { change_variable = { name = mam_cf_total_cost add = prev.var:mam_cf_cost } }
 if = { limit = { this != title:e_minister_of_revenue }
  save_scope_value_as = { name = mam_cf_shortfall value = { value = mam_revenue_fund_target subtract = holder.treasury add = var:mam_cf_project_cash min = 0 max = var:mam_cf_remaining } }
  title:h_china = { change_variable = { name = mam_cf_unfunded add = scope:mam_cf_shortfall } }
 }
}
mam_revenue_fund_count_essential_effect = {
 if = { limit = { this != title:e_minister_of_revenue }
  save_scope_value_as = { name = mam_cf_essential_gap value = {
   value = var:mam_cf_cost multiply = 2 add = var:mam_cf_project_cash subtract = holder.treasury
   min = 0 max = var:mam_cf_remaining
  } }
  title:h_china = { change_variable = { name = mam_cf_essential_due add = scope:mam_cf_essential_gap } }
 }
}
# Two passes: protected salaries/standing armies before discretionary buffers.
mam_revenue_fund_refill_effect = {
 if = { limit = { this != title:e_minister_of_revenue var:mam_cf_remaining > 0 }
  save_scope_value_as = { name = mam_cf_goal value = { value = var:mam_cf_cost multiply = 2 add = var:mam_cf_project_cash } }
  if = { limit = { always = $EXTRA$ }
   save_scope_value_as = { name = mam_cf_goal value = mam_revenue_fund_cash_target }
  }
  save_scope_value_as = { name = mam_cf_floor value = title:e_minister_of_revenue.mam_revenue_fund_cash_target }
  if = { limit = { always = $EXTRA$ }
   save_scope_value_as = { name = mam_cf_floor value = { value = scope:mam_cf_floor add = title:h_china.var:mam_cf_reserve } }
  }
  save_scope_value_as = { name = mam_cf_amount value = {
   value = scope:mam_cf_goal subtract = holder.treasury min = 0 max = var:mam_cf_remaining
   max = { value = title:e_minister_of_revenue.holder.treasury subtract = scope:mam_cf_floor min = 0 }
   floor = yes
  } }
  if = { limit = { always = $EXTRA$ } }
  else_if = { limit = { title:h_china.var:mam_cf_essential_due > 0 }
   save_scope_value_as = { name = mam_cf_amount value = { value = scope:mam_cf_amount
    max = { value = title:h_china.var:mam_cf_essential_cash
     multiply = { value = scope:mam_cf_goal subtract = holder.treasury min = 0 max = var:mam_cf_remaining }
     divide = title:h_china.var:mam_cf_essential_due floor = yes }
   } }
  }
  holder = { save_scope_as = mam_cf_payee }
  title:e_minister_of_revenue.holder = { save_scope_as = mam_cf_payer }
  mam_revenue_fund_transfer_effect = yes
  change_variable = { name = mam_cf_remaining subtract = scope:mam_cf_paid }
  change_variable = { name = mam_cf_issued add = scope:mam_cf_paid }
 }
}
mam_revenue_fund_month_effect = {
 if = { limit = { mam_revenue_emperor_trigger = yes mam_revenue_fund_enabled_trigger = yes
  OR = { title:h_china = { NOT = { has_variable = mam_cf_next_month } } title:h_china.var:mam_cf_next_month <= current_date }
 }
  title:h_china = { set_variable = { name = mam_cf_next_month value = { value = current_date add = 25 } } }
  @INIT@
  if = { limit = { exists = title:e_minister_of_revenue.holder title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes } }
   @SWEEP@
   title:h_china = {
    set_variable = { name = mam_cf_essential_due value = 0 }
    set_variable = { name = mam_cf_essential_cash value = { value = title:e_minister_of_revenue.holder.treasury
     subtract = title:e_minister_of_revenue.mam_revenue_fund_cash_target min = 0 } }
   }
   @ESSENTIAL_COUNT@
   @ESSENTIAL@
   @EXTRA@
   title:h_china = {
    set_variable = { name = mam_cf_total_cost value = 0 }
    set_variable = { name = mam_cf_unfunded value = 0 }
   }
   @COUNT@
   title:h_china = {
    set_variable = { name = mam_cf_reserve value = { value = var:mam_cf_total_cost multiply = 2 add = 200 } }
    if = { limit = { var:mam_cf_programme = 1 } change_variable = { name = mam_cf_reserve add = 500 } }
    if = { limit = { var:mam_cf_programme = 2 } change_variable = { name = mam_cf_reserve add = 300 } }
   }
   mam_revenue_fund_initiative_effect = yes
  }
  mam_revenue_fund_wake_effect = yes
 }
}
mam_revenue_fund_refresh_totals_effect = {
 title:h_china = {
  set_variable = { name = mam_cf_total_cost value = 0 }
  set_variable = { name = mam_cf_unfunded value = 0 }
  set_variable = { name = mam_cf_essential_due value = 0 }
  set_variable = { name = mam_cf_claims_due value = 0 }
  every_in_list = { variable = mam_cf_cases limit = { var:mam_cf_pending = 1 var:mam_cf_kind >= 10 }
   save_scope_value_as = { name = mam_cf_liability value = var:mam_cf_amount }
   title:h_china = { change_variable = { name = mam_cf_claims_due add = scope:mam_cf_liability } }
  }
 }
 @COUNT@
 @ESSENTIAL_COUNT@
 title:h_china = {
  set_variable = { name = mam_cf_reserve value = { value = var:mam_cf_total_cost multiply = 2 add = 200 } }
  if = { limit = { var:mam_cf_programme = 1 } change_variable = { name = mam_cf_reserve add = 500 } }
  if = { limit = { var:mam_cf_programme = 2 } change_variable = { name = mam_cf_reserve add = 300 } }
  change_variable = { name = mam_cf_reserve add = var:mam_cf_claims_due }
 }
}
'''
core = core.replace('@INIT@', roster('mam_revenue_fund_init_office_effect = yes'))
core = core.replace('@SWEEP@', roster('mam_revenue_fund_sweep_effect = yes'))
core = core.replace('@ESSENTIAL@', roster('mam_revenue_fund_refill_effect = { EXTRA = no }'))
core = core.replace('@EXTRA@', roster('mam_revenue_fund_refill_effect = { EXTRA = yes }'))
core = core.replace('@COUNT@', roster('mam_revenue_fund_count_effect = yes'))
core = core.replace('@ESSENTIAL_COUNT@', roster('mam_revenue_fund_count_essential_effect = yes'))
write('common/scripted_effects/mam_revenue_common_cash_effects.txt', core)

write('common/on_action/mam_revenue_on_actions.txt', r'''
on_game_start_after_lobby = { on_actions = { mam_revenue_fund_startup } }
mam_revenue_fund_startup = { effect = {
 every_independent_ruler = { limit = { mam_revenue_emperor_trigger = yes } mam_revenue_fund_start_effect = yes }
} }
monthly_playable_pulse = { on_actions = { mam_revenue_fund_monthly } }
mam_revenue_fund_monthly = { trigger = { mam_revenue_emperor_trigger = yes }
 effect = { mam_revenue_fund_start_effect = yes }
}
on_title_gain = { on_actions = { mam_revenue_fund_office_gain } }
mam_revenue_fund_office_gain = {
 trigger = { exists = scope:title OR = { scope:title = title:h_china scope:title = { tgp_is_minister_title = yes } } }
 effect = { title:h_china.holder ?= { trigger_event = { id = mam_fund.99 days = 3 } } }
}
''')

write('common/scripted_effects/mam_revenue_common_queue_effects.txt', r'''
# Character caller; TARGET is an office title, never an account-name string.
mam_revenue_fund_request_effect = {
 clear_saved_scope = mam_cf_created
 save_scope_as = mam_cf_requester
 $TARGET$ = { save_scope_as = mam_cf_request_title }
 save_scope_value_as = { name = mam_cf_requested_amount value = $AMOUNT$ }
 scope:mam_cf_request_title = {
  if = { limit = { has_variable = mam_cf_case_$KIND$ }
   if = { limit = { NOT = { exists = var:mam_cf_case_$KIND$ } } remove_variable = mam_cf_case_$KIND$ }
   else_if = { limit = { var:mam_cf_case_$KIND$ = { mam_revenue_fund_live_case_trigger = no } }
    remove_variable = mam_cf_case_$KIND$
   }
  }
 }
 if = { limit = { mam_revenue_fund_enabled_trigger = yes exists = scope:mam_cf_request_title.holder
  exists = title:e_minister_of_revenue.holder
  title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }
  scope:mam_cf_request_title = { NOT = { has_variable = mam_cf_case_$KIND$ } }
 }
  title:h_china.holder = { create_story = { type = mam_revenue_fund_story save_scope_as = mam_cf_created } }
  if = { limit = { exists = scope:mam_cf_created }
   title:h_china = {
    change_variable = { name = mam_cf_serial add = 1 }
    add_to_variable_list = { name = mam_cf_cases target = scope:mam_cf_created }
   }
   scope:mam_cf_created = {
    set_variable = { name = mam_cf_target value = scope:mam_cf_request_title }
    set_variable = { name = mam_cf_snapshot value = scope:mam_cf_request_title.holder }
    set_variable = { name = mam_cf_requester value = scope:mam_cf_requester }
    set_variable = { name = mam_cf_emperor value = title:h_china.holder }
    set_variable = { name = mam_cf_revenue value = title:e_minister_of_revenue.holder }
    set_variable = { name = mam_cf_kind value = $KIND$ }
    set_variable = { name = mam_cf_amount value = scope:mam_cf_requested_amount }
    set_variable = { name = mam_cf_cost value = 0 }
    set_variable = { name = mam_cf_headroom value = 75 }
    set_variable = { name = mam_cf_mode value = 0 }
    set_variable = { name = mam_cf_pending value = 1 }
    set_variable = { name = mam_cf_stage value = 0 }
    if = { limit = { OR = { var:mam_cf_kind = 5 var:mam_cf_kind = 7 } }
     set_variable = { name = mam_cf_stage value = 1 }
    }
    set_variable = { name = mam_cf_generation value = 0 }
    set_variable = { name = mam_cf_serial value = title:h_china.var:mam_cf_serial }
    set_variable = { name = mam_cf_created value = current_date }
   }
   scope:mam_cf_request_title = { set_variable = { name = mam_cf_case_$KIND$ value = scope:mam_cf_created } }
  }
 }
}
mam_revenue_fund_release_effect = {
 save_scope_as = mam_cf_releasing
 var:mam_cf_actor ?= { if = { limit = { exists = var:mam_cf_open var:mam_cf_open = scope:mam_cf_releasing } remove_variable = mam_cf_open } }
 remove_variable = mam_cf_actor remove_variable = mam_cf_presented
 if = { limit = { mam_revenue_fund_earned_claim_trigger = no }
  title:h_china.holder ?= { trigger_event = { id = mam_fund.98 days = 2 } }
 }
}
mam_revenue_fund_close_effect = {
 save_scope_as = mam_cf_closing
 set_variable = { name = mam_cf_pending value = 0 }
 set_variable = { name = mam_cf_result value = $RESULT$ }
 set_variable = { name = mam_cf_closed value = current_date }
 @CLEAR@
 every_in_list = { variable = mam_cf_claim_counties limit = { var:mam_cf_insurance_claim = scope:mam_cf_closing }
  remove_variable = mam_cf_insurance_claim
 }
 title:h_china = { remove_list_variable = { name = mam_cf_cases target = scope:mam_cf_closing } }
 mam_revenue_fund_release_effect = yes
}
# Story scope, choose the current legal reviewer every time. A changed office or
# law invalidates the old actor lease before another event is displayed.
mam_revenue_fund_resolve_effect = {
 clear_saved_scope = mam_cf_next_actor
 if = { limit = { mam_revenue_fund_live_case_trigger = yes }
  if = { limit = { exists = title:e_minister_of_revenue.holder
   var:mam_cf_revenue != title:e_minister_of_revenue.holder
   var:mam_cf_kind != 4 var:mam_cf_kind != 5 var:mam_cf_kind != 7
  }
   set_variable = { name = mam_cf_revenue value = title:e_minister_of_revenue.holder }
   set_variable = { name = mam_cf_stage value = 0 }
   remove_variable = mam_cf_authorized
   mam_revenue_fund_release_effect = yes
  }
  if = { limit = { var:mam_cf_stage = 2 }
   var:mam_cf_target.holder = { save_scope_as = mam_cf_next_actor }
  }
  else_if = { limit = { var:mam_cf_kind = 4 var:mam_cf_stage = 0
   exists = title:e_minister_chancellor.holder title:e_minister_chancellor.holder = { mam_revenue_chancellor_trigger = yes }
   var:mam_cf_requester != title:h_china.holder title:h_china = { NOT = { has_variable = mam_cf_imperial_programme } }
  } title:e_minister_chancellor.holder = { save_scope_as = mam_cf_next_actor } }
  else_if = { limit = { OR = { var:mam_cf_stage = 1 var:mam_cf_kind = 4 var:mam_cf_kind = 5 var:mam_cf_kind = 7 } }
   if = { limit = { OR = { mam_revenue_fund_imperial_trigger = yes
    NOT = { exists = title:e_minister_chancellor.holder }
    title:e_minister_chancellor.holder = { mam_revenue_chancellor_trigger = no }
   } }
    title:h_china.holder = { save_scope_as = mam_cf_next_actor }
   }
   else = { title:e_minister_chancellor.holder = { save_scope_as = mam_cf_next_actor } }
  }
  else = { title:e_minister_of_revenue.holder ?= { if = { limit = { mam_revenue_officer_trigger = yes } save_scope_as = mam_cf_next_actor } } }
 }
}
mam_revenue_fund_wake_effect = {
 if = { limit = { mam_revenue_emperor_trigger = yes mam_revenue_fund_enabled_trigger = yes }
  title:h_china = {
   every_in_list = { variable = mam_cf_cases
    if = { limit = { mam_revenue_fund_live_case_trigger = no } mam_revenue_fund_close_effect = { RESULT = 4 } }
    else_if = { limit = { var:mam_cf_kind >= 10 } mam_revenue_fund_claim_commit_effect = yes }
    else = {
     mam_revenue_fund_resolve_effect = yes
     if = { limit = { exists = var:mam_cf_actor OR = { NOT = { exists = scope:mam_cf_next_actor } var:mam_cf_actor != scope:mam_cf_next_actor } }
      mam_revenue_fund_release_effect = yes
     }
     if = { limit = { exists = scope:mam_cf_next_actor }
      set_variable = { name = mam_cf_next_actor value = scope:mam_cf_next_actor }
     }
     else = { remove_variable = mam_cf_next_actor }
    }
   }
   every_in_list = { variable = mam_cf_cases limit = { mam_revenue_fund_live_case_trigger = yes exists = var:mam_cf_next_actor }
    var:mam_cf_next_actor = {
     if = { limit = { has_variable = mam_cf_open OR = { NOT = { exists = var:mam_cf_open } var:mam_cf_open = { mam_revenue_fund_live_case_trigger = no } } } remove_variable = mam_cf_open }
     if = { limit = { NOT = { has_variable = mam_cf_open } is_alive = yes is_imprisoned = no NOT = { has_trait = incapable } }
      save_scope_as = mam_cf_queue_actor
      clear_saved_scope = mam_cf_next_file
      title:h_china = { ordered_in_list = { variable = mam_cf_cases
       limit = { mam_revenue_fund_live_case_trigger = yes NOT = { has_variable = mam_cf_actor }
        var:mam_cf_next_actor = scope:mam_cf_queue_actor
        trigger_if = { limit = { has_variable = mam_cf_snooze } var:mam_cf_snooze <= current_date }
       }
       order_by = mam_revenue_fund_queue_score max = 1 check_range_bounds = no save_scope_as = mam_cf_next_file
      } }
      if = { limit = { exists = scope:mam_cf_next_file }
       set_variable = { name = mam_cf_open value = scope:mam_cf_next_file }
       scope:mam_cf_next_file = {
        set_variable = { name = mam_cf_actor value = scope:mam_cf_queue_actor }
        change_variable = { name = mam_cf_generation add = 1 }
       }
       trigger_event = { id = mam_fund.90 days = 1 }
      }
     }
    }
   }
  }
 }
}
mam_revenue_fund_bind_effect = {
 clear_saved_scope = mam_cf_result_payer clear_saved_scope = mam_cf_result_payee
 clear_saved_scope = mam_cf_result_payer_title clear_saved_scope = mam_cf_result_payee_title
 clear_saved_scope = mam_cf_selected_project clear_saved_scope = mam_cf_project_target
 mam_revenue_fund_refresh_totals_effect = yes
 scope:mam_cf_file = {
  var:mam_cf_target = { save_scope_as = mam_cf_title }
  var:mam_cf_target.holder = { save_scope_as = mam_cf_subject }
  var:mam_cf_requester = { save_scope_as = mam_cf_sender }
  if = { limit = { var:mam_cf_pending = 0 }
   var:mam_cf_authorized ?= { save_scope_as = mam_cf_sender }
   var:mam_cf_decider ?= { save_scope_as = mam_cf_sender }
  }
  if = { limit = { var:mam_cf_stage = 1 exists = title:e_minister_of_revenue.holder } title:e_minister_of_revenue.holder = { save_scope_as = mam_cf_sender } }
  save_scope_value_as = { name = mam_cf_generation value = var:mam_cf_generation }
  save_scope_value_as = { name = mam_cf_stage value = var:mam_cf_stage }
  save_scope_value_as = { name = mam_cf_quote value = var:mam_cf_amount }
  save_scope_value_as = { name = mam_cf_half value = { value = var:mam_cf_amount divide = 2 floor = yes min = 1 } }
  save_scope_value_as = { name = mam_cf_cost value = var:mam_cf_cost }
  save_scope_value_as = { name = mam_cf_headroom value = var:mam_cf_headroom }
  var:mam_cf_project_target ?= { save_scope_as = mam_cf_project_target }
  var:mam_cf_project_instance ?= { save_scope_as = mam_cf_selected_project }
  var:mam_cf_paid_from ?= { save_scope_as = mam_cf_result_payer }
  var:mam_cf_paid_to ?= { save_scope_as = mam_cf_result_payee }
  var:mam_cf_paid_from_title ?= { save_scope_as = mam_cf_result_payer_title }
  var:mam_cf_paid_to_title ?= { save_scope_as = mam_cf_result_payee_title }
  if = { limit = { has_variable = mam_cf_paid_amount } save_scope_value_as = { name = mam_cf_result_amount value = var:mam_cf_paid_amount } }
 }
 title:h_china.holder = { save_scope_as = mam_cf_emperor }
 title:e_minister_of_revenue.holder ?= { save_scope_as = mam_cf_custodian }
 if = { limit = { scope:mam_cf_file.var:mam_cf_pending = 0 scope:mam_cf_sender = root }
  if = { limit = { scope:mam_cf_subject != root } scope:mam_cf_subject = { save_scope_as = mam_cf_sender } }
  else_if = { limit = { exists = scope:mam_cf_custodian scope:mam_cf_custodian != root } scope:mam_cf_custodian = { save_scope_as = mam_cf_sender } }
 }
 save_scope_value_as = { name = mam_cf_free value = title:h_china.mam_revenue_fund_available }
 save_scope_value_as = { name = mam_cf_fund_balance value = 0 }
 title:e_minister_of_revenue.holder ?= { save_scope_value_as = { name = mam_cf_fund_balance value = treasury } }
 save_scope_value_as = { name = mam_cf_reserve value = title:h_china.var:mam_cf_reserve }
 save_scope_value_as = { name = mam_cf_monthly value = title:h_china.var:mam_cf_total_cost }
 save_scope_value_as = { name = mam_cf_max value = scope:mam_cf_free }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 2 title:h_china.var:mam_cf_programme = 2 }
  save_scope_value_as = { name = mam_cf_max value = { value = scope:mam_cf_free add = 300
   max = { value = scope:mam_cf_fund_balance subtract = title:e_minister_of_revenue.mam_revenue_fund_cash_target
    subtract = title:h_china.var:mam_cf_unfunded subtract = { value = title:h_china.var:mam_cf_reserve subtract = 300 } min = 0 }
  } }
 }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 5 }
  save_scope_value_as = { name = mam_cf_max value = { value = title:h_china.holder.treasury subtract = 500 min = 0 floor = yes } }
 }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 6 }
  save_scope_value_as = { name = mam_cf_max value = { value = scope:mam_cf_subject.treasury subtract = 200 min = 0 floor = yes } }
 }
}
mam_revenue_fund_present_effect = {
 if = { limit = { exists = var:mam_cf_open var:mam_cf_open = { mam_revenue_fund_live_case_trigger = yes NOT = { has_variable = mam_cf_presented } } }
  var:mam_cf_open = { save_scope_as = mam_cf_file }
  mam_revenue_fund_bind_effect = yes
  if = { limit = { mam_revenue_fund_actor_trigger = yes }
   scope:mam_cf_file = { set_variable = { name = mam_cf_presented value = 1 } }
   if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 4 } trigger_event = mam_fund.4 }
   else_if = { limit = { OR = { scope:mam_cf_file.var:mam_cf_kind = 1 scope:mam_cf_file.var:mam_cf_kind = 7 } } trigger_event = mam_fund.2 }
   else = { trigger_event = mam_fund.1 }
  }
 }
}
mam_revenue_fund_defer_effect = {
 if = { limit = { mam_revenue_fund_actor_trigger = yes }
  scope:mam_cf_file = { set_variable = { name = mam_cf_snooze value = { value = current_date add = 30 } } mam_revenue_fund_release_effect = yes }
 }
}
'''.replace('@CLEAR@', '\n'.join(f'if = {{ limit = {{ var:mam_cf_kind = {i} }} var:mam_cf_target = {{ if = {{ limit = {{ has_variable = mam_cf_case_{i} var:mam_cf_case_{i} = scope:mam_cf_closing }} remove_variable = mam_cf_case_{i} }} }} }}' for i in range(1,13))))

write('common/scripted_effects/mam_revenue_common_choice_effects.txt', r'''
mam_revenue_fund_recommend_effect = {
 if = { limit = { mam_revenue_fund_actor_trigger = yes }
  scope:mam_cf_file = {
   if = { limit = { var:mam_cf_kind = 1 }
    set_variable = { name = mam_cf_amount value = { value = var:mam_cf_cost subtract = var:mam_cf_target.var:mam_cf_cost
     multiply = 3 add = var:mam_cf_headroom subtract = var:mam_cf_target.var:mam_cf_headroom min = 0 } }
   }
   if = { limit = { var:mam_cf_kind = 6 NOT = { exists = var:mam_cf_consent } }
    set_variable = { name = mam_cf_stage value = 2 } mam_revenue_fund_release_effect = yes
   }
   else_if = { limit = { mam_revenue_fund_delegated_trigger = yes }
    set_variable = { name = mam_cf_authorized value = root } mam_revenue_fund_commit_effect = yes
   }
   else = { set_variable = { name = mam_cf_stage value = 1 } mam_revenue_fund_release_effect = yes }
  }
 }
}
mam_revenue_fund_approve_effect = {
 if = { limit = { mam_revenue_fund_actor_trigger = yes }
  scope:mam_cf_file = {
   set_variable = { name = mam_cf_authorized value = root }
   mam_revenue_fund_commit_effect = yes
  }
 }
}
mam_revenue_fund_refuse_effect = {
 if = { limit = { mam_revenue_fund_actor_trigger = yes }
  if = { limit = { has_trait = compassionate scope:mam_cf_file.var:mam_cf_kind = 2
   scope:mam_cf_subject = { mam_revenue_has_recovery_need_trigger = yes }
   scope:mam_cf_max >= scope:mam_cf_quote
  } add_stress = 15 }
  scope:mam_cf_file = {
   set_variable = { name = mam_cf_decider value = root }
   # A materially reduced allocation can be appealed once by its holder.
   if = { limit = { var:mam_cf_kind = 1 }
    var:mam_cf_target = {
     set_variable = { name = mam_cf_cut_before value = var:mam_cf_headroom }
     set_variable = { name = mam_cf_cut_until value = { value = current_date add = 180 } }
     set_variable = { name = mam_cf_cut_holder value = holder }
     remove_variable = mam_cf_appeal_used
     holder = { trigger_event = { id = mam_fund.97 days = 3 } }
    }
   }
   if = { limit = { var:mam_cf_kind = 2 }
    var:mam_cf_target = { set_variable = { name = mam_cf_relief_until value = { value = current_date add = 90 } } }
   }
   if = { limit = { var:mam_cf_kind = 6 }
    var:mam_cf_target = { set_variable = { name = mam_cf_remit_until value = { value = current_date add = 90 } } }
   }
   mam_revenue_fund_close_effect = { RESULT = 2 }
   mam_revenue_fund_notify_effect = yes
  }
 }
}
# Story scope. Authority and money are validated again at the actual payment.
mam_revenue_fund_commit_effect = {
 mam_revenue_fund_refresh_totals_effect = yes
 save_scope_as = mam_cf_committing
 if = { limit = { mam_revenue_fund_live_case_trigger = yes exists = var:mam_cf_authorized
  exists = title:e_minister_of_revenue.holder
  title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }
  trigger_if = { limit = { var:mam_cf_kind = 6 } var:mam_cf_consent = var:mam_cf_target.holder }
  trigger_if = { limit = { OR = { var:mam_cf_kind = 3 var:mam_cf_kind = 9 } }
   var:mam_cf_target = { var:mam_cf_project_cash = 0 }
  }
  trigger_if = { limit = { var:mam_cf_kind = 3 } exists = var:mam_cf_project_target.holder }
  trigger_if = { limit = { var:mam_cf_kind = 9 }
   exists = var:mam_cf_project_instance var:mam_cf_project_instance = { great_project_owner = { top_liege = title:h_china.holder } }
  }
  OR = {
   var:mam_cf_authorized = title:h_china.holder
   AND = { mam_revenue_fund_imperial_trigger = no var:mam_cf_authorized = title:e_minister_chancellor.holder
    title:e_minister_chancellor.holder = { mam_revenue_chancellor_trigger = yes } }
   AND = { mam_revenue_fund_delegated_trigger = yes var:mam_cf_authorized = title:e_minister_of_revenue.holder
    title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes } }
  }
 }
  if = { limit = { OR = { var:mam_cf_kind = 1 var:mam_cf_kind = 7 } }
   var:mam_cf_target = {
    if = { limit = { scope:mam_cf_committing.var:mam_cf_headroom < var:mam_cf_headroom }
     set_variable = { name = mam_cf_cut_before value = var:mam_cf_headroom }
     set_variable = { name = mam_cf_cut_until value = { value = current_date add = 180 } }
     set_variable = { name = mam_cf_cut_holder value = holder }
     remove_variable = mam_cf_appeal_used
     holder = { trigger_event = { id = mam_fund.97 days = 3 } }
     holder = { add_opinion = { target = scope:mam_cf_committing.var:mam_cf_authorized modifier = mam_revenue_fund_cut_opinion years = 2 } }
    }
    else_if = { limit = { scope:mam_cf_committing.var:mam_cf_headroom > var:mam_cf_headroom }
     holder = { add_opinion = { target = scope:mam_cf_committing.var:mam_cf_authorized modifier = mam_revenue_fund_support_opinion years = 2 } }
    }
    # Newly observed commitments become protected only through this approval.
    set_variable = { name = mam_cf_cost value = scope:mam_cf_committing.var:mam_cf_cost }
    set_variable = { name = mam_cf_headroom value = scope:mam_cf_committing.var:mam_cf_headroom }
    set_variable = { name = mam_cf_remaining value = { value = var:mam_cf_cost multiply = 3 add = var:mam_cf_headroom subtract = var:mam_cf_issued min = 0 } }
    set_variable = { name = mam_cf_review_until value = { value = current_date add = 90 } }
   }
   mam_revenue_fund_close_effect = { RESULT = 1 } mam_revenue_fund_notify_effect = yes
  }
  else_if = { limit = { var:mam_cf_kind = 4 }
   title:h_china = {
    set_variable = { name = mam_cf_programme value = scope:mam_cf_committing.var:mam_cf_mode }
    set_variable = { name = mam_cf_programme_until value = { value = current_date add = 365 } }
    set_variable = { name = mam_cf_programme_approved value = holder }
    if = { limit = { scope:mam_cf_committing.var:mam_cf_requester = holder } set_variable = { name = mam_cf_imperial_programme value = holder } }
   }
   mam_revenue_fund_close_effect = { RESULT = 1 } mam_revenue_fund_notify_effect = yes
  }
  else = {
   clear_saved_scope = mam_cf_payer clear_saved_scope = mam_cf_payee
   save_scope_value_as = { name = mam_cf_paid value = 0 }
   save_scope_value_as = { name = mam_cf_amount value = var:mam_cf_amount }
   save_scope_value_as = { name = mam_cf_floor value = { value = title:e_minister_of_revenue.mam_revenue_fund_cash_target
    add = title:h_china.var:mam_cf_reserve add = title:h_china.var:mam_cf_unfunded } }
   if = { limit = { var:mam_cf_kind = 2 title:h_china.var:mam_cf_programme = 2 }
    save_scope_value_as = { name = mam_cf_floor value = { value = scope:mam_cf_floor subtract = 300 min = 0 } }
   }
   title:e_minister_of_revenue.holder ?= { save_scope_as = mam_cf_payer }
   var:mam_cf_target.holder = { save_scope_as = mam_cf_payee }
   if = { limit = { var:mam_cf_kind = 5 }
    title:h_china.holder = { save_scope_as = mam_cf_payer }
    title:e_minister_of_revenue.holder ?= { save_scope_as = mam_cf_payee }
    save_scope_value_as = { name = mam_cf_floor value = 500 }
   }
   else_if = { limit = { var:mam_cf_kind = 6 }
    var:mam_cf_target.holder = { save_scope_as = mam_cf_payer }
    title:e_minister_of_revenue.holder ?= { save_scope_as = mam_cf_payee }
    save_scope_value_as = { name = mam_cf_floor value = 200 }
   }
   # Custodian projects reserve real cash locally; there is no self-payment.
   if = { limit = { OR = { var:mam_cf_kind = 3 var:mam_cf_kind = 9 var:mam_cf_kind = 12 }
    var:mam_cf_target = title:e_minister_of_revenue
    var:mam_cf_amount <= title:h_china.mam_revenue_fund_available
   }
    save_scope_value_as = { name = mam_cf_paid value = var:mam_cf_amount }
   }
   else_if = { limit = { exists = scope:mam_cf_payer exists = scope:mam_cf_payee }
    mam_revenue_fund_transfer_effect = yes
   }
   if = { limit = { scope:mam_cf_paid > 0 }
    set_variable = { name = mam_cf_paid_amount value = scope:mam_cf_paid }
    set_variable = { name = mam_cf_paid_from value = scope:mam_cf_payer }
    set_variable = { name = mam_cf_paid_to value = scope:mam_cf_payee }
    set_variable = { name = mam_cf_paid_from_title value = scope:mam_cf_payer.primary_title }
    set_variable = { name = mam_cf_paid_to_title value = scope:mam_cf_payee.primary_title }
    if = { limit = { var:mam_cf_kind = 12 }
     var:mam_cf_target = {
      change_variable = { name = mam_cf_special_target add = scope:mam_cf_paid }
      set_variable = { name = mam_cf_special_until value = { value = current_date add = 90 } }
     }
    }
    else_if = { limit = { OR = { var:mam_cf_kind = 3 var:mam_cf_kind = 9 } }
     var:mam_cf_target = {
      change_variable = { name = mam_cf_project_cash add = scope:mam_cf_paid }
      set_variable = { name = mam_cf_project_until value = { value = current_date add = 365 } }
      if = { limit = { scope:mam_cf_committing.var:mam_cf_kind = 3 }
       set_variable = { name = mam_cf_project_type value = scope:mam_cf_committing.var:mam_cf_project_type }
       set_variable = { name = mam_cf_project_target value = scope:mam_cf_committing.var:mam_cf_project_target }
       remove_variable = mam_cf_project_instance
      }
      else = { set_variable = { name = mam_cf_project_instance value = scope:mam_cf_committing.var:mam_cf_project_instance } }
     }
    }
    if = { limit = { var:mam_cf_kind = 2 }
     var:mam_cf_target = { set_variable = { name = mam_cf_relief_until value = { value = current_date add = 365 } } }
     var:mam_cf_target.holder = {
      save_scope_as = mam_cf_recovery_office
      add_character_modifier = { modifier = mam_revenue_recovery_office_modifier years = 1 }
      every_sub_realm_county = { limit = { county_control < 60 holder.top_liege = title:h_china.holder
       NOT = { holder = { mam_revenue_province_trigger = yes primary_title = { tier = tier_kingdom } this != scope:mam_cf_recovery_office } }
       NOT = { holder = { any_liege_or_above = {
        mam_revenue_province_trigger = yes primary_title = { tier = tier_kingdom }
        this != scope:mam_cf_recovery_office is_vassal_or_below_of = scope:mam_cf_recovery_office
       } } }
      }
       add_county_modifier = { modifier = mam_revenue_recovery_county_modifier years = 1 }
      }
     }
    }
    if = { limit = { var:mam_cf_kind = 6 }
     var:mam_cf_target = { set_variable = { name = mam_cf_remit_until value = { value = current_date add = 365 } } }
     var:mam_cf_target.holder = { add_opinion = { target = scope:mam_cf_committing.var:mam_cf_authorized modifier = mam_revenue_fund_levy_opinion years = 2 } }
    }
    else_if = { limit = { var:mam_cf_target != title:h_china }
     var:mam_cf_target.holder = { add_opinion = { target = scope:mam_cf_committing.var:mam_cf_authorized modifier = mam_revenue_fund_support_opinion years = 2 } }
    }
    mam_revenue_fund_native_rewards_effect = yes
    mam_revenue_fund_close_effect = { RESULT = 1 } mam_revenue_fund_notify_effect = yes
   }
   else = {
    # Failed/uncertain payments close without success or an automatic repeat.
    mam_revenue_fund_close_effect = { RESULT = 3 } mam_revenue_fund_notify_effect = yes
   }
  }
 }
 else = { mam_revenue_fund_release_effect = yes }
}
mam_revenue_fund_notify_effect = {
 save_scope_as = mam_cf_outcome
 var:mam_cf_requester ?= { if = { limit = { is_alive = yes is_ai = no }
  scope:mam_cf_outcome = { save_scope_as = mam_cf_file }
  mam_revenue_fund_bind_effect = yes
  trigger_event = { id = mam_fund.20 days = 1 }
 } }
 var:mam_cf_authorized ?= { if = { limit = { is_alive = yes is_ai = no this != scope:mam_cf_outcome.var:mam_cf_requester }
  scope:mam_cf_outcome = { save_scope_as = mam_cf_file }
  mam_revenue_fund_bind_effect = yes trigger_event = { id = mam_fund.20 days = 1 }
 } }
 var:mam_cf_decider ?= { if = { limit = { is_alive = yes is_ai = no this != scope:mam_cf_outcome.var:mam_cf_requester }
  scope:mam_cf_outcome = { save_scope_as = mam_cf_file }
  mam_revenue_fund_bind_effect = yes trigger_event = { id = mam_fund.20 days = 1 }
 } }
}
''')

write('common/scripted_effects/mam_revenue_common_initiative_effects.txt', r'''
# Character scope: establish a material operating review, never quietly endorse
# every new court position/regiment. One review per office per quarter.
mam_revenue_fund_open_operations_effect = {
 save_scope_as = mam_cf_reviewed
 mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 1 AMOUNT = 0 }
 if = { limit = { exists = scope:mam_cf_created }
  scope:mam_cf_created = {
   set_variable = { name = mam_cf_cost value = scope:mam_cf_reviewed.mam_revenue_fund_observed_cost }
   set_variable = { name = mam_cf_headroom value = scope:mam_cf_reviewed.primary_title.var:mam_cf_headroom }
   set_variable = { name = mam_cf_old_headroom value = scope:mam_cf_reviewed.primary_title.var:mam_cf_headroom }
   set_variable = { name = mam_cf_old_cost value = scope:mam_cf_reviewed.primary_title.var:mam_cf_cost }
  }
 }
}
mam_revenue_fund_open_relief_effect = {
 if = { limit = { mam_revenue_province_trigger = yes
  primary_title = { NOT = { has_variable = mam_cf_relief_until } }
 }
  mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 2 AMOUNT = 150 }
  if = { limit = { exists = scope:mam_cf_created }
   # Allow a smaller useful grant when the fund cannot meet the default request.
   # Projects are deliberately excluded: their native start must be fully paid.
   scope:mam_cf_created = {
    if = { limit = { title:h_china.mam_revenue_fund_available > 0 title:h_china.mam_revenue_fund_available < 150 }
     set_variable = { name = mam_cf_amount value = { value = title:h_china.mam_revenue_fund_available floor = yes min = 1 } }
    }
   }
  }
 }
}
# Target province/realm and type have been chosen in a character event. Quote the
# installed native starting cost; Influence and site eligibility remain native.
mam_revenue_fund_open_project_effect = {
 mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 3 AMOUNT = $COST$ }
 if = { limit = { exists = scope:mam_cf_created }
  scope:mam_cf_created = {
   set_variable = { name = mam_cf_project_type value = $TYPE$ }
   set_variable = { name = mam_cf_project_target value = scope:mam_cf_site_title }
  }
 }
}
mam_revenue_fund_open_contribution_effect = {
 mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 9 AMOUNT = great_project_base_contribution_cost }
 if = { limit = { exists = scope:mam_cf_created }
  scope:mam_cf_created = { set_variable = { name = mam_cf_project_instance value = scope:mam_cf_selected_project } }
 }
}
mam_revenue_fund_open_appeal_effect = {
 save_scope_as = mam_cf_appellant
 mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 7 AMOUNT = 0 }
 if = { limit = { exists = scope:mam_cf_created }
  primary_title = { set_variable = { name = mam_cf_appeal_used value = 1 } }
  scope:mam_cf_created = {
   set_variable = { name = mam_cf_cost value = scope:mam_cf_appellant.mam_revenue_fund_observed_cost }
   set_variable = { name = mam_cf_headroom value = scope:mam_cf_appellant.primary_title.var:mam_cf_cut_before }
  }
 }
}
mam_revenue_fund_initiative_effect = {
 # Unsolicited matters are bounded: quarterly, at most one operating review,
 # two genuine provincial needs, one contribution and one shortage proposal.
 if = { limit = { OR = { title:h_china = { NOT = { has_variable = mam_cf_next_review } }
  title:h_china.var:mam_cf_next_review <= current_date } }
  title:h_china = { set_variable = { name = mam_cf_next_review value = { value = current_date add = 90 } } }
  every_vassal_or_below = { limit = { mam_revenue_province_trigger = yes }
   primary_title = {
    if = { limit = { has_variable = mam_cf_relief_until var:mam_cf_relief_until <= current_date } remove_variable = mam_cf_relief_until }
    if = { limit = { has_variable = mam_cf_remit_until var:mam_cf_remit_until <= current_date } remove_variable = mam_cf_remit_until }
   }
  }
  random_vassal_or_below = { limit = {
   mam_revenue_ministry_trigger = yes
   primary_title = { NOT = { has_variable = mam_cf_case_1 }
    trigger_if = { limit = { has_variable = mam_cf_review_until } var:mam_cf_review_until <= current_date }
   }
   mam_revenue_fund_observed_cost > { value = primary_title.var:mam_cf_cost add = 10 }
  } mam_revenue_fund_open_operations_effect = yes }
  ordered_vassal_or_below = {
   limit = { mam_revenue_province_trigger = yes mam_revenue_has_recovery_need_trigger = yes mam_revenue_needs_help_trigger = yes
    primary_title = { NOT = { has_variable = mam_cf_relief_until } NOT = { has_variable = mam_cf_case_2 } }
   }
   order_by = mam_revenue_need_score max = 2 check_range_bounds = no
   mam_revenue_fund_open_relief_effect = yes
  }
  if = { limit = { title:h_china = { OR = { NOT = { has_variable = mam_cf_programme_until } var:mam_cf_programme_until <= current_date } }
   title:h_china = { NOT = { has_variable = mam_cf_case_4 } }
  }
   if = { limit = { exists = title:e_minister_chancellor.holder title:e_minister_chancellor.holder = { mam_revenue_chancellor_trigger = yes } }
    title:e_minister_chancellor.holder = { mam_revenue_fund_request_effect = { TARGET = title:h_china KIND = 4 AMOUNT = 0 } }
   }
   else = { mam_revenue_fund_request_effect = { TARGET = title:h_china KIND = 4 AMOUNT = 0 } }
  }
  if = { limit = { OR = { title:h_china.var:mam_cf_unfunded > 0 title:h_china.var:mam_cf_claims_due > 0
   title:e_minister_of_revenue.holder.treasury < title:e_minister_of_revenue.mam_revenue_fund_cash_target }
   title:h_china.holder.treasury > 600 title:h_china = { NOT = { has_variable = mam_cf_case_5 } }
   OR = { title:h_china = { NOT = { has_variable = mam_cf_topup_until } } title:h_china.var:mam_cf_topup_until <= current_date }
  }
   mam_revenue_fund_request_effect = { TARGET = title:h_china KIND = 5 AMOUNT = {
    value = title:h_china.var:mam_cf_unfunded add = title:h_china.var:mam_cf_claims_due
    add = title:e_minister_of_revenue.mam_revenue_fund_cash_target subtract = title:e_minister_of_revenue.holder.treasury
    min = 200 max = 1000 max = { value = treasury subtract = 500 min = 0 }
   } }
   title:h_china = { set_variable = { name = mam_cf_topup_until value = { value = current_date add = 365 } } }
  }
  # Ministers can seek native project money without waiting for a player. The
  # funded proposal still passes the identical law/cash/earmark checks.
  random_vassal_or_below = { limit = {
   mam_revenue_ministry_trigger = yes is_ai = yes
   primary_title = { var:mam_cf_project_cash = 0 NOT = { has_variable = mam_cf_case_3 } NOT = { has_variable = mam_cf_case_9 } }
   OR = { has_title = title:e_minister_of_works has_title = title:e_minister_of_rites
    has_title = title:e_minister_of_war has_title = title:e_minister_of_justice has_title = title:e_minister_of_revenue }
   NOT = { has_trait = lazy }
   top_liege = { mam_revenue_fund_available > 500 }
  } trigger_event = { id = mam_fund.96 days = 1 } }
  # Under reserves, seek one affordable, non-distressed provincial contribution.
  if = { limit = { title:h_china.var:mam_cf_programme = 1 }
   random_vassal_or_below = { limit = {
    mam_revenue_province_trigger = yes treasury >= 1000 mam_revenue_has_recovery_need_trigger = no
    primary_title = { NOT = { has_variable = mam_cf_remit_until } NOT = { has_variable = mam_cf_case_6 } }
   } mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 6 AMOUNT = 100 } }
  }
 }
}
''')

write('common/opinion_modifiers/mam_revenue_common_opinions.txt', r'''
mam_revenue_fund_support_opinion = { opinion = 10 decaying = yes }
mam_revenue_fund_cut_opinion = { opinion = -15 decaying = yes }
mam_revenue_fund_levy_opinion = { opinion = -10 decaying = yes }
''')

def interaction(key, shown, valid, effect, cooldown=3):
    return f'''{key} = {{
 category = interaction_category_ministry icon = icon_imperial_treasury interface_priority = 65
 desc = {key}_desc common_interaction = yes auto_accept = yes
 cooldown = {{ months = {cooldown} }}
 is_shown = {{ {shown} }}
 is_valid = {{ {valid} }}
 on_accept = {{ custom_tooltip = {key}_desc hidden_effect = {{ {effect}
  title:h_china.holder ?= {{ mam_revenue_fund_wake_effect = yes }}
 }} }}
}}
'''

ui = ''
ui += interaction('mam_revenue_fund_review_operations_interaction',
 'scope:actor = { mam_revenue_authority_trigger = yes is_ai = no mam_revenue_fund_enabled_trigger = yes } scope:recipient = { mam_revenue_ministry_trigger = yes }',
 'scope:recipient.primary_title = { NOT = { has_variable = mam_cf_case_1 } trigger_if = { limit = { has_variable = mam_cf_review_until } var:mam_cf_review_until <= current_date } }',
 'scope:recipient = { mam_revenue_fund_open_operations_effect = yes } if = { limit = { exists = scope:mam_cf_created scope:actor = { mam_revenue_officer_trigger = no } } scope:mam_cf_created = { set_variable = { name = mam_cf_stage value = 1 } } }')
ui += interaction('mam_revenue_fund_request_operations_interaction',
 'scope:actor = { mam_revenue_fund_member_trigger = yes is_ai = no } scope:recipient = { mam_revenue_officer_trigger = yes this != scope:actor }',
 'scope:actor.primary_title = { NOT = { has_variable = mam_cf_case_1 } trigger_if = { limit = { has_variable = mam_cf_review_until } var:mam_cf_review_until <= current_date } }',
 'scope:actor = { mam_revenue_fund_open_operations_effect = yes }')
ui += interaction('mam_revenue_fund_petition_interaction',
 'scope:actor = { mam_revenue_province_trigger = yes is_ai = no mam_revenue_fund_enabled_trigger = yes } scope:recipient = { mam_revenue_officer_trigger = yes }',
 'scope:actor = { OR = { treasury < 0 mam_revenue_has_recovery_need_trigger = yes } primary_title = { NOT = { has_variable = mam_cf_case_2 } NOT = { has_variable = mam_cf_relief_until } } }',
 'scope:actor = { mam_revenue_fund_open_relief_effect = yes }', 6)
ui += interaction('mam_revenue_fund_remittance_interaction',
 'scope:actor = { mam_revenue_officer_trigger = yes is_ai = no mam_revenue_fund_enabled_trigger = yes } scope:recipient = { mam_revenue_province_trigger = yes }',
 'scope:recipient = { treasury > 300 mam_revenue_has_recovery_need_trigger = no primary_title = { NOT = { has_variable = mam_cf_case_6 } NOT = { has_variable = mam_cf_remit_until } } }',
 'scope:actor = { mam_revenue_fund_request_effect = { TARGET = scope:recipient.primary_title KIND = 6 AMOUNT = 100 } }')
ui += interaction('mam_revenue_fund_project_interaction',
 'scope:actor = { mam_revenue_fund_member_trigger = yes is_ai = no OR = { has_title = title:e_minister_of_works has_title = title:e_minister_of_rites has_title = title:e_minister_of_war has_title = title:e_minister_of_justice has_title = title:e_minister_of_revenue has_title = title:e_minister_grand_marshal } } scope:recipient = { is_landed = yes primary_title = { tier >= tier_kingdom } }',
 'scope:actor.primary_title = { var:mam_cf_project_cash = 0 NOT = { has_variable = mam_cf_case_3 } NOT = { has_variable = mam_cf_case_9 } } OR = { scope:recipient = { mam_revenue_province_trigger = yes } scope:actor = { has_title = title:e_minister_grand_marshal } }',
 'scope:recipient.primary_title = { save_scope_as = mam_cf_site_title } scope:actor = { trigger_event = mam_fund.5 }', 1)
ui += interaction('mam_revenue_fund_appeal_interaction',
 'scope:actor = { mam_revenue_fund_member_trigger = yes is_ai = no } scope:recipient = { OR = { mam_revenue_chancellor_trigger = yes mam_revenue_emperor_trigger = yes } this != scope:actor }',
 'scope:actor.primary_title = { has_variable = mam_cf_cut_until var:mam_cf_cut_until > current_date var:mam_cf_cut_holder = scope:actor NOT = { has_variable = mam_cf_appeal_used } NOT = { has_variable = mam_cf_case_7 } }',
 'scope:actor = { mam_revenue_fund_open_appeal_effect = yes }', 1)
ui += interaction('mam_revenue_fund_supplement_interaction',
 'scope:actor = { mam_revenue_fund_member_trigger = yes is_ai = no } scope:recipient = { mam_revenue_officer_trigger = yes }',
 'scope:actor.primary_title = { NOT = { has_variable = mam_cf_case_12 } NOT = { has_variable = mam_cf_special_until } }',
 'scope:actor = { mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 12 AMOUNT = major_treasury_value } }', 3)
write('common/character_interactions/mam_revenue_common_interactions.txt', ui)

def decision(key, shown, effect):
    return f'''{key} = {{
 decision_group_type = mam_ministries ai_check_interval = 0
 picture = {{ reference = "gfx/interface/illustrations/event_scenes/tgp_study_asia.dds" }}
 desc = {key}_desc selection_tooltip = {key}_desc confirm_text = mam_cf.open
 is_shown = {{ is_ai = no mam_revenue_fund_enabled_trigger = yes {shown} }}
 effect = {{ {effect} }}
 ai_potential = {{ always = no }} ai_will_do = {{ base = 0 }}
}}
'''

dec = decision('mam_revenue_fund_accounts_decision',
 'OR = { mam_revenue_authority_trigger = yes mam_revenue_ministry_trigger = yes }', 'trigger_event = mam_fund.6')
dec += decision('mam_revenue_fund_programme_decision',
 'OR = { mam_revenue_chancellor_trigger = yes mam_revenue_emperor_trigger = yes }',
 '''mam_revenue_fund_request_effect = { TARGET = title:h_china KIND = 4 AMOUNT = 0 }
 title:h_china.holder = { mam_revenue_fund_wake_effect = yes }''')
dec += decision('mam_revenue_fund_topup_decision',
 'mam_revenue_authority_trigger = yes',
 '''mam_revenue_fund_request_effect = { TARGET = title:h_china KIND = 5 AMOUNT = 200 }
 title:h_china.holder = { mam_revenue_fund_wake_effect = yes }''')
dec += decision('mam_revenue_fund_contribution_decision',
 'mam_revenue_ministry_trigger = yes primary_title = { var:mam_cf_project_cash = 0 NOT = { has_variable = mam_cf_case_3 } NOT = { has_variable = mam_cf_case_9 } }',
 'trigger_event = mam_fund.7')
dec += decision('mam_revenue_fund_resume_decision',
 'mam_revenue_authority_trigger = yes',
 '''var:mam_cf_open ?= { mam_revenue_fund_release_effect = yes }
 title:h_china = { every_in_list = { variable = mam_cf_cases remove_variable = mam_cf_snooze } }
 title:h_china.holder = { mam_revenue_fund_wake_effect = yes }''')
dec += decision('mam_revenue_fund_return_advance_decision',
 'mam_revenue_ministry_trigger = yes primary_title = { var:mam_cf_project_cash > 0 }',
 '''primary_title = {
 set_variable = { name = mam_cf_project_cash value = 0 }
 remove_variable = mam_cf_project_type remove_variable = mam_cf_project_target
 remove_variable = mam_cf_project_instance remove_variable = mam_cf_project_until
 }''')
dec += decision('mam_revenue_fund_supplement_decision',
 'mam_revenue_officer_trigger = yes primary_title = { NOT = { has_variable = mam_cf_case_12 } NOT = { has_variable = mam_cf_special_until } }',
 '''mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 12 AMOUNT = major_treasury_value }
 title:h_china.holder = { mam_revenue_fund_wake_effect = yes }''')
write('common/decisions/mam_revenue_common_decisions.txt', dec)

events = r'''
namespace = mam_fund
mam_fund.99 = { type = character_event hidden = yes immediate = { mam_revenue_fund_start_effect = yes } }
mam_fund.98 = { type = character_event hidden = yes immediate = { mam_revenue_fund_wake_effect = yes } }
mam_fund.90 = { type = character_event hidden = yes immediate = { mam_revenue_fund_present_effect = yes } }
mam_fund.1 = {
 type = letter_event title = mam_cf.request_title sender = scope:mam_cf_sender
 opening = { desc = mam_cf.opening }
 desc = { first_valid = {
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 5 } desc = mam_cf.topup_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 6 } desc = mam_cf.remit_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 3 } desc = mam_cf.project_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 9 } desc = mam_cf.contribution_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_kind = 12 } desc = mam_cf.supplement_desc }
  desc = mam_cf.relief_desc
 } }
 trigger = { mam_revenue_fund_actor_trigger = yes }
 option = {
  name = mam_cf.revise trigger = { mam_revenue_fund_actor_trigger = yes is_ai = no scope:mam_cf_file.var:mam_cf_stage != 2 }
  custom_tooltip = mam_cf.revise_tt
  hidden_effect = { trigger_event = mam_fund.3 } ai_chance = { base = 0 }
 }
 option = {
  name = mam_cf.recommend
  trigger = { mam_revenue_fund_actor_trigger = yes scope:mam_cf_file.var:mam_cf_stage = 0
   scope:mam_cf_quote > 0 scope:mam_cf_quote <= scope:mam_cf_max
  }
  custom_tooltip = mam_cf.recommend_tt
  if = { limit = { scope:mam_cf_file = { mam_revenue_fund_delegated_trigger = yes } }
   mam_revenue_fund_preview_effect = yes
  }
  hidden_effect = { mam_revenue_fund_recommend_effect = yes }
  ai_chance = { base = mam_revenue_fund_support_weight }
 }
 option = {
  name = mam_cf.approve
  trigger = { mam_revenue_fund_actor_trigger = yes scope:mam_cf_file.var:mam_cf_stage = 1 scope:mam_cf_quote <= scope:mam_cf_max scope:mam_cf_quote > 0 }
  mam_revenue_fund_preview_effect = yes
  hidden_effect = { mam_revenue_fund_approve_effect = yes }
  ai_chance = { base = mam_revenue_fund_support_weight }
 }
 option = {
  name = mam_cf.consent
  trigger = { mam_revenue_fund_actor_trigger = yes scope:mam_cf_file.var:mam_cf_stage = 2 scope:mam_cf_quote <= scope:mam_cf_max }
  custom_tooltip = mam_cf.consent_tt
  hidden_effect = { scope:mam_cf_file = {
   set_variable = { name = mam_cf_consent value = root }
   if = { limit = { mam_revenue_fund_delegated_trigger = yes }
    set_variable = { name = mam_cf_authorized value = title:e_minister_of_revenue.holder }
    mam_revenue_fund_commit_effect = yes
   }
   else = { set_variable = { name = mam_cf_stage value = 1 } mam_revenue_fund_release_effect = yes }
  } }
  ai_chance = { base = 70 modifier = { add = 30 has_trait = generous } modifier = { factor = 0.5 has_trait = greedy } }
 }
 option = {
  name = mam_cf.refuse trigger = { mam_revenue_fund_actor_trigger = yes }
  custom_tooltip = mam_cf.refuse_tt
  if = { limit = { has_trait = compassionate scope:mam_cf_file.var:mam_cf_kind = 2 scope:mam_cf_max >= scope:mam_cf_quote scope:mam_cf_subject = { mam_revenue_has_recovery_need_trigger = yes } }
   show_as_tooltip = { add_stress = 15 }
  }
  hidden_effect = { mam_revenue_fund_refuse_effect = yes }
  ai_chance = { base = 25 modifier = { add = 25 has_trait = lazy } modifier = { add = 25 has_trait = paranoid } modifier = { add = 20 has_trait = greedy } modifier = { add = 70 has_trait = vengeful has_relation_rival = scope:mam_cf_subject } }
 }
 option = { name = mam_cf.defer trigger = { mam_revenue_fund_actor_trigger = yes is_ai = no }
  custom_tooltip = mam_cf.defer_tt hidden_effect = { mam_revenue_fund_defer_effect = yes } ai_chance = { base = 0 }
 }
}
mam_fund.2 = {
 type = character_event theme = stewardship title = mam_cf.operations_title desc = mam_cf.operations_desc
 trigger = { mam_revenue_fund_actor_trigger = yes }
 left_portrait = { character = root animation = reading }
 right_portrait = { trigger = { scope:mam_cf_subject != root } character = scope:mam_cf_subject animation = thinking }
 @OPERATING_CHOICES@
 option = { name = mam_cf.decline_increase trigger = { mam_revenue_fund_actor_trigger = yes }
  custom_tooltip = mam_cf.decline_increase_tt hidden_effect = { mam_revenue_fund_refuse_effect = yes }
  ai_chance = { base = 10 modifier = { add = 25 has_trait = stubborn } modifier = { add = 25 has_trait = lazy } }
 }
 option = { name = mam_cf.defer trigger = { mam_revenue_fund_actor_trigger = yes is_ai = no }
  custom_tooltip = mam_cf.defer_tt hidden_effect = { mam_revenue_fund_defer_effect = yes } ai_chance = { base = 0 }
 }
}
mam_fund.3 = {
 type = character_event theme = stewardship title = mam_cf.amount_title desc = mam_cf.amount_desc
 trigger = { mam_revenue_fund_actor_trigger = yes }
 left_portrait = { character = root animation = reading }
 right_portrait = { trigger = { scope:mam_cf_subject != root } character = scope:mam_cf_subject animation = thinking }
 @AMOUNT_CHOICES@
 option = { name = mam_cf.amount_max trigger = { mam_revenue_fund_actor_trigger = yes scope:mam_cf_max > 0 }
  hidden_effect = { scope:mam_cf_file = { set_variable = { name = mam_cf_amount value = scope:mam_cf_max } } mam_revenue_fund_bind_effect = yes trigger_event = mam_fund.3 }
  ai_chance = { base = 0 }
 }
 option = { name = mam_cf.amount_done trigger = { mam_revenue_fund_actor_trigger = yes }
  hidden_effect = { mam_revenue_fund_bind_effect = yes trigger_event = mam_fund.1 } ai_chance = { base = 100 }
 }
}
mam_fund.4 = {
 type = character_event theme = stewardship title = mam_cf.programme_title desc = mam_cf.programme_desc
 trigger = { mam_revenue_fund_actor_trigger = yes }
 left_portrait = { character = root animation = reading }
 right_portrait = { trigger = { exists = scope:mam_cf_custodian scope:mam_cf_custodian != root } character = scope:mam_cf_custodian animation = thinking }
 @PROGRAMME_CHOICES@
 option = { name = mam_cf.defer trigger = { mam_revenue_fund_actor_trigger = yes is_ai = no }
  custom_tooltip = mam_cf.defer_tt hidden_effect = { mam_revenue_fund_defer_effect = yes } ai_chance = { base = 0 }
 }
}
mam_fund.5 = {
 type = character_event theme = stewardship title = mam_cf.project_title desc = mam_cf.project_choose_desc
 trigger = { mam_revenue_fund_member_trigger = yes exists = scope:mam_cf_site_title.holder
  primary_title = { var:mam_cf_project_cash = 0 NOT = { has_variable = mam_cf_case_3 } NOT = { has_variable = mam_cf_case_9 } }
 }
 left_portrait = { character = root animation = reading }
 right_portrait = { character = scope:mam_cf_site_title.holder animation = thinking }
 immediate = { save_scope_as = founder current_heir ?= { save_scope_as = founder_heir } }
 @PROJECT_CHOICES@
 option = { name = mam_cf.cancel ai_chance = { base = 1 } }
}
mam_fund.6 = {
 type = character_event theme = stewardship title = mam_cf.accounts_title
 desc = { first_valid = { triggered_desc = { trigger = { mam_revenue_ministry_trigger = yes } desc = mam_cf.accounts_minister_desc } desc = mam_cf.accounts_desc } }
 trigger = { OR = { mam_revenue_authority_trigger = yes mam_revenue_ministry_trigger = yes } mam_revenue_fund_enabled_trigger = yes }
 immediate = {
  mam_revenue_fund_refresh_totals_effect = yes
  title:h_china.holder = { save_scope_as = mam_cf_emperor }
  save_scope_value_as = { name = mam_cf_fund_balance value = 0 }
  title:e_minister_of_revenue.holder ?= { save_scope_value_as = { name = mam_cf_fund_balance value = treasury } }
  save_scope_value_as = { name = mam_cf_monthly value = title:h_china.var:mam_cf_total_cost }
  save_scope_value_as = { name = mam_cf_reserve value = title:h_china.var:mam_cf_reserve }
  save_scope_value_as = { name = mam_cf_free value = title:h_china.mam_revenue_fund_available }
  if = { limit = { mam_revenue_ministry_trigger = yes }
   save_scope_value_as = { name = mam_cf_local value = treasury }
   save_scope_value_as = { name = mam_cf_cost value = primary_title.var:mam_cf_cost }
   save_scope_value_as = { name = mam_cf_headroom value = primary_title.var:mam_cf_headroom }
   save_scope_value_as = { name = mam_cf_left value = primary_title.var:mam_cf_remaining }
   save_scope_value_as = { name = mam_cf_earmark value = primary_title.var:mam_cf_project_cash }
  }
 }
 left_portrait = { character = root animation = reading }
 right_portrait = { trigger = { exists = title:e_minister_of_revenue.holder root != title:e_minister_of_revenue.holder } character = title:e_minister_of_revenue.holder animation = thinking }
 option = { name = mam_cf.accounts_close custom_tooltip = mam_cf.accounts_tt }
 option = { name = mam_cf.review_mine trigger = { mam_revenue_ministry_trigger = yes primary_title = {
  NOT = { has_variable = mam_cf_case_1 }
  trigger_if = { limit = { has_variable = mam_cf_review_until } var:mam_cf_review_until <= current_date }
 } }
  hidden_effect = { mam_revenue_fund_open_operations_effect = yes title:h_china.holder = { mam_revenue_fund_wake_effect = yes } }
 }
 option = { name = mam_cf.release_programme trigger = { mam_revenue_emperor_trigger = yes title:h_china = { has_variable = mam_cf_imperial_programme } }
  custom_tooltip = mam_cf.release_programme_tt hidden_effect = { title:h_china = { remove_variable = mam_cf_imperial_programme } }
 }
 option = { name = mam_cf.suspend trigger = { OR = { mam_revenue_emperor_trigger = yes mam_revenue_chancellor_trigger = yes } title:h_china = { NOT = { has_variable = mam_cf_suspended } } }
  custom_tooltip = mam_cf.suspend_tt
  hidden_effect = { title:h_china = {
   set_variable = { name = mam_cf_suspended value = 1 days = 90 }
   set_variable = { name = mam_cf_suspender value = root }
  } }
 }
 option = { name = mam_cf.restore trigger = { title:h_china = { has_variable = mam_cf_suspended }
  OR = { mam_revenue_emperor_trigger = yes title:h_china.var:mam_cf_suspender = root }
 }
  custom_tooltip = mam_cf.restore_tt hidden_effect = { title:h_china = { remove_variable = mam_cf_suspended remove_variable = mam_cf_suspender } }
 }
}
mam_fund.7 = {
 type = character_event theme = stewardship title = mam_cf.contribution_title desc = mam_cf.contribution_choose_desc
 trigger = { mam_revenue_fund_member_trigger = yes }
 left_portrait = { character = root animation = reading }
 immediate = {
  ordered_great_project = { limit = { great_project_owner = { top_liege = title:h_china.holder } }
   order_by = { value = 1 } position = 0 check_range_bounds = no save_scope_as = mam_cf_project_one
  }
  ordered_great_project = { limit = { great_project_owner = { top_liege = title:h_china.holder } }
   order_by = { value = 1 } position = 1 check_range_bounds = no save_scope_as = mam_cf_project_two
  }
  ordered_great_project = { limit = { great_project_owner = { top_liege = title:h_china.holder } }
   order_by = { value = 1 } position = 2 check_range_bounds = no save_scope_as = mam_cf_project_three
  }
 }
 @CONTRIBUTION_CHOICES@
 option = { name = mam_cf.cancel }
}
mam_fund.20 = {
 type = letter_event title = mam_cf.outcome_title sender = scope:mam_cf_sender
 opening = { desc = mam_cf.opening }
 desc = { first_valid = {
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 1 scope:mam_cf_file.var:mam_cf_kind = 4 } desc = mam_cf.programme_result_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 1 OR = { scope:mam_cf_file.var:mam_cf_kind = 1 scope:mam_cf_file.var:mam_cf_kind = 7 } } desc = mam_cf.operations_result_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 1 scope:mam_cf_file.var:mam_cf_kind = 12 scope:mam_cf_file.var:mam_cf_paid_from = scope:mam_cf_file.var:mam_cf_paid_to } desc = mam_cf.supplement_self_result_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 1 scope:mam_cf_file.var:mam_cf_paid_from = scope:mam_cf_file.var:mam_cf_paid_to } desc = mam_cf.reserved_result_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 1 scope:mam_cf_file.var:mam_cf_paid_amount > 0 } desc = mam_cf.paid_result_desc }
  triggered_desc = { trigger = { scope:mam_cf_file.var:mam_cf_result = 2 } desc = mam_cf.refused_result_desc }
  desc = mam_cf.unpaid_result_desc
 } }
 option = { name = mam_cf.recorded }
}
mam_fund.96 = {
 type = character_event hidden = yes
 trigger = { mam_revenue_fund_member_trigger = yes is_ai = yes }
 immediate = {
  clear_saved_scope = mam_cf_site_title
  top_liege = {
   random_vassal_or_below = { limit = { mam_revenue_province_trigger = yes }
    primary_title = { save_scope_as = mam_cf_site_title }
   }
  }
  if = { limit = { exists = scope:mam_cf_site_title } trigger_event = mam_fund.5 }
 }
}
mam_fund.97 = {
 type = character_event hidden = yes
 trigger = { mam_revenue_fund_member_trigger = yes is_ai = yes primary_title = {
  var:mam_cf_cut_holder = root has_variable = mam_cf_cut_until var:mam_cf_cut_until > current_date
  NOT = { has_variable = mam_cf_appeal_used } NOT = { has_variable = mam_cf_case_7 }
 } }
 immediate = {
  if = { limit = { OR = { has_trait = ambitious has_trait = stubborn has_trait = greedy
   opinion = { target = title:e_minister_of_revenue.holder value < 0 }
  } } mam_revenue_fund_open_appeal_effect = yes title:h_china.holder = { mam_revenue_fund_wake_effect = yes } }
 }
}
'''

operating = []
for value, label, weight, traits in [(25,'lean',25,'greedy paranoid'), (75,'standard',80,'just honest diligent lazy'), (150,'expanded',25,'generous trusting ambitious')]:
    bonuses = ' '.join(f'modifier = {{ add = 25 has_trait = {t} }}' for t in traits.split())
    operating.append(f'''option = {{ name = mam_cf.{label}
 trigger = {{ mam_revenue_fund_actor_trigger = yes }}
 custom_tooltip = mam_cf.{label}_tt
 if = {{ limit = {{ has_trait = vengeful has_relation_rival = scope:mam_cf_subject }} show_as_tooltip = {{ add_stress = 10 }} }}
 hidden_effect = {{
  if = {{ limit = {{ has_trait = vengeful has_relation_rival = scope:mam_cf_subject }} add_stress = 10 }}
  scope:mam_cf_file = {{ set_variable = {{ name = mam_cf_headroom value = {value} }} }}
  if = {{ limit = {{ scope:mam_cf_file.var:mam_cf_stage = 1 }} mam_revenue_fund_approve_effect = yes }}
  else = {{ mam_revenue_fund_recommend_effect = yes }}
 }}
 ai_chance = {{ base = {weight} {bonuses}
  modifier = {{ factor = 0.5 has_trait = vengeful has_relation_rival = scope:mam_cf_subject }}
  modifier = {{ factor = 1.5 has_trait = ambitious has_relation_friend = scope:mam_cf_subject }}
 }}
}}''')
events = events.replace('@OPERATING_CHOICES@', '\n'.join(operating))
amounts = []
for amount in [25,100,-25,-100]:
    key = ('plus' if amount > 0 else 'minus') + str(abs(amount))
    gate = f'scope:mam_cf_quote <= {{ value = scope:mam_cf_max subtract = {amount} }}' if amount > 0 else f'scope:mam_cf_quote > {abs(amount)}'
    amounts.append(f'''option = {{ name = mam_cf.{key}
 trigger = {{ mam_revenue_fund_actor_trigger = yes {gate} }}
 hidden_effect = {{ scope:mam_cf_file = {{ change_variable = {{ name = mam_cf_amount add = {amount} }} }} mam_revenue_fund_bind_effect = yes trigger_event = mam_fund.3 }}
 ai_chance = {{ base = 0 }}
}}''')
events = events.replace('@AMOUNT_CHOICES@','\n'.join(amounts))
programmes = []
for mode,key,weight,bonus in [(0,'balanced',80,'just'),(1,'reserves',30,'greedy'),(2,'recovery',30,'compassionate')]:
    programmes.append(f'''option = {{ name = mam_cf.{key} trigger = {{ mam_revenue_fund_actor_trigger = yes }}
 custom_tooltip = mam_cf.{key}_tt
 hidden_effect = {{ scope:mam_cf_file = {{ set_variable = {{ name = mam_cf_mode value = {mode} }} }}
  if = {{ limit = {{ OR = {{ mam_revenue_emperor_trigger = yes AND = {{ mam_revenue_chancellor_trigger = yes title:h_china.holder = {{ NOT = {{ has_realm_law = mam_revenue_authority_reserved }} }} }} }} }} mam_revenue_fund_approve_effect = yes }}
  else = {{ mam_revenue_fund_recommend_effect = yes }}
 }}
 ai_chance = {{ base = {weight} modifier = {{ add = 50 has_trait = {bonus} }} }}
}}''')
events = events.replace('@PROGRAMME_CHOICES@','\n'.join(programmes))

PROJECTS = [('grand_campaign_project','e_minister_grand_marshal'),
 ('minister_project_culture','e_minister_of_rites'),('minister_project_development','e_minister_of_works'),
 ('minister_project_establish_control','e_minister_of_justice'),('minister_project_train_troops','e_minister_of_war'),
 ('minister_project_conduct_census','e_minister_of_revenue'),('minister_compel_religious_uniformity','e_minister_of_rites')]
# Include every installed treasury-funded type, retaining its native eligibility.
# This also covers future planning for walls/barracks and the installed PAM types.
native_project_sources = {}
native_project_nodes = {}
for f in sorted((GAME / 'common/great_projects/types').glob('*.txt')):
    source = f.read_text(encoding='utf-8-sig')
    native_project_sources[f] = source
    for node in parse(source):
        if node.children:
            native_project_nodes[node.key] = (f, node)
            cost = next((c for c in node.children if c.key == 'cost'), None)
            cash = next((c for c in cost.children if c.key in {'treasury', 'treasury_or_gold'}), None) if cost else None
            if cash and node.key not in {p for p,_ in PROJECTS}:
                PROJECTS.append((node.key, None))
project_choices = []
for i,(project,title) in enumerate(PROJECTS,1):
    project_choices.append(f'''option = {{ name = mam_cf.project_{i}
 trigger = {{ mam_revenue_fund_eligible_project_{i} = yes mam_revenue_fund_member_trigger = yes exists = scope:mam_cf_site_title.holder }}
 custom_tooltip = mam_cf.project_request_tt
 hidden_effect = {{ mam_revenue_fund_open_project_effect = {{ TYPE = {i} COST = mam_revenue_fund_start_cost_{i} }} title:h_china.holder = {{ mam_revenue_fund_wake_effect = yes }} }}
 ai_chance = {{ base = 100 }}
}}''')
events = events.replace('@PROJECT_CHOICES@','\n'.join(project_choices))
contrib = []
for ordinal in ['one','two','three']:
    contrib.append(f'''option = {{ name = mam_cf.contribution_{ordinal}
 trigger = {{ exists = scope:mam_cf_project_{ordinal} mam_revenue_fund_member_trigger = yes
  primary_title = {{ var:mam_cf_project_cash = 0 NOT = {{ has_variable = mam_cf_case_3 }} NOT = {{ has_variable = mam_cf_case_9 }} }}
 }}
 custom_tooltip = mam_cf.contribution_request_tt
 hidden_effect = {{ scope:mam_cf_project_{ordinal} = {{ save_scope_as = mam_cf_selected_project }} mam_revenue_fund_open_contribution_effect = yes title:h_china.holder = {{ mam_revenue_fund_wake_effect = yes }} }}
}}''')
events = events.replace('@CONTRIBUTION_CHOICES@','\n'.join(contrib))
write('events/mam_revenue_common_events.txt',events)

write('common/scripted_effects/mam_revenue_common_preview_effects.txt', r'''
mam_revenue_fund_preview_effect = {
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 5 }
  show_as_tooltip = { scope:mam_cf_emperor = { pay_short_term_treasury = { target = scope:mam_cf_custodian treasury = scope:mam_cf_quote } } }
 }
 else_if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 6 }
  show_as_tooltip = { scope:mam_cf_subject = { pay_short_term_treasury = { target = scope:mam_cf_custodian treasury = scope:mam_cf_quote } } }
 }
 else_if = { limit = { scope:mam_cf_subject != scope:mam_cf_custodian }
  show_as_tooltip = { scope:mam_cf_custodian = { pay_short_term_treasury = { target = scope:mam_cf_subject treasury = scope:mam_cf_quote } } }
 }
 else = { custom_tooltip = mam_cf.reserve_self_tt }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 2 }
  show_as_tooltip = { scope:mam_cf_subject = { add_character_modifier = { modifier = mam_revenue_recovery_office_modifier years = 1 } } }
 }
 if = { limit = { scope:mam_cf_file.var:mam_cf_kind = 6 scope:mam_cf_subject != root }
  show_as_tooltip = { scope:mam_cf_subject = { add_opinion = {
   target = root modifier = mam_revenue_fund_levy_opinion years = 2
  } } }
 }
 else_if = { limit = { scope:mam_cf_file.var:mam_cf_kind != 5 scope:mam_cf_subject != root }
  show_as_tooltip = { scope:mam_cf_subject = { add_opinion = {
   target = root modifier = mam_revenue_fund_support_opinion years = 2
  } } }
 }
 custom_tooltip = mam_cf.approval_tt
}
''')

write('common/scripted_effects/mam_revenue_common_native_rewards.txt',r'''
# Preserve the creditor's native credit only after the real grant, once. An old
# minister who has left office cannot receive a new personal hook or Influence.
mam_revenue_fund_native_rewards_effect = {
 if = { limit = { has_variable = mam_cf_native_petition NOT = { has_variable = mam_cf_native_rewarded }
  var:mam_cf_paid_from != var:mam_cf_paid_to
  exists = var:mam_cf_native_actor exists = var:mam_cf_native_credit
  var:mam_cf_native_credit_title.holder = var:mam_cf_native_credit
  var:mam_cf_native_actor = var:mam_cf_target.holder
 }
  set_variable = { name = mam_cf_native_rewarded value = 1 }
  save_scope_as = mam_cf_native_reward
  var:mam_cf_native_credit = { change_influence = major_influence_value }
  if = { limit = { has_variable = mam_cf_native_hook
   var:mam_cf_native_actor = { has_usable_hook = scope:mam_cf_native_reward.var:mam_cf_native_credit }
  }
   var:mam_cf_native_actor = { use_hook = scope:mam_cf_native_reward.var:mam_cf_native_credit }
  }
  if = { limit = { has_variable = mam_cf_clear_debt var:mam_cf_native_actor.treasury >= 0 }
   var:mam_cf_native_credit = { add_hook = { type = strong_indebted_hook target = scope:mam_cf_native_reward.var:mam_cf_native_actor } }
   situation:dynastic_cycle ?= {
    if = { limit = { situation_top_has_catalyst = catalyst_cleared_treasury_debt
     any_situation_participant = { this = scope:mam_cf_native_reward.var:mam_cf_native_actor }
    }
     trigger_situation_catalyst = { catalyst = catalyst_cleared_treasury_debt character = scope:mam_cf_native_reward.var:mam_cf_native_actor }
    }
   }
  }
  var:mam_cf_native_actor = {
   tgp_activate_catalyst_against_hegemon_effect = {
    HEGEMON = scope:mam_cf_native_reward.var:mam_cf_native_credit
    CATALYST = catalyst_hegemon_influenced_by_interaction
   }
  }
 }
}
''')

write('common/scripted_effects/mam_revenue_common_claims_effects.txt', r'''
# Existing native benefits are earned liabilities, not discretionary new grants.
# Context is a situation (insurance) or great project (Census debt purge).
mam_revenue_fund_create_claim_effect = {
 clear_saved_scope = mam_cf_claim
 save_scope_as = mam_cf_claimant
 if = { limit = { mam_revenue_fund_enabled_trigger = yes has_treasury = yes
  top_liege = title:h_china.holder exists = scope:mam_cf_claim_context
 }
  scope:mam_cf_claim_context = {
   if = { limit = { NOT = { has_variable = mam_cf_context_serial } }
    title:h_china = { change_variable = { name = mam_cf_serial add = 1 } }
    set_variable = { name = mam_cf_context_serial value = title:h_china.var:mam_cf_serial }
   }
   save_scope_value_as = { name = mam_cf_context_serial value = var:mam_cf_context_serial }
  }
  if = { limit = { title:h_china = { NOT = { any_in_list = { variable = mam_cf_cases
   var:mam_cf_pending = 1 var:mam_cf_kind = $KIND$
   var:mam_cf_target = scope:mam_cf_claimant.primary_title var:mam_cf_context_serial = scope:mam_cf_context_serial
  } } } }
   title:h_china.holder = { create_story = { type = mam_revenue_fund_story save_scope_as = mam_cf_claim } }
   if = { limit = { exists = scope:mam_cf_claim }
    title:h_china = {
     change_variable = { name = mam_cf_serial add = 1 }
     add_to_variable_list = { name = mam_cf_cases target = scope:mam_cf_claim }
    }
    scope:mam_cf_claim = {
     set_variable = { name = mam_cf_target value = scope:mam_cf_claimant.primary_title }
     set_variable = { name = mam_cf_snapshot value = scope:mam_cf_claimant }
     set_variable = { name = mam_cf_requester value = scope:mam_cf_claimant }
     set_variable = { name = mam_cf_emperor value = title:h_china.holder }
     set_variable = { name = mam_cf_kind value = $KIND$ }
     set_variable = { name = mam_cf_amount value = $AMOUNT$ }
     set_variable = { name = mam_cf_pending value = 1 }
     set_variable = { name = mam_cf_stage value = 0 }
     set_variable = { name = mam_cf_generation value = 0 }
     set_variable = { name = mam_cf_serial value = title:h_china.var:mam_cf_serial }
     set_variable = { name = mam_cf_created value = current_date }
     set_variable = { name = mam_cf_context_serial value = scope:mam_cf_context_serial }
    }
   }
  }
 }
}
mam_revenue_fund_insurance_claim_effect = {
 if = { limit = { any_sub_realm_county = {
  has_county_modifier = tgp_minister_project_conduct_census_natural_disaster_insurance_modifier
  any_county_situation = { this = scope:situation }
  NOT = { has_variable = mam_cf_insurance_claim }
 } }
  scope:situation = { save_scope_as = mam_cf_claim_context }
  mam_revenue_fund_create_claim_effect = { KIND = 10 AMOUNT = conduct_census_natural_disaster_payout_value }
  if = { limit = { exists = scope:mam_cf_claim }
   every_sub_realm_county = { limit = {
    has_county_modifier = tgp_minister_project_conduct_census_natural_disaster_insurance_modifier
    any_county_situation = { this = scope:situation }
    NOT = { has_variable = mam_cf_insurance_claim }
   }
    set_variable = { name = mam_cf_insurance_claim value = scope:mam_cf_claim }
    scope:mam_cf_claim = { add_to_variable_list = { name = mam_cf_claim_counties target = prev } }
   }
   scope:mam_cf_claim = { mam_revenue_fund_claim_commit_effect = yes }
  }
 }
}
mam_revenue_fund_debt_claim_effect = {
 mam_revenue_fund_create_claim_effect = { KIND = 11 AMOUNT = 1000 }
 if = { limit = { exists = scope:mam_cf_claim }
  scope:mam_cf_claim = { mam_revenue_fund_claim_commit_effect = yes }
 }
}
# A claim waits without an approval popup if funds are insufficient. It survives
# imperial succession and has no one-year proposal expiry. The title remains
# the beneficiary; no deceased minister's personal consent is reused.
mam_revenue_fund_claim_commit_effect = {
 save_scope_as = mam_cf_claim_paying
 mam_revenue_fund_refresh_totals_effect = yes
 if = { limit = { mam_revenue_fund_live_case_trigger = yes
  exists = title:e_minister_of_revenue.holder title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }
 }
  title:e_minister_of_revenue.holder = { save_scope_as = mam_cf_payer }
  var:mam_cf_target.holder = { save_scope_as = mam_cf_payee }
  save_scope_value_as = { name = mam_cf_amount value = var:mam_cf_amount }
  save_scope_value_as = { name = mam_cf_floor value = {
   value = title:e_minister_of_revenue.mam_revenue_fund_cash_target add = title:h_china.var:mam_cf_essential_due
  } }
  mam_revenue_fund_transfer_effect = yes
  if = { limit = { OR = { scope:mam_cf_paid > 0 scope:mam_cf_payer = scope:mam_cf_payee } }
   set_variable = { name = mam_cf_paid_amount value = scope:mam_cf_paid }
   if = { limit = { var:mam_cf_kind = 10 }
    every_in_list = { variable = mam_cf_claim_counties limit = {
     var:mam_cf_insurance_claim = scope:mam_cf_claim_paying holder.top_liege = title:h_china.holder
    }
     remove_county_modifier = tgp_minister_project_conduct_census_natural_disaster_insurance_modifier
    }
   }
   else = { var:mam_cf_target.holder = {
    add_character_modifier = { modifier = tgp_minister_project_conduct_census_purge_treasury_debt_modifier years = 5 }
   } }
   if = { limit = { scope:mam_cf_paid > 0 }
    var:mam_cf_target.holder = { send_interface_toast = {
     type = event_toast_effect_good title = mam_cf.earned_payment
     left_icon = title:e_minister_of_revenue right_icon = scope:mam_cf_payee
     custom_tooltip = mam_cf.earned_payment_tt
    } }
   }
   mam_revenue_fund_close_effect = { RESULT = 1 }
  }
  else_if = { limit = { scope:mam_cf_uncertain = 1 }
   mam_revenue_fund_close_effect = { RESULT = 3 }
  }
 }
}
''')

# Native insurance keeps its original foreign/non-pooled behavior. Chinese
# coverage instead creates a conserved, durable claim and never mints a fallback.
insurance_path=GAME/'common/scripted_effects/10_dlc_tgp_natural_disaster_scripted_effects.txt'
insurance_source=insurance_path.read_text(encoding='utf-8-sig')
insurance_node=next(n for n in parse(insurance_source) if n.key=='natural_disaster_insurance_effect')
insurance_original=insurance_source[insurance_node.start:insurance_node.end]
insurance_edits=[]
selection=insurance_node.children[0]
selection_limit=next(n for n in selection.children if n.key=='limit')
insurance_edits.append((insurance_source.index('{',selection_limit.start)+1,'\n mam_revenue_fund_enabled_trigger = no\n'))
participants=next(n for n in insurance_node.children if n.key=='every_situation_participant')
message=next(n for n in participants.children if n.key=='send_interface_message')
insurance_edits.append((message.start,'''if = { limit = { mam_revenue_fund_enabled_trigger = yes has_treasury = yes top_liege = title:h_china.holder }
 mam_revenue_fund_insurance_claim_effect = yes
} else = {
'''))
insurance_edits.append((message.end,'\n}\n'))
insurance_changed=insurance_original
for at,ins in sorted(insurance_edits,reverse=True):
    rel=at-insurance_node.start
    insurance_changed=insurance_changed[:rel]+ins+insurance_changed[rel:]
write('common/scripted_effects/zz_mam_revenue_common_native_obligations.txt',insurance_changed)
write('docs/COMMON-FUND-NATIVE-OBLIGATIONS.json',json.dumps({
 'native_source':str(insurance_path),'definition':'natural_disaster_insurance_effect',
 'native_sha256':hashlib.sha256(insurance_original.encode()).hexdigest(),
 'insertions':[{'at':at-insurance_node.start,'text':ins} for at,ins in insurance_edits],
},indent=2))

def body(source, node):
    return source[source.index('{', node.start) + 1:node.end - 1]

def expression(source, node):
    if node.children:
        return '{' + body(source, node) + '}'
    return '{ value = ' + node.value + ' }'

def append_block(source, owner, key, addition, edits):
    if key.startswith('on_'):
        addition = 'hidden_effect = {\n' + addition + '\n}'
    child = next((c for c in owner.children if c.key == key), None)
    if child:
        edits.append((child.end - 1, '\n# MAM COMMON FUND bridge\n' + addition + '\n'))
    else:
        edits.append((owner.end - 1, '\n# MAM COMMON FUND bridge\n' + key + ' = {\n' + addition + '\n}\n'))

cost_values = []
eligibility = []
project_effects = []
manifest = {'native_files': {}, 'definitions': {}, 'contribution_costs': {}, 'version': 49}
bridged_projects = []
for path, source in native_project_sources.items():
    manifest['native_files'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Global @ constants are file-local; copy exact native declarations.
    globals_ = [source[n.start:n.end] for n in parse(source) if not n.children]
    bridged_projects = list(globals_)
    for node in parse(source):
        if not node.children:
            continue
        edits = []
        index = next((i for i,(name,_) in enumerate(PROJECTS,1) if name == node.key), None)
        if index:
            cost = next(c for c in node.children if c.key == 'cost')
            cash = next(c for c in cost.children if c.key in {'treasury','treasury_or_gold'})
            cost_values.append(f'mam_revenue_fund_start_cost_{index} = ' + expression(source, cash))
            originals = [c for c in node.children if c.key in {'is_shown','can_start_planning'}]
            eligibility.append(f'mam_revenue_fund_eligible_project_{index} = {{\n' + '\n'.join(body(source,c) for c in originals) + '\n}')
            append_block(source,node,'can_start_planning',f'''custom_tooltip = {{ text = mam_cf.project_authorization_tt
 OR = {{ mam_revenue_fund_member_trigger = no
  mam_revenue_fund_project_start_trigger = {{ TYPE = {index} COST = mam_revenue_fund_start_cost_{index} }}
 }}
}}''',edits)
            append_block(source,node,'is_location_valid','''custom_tooltip = { text = mam_cf.project_location_tt
 OR = { mam_revenue_fund_member_trigger = no mam_revenue_fund_project_location_trigger = yes }
}''',edits)
            append_block(source,node,'on_plan_build',f'''save_scope_as = mam_cf_planned_project
scope:founder ?= {{ if = {{ limit = {{ mam_revenue_fund_member_trigger = yes }}
 save_scope_value_as = {{ name = mam_cf_native_cost value = mam_revenue_fund_start_cost_{index} }}
 primary_title = {{
  change_variable = {{ name = mam_cf_project_cash subtract = scope:mam_cf_native_cost }}
  set_variable = {{ name = mam_cf_project_instance value = scope:mam_cf_planned_project }}
 }}
}} }}''',edits)
        contributions = next((c for c in node.children if c.key == 'project_contributions'),None)
        if contributions:
            for c_index, contribution in enumerate(contributions.children):
                cost = next((c for c in contribution.children if c.key == 'cost'),None)
                cash = next((c for c in cost.children if c.key in {'treasury','treasury_or_gold'}),None) if cost else None
                if not cash:
                    continue
                value_key = 'mam_revenue_fund_contribution_cost_' + node.key + '_' + str(c_index)
                cost_values.append(value_key + ' = ' + expression(source,cash))
                manifest['contribution_costs'][value_key] = {'project':node.key,'contribution':contribution.key,'native_expression':expression(source,cash)}
                append_block(source,contribution,'contributor_is_valid',f'''custom_tooltip = {{ text = mam_cf.contribution_authorization_tt
 OR = {{ mam_revenue_fund_member_trigger = no mam_revenue_fund_contribution_trigger = {{ COST = {value_key} }} }}
}}''',edits)
                append_block(source,contribution,'on_contribution_funded',f'''if = {{ limit = {{ mam_revenue_fund_member_trigger = yes }}
 save_scope_value_as = {{ name = mam_cf_native_cost value = {value_key} }}
 primary_title = {{ change_variable = {{ name = mam_cf_project_cash subtract = scope:mam_cf_native_cost }} }}
}}''',edits)
                if node.key == 'minister_project_conduct_census' and contribution.key == 'purge_treasury_debt':
                    completion=next(c for c in contribution.children if c.key=='on_complete')
                    message=next(c for c in completion.walk() if c.key=='send_interface_message'
                                 and any(p.key=='pay_short_term_treasury' for p in c.walk()))
                    edits.append((message.start,'''if = { limit = { mam_revenue_fund_enabled_trigger = yes
 has_treasury = yes top_liege = title:h_china.holder treasury < 0 }
 scope:great_project = { save_scope_as = mam_cf_claim_context }
 mam_revenue_fund_debt_claim_effect = yes
} else = {
'''))
                    edits.append((message.end,'\n}\n'))
        if not edits:
            continue
        release = 'save_scope_as = mam_cf_releasing_project\n' + roster('''if = { limit = { has_variable = mam_cf_project_instance }
 if = { limit = { var:mam_cf_project_instance = scope:mam_cf_releasing_project }
 set_variable = { name = mam_cf_project_cash value = 0 }
 remove_variable = mam_cf_project_type remove_variable = mam_cf_project_target
 remove_variable = mam_cf_project_instance remove_variable = mam_cf_project_until
} }''')
        append_block(source,node,'on_cancel',release,edits)
        append_block(source,node,'on_complete',release,edits)
        original = source[node.start:node.end]
        transformed = original
        for pos, insertion in sorted(edits,reverse=True):
            rel = pos-node.start
            transformed = transformed[:rel]+insertion+transformed[rel:]
        manifest['definitions'][node.key] = {'native_source':str(path), 'original_sha256':hashlib.sha256(original.encode()).hexdigest(),
                                            'insertions':[{'at':pos-node.start,'text':ins} for pos,ins in edits]}
        bridged_projects.append(transformed)
    write('common/great_projects/types/zz_mam_revenue_common_'+path.name,'\n\n'.join(bridged_projects))
# Remove only the superseded generator output from this workspace, if present.
obsolete=ROOT/'common/great_projects/types/zz_mam_revenue_common_projects.txt'
if obsolete.exists(): obsolete.unlink()
write('common/script_values/mam_revenue_common_project_costs.txt','\n\n'.join(cost_values))
write('common/scripted_triggers/mam_revenue_common_project_eligibility.txt','\n\n'.join(eligibility))
write('docs/COMMON-FUND-NATIVE-PROJECTS.json',json.dumps(manifest,indent=2))

# Native direct gifts/demands/debt may otherwise spend the same pooled cash a
# second time. Preserve the complete native definition outside the new guard.
native_interactions = GAME/'common/character_interactions/10_tgp_interactions.txt'
source = native_interactions.read_text(encoding='utf-8-sig')
bridge_interactions = []
interaction_manifest = {'source':str(native_interactions),'definitions':{}}
for key in ['celestial_give_treasury_interaction','celestial_demand_treasury_interaction','pay_treasury_debt_interaction']:
    node = next(n for n in parse(source) if n.key == key)
    originals = source[node.start:node.end]
    edits = []
    guard = '''custom_tooltip = { text = mam_cf.native_payment_guard_tt
 scope:actor = { mam_revenue_fund_member_trigger = no }
 scope:recipient = { mam_revenue_fund_member_trigger = no }
}'''
    append_block(source,node,'is_valid_showing_failures_only',guard,edits)
    # Acceptance is rechecked too: queued pre-upgrade interactions cannot debit
    # a pooled office after activation.
    accept = next(c for c in node.children if c.key == 'on_accept')
    original_body = body(source,accept)
    replacement = '''\n if = { limit = {
 scope:actor = { mam_revenue_fund_member_trigger = no }
 scope:recipient = { mam_revenue_fund_member_trigger = no }
 }\n''' + original_body + '\n }\n'
    transformed = originals
    for pos,ins in sorted(edits,reverse=True):
        rel=pos-node.start
        transformed=transformed[:rel]+ins+transformed[rel:]
    # Edits above do not precede the native acceptance block in all versions;
    # reparse its transformed offsets rather than assuming an unchanged index.
    nt = parse(transformed)[0]
    na = next(c for c in nt.children if c.key == 'on_accept')
    opening=transformed.index('{',na.start)
    transformed=transformed[:opening+1]+replacement+transformed[na.end-1:]
    bridge_interactions.append(transformed)
    interaction_manifest['definitions'][key]={'sha256':hashlib.sha256(originals.encode()).hexdigest(), 'original_accept_body':original_body}
write('common/character_interactions/zz_mam_revenue_common_native_spending.txt','\n\n'.join(bridge_interactions))
write('docs/COMMON-FUND-NATIVE-INTERACTIONS.json',json.dumps(interaction_manifest,indent=2))

loc = {
 'mam_cf.open':'Open the papers', 'mam_cf.opening':'Concerning the public accounts,',
 'mam_cf.request_title':'A Request for Public Funds',
 'mam_cf.relief_desc':"#high [scope:mam_cf_title.GetName]#! needs help with its public expenses. The proposed grant is #high [scope:mam_cf_quote|0]#! [treasury_i], paid from the common ministerial fund held by Revenue.\n\nThe fund holds [scope:mam_cf_fund_balance|0] [treasury_i]. After operating commitments and reserves, [scope:mam_cf_free|0] [treasury_i] is available for new grants. A grant for a distressed province also supports recovery for one year.",
 'mam_cf.topup_desc':"The ministries need additional provision. I propose that the imperial treasury contribute #high [scope:mam_cf_quote|0]#! [treasury_i] to the common fund in Revenue's custody.\n\nThis is an additional appropriation. The existing Ministry Budget continues to supply the offices in the usual way; those receipts are collected into the common fund once. The imperial treasury must retain at least #high 500#! [treasury_i].",
 'mam_cf.remit_desc':"I propose a contribution of #high [scope:mam_cf_quote|0]#! [treasury_i] from #high [scope:mam_cf_title.GetName]#! to the common ministerial fund.\n\nThe governor must consent, and the province must retain 200 [treasury_i]. A distressed province is exempt. This contribution uses the province's public treasury; it does not pay money to any minister personally.",
 'mam_cf.project_desc':"#high [scope:mam_cf_subject.GetShortUIName]#! seeks #high [scope:mam_cf_quote|0]#! [treasury_i] for a great project in #high [scope:mam_cf_project_target.GetName]#!. The initial request uses the project's current native starting cost.\n\nIf authorized, the advance is reserved for this office's chosen project and jurisdiction. The minister must still plan the project, meet its other requirements, and pay its native cost. Later contributions need their own allowance. Unspent authorization expires after one year.",
 'mam_cf.contribution_desc':"#high [scope:mam_cf_subject.GetShortUIName]#! asks for an allowance of #high [scope:mam_cf_quote|0]#! [treasury_i] towards #high [scope:mam_cf_selected_project.GetName]#!.\n\nThe money may fund native contributions to this project only. Each contribution consumes its actual cost from the allowance; it does not refill itself. The proposed amount is a ceiling, not a claim that every contribution has the same price.",
 'mam_cf.revise':'Let me revise the amount.', 'mam_cf.revise_tt':'Choose the amount before submitting or approving it. No money moves while editing.',
 'mam_cf.recommend':'Submit [scope:mam_cf_quote|0] [treasury_i] for consideration.',
 'mam_cf.recommend_tt':"Revenue may authorize an eligible ordinary request under delegated administration. Other proposals go to the current lawful superior. Provincial contributions first require the governor's consent. This choice does not promise payment if the available balance changes.",
 'mam_cf.approve':'Authorize [scope:mam_cf_quote|0] [treasury_i].',
 'mam_cf.approval_tt':"The payment uses the named public accounts. Existing operating obligations and the common reserve remain protected. The beneficiary gains 10 Opinion of the authorizing official for two years; provincial contributors instead lose 10 Opinion. No personal gold changes hands.",
 'mam_cf.consent':'I will make this contribution.',
 'mam_cf.consent_tt':'Consent to the stated public contribution. Any further approval required by the fiscal law still comes before payment.',
 'mam_cf.refuse':'I cannot support this request.', 'mam_cf.refuse_tt':'Close this request without a payment. A refused operating increase can be appealed once. Existing authorized salaries and standing costs continue.',
 'mam_cf.defer':'I will return to these papers later.', 'mam_cf.defer_tt':'Set this request aside for 30 days. Other pending matters can proceed. The Revenue: Resume Fiscal Papers decision can recall it sooner.',
 'mam_cf.operations_title':'The Means to Carry Out the Work',
 'mam_cf.operations_desc':"#high [scope:mam_cf_title.GetName]#! reports recurring expenses of #high [scope:mam_cf_cost|1]#! [treasury_i] each month. Its proposed discretionary working balance is #high [scope:mam_cf_headroom|0]#! [treasury_i].\n\nAn approved office retains two months of authorized costs and its chosen working balance. Revenue replenishes only what is missing, within the quarter's advance limit. New staff and military commitments require this review before they become protected obligations. Project funds are accounted for separately.",
 'mam_cf.lean':'Keep only a modest working balance for [scope:mam_cf_title.GetName].',
 'mam_cf.standard':'Provide ordinary means for [scope:mam_cf_title.GetName].',
 'mam_cf.expanded':'Give [scope:mam_cf_title.GetName] more room to act.',
 'mam_cf.lean_tt':'Authorize the reported recurring cost and 25 [treasury_i] of discretionary headroom. The protected two-month operating buffer remains. A material cut causes -15 Opinion for two years and permits one appeal.',
 'mam_cf.standard_tt':'Authorize the reported recurring cost and 75 [treasury_i] of discretionary headroom. Raising the working balance grants +10 Opinion for two years. Actual advances remain limited by available funds and the quarterly allowance.',
 'mam_cf.expanded_tt':'Authorize the reported recurring cost and 150 [treasury_i] of discretionary headroom. Raising the working balance grants +10 Opinion for two years. This authorizes a target, not an immediate unconditional payment.',
 'mam_cf.decline_increase':'The existing provision must suffice.',
 'mam_cf.decline_increase_tt':'Do not authorize new recurring commitments or a larger allowance. Retain the office\'s existing authorization. Its holder may appeal this material refusal once.',
 'mam_cf.amount_title':'How Much Can Be Committed?',
 'mam_cf.amount_desc':"The current draft is #high [scope:mam_cf_quote|0]#! [treasury_i]. Up to #high [scope:mam_cf_max|0]#! [treasury_i] can presently be proposed without breaching the payer's protected balance.\n\nEditing the draft moves no money. A project advance smaller than its native starting cost cannot fund the start; it must be amended before the project can proceed.",
 'mam_cf.plus25':'Add 25 [treasury_i].', 'mam_cf.plus100':'Add 100 [treasury_i].',
 'mam_cf.minus25':'Reduce it by 25 [treasury_i].', 'mam_cf.minus100':'Reduce it by 100 [treasury_i].',
 'mam_cf.amount_max':'Use the available [scope:mam_cf_max|0] [treasury_i].', 'mam_cf.amount_done':'Return to the request.',
 'mam_cf.programme_title':"The Government's Spending Programme",
 'mam_cf.programme_desc':"The common fund holds #high [scope:mam_cf_fund_balance|0]#! [treasury_i]. Approved recurring commitments amount to #high [scope:mam_cf_monthly|1]#! [treasury_i] a month. The present protected reserve is #high [scope:mam_cf_reserve|0]#! [treasury_i].\n\nI must decide what the remaining resources should accomplish. The programme governs new allocations for the next year. It does not cancel existing salaries, standing military obligations or already paid native projects. The fiscal law determines whose seal is needed.",
 'mam_cf.balanced':'Give Revenue room to meet the ordinary needs of government.',
 'mam_cf.reserves':'Build our reserves before undertaking optional work.',
 'mam_cf.recovery':'Put the recovery of the provinces first.',
 'mam_cf.balanced_tt':'Protect two months of aggregate approved recurring costs plus 200 [treasury_i]. Under Revenue delegation, eligible ordinary projects and grants up to 500 [treasury_i] may be approved by Revenue. Other laws require superior approval.',
 'mam_cf.reserves_tt':'Protect two months of aggregate recurring costs plus 700 [treasury_i]. New projects require superior approval. Revenue seeks at most one affordable voluntary provincial contribution per quarter. Routine obligations remain automatic.',
 'mam_cf.recovery_tt':'Protect two months of aggregate recurring costs plus 500 [treasury_i], including a 300 [treasury_i] relief provision. Genuine recovery requests take precedence. Optional projects require superior approval; distressed provinces are exempt from extraordinary contributions.',
 'mam_cf.project_title':'Provision for a Great Project',
 'mam_cf.project_choose_desc':"What work should I propose for #high [scope:mam_cf_site_title.GetName]#!? I will request its native starting cost from the common fund, then use the ordinary project controls once the advance is authorized.\n\nFunding does not waive the project's site, Influence, construction or other requirements.",
 'mam_cf.project_request_tt':'Submit a project-specific advance for the selected jurisdiction. No money moves until authorized. The native project must still be planned and funded through its own controls.',
 'mam_cf.cancel':'I need more time to consider this.',
 'mam_cf.accounts_title':'The Common Ministerial Fund',
 'mam_cf.accounts_desc':"Revenue holds #high [scope:mam_cf_fund_balance|0]#! [treasury_i] in common custody for the nine ministries. Approved recurring costs total #high [scope:mam_cf_monthly|1]#! [treasury_i] a month. The protected common reserve is #high [scope:mam_cf_reserve|0]#! [treasury_i]; #high [scope:mam_cf_free|0]#! [treasury_i] remains available for new grants.\n\nOffices keep operating buffers and approved project advances. Other surplus is collected monthly. The emperor's native Ministry Budget supplies the overall funding; exceptional imperial appropriations are separate. Personal gold and provincial treasuries remain outside the pool.",
 'mam_cf.accounts_close':'The accounts are before me.',
 'mam_cf.accounts_tt':'Monthly refills pay only the shortfall to an authorized target. Quarterly advances are limited to three months of approved costs plus discretionary headroom; initial establishment also provides a starting buffer. Unused project advances are protected until consumed, cancelled or expired.',
 'mam_cf.suspend':'Require superior review of discretionary releases.',
 'mam_cf.suspend_tt':'For 90 days, Revenue must submit discretionary proposals to the lawful superior. Routine authorized operating advances continue. The emperor or the official imposing the suspension may lift it early.',
 'mam_cf.restore':'Restore the ordinary delegation rules.',
 'mam_cf.restore_tt':'End this administrative suspension. The fiscal law and programme still govern new allocations.',
 'mam_cf.release_programme':'Let the Chancellor direct the next programme.',
 'mam_cf.release_programme_tt':'Withdraw the standing imperial programme override. The Chancellor may prepare the next programme, subject to the fiscal law. Existing allocations remain in effect.',
 'mam_cf.contribution_title':'An Allowance for Ongoing Work',
 'mam_cf.contribution_choose_desc':'Which existing imperial project should receive a contribution allowance? This allowance belongs to the selected project. Its native contribution costs and requirements still apply.',
 'mam_cf.contribution_request_tt':'Request a ceiling initially equal to one native base contribution. Revenue can revise it. This is not an automatic payment for every contribution, and it does not complete the project.',
 'mam_cf.outcome_title':'The Public Accounts: A Decision',
 'mam_cf.programme_result_desc':'The spending programme has received the required seal. Future uncommitted requests will be judged against these instructions and the current fiscal law. Existing commitments continue.',
 'mam_cf.operations_result_desc':"The operating authorization for #high [scope:mam_cf_title.GetName]#! has been recorded: #high [scope:mam_cf_cost|1]#! [treasury_i] in recurring monthly costs and #high [scope:mam_cf_headroom|0]#! [treasury_i] of discretionary headroom. Monthly advances will follow when funded. This decision alone does not create money.",
 'mam_cf.reserved_result_desc':"#high [scope:mam_cf_result_amount|0]#! [treasury_i] has been earmarked within Revenue's common account for its approved project. There was no payment from Revenue to itself. The native project will consume this allowance when funded.",
 'mam_cf.paid_result_desc':"#high [scope:mam_cf_result_amount|0]#! [treasury_i] was paid from #high [scope:mam_cf_result_payer.GetShortUIName]#!'s public account to #high [scope:mam_cf_result_payee.GetShortUIName]#!'s public account. Both account changes were checked.\n\nThe stated allocation and any applicable opinion or recovery effects have taken effect. Personal gold was unaffected.",
 'mam_cf.refused_result_desc':'The request concerning #high [scope:mam_cf_title.GetName]#! was refused. No payment was made. Existing authorized operations continue; a material operating refusal may be appealed once.',
 'mam_cf.unpaid_result_desc':'The proposed measure could not be completed. No successful payment is recorded. The current holder, approval or available funds may have changed. An uncertain native transfer places the affected accounts on hold rather than trying again.',
 'mam_cf.recorded':'I have received the decision.',
 'mam_cf.reserve_self_tt':'Earmark this amount inside the common fund for Revenue\'s approved project. No self-transfer or personal gold payment occurs.',
 'mam_cf.project_authorization_tt':'A ministry using the common fund needs an approved advance for this project type, sufficient unspent project money and an unexpired authorization. Request funding through the Ministry interaction on the intended senior governor.',
 'mam_cf.project_location_tt':'Use the senior jurisdiction named in the approved project request. All native site requirements still apply.',
 'mam_cf.contribution_authorization_tt':'A pooled ministry needs a contribution allowance for this exact project sufficient to pay this contribution\'s native treasury cost. Use Revenue: Fund a Project Contribution.',
 'mam_cf.native_payment_guard_tt':'Public funds of the nine pooled ministries must use the common-fund requests and approvals. Use the Ministry interactions for operating allocations, provincial relief and project advances, or Revenue: Appropriate Imperial Funds for a top-up.',
 'mam_revenue_fund_support_opinion':'Supported My Department', 'mam_revenue_fund_cut_opinion':'Reduced My Provision', 'mam_revenue_fund_levy_opinion':'Requested a Provincial Contribution',
}
for key,name,desc in [
 ('review_operations_interaction','Revenue: Review Operating Provision','Review this ministry\'s actual recurring costs and discretionary working balance. Current law determines who may authorize a change.'),
 ('request_operations_interaction','Revenue: Request Operating Provision','Ask Revenue to review this office\'s recurring costs and operating allowance. Existing commitments remain protected; new costs need approval.'),
 ('petition_interaction','Revenue: Petition for Public Funds','Request common funds for public debt or genuine provincial distress. Revenue reviews the request; the fiscal law determines the required approval.'),
 ('remittance_interaction','Revenue: Request Provincial Contribution','Seek a voluntary contribution from an affordable, non-distressed provincial treasury. The province must retain 200 treasury and can refuse.'),
 ('project_interaction','Revenue: Request Great Project Funding','Choose a native project for this senior jurisdiction and request its starting cost. Once funded, use the native project controls to plan it.'),
 ('appeal_interaction','Revenue: Appeal Operating Provision','Appeal a material cut or refusal once within six months. The Chancellor hears ordinary appeals; reserved or self-interested matters reach the emperor.'),
 ('accounts_decision','Revenue: Examine Common Accounts','Examine common cash, approved recurring obligations and the reserve.'),
 ('programme_decision','Revenue: Set the Spending Programme','Set funded priorities for the coming year. Imperial control requires the emperor\'s approval; the other laws permit Chancellor direction.'),
 ('topup_decision','Revenue: Appropriate Imperial Funds','Ask the emperor to transfer additional public money into the common ministerial fund. The imperial treasury must retain 500 treasury.'),
 ('contribution_decision','Revenue: Fund a Project Contribution','Request an earmarked allowance for native contributions to a specific ongoing imperial project.'),
 ('resume_decision','Revenue: Resume Fiscal Papers','Recall deferred fiscal papers for the current lawful reviewers. One actionable request is displayed at a time per reviewer.'),
 ('return_advance_decision','Revenue: Return Uncommitted Project Funds','Cancel this office\'s unused project allowance. Surviving native projects and paid costs remain intact. Actual cash above the operating target returns to common custody at the next monthly reconciliation.'),
 ('supplement_interaction','Revenue: Request Supplementary Provision','Request a one-time public-treasury advance for an exceptional operating expense, such as recruitment or native military assistance. The amount can be revised before approval. Standing maintenance still needs its own operating review.'),
 ('supplement_decision','Revenue: Request Supplementary Provision','Seek superior approval for Revenue\'s own exceptional operating allowance. This reserves funds within the common account and cannot create a self-payment.'),
]:
    loc['mam_revenue_fund_'+key] = name
    loc['mam_revenue_fund_'+key+'_desc'] = desc
for i,(project,_) in enumerate(PROJECTS,1):
    loc[f'mam_cf.project_{i}'] = f'Request provision for $great_project_type_{project}$.'
for ordinal in ['one','two','three']:
    loc[f'mam_cf.contribution_{ordinal}'] = f'Provide for #high [scope:mam_cf_project_{ordinal}.GetName]#!.'
loc.update({
 'mam_cf.accounts_minister_desc':"$mam_cf.accounts_desc$\n\nMy office holds [scope:mam_cf_local|0] [treasury_i]. Its authorization covers [scope:mam_cf_cost|1] [treasury_i] in monthly recurring costs and [scope:mam_cf_headroom|0] [treasury_i] in ordinary discretionary headroom. Up to [scope:mam_cf_left|0] [treasury_i] remains available in ordinary advances this quarter. A further [scope:mam_cf_earmark|0] [treasury_i] is reserved for an approved project.",
 'mam_cf.review_mine':'Review the provision for my own office.',
 'mam_cf.supplement_desc':"#high [scope:mam_cf_subject.GetShortUIName]#! requests a one-time advance of #high [scope:mam_cf_quote|0]#! [treasury_i] for exceptional public expenditure.\n\nRecruitment and other native expenses vary: the minister should request the actual price shown by the relevant native control. This is an operating advance, not a great-project grant or personal gold. The extra working balance expires after 90 days; unused cash returns to common custody. New recurring maintenance still needs a separate operating review.",
 'mam_cf.supplement_self_result_desc':"An additional operating provision of #high [scope:mam_cf_result_amount|0]#! [treasury_i] has been authorized for Revenue for 90 days. It remains within the common account; there was no self-payment. Unspent authorization lapses when the period ends.",
 'mam_cf.earned_payment':'An Earned Public Payment',
 'mam_cf.earned_payment_tt':"The common ministerial fund paid [scope:mam_cf_paid|0] [treasury_i] for an existing Census insurance or debt-relief entitlement. The payer's debit and recipient's credit were checked. This is an earned native benefit, separate from a discretionary relief grant.",
})
write('localization/english/mam_revenue_common_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))

# Migrate the old source-facing entry points. Retain old definitions so a save
# containing a displayed dev.48 event can close safely without spending.
def edit_definition(path, key, transform):
    p=ROOT/path
    source=p.read_text(encoding='utf-8-sig')
    node=next(n for n in parse(source) if n.key==key)
    changed=transform(source[node.start:node.end])
    write(path,source[:node.start]+changed+source[node.end:])

for path in ['common/character_interactions/mam_revenue_interactions.txt','common/decisions/mam_revenue_decisions.txt']:
    p=ROOT/path
    source=p.read_text(encoding='utf-8-sig')
    edits=[]
    for node in parse(source):
        shown=next((c for c in node.children if c.key=='is_shown'),None)
        if shown and 'always = no # retired common-fund entry' not in body(source,shown):
            edits.append((source.index('{',shown.start)+1,'\n always = no # retired common-fund entry\n'))
    for pos,ins in sorted(edits,reverse=True):
        source=source[:pos]+ins+source[pos:]
    write(path,source)

edit_definition('common/scripted_triggers/mam_revenue_triggers.txt','mam_revenue_actor_trigger',
 lambda s: s if 'NOT = { has_variable = mam_cf_active }' in s else s.replace('{','{\n title:h_china = { NOT = { has_variable = mam_cf_active } }',1))
for key,path in [('mam_revenue_maintenance_effect','common/scripted_effects/mam_revenue_initiative_effects.txt'),
                 ('mam_revenue_quarter_effect','common/scripted_effects/mam_revenue_initiative_effects.txt'),
                 ('mam_revenue_wake_effect','common/scripted_effects/mam_revenue_queue_effects.txt')]:
    def wrap(s):
        if '# legacy common-fund guard' in s: return s
        opening=s.index('{')
        return s[:opening+1]+'\n # legacy common-fund guard\n if = { limit = { title:h_china = { NOT = { has_variable = mam_cf_active } } }\n'+s[opening+1:-1]+'\n }\n}'
    edit_definition(path,key,wrap)

edit_definition('common/scripted_effects/mam_revenue_policy_effects.txt','mam_revenue_pass_authority_law_effect',lambda s:r'''mam_revenue_pass_authority_law_effect = {
 set_variable = { name = mam_rv_law_migrated value = 1 }
 set_variable = { name = mam_rv_law_cooldown value = 1 years = 5 }
 mam_revenue_set_mandate_effect = { LEVEL = $LEVEL$ }
 # Re-route uncommitted papers under the current control rights immediately.
 holder = { mam_revenue_fund_wake_effect = yes }
}''')
edit_definition('common/scripted_effects/mam_revenue_bridges_effects.txt','mam_revenue_native_request_effect',lambda s:r'''mam_revenue_native_request_effect = {
 if = { limit = { mam_revenue_native_request_trigger = yes }
  if = { limit = { scope:actor = { mam_revenue_fund_member_trigger = yes } }
   scope:actor = { mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 12 AMOUNT = request_treasury_value } }
   if = { limit = { exists = scope:mam_cf_created scope:recipient = title:h_china.holder }
    scope:mam_cf_created = {
     set_variable = { name = mam_cf_explicit_imperial value = 1 }
     set_variable = { name = mam_cf_stage value = 1 }
    }
   }
  }
  else = { scope:actor = { mam_revenue_fund_open_relief_effect = yes } }
  if = { limit = { exists = scope:mam_cf_created }
   scope:mam_cf_created = {
    set_variable = { name = mam_cf_native_petition value = 1 }
    set_variable = { name = mam_cf_native_actor value = scope:actor }
    set_variable = { name = mam_cf_native_credit value = scope:recipient }
    set_variable = { name = mam_cf_native_credit_title value = scope:recipient.primary_title }
    if = { limit = { exists = scope:hook scope:hook = yes } set_variable = { name = mam_cf_native_hook value = 1 } }
    if = { limit = { exists = scope:clear_debt scope:clear_debt = yes }
     set_variable = { name = mam_cf_clear_debt value = 1 }
     set_variable = { name = mam_cf_amount value = { value = scope:actor.treasury multiply = -1 min = 1 ceiling = yes } }
    }
   }
  }
  title:h_china.holder = { mam_revenue_fund_wake_effect = yes }
 }
}''')
edit_definition('common/scripted_triggers/mam_revenue_triggers.txt','mam_revenue_native_request_trigger',lambda s:r'''mam_revenue_native_request_trigger = {
 exists = title:h_china.holder exists = scope:actor exists = scope:recipient
 trigger_if = { limit = { exists = title:h_china.holder exists = scope:actor exists = scope:recipient }
  mam_revenue_fund_enabled_trigger = yes
  OR = {
   AND = { scope:actor = { mam_revenue_province_trigger = yes } scope:recipient = { mam_revenue_officer_trigger = yes } }
   AND = { scope:actor = { mam_revenue_fund_member_trigger = yes }
    OR = { scope:recipient = title:h_china.holder scope:recipient = { mam_revenue_officer_trigger = yes } }
   }
  }
 }
}''')

oldloc=ROOT/'localization/english/mam_revenue_l_english.yml'
old=oldloc.read_text(encoding='utf-8-sig')
lawloc={
 'mam_revenue_fiscal_authority_laws':'Revenue Fiscal Authority',
 'mam_revenue_authority_reserved':'Imperial Fiscal Control',
 'mam_revenue_authority_limited':'Supervised Fiscal Administration',
 'mam_revenue_authority_expanded':'Delegated Fiscal Administration',
 'mam_revenue_authority_reserved_desc':'The emperor approves the spending programme and every new material allocation. Revenue executes existing authorized operations automatically.',
 'mam_revenue_authority_limited_desc':'The Chancellor directs the programme and approves ordinary material allocations. The emperor reserves exceptional imperial funding and sensitive offices.',
 'mam_revenue_authority_expanded_desc':'Revenue authorizes ordinary allocations within the approved programme. The Chancellor directs priorities and hears appeals; the emperor retains reserved powers.',
}
commonlaw=[
 'Existing authorized salaries and standing military commitments are funded automatically when cash permits',
 'The imperial Ministry Budget remains the overall native funding provision; additional imperial top-ups always require imperial approval',
 'The common reserve protects two months of approved recurring costs plus the programme reserve',
 'Personal gold and provincial treasuries remain separate; no new currency is created',
 'Changes cost 150 Prestige, require peace and have a five-year cooldown',
]
rights={
 'reserved':['The emperor approves the consolidated programme, new grants and material operating changes','The Chancellor prepares priorities and hears ordinary appeals for imperial submission'],
 'limited':['The Chancellor approves the spending programme and ordinary material allocations','Imperial top-ups, Chancellor funding and sensitive senior offices remain reserved to the emperor'],
 'expanded':['Revenue may approve ordinary requests up to 500 treasury within the programme','New optional projects require superior approval under reserve-building or recovery programmes','Revenue cannot approve its own increased allowance; appeals go to the lawful superior','Imperial top-ups and sensitive senior offices remain reserved to the emperor'],
}
for level,lines in rights.items():
    lawloc['mam_revenue_authority_'+level+'_effects']='\n'.join('$EFFECT_LIST_BULLET$#indent_newline:3 '+line+'#!' for line in lines+commonlaw)
import re
for key,value in lawloc.items():
    old=re.sub(r'^ '+re.escape(key)+r':0 .*$',lambda m:' '+key+':0 '+json.dumps(value,ensure_ascii=False),old,flags=re.M)
write(str(oldloc.relative_to(ROOT)),old)

descriptor=ROOT/'descriptor.mod'
descriptor.write_text(descriptor.read_text(encoding='utf-8-sig').replace('0.4.0-alpha.20-dev.48','0.4.0-alpha.20-dev.49'),encoding='utf-8')

# Final integrations apply only to generated common-fund files.
for folder in ['common','events']:
    for p in (ROOT/folder).rglob('*revenue_common*.txt'):
        s=p.read_text(encoding='utf-8-sig')
        s=s.replace('var:mam_cf_kind < 10','mam_revenue_fund_earned_claim_trigger = no')
        s=s.replace('var:mam_cf_kind >= 10','mam_revenue_fund_earned_claim_trigger = yes')
        write(str(p.relative_to(ROOT)),s)
trig=ROOT/'common/scripted_triggers/mam_revenue_common_triggers.txt'
write(str(trig.relative_to(ROOT)),trig.read_text(encoding='utf-8-sig')+r'''
mam_revenue_fund_earned_claim_trigger = { OR = { var:mam_cf_kind = 10 var:mam_cf_kind = 11 } }
''')

# Current insurance/debt claims reserve cash against optional allocations. Keep
# one proportional essential-need snapshot before refill, then refresh all totals.
p=ROOT/'common/scripted_effects/mam_revenue_common_cash_effects.txt'
s=p.read_text(encoding='utf-8-sig')
tree=parse(s)
month=next(n for n in tree if n.key=='mam_revenue_fund_month_effect')
block=s[month.start:month.end]
begin=block.index('title:h_china = {\n    set_variable = { name = mam_cf_total_cost value = 0 }')
end=block.index('mam_revenue_fund_initiative_effect = yes',begin)
block=block[:begin]+'mam_revenue_fund_refresh_totals_effect = yes\n   '+block[end:]
write(str(p.relative_to(ROOT)),s[:month.start]+block+s[month.end:])

# Keep War's native proactive debt assistance available from its approved local
# operating provision. Revenue's custodial account must use the common route.
p=ROOT/'common/character_interactions/zz_mam_revenue_common_native_spending.txt'
s=p.read_text(encoding='utf-8-sig')
node=next(n for n in parse(s) if n.key=='pay_treasury_debt_interaction')
part=s[node.start:node.end].replace(
 'scope:actor = { mam_revenue_fund_member_trigger = no }',
 'scope:actor = { OR = { mam_revenue_fund_member_trigger = no primary_title = title:e_minister_of_war } }')
write(str(p.relative_to(ROOT)),s[:node.start]+part+s[node.end:])

# Offer an explicit supplementary military operating advance when large native
# recruitment/assistance costs would otherwise exceed a normal working buffer.
p=ROOT/'common/scripted_effects/mam_revenue_common_initiative_effects.txt'
s=p.read_text(encoding='utf-8-sig')
node=next(n for n in parse(s) if n.key=='mam_revenue_fund_initiative_effect')
outer=next(c for c in node.children if c.key=='if')
at=outer.end-1
extra=r'''
 random_vassal_or_below = { limit = {
  mam_revenue_ministry_trigger = yes is_ai = yes treasury < major_treasury_value
  primary_title = { NOT = { has_variable = mam_cf_case_12 } NOT = { has_variable = mam_cf_special_until } }
  OR = {
   AND = { has_title = title:e_minister_grand_marshal OR = {
    top_liege = { is_at_war = yes } maa_regiments_count < maa_regiments_max_count
   } }
   AND = { has_title = title:e_minister_of_war top_liege = { any_vassal_or_below = {
    vassal_contract_has_flag = celestial_military_appointment treasury < 0
   } } }
  }
  title:h_china = { mam_revenue_fund_available > 1000 }
 }
 mam_revenue_fund_request_effect = { TARGET = primary_title KIND = 12 AMOUNT = mam_revenue_fund_military_advance }
 }
'''
write(str(p.relative_to(ROOT)),s[:at]+extra+s[at:])

# Only a visible discretionary increase towards a rival conflicts with Vengeful.
# Honest is not charged stress merely for openly authorizing public spending.
p=ROOT/'events/mam_revenue_common_events.txt'
s=p.read_text(encoding='utf-8-sig')
for node in reversed(parse(s)):
    if node.key!='mam_fund.2': continue
    section=s[node.start:node.end]
    for value,label in [(25,'lean'),(75,'standard'),(150,'expanded')]:
        opt=next(c for c in parse(section)[0].children if c.key=='option' and any(x.key=='name' and x.value=='mam_cf.'+label for x in c.children))
        text=section[opt.start:opt.end]
        text=text.replace('has_trait = vengeful has_relation_rival = scope:mam_cf_subject }',
                          f'has_trait = vengeful has_relation_rival = scope:mam_cf_subject scope:mam_cf_subject.primary_title.var:mam_cf_headroom < {value} }}')
        if value==25:
            text=text.replace('ai_chance = { base = 25','ai_chance = { base = 25 modifier = { add = 80 has_trait = vengeful has_relation_rival = scope:mam_cf_subject }')
        if value==150:
            text=text.replace('ai_chance = { base = 25','ai_chance = { base = 25 modifier = { add = 35 has_trait = ambitious OR = { is_close_or_extended_family_of = scope:mam_cf_subject has_relation_friend = scope:mam_cf_subject is_in_same_movement_as = { TARGET = scope:mam_cf_subject } } }')
        section=section[:opt.start]+text+section[opt.end:]
    s=s[:node.start]+section+s[node.end:]
write(str(p.relative_to(ROOT)),s)

write('common/customizable_localization/mam_revenue_common_loc.txt',r'''
MamRevenueFundProgramme = {
 type = character
 text = { trigger = { title:h_china.var:mam_cf_programme = 1 } localization_key = mam_cf.programme_reserves }
 text = { trigger = { title:h_china.var:mam_cf_programme = 2 } localization_key = mam_cf.programme_recovery }
 text = { localization_key = mam_cf.programme_balanced }
}
MamRevenueFundAuthority = {
 type = character
 text = { trigger = { title:h_china.holder = { has_realm_law = mam_revenue_authority_expanded } } localization_key = mam_revenue_authority_expanded }
 text = { trigger = { title:h_china.holder = { has_realm_law = mam_revenue_authority_limited } } localization_key = mam_revenue_authority_limited }
 text = { localization_key = mam_revenue_authority_reserved }
}
''')
loc.update({
 'mam_cf.programme_balanced':'balanced administration', 'mam_cf.programme_reserves':'building reserves',
 'mam_cf.programme_recovery':'provincial recovery',
})
loc['mam_cf.accounts_desc'] += "\n\nThe programme is #high [scope:mam_cf_emperor.Custom('MamRevenueFundProgramme')]#! under #high [scope:mam_cf_emperor.Custom('MamRevenueFundAuthority')]#!."

# Let the native ledger settle before taking its first cost baseline and sweeping
# opening balances. This is a one-time adoption period, not a repeated delay.
edit_definition('common/scripted_effects/mam_revenue_common_cash_effects.txt','mam_revenue_fund_start_effect',
 lambda s:s.replace('set_variable = { name = mam_cf_active value = 1 }', '''set_variable = { name = mam_cf_active value = 1 }
    set_variable = { name = mam_cf_bootstrap_until value = { value = current_date add = 35 } }
    holder = { trigger_event = { id = mam_fund.99 days = 35 } }''').replace('mam_revenue_fund_month_effect = yes', '''if = { limit = { title:h_china = { NOT = { has_variable = mam_cf_bootstrap_done } var:mam_cf_bootstrap_until <= current_date } }
  '''+roster('''set_variable = { name = mam_cf_cost value = { value = holder.mam_revenue_fund_observed_cost min = var:mam_cf_cost } }
  set_variable = { name = mam_cf_remaining value = { value = var:mam_cf_cost multiply = 5 add = 150 } }''')+'''
   title:h_china = { set_variable = { name = mam_cf_bootstrap_done value = 1 } remove_variable = mam_cf_next_month }
  }
  mam_revenue_fund_month_effect = yes'''))
edit_definition('common/scripted_effects/mam_revenue_common_cash_effects.txt','mam_revenue_fund_month_effect',
 lambda s:s.replace('mam_revenue_emperor_trigger = yes mam_revenue_fund_enabled_trigger = yes',
                    'mam_revenue_emperor_trigger = yes mam_revenue_fund_ready_trigger = yes'))
edit_definition('common/scripted_effects/mam_revenue_common_queue_effects.txt','mam_revenue_fund_request_effect',
 lambda s:s.replace('mam_revenue_fund_enabled_trigger = yes','mam_revenue_fund_ready_trigger = yes'))
edit_definition('common/scripted_effects/mam_revenue_common_claims_effects.txt','mam_revenue_fund_claim_commit_effect',
 lambda s:s.replace('mam_revenue_fund_live_case_trigger = yes','mam_revenue_fund_live_case_trigger = yes mam_revenue_fund_ready_trigger = yes'))
edit_definition('common/scripted_triggers/mam_revenue_triggers.txt','mam_revenue_native_request_trigger',
 lambda s:s.replace('mam_revenue_fund_enabled_trigger = yes','mam_revenue_fund_ready_trigger = yes'))
p=ROOT/'common/scripted_triggers/mam_revenue_common_triggers.txt'
write(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8-sig')+'''
mam_revenue_fund_ready_trigger = {
 mam_revenue_fund_enabled_trigger = yes title:h_china = { has_variable = mam_cf_bootstrap_done }
}
''')
for rel in ['common/character_interactions/mam_revenue_common_interactions.txt','common/decisions/mam_revenue_common_decisions.txt']:
    p=ROOT/rel; s=p.read_text(encoding='utf-8-sig'); edits=[]
    for n in parse(s):
        if n.key=='mam_revenue_fund_accounts_decision': continue
        valid=next((c for c in n.children if c.key=='is_valid'),None)
        gate='custom_tooltip = { text = mam_cf.ready_tt mam_revenue_fund_ready_trigger = yes }'
        if valid: edits.append((s.index('{',valid.start)+1,'\n '+gate+'\n'))
        else: edits.append((n.end-1,'\n is_valid = { '+gate+' }\n'))
    for at,ins in sorted(edits,reverse=True): s=s[:at]+ins+s[at:]
    write(rel,s)

# The public debt option retains the native creditor reward after a verified
# payment which actually clears the debt, rather than granting it on submission.
edit_definition('common/character_interactions/mam_revenue_common_interactions.txt','mam_revenue_fund_petition_interaction',
 lambda s:s[:-1]+r'''
 cost = { influence = medium_influence_value }
 send_options_exclusive = no
 send_option = {
  flag = clear_debt localization = OPTION_CLEAR_DEBT
  is_shown = { scope:actor = { treasury < 0 } }
  is_valid = { scope:actor = { treasury < 0 } }
 }
 on_send = { }
}''')
p=ROOT/'common/character_interactions/mam_revenue_common_interactions.txt'
s=p.read_text(encoding='utf-8-sig')
node=next(n for n in parse(s) if n.key=='mam_revenue_fund_petition_interaction')
part=s[node.start:node.end]
part=part.replace('scope:actor = { mam_revenue_fund_open_relief_effect = yes }',r'''
scope:actor = { mam_revenue_fund_open_relief_effect = yes }
if = { limit = { exists = scope:mam_cf_created exists = scope:clear_debt scope:clear_debt = yes }
 scope:mam_cf_created = {
  set_variable = { name = mam_cf_amount value = { value = scope:actor.treasury multiply = -1 min = 1 ceiling = yes } }
  set_variable = { name = mam_cf_native_petition value = 1 }
  set_variable = { name = mam_cf_clear_debt value = 1 }
  set_variable = { name = mam_cf_native_actor value = scope:actor }
  set_variable = { name = mam_cf_native_credit value = scope:recipient }
  set_variable = { name = mam_cf_native_credit_title value = scope:recipient.primary_title }
 }
}
''')
write(str(p.relative_to(ROOT)),s[:node.start]+part+s[node.end:])
loc['mam_revenue_fund_petition_interaction_desc'] += ' Requesting costs native medium Influence. The optional debt-clearance request uses the present public debt; a payment which clears it grants the continuing creditor the native indebted hook and Influence reward.'

# Material cost changes are considered each month; optional initiatives remain
# quarterly. A quarter-long office review interval prevents repeat refusal spam.
p=ROOT/'common/scripted_effects/mam_revenue_common_initiative_effects.txt'
s=p.read_text(encoding='utf-8-sig')
initiative=next(n for n in parse(s) if n.key=='mam_revenue_fund_initiative_effect')
quarter=next(c for c in initiative.children if c.key=='if')
review=next(c for c in quarter.children if c.key=='random_vassal_or_below')
review_text=s[review.start:review.end].replace(
 'mam_revenue_fund_observed_cost > { value = primary_title.var:mam_cf_cost add = 10 }',
 '''OR = {
 mam_revenue_fund_observed_cost > { value = primary_title.var:mam_cf_cost add = 10 }
 mam_revenue_fund_observed_cost < { value = primary_title.var:mam_cf_cost subtract = 10 min = 0 }
 }''')
s=s[:review.start]+s[review.end:]
initiative=next(n for n in parse(s) if n.key=='mam_revenue_fund_initiative_effect')
opening=s.index('{',initiative.start)+1
s=s[:opening]+'\n'+review_text+'\n'+s[opening:]
write(str(p.relative_to(ROOT)),s)
edit_definition('common/scripted_effects/mam_revenue_common_initiative_effects.txt','mam_revenue_fund_open_operations_effect',
 lambda s:s.replace('if = { limit = { exists = scope:mam_cf_created }', '''if = { limit = { exists = scope:mam_cf_created }
  primary_title = { set_variable = { name = mam_cf_review_until value = { value = current_date add = 90 } } }''',1))

# The delayed setup takes a fresh native expense baseline, not a guessed equal
# share. Standing costs and supplementary recruitment advances remain separate.
loc['mam_cf.supplement_desc'] += ' This allowance does not pay expenses charged by the native game to personal Gold.'

write('common/scripted_effects/mam_revenue_common_returns.txt',r'''
# Title scope. Return only cash actually present above current operating needs.
mam_revenue_fund_settle_return_effect = {
 if = { limit = { has_variable = mam_cf_return_pending }
  if = { limit = { this = title:e_minister_of_revenue } remove_variable = mam_cf_return_pending }
  else_if = { limit = { exists = holder exists = title:e_minister_of_revenue.holder
   title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }
  }
   mam_revenue_fund_sweep_effect = yes
   if = { limit = { holder.treasury < { value = mam_revenue_fund_cash_target add = 1 } }
    remove_variable = mam_cf_return_pending
   }
  }
 }
}
mam_revenue_fund_return_project_effect = {
 set_variable = { name = mam_cf_project_cash value = 0 }
 remove_variable = mam_cf_project_type remove_variable = mam_cf_project_target
 remove_variable = mam_cf_project_instance remove_variable = mam_cf_project_until
 set_variable = { name = mam_cf_return_pending value = 1 }
 mam_revenue_fund_settle_return_effect = yes
}
''')
# Use parsed offsets instead of relying on whitespace from the decision template.
p=ROOT/'common/decisions/mam_revenue_common_decisions.txt'
s=p.read_text(encoding='utf-8-sig'); n=next(n for n in parse(s) if n.key=='mam_revenue_fund_return_advance_decision')
eff=next(c for c in n.children if c.key=='effect')
s=s[:eff.start]+'effect = { primary_title = { mam_revenue_fund_return_project_effect = yes } }'+s[eff.end:]
write(str(p.relative_to(ROOT)),s)
edit_definition('common/scripted_effects/mam_revenue_common_cash_effects.txt','mam_revenue_fund_init_office_effect',
 lambda s:s[:-1]+'\n mam_revenue_fund_settle_return_effect = yes\n}')
edit_definition('common/scripted_effects/mam_revenue_common_choice_effects.txt','mam_revenue_fund_commit_effect',
 lambda s:s.replace('change_variable = { name = mam_cf_project_cash add = scope:mam_cf_paid }',
 '''change_variable = { name = mam_cf_project_cash add = scope:mam_cf_paid }
      set_variable = { name = mam_cf_next_project_request value = { value = current_date add = 90 } }'''))
for rel, keys in [
 ('common/scripted_effects/mam_revenue_common_initiative_effects.txt',['mam_revenue_fund_open_project_effect','mam_revenue_fund_open_contribution_effect']),
]:
    for key in keys:
        edit_definition(rel,key,lambda s:s.replace('{','''{
 if = { limit = { primary_title = {
  NOT = { has_variable = mam_cf_return_pending }
  trigger_if = { limit = { has_variable = mam_cf_next_project_request } var:mam_cf_next_project_request <= current_date }
 } }
''',1)[:-1]+'\n }\n}')
# Prevent a duplicate advance during cancellation/regrant or an unrefunded hold.
p=ROOT/'common/character_interactions/mam_revenue_common_interactions.txt'
s=p.read_text(encoding='utf-8-sig'); node=next(n for n in parse(s) if n.key=='mam_revenue_fund_project_interaction')
valid=next(c for c in node.children if c.key=='is_valid'); at=s.index('{',valid.start)+1
s=s[:at]+'''\n custom_tooltip = { text = mam_cf.project_interval_tt scope:actor.primary_title = {
 NOT = { has_variable = mam_cf_return_pending }
 trigger_if = { limit = { has_variable = mam_cf_next_project_request } var:mam_cf_next_project_request <= current_date }
 } }\n'''+s[at:]
write(str(p.relative_to(ROOT)),s)
loc['mam_cf.project_interval_tt']='An office can receive one new project or contribution allowance per 90 days. An uncommitted return must be reconciled before another advance. Paid project costs and native benefits remain intact.'
loc['mam_revenue_fund_return_advance_decision_desc']='Cancel this office\'s unused project allowance. Cash actually present above its operating target returns to common custody immediately when the custodian is available, or at the next reconciliation. Paid native costs remain intact. Returning an advance does not reset its 90-day grant interval.'

# Internal drafting is a portrait event; correspondence between different people
# uses the native letter layout. No letter is sent from a character to themself.
p=ROOT/'events/mam_revenue_common_events.txt'
s=p.read_text(encoding='utf-8-sig')
first=next(n for n in parse(s) if n.key=='mam_fund.1')
draft=s[first.start:first.end].replace('mam_fund.1 =','mam_fund.8 =',1)
nodes=parse(draft)[0]
edits=[]
for n in nodes.children:
    if n.key=='type': edits.append((n.start,n.end,'type = character_event theme = stewardship'))
    if n.key in {'sender','opening'}: edits.append((n.start,n.end,''))
for a,b,value in sorted(edits,reverse=True): draft=draft[:a]+value+draft[b:]
draft=draft[:-1]+'''
 left_portrait = { character = root animation = reading }
 right_portrait = { trigger = { scope:mam_cf_subject != root } character = scope:mam_cf_subject animation = thinking }
}'''
s+='\n'+draft+'\n'
s=s.replace('trigger_event = mam_fund.1','mam_revenue_fund_show_request_effect = yes')
write(str(p.relative_to(ROOT)),s)
p=ROOT/'common/scripted_effects/mam_revenue_common_queue_effects.txt'
s=p.read_text(encoding='utf-8-sig').replace('trigger_event = mam_fund.1','mam_revenue_fund_show_request_effect = yes')
s+=r'''
mam_revenue_fund_show_request_effect = {
 if = { limit = { scope:mam_cf_file.var:mam_cf_requester = root scope:mam_cf_file.var:mam_cf_stage = 0 }
  trigger_event = mam_fund.8
 }
 else = { trigger_event = mam_fund.1 }
}
'''
write(str(p.relative_to(ROOT)),s)
# Stale windows always have an exit and cannot cancel a newer generation.
p=ROOT/'events/mam_revenue_common_events.txt'
s=p.read_text(encoding='utf-8-sig')
for node in reversed(parse(s)):
    if node.key not in {'mam_fund.1','mam_fund.2','mam_fund.3','mam_fund.4','mam_fund.8'}: continue
    extra=r'''
 option = { name = mam_cf.changed trigger = { mam_revenue_fund_actor_trigger = no }
  custom_tooltip = mam_cf.changed_tt
  hidden_effect = { if = { limit = { exists = scope:mam_cf_file }
   scope:mam_cf_file = { if = { limit = { var:mam_cf_pending = 1 mam_revenue_fund_live_case_trigger = no }
    mam_revenue_fund_close_effect = { RESULT = 4 }
   } }
  } }
  ai_chance = { base = 100 }
 }
'''
    s=s[:node.end-1]+extra+s[node.end-1:]
write(str(p.relative_to(ROOT)),s)
edit_definition('common/scripted_triggers/mam_revenue_common_triggers.txt','mam_revenue_fund_actor_trigger',
 lambda s:s[:s.index(' var:mam_cf_open = scope:mam_cf_file')]+''' trigger_if = { limit = { exists = scope:mam_cf_file exists = var:mam_cf_open }
'''+s[s.index(' var:mam_cf_open = scope:mam_cf_file'):-1]+'\n }\n}')
edit_definition('common/scripted_triggers/mam_revenue_common_triggers.txt','mam_revenue_fund_live_case_trigger',
 lambda s:s[:s.index(' trigger_if =')]+''' trigger_if = { limit = { exists = var:mam_cf_target.holder exists = var:mam_cf_requester }
'''+s[s.index(' trigger_if ='):-1]+'\n }\n}')
edit_definition('common/story_cycles/mam_revenue_common_story.txt','mam_revenue_fund_story',
 lambda s:s.replace('on_owner_death = {','on_owner_death = {\n clear_saved_scope = mam_cf_heir',1).replace(
 'if = { limit = { exists = scope:mam_cf_heir } make_story_owner = scope:mam_cf_heir }',
 '''if = { limit = { NOT = { exists = scope:mam_cf_heir } }
  title:h_china.current_heir ?= { if = { limit = { is_alive = yes } save_scope_as = mam_cf_heir } }
 }
 if = { limit = { exists = scope:mam_cf_heir } make_story_owner = scope:mam_cf_heir }'''))
loc['mam_cf.changed']='The circumstances have changed. Set these papers aside.'
loc['mam_cf.changed_tt']='Close this outdated window without authorizing a payment. A pending valid request remains with its current lawful reviewer.'

# Page through real ongoing projects; the next-page option exists only when a
# fourth unseen project exists. There is no empty "another shortlist" action.
write('common/scripted_effects/mam_revenue_common_project_menu.txt',r'''
mam_revenue_fund_reset_project_menu_effect = {
 save_scope_as = mam_cf_project_reader
 every_in_list = { variable = mam_cf_seen_projects
  scope:mam_cf_project_reader = { remove_list_variable = { name = mam_cf_seen_projects target = prev } }
 }
}
''')
edit_definition('common/decisions/mam_revenue_common_decisions.txt','mam_revenue_fund_contribution_decision',
 lambda s:s.replace('trigger_event = mam_fund.7','mam_revenue_fund_reset_project_menu_effect = yes trigger_event = mam_fund.7').replace(
 'is_valid = {','''is_valid = { custom_tooltip = { text = mam_cf.project_interval_tt primary_title = {
 NOT = { has_variable = mam_cf_return_pending }
 trigger_if = { limit = { has_variable = mam_cf_next_project_request } var:mam_cf_next_project_request <= current_date }
 } }''',1))
p=ROOT/'events/mam_revenue_common_events.txt'
s=p.read_text(encoding='utf-8-sig'); node=next(n for n in parse(s) if n.key=='mam_fund.7')
part=s[node.start:node.end]
part=part.replace('immediate = {','''immediate = {
 clear_saved_scope = mam_cf_project_one clear_saved_scope = mam_cf_project_two
 clear_saved_scope = mam_cf_project_three clear_saved_scope = mam_cf_project_four
''',1)
where='limit = { great_project_owner = { top_liege = title:h_china.holder } }'
where_paged='''limit = { great_project_owner = { top_liege = title:h_china.holder }
 save_temporary_scope_as = mam_cf_possible_project
 NOT = { root = { any_in_list = { variable = mam_cf_seen_projects this = scope:mam_cf_possible_project } } }
 }'''
part=part.replace(where,where_paged)
immediate=next(c for c in parse(part)[0].children if c.key=='immediate')
fourth=f'''\n ordered_great_project = {{ {where_paged}
 order_by = {{ value = 1 }} position = 3 check_range_bounds = no save_scope_as = mam_cf_project_four
 }}\n'''
part=part[:immediate.end-1]+fourth+part[immediate.end-1:]
part=part[:-1]+r'''
 option = { name = mam_cf.next_projects trigger = { exists = scope:mam_cf_project_four mam_revenue_fund_member_trigger = yes }
  hidden_effect = {
   if = { limit = { exists = scope:mam_cf_project_one } add_to_variable_list = { name = mam_cf_seen_projects target = scope:mam_cf_project_one } }
   if = { limit = { exists = scope:mam_cf_project_two } add_to_variable_list = { name = mam_cf_seen_projects target = scope:mam_cf_project_two } }
   if = { limit = { exists = scope:mam_cf_project_three } add_to_variable_list = { name = mam_cf_seen_projects target = scope:mam_cf_project_three } }
   trigger_event = mam_fund.7
  }
 }
 option = { name = mam_cf.first_projects trigger = { any_in_list = { variable = mam_cf_seen_projects always = yes } }
  hidden_effect = { mam_revenue_fund_reset_project_menu_effect = yes trigger_event = mam_fund.7 }
 }
}'''
s=s[:node.start]+part+s[node.end:]; write(str(p.relative_to(ROOT)),s)
loc['mam_cf.next_projects']='Bring me the next project papers.'
loc['mam_cf.first_projects']='Return to the first project papers.'

# A debt request cannot become an overpayment or a free debt-clearance hook
# after another source has already paid the office's debt.
edit_definition('common/scripted_triggers/mam_revenue_common_triggers.txt','mam_revenue_fund_live_case_trigger',
 lambda s:s[:-1]+'''
 trigger_if = { limit = { has_variable = mam_cf_clear_debt exists = var:mam_cf_target.holder } var:mam_cf_target.holder = { treasury < 0 } }
}''')
edit_definition('common/scripted_effects/mam_revenue_common_choice_effects.txt','mam_revenue_fund_commit_effect',
 lambda s:s.replace('save_scope_value_as = { name = mam_cf_amount value = var:mam_cf_amount }', '''if = { limit = { has_variable = mam_cf_clear_debt }
    set_variable = { name = mam_cf_amount value = { value = var:mam_cf_amount
     max = { value = var:mam_cf_target.holder.treasury multiply = -1 min = 0 } }
    }
   }
   save_scope_value_as = { name = mam_cf_amount value = var:mam_cf_amount }''',1))
loc['mam_cf.debt_desc']="#high [scope:mam_cf_subject.GetShortUIName]#! requests up to #high [scope:mam_cf_quote|0]#! [treasury_i] to settle the public debt of #high [scope:mam_cf_title.GetName]#!. Payment comes from the common ministerial fund and is capped at the debt remaining when the money is released.\n\nIf this payment clears the debt, the continuing native creditor receives the native Influence and indebted-hook benefit. A refused request or insufficient partial payment does not create a clearance hook. Personal Gold remains separate."
for key in ['mam_fund.1','mam_fund.8']:
    edit_definition('events/mam_revenue_common_events.txt',key,
      lambda s:s.replace('first_valid = {','first_valid = { triggered_desc = { trigger = { scope:mam_cf_file = { has_variable = mam_cf_clear_debt } } desc = mam_cf.debt_desc }',1))

# Legacy saved action windows remain dismissible after the old system retires.
p=ROOT/'events/mam_revenue_events.txt'; s=p.read_text(encoding='utf-8-sig')
for node in reversed(parse(s)):
    if not any(n.key=='mam_revenue_actor_trigger' for c in node.children if c.key=='trigger' for n in c.walk()): continue
    if 'mam_cf.legacy_changed' in s[node.start:node.end]: continue
    extra=r'''
 option = { name = mam_cf.legacy_changed
  trigger = { title:h_china = { has_variable = mam_cf_active } mam_revenue_actor_trigger = no }
  custom_tooltip = mam_cf.changed_tt
  hidden_effect = { if = { limit = { exists = scope:mam_rv_file }
   scope:mam_rv_file = { if = { limit = { var:mam_rv_pending = 1 } mam_revenue_close_effect = yes } }
  } }
 }
'''
    s=s[:node.end-1]+extra+s[node.end-1:]
write(str(p.relative_to(ROOT)),s)
loc['mam_cf.legacy_changed']='These papers belong to the former fiscal arrangement. Close them.'
p=ROOT/'events/mam_revenue_events.txt'; s=p.read_text(encoding='utf-8-sig'); fixes=[]
for top in parse(s):
    for opt in (n for n in top.children if n.key=='option'):
        if any(n.key=='name' and n.value=='mam_cf.legacy_changed' for n in opt.children) and not any(n.key=='custom_tooltip' for n in opt.children):
            fixes.append(opt.end-1)
for at in sorted(fixes,reverse=True): s=s[:at]+'\n custom_tooltip = mam_cf.changed_tt\n'+s[at:]
write(str(p.relative_to(ROOT)),s)

# A minor sovereign does not stop the institution. These Revenue-only role
# guards leave ministerial adulthood rules and Personnel's roles untouched.
edit_definition('common/scripted_triggers/mam_revenue_triggers.txt','mam_revenue_emperor_trigger',
 lambda s:s.replace('is_adult = yes ',''))
edit_definition('common/scripted_triggers/mam_revenue_triggers.txt','mam_revenue_authority_trigger',
 lambda s:r'''mam_revenue_authority_trigger = {
 OR = { mam_revenue_officer_trigger = yes mam_revenue_chancellor_trigger = yes mam_revenue_emperor_trigger = yes }
 is_imprisoned = no OR = { is_adult = yes mam_revenue_emperor_trigger = yes }
 NOT = { has_trait = incapable }
}''')
edit_definition('common/scripted_effects/mam_revenue_common_queue_effects.txt','mam_revenue_fund_resolve_effect',
 lambda s:s.replace('mam_revenue_fund_live_case_trigger = yes',
 '''mam_revenue_fund_live_case_trigger = yes exists = title:e_minister_of_revenue.holder
  title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }''',1))
edit_definition('common/scripted_triggers/mam_revenue_common_triggers.txt','mam_revenue_fund_actor_trigger',
 lambda s:s.replace('mam_revenue_fund_live_case_trigger = yes',
 '''mam_revenue_fund_live_case_trigger = yes exists = title:e_minister_of_revenue.holder
  title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }''',1))
for rel in ['common/scripted_effects/mam_revenue_common_queue_effects.txt','events/mam_revenue_common_events.txt']:
    p=ROOT/rel; s=p.read_text(encoding='utf-8-sig')
    old='title:e_minister_of_revenue.holder ?= { save_scope_value_as = { name = mam_cf_fund_balance value = treasury } }'
    new='title:e_minister_of_revenue.holder ?= { if = { limit = { mam_revenue_officer_trigger = yes } save_scope_value_as = { name = mam_cf_fund_balance value = treasury } } }'
    s=s.replace(old,new); write(rel,s)

# Distinct native debt benefits must not be swallowed when several contributors
# complete together. Insurance deduplicates by its marked covered counties;
# periodic maintenance only settles an existing claim and never creates another.
def lift_claim_dedup(s):
    outer=next(c for c in parse(s)[0].children if c.key=='if')
    gate=next(c for c in outer.children if c.key=='if' and any(n.key=='any_in_list' for n in c.walk()))
    limit=next(c for c in gate.children if c.key=='limit')
    return s[:gate.start]+s[limit.end:gate.end-1]+s[gate.end:]
edit_definition('common/scripted_effects/mam_revenue_common_claims_effects.txt','mam_revenue_fund_create_claim_effect',lift_claim_dedup)

# Fickle can favor a permissible annual change; Stubborn favors continuity.
p=ROOT/'events/mam_revenue_common_events.txt'
s=p.read_text(encoding='utf-8-sig'); programme=next(n for n in parse(s) if n.key=='mam_fund.4')
part=s[programme.start:programme.end]
for mode,label in [(0,'balanced'),(1,'reserves'),(2,'recovery')]:
    opt=next(c for c in parse(part)[0].children if c.key=='option' and any(x.key=='name' and x.value=='mam_cf.'+label for x in c.children))
    ai=next(c for c in opt.children if c.key=='ai_chance'); at=part.index('{',ai.start)+1
    bias=f''' modifier = {{ add = 35 has_trait = stubborn title:h_china.var:mam_cf_programme = {mode} }}
 modifier = {{ add = 20 has_trait = fickle title:h_china = {{ NOT = {{ var:mam_cf_programme = {mode} }} }} }}\n'''
    part=part[:at]+bias+part[at:]
s=s[:programme.start]+part+s[programme.end:]; write(str(p.relative_to(ROOT)),s)
loc['mam_cf.paid_result_desc']="#high [scope:mam_cf_result_amount|0]#! [treasury_i] was paid from the public treasury of #high [scope:mam_cf_result_payer_title.GetName]#!, administered by [scope:mam_cf_result_payer.GetShortUIName], to #high [scope:mam_cf_result_payee_title.GetName]#!, administered by [scope:mam_cf_result_payee.GetShortUIName]. Both account changes were checked.\n\nThe allocation and applicable opinion or recovery effects have taken effect. Personal Gold was unaffected."
edit_definition('common/scripted_triggers/mam_revenue_common_triggers.txt','mam_revenue_fund_ready_trigger',
 lambda s:s[:-1]+'\n mam_revenue_fund_custodian_trigger = yes\n}')
p=ROOT/'common/scripted_triggers/mam_revenue_common_triggers.txt'
write(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8-sig')+r'''
mam_revenue_fund_custodian_trigger = {
 exists = title:e_minister_of_revenue.holder
 trigger_if = { limit = { exists = title:e_minister_of_revenue.holder }
  title:e_minister_of_revenue.holder = { mam_revenue_officer_trigger = yes }
 }
}
''')
edit_definition('events/mam_revenue_common_events.txt','mam_fund.6',
 lambda s:s.replace('first_valid = {','''first_valid = {
 triggered_desc = { trigger = { mam_revenue_fund_custodian_trigger = no } desc = mam_cf.accounts_paused_desc }
 triggered_desc = { trigger = { title:e_minister_of_revenue = { has_variable = mam_cf_payment_hold } } desc = mam_cf.accounts_held_desc }
''',1))
loc['mam_cf.accounts_paused_desc']='The common fund awaits a qualified Revenue custodian. The imperial treasury will not be treated as the common account during temporary custody. Office records and pending claims remain in place, while native income and ordinary local expenses continue. Pooled releases resume when the Revenue title and council seat agree.'
loc['mam_cf.accounts_held_desc']='The common account is on hold after a payment could not be verified. Further releases have stopped so that the same money is not paid twice. The receipt records both account readings for inspection. Keep the immediate save and error log before attempting another transaction.'
loc['mam_cf.ready_tt']='The common-fund administration needs a qualified Revenue custodian and a one-time 35-day transition for native income and expenses to settle. Existing native funding continues during that period.'
loc['mam_cf.accounts_tt'] += ' The first common reconciliation follows a one-time 35-day adoption period.'
loc['mam_cf.accounts_desc'] = "Revenue holds #high [scope:mam_cf_fund_balance|0]#! [treasury_i] for the nine ministries. Recurring commitments total #high [scope:mam_cf_monthly|1]#! [treasury_i] a month. The protected reserve is #high [scope:mam_cf_reserve|0]#! [treasury_i]; #high [scope:mam_cf_free|0]#! [treasury_i] is available for new grants.\n\nThe programme is #high [scope:mam_cf_emperor.Custom('MamRevenueFundProgramme')]#! under #high [scope:mam_cf_emperor.Custom('MamRevenueFundAuthority')]#!. Offices retain operating buffers and approved project advances. Imperial funding, personal gold and provincial accounts remain distinct."
loc['mam_cf.accounts_minister_desc'] = "$mam_cf.accounts_desc$\n\nMy office holds [scope:mam_cf_local|0] [treasury_i]. Its authorization covers [scope:mam_cf_cost|1] [treasury_i] a month and [scope:mam_cf_headroom|0] [treasury_i] in ordinary headroom. [scope:mam_cf_left|0] [treasury_i] remains in this quarter's ordinary advances, with [scope:mam_cf_earmark|0] [treasury_i] earmarked for a project."
write('localization/english/mam_revenue_common_l_english.yml','l_english:\n'+'\n'.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False) for k,v in loc.items()))

if __name__ == '__main__':
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev50.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev51.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev52.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev53.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev54.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev55.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev56.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev57.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev58.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev59.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev60.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/upgrade_common_fund_dev61.py'), run_name='__main__')
    runpy.run_path(str(ROOT/'tools/build_censor.py'))['generate'](ROOT)
    runpy.run_path(str(ROOT/'tools/build_justice.py'))['generate'](ROOT)
    print('Common-fund core generated.')

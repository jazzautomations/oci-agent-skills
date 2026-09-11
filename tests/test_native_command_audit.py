import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/eval'))
import audit_native_commands as audit


def test_required_alias_and_quoted_query_operator_are_recognized():
    aliases={'iam policy list':{'-c':'--compartment-id'}}
    result=audit.inspect("oci iam policy list -c '$TENANCY_ID' --limit 10 --query 'data[?name==`a` || name==`b`]'",aliases,{})
    assert result['valid']


def test_all_and_limit_conflict_and_invalid_query_fail():
    aliases={'iam policy list':{}}
    prefix='oci iam policy list --compartment-id "$TENANCY_ID" --limit 10 '
    assert audit.inspect(prefix+'--all --query data',aliases,{})['reason']=='all_and_limit_conflict'
    assert not audit.inspect(prefix+'--query "data["',aliases,{})['valid']


def test_shell_operator_outside_query_is_not_executed():
    aliases={'iam policy list':{}}
    result=audit.inspect('oci iam policy list --compartment-id "$TENANCY_ID" --limit 10 --query data || echo unexpected',aliases,{})
    assert result['reason']=='shell_composition_or_substitution'


def test_enum_uses_pinned_choice_conversion_including_case_insensitivity():
    import click
    aliases={'resource-manager job list':{}}
    choices={'resource-manager job list':{'--sort-by':click.Choice(['TIMECREATED'],case_sensitive=False)}}
    command='oci resource-manager job list --stack-id "$STACK_ID" --limit 10 --query data --sort-by '
    assert audit.inspect(command+'timeCreated',aliases,choices)['valid']
    assert audit.inspect(command+'UNKNOWN',aliases,choices)['reason']=='invalid_enum_option'

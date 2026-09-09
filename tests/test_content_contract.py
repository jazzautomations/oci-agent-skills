"""Content regressions for bounded read examples and meaningful routing."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/ci'),str(ROOT/'scripts')]
import lint_fences
import check_refs


def test_read_fence_requires_query_and_supported_limit(tmp_path):
    p=tmp_path/'guide.md'
    p.write_text('```bash\noci compute instance list --compartment-id "$COMPARTMENT_ID" --limit 20\n```\n')
    assert any(f['code']=='missing_read_query' for f in lint_fences.validate(p))
    p.write_text('```bash\noci compute instance list --compartment-id "$COMPARTMENT_ID" --all --query data\n```\n')
    assert any(f['code']=='unbounded_list' for f in lint_fences.validate(p))
    p.write_text('```bash\noci os ns get --query data\n```\n')
    assert not lint_fences.validate(p)


def test_route_rejects_boilerplate(tmp_path):
    p=tmp_path/'SKILL.md'
    p.write_text('## Route\n| Intent | Load | Why |\n|---|---|---|\n| DNS | dns | Load when needed. |\n')
    assert any(f['code']=='route_without_discriminator' for f in check_refs.validate(p))

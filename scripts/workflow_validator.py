import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValidationError(Exception):
    pass


def load_json(path: Path):
    with path.open('r', encoding='utf-8-sig') as f:
        return json.load(f)


def validate_agents(flow: dict) -> None:
    agents = flow.get('agents', [])
    if len(agents) < 8:
        raise ValidationError('At least 8 agents are required.')

    for agent in agents:
        role_file = ROOT / 'agents' / agent / 'role.md'
        skills_file = ROOT / 'agents' / agent / 'skills.json'
        skill_md = ROOT / 'skills' / agent / 'SKILL.md'

        if not role_file.exists():
            raise ValidationError(f'Missing role file: {role_file}')
        if not skills_file.exists():
            raise ValidationError(f'Missing skills file: {skills_file}')
        if not skill_md.exists():
            raise ValidationError(f'Missing local skill file: {skill_md}')

        skill_data = load_json(skills_file)
        supporting = skill_data.get('supporting_skills', [])
        if len(supporting) < 2:
            raise ValidationError(f'Agent {agent} must have at least 2 supporting skills.')


def validate_stages(flow: dict) -> None:
    agents = set(flow.get('agents', []))
    stages = flow.get('stages', [])
    stage_ids = {stage['id'] for stage in stages}

    if len(stage_ids) != len(stages):
        raise ValidationError('Stage IDs must be unique.')

    used_agents = set()

    for stage in stages:
        deps = stage.get('depends_on', [])
        for dep in deps:
            if dep not in stage_ids:
                raise ValidationError(f'Stage {stage["id"]} has unknown dependency: {dep}')

        if stage.get('parallel'):
            tracks = stage.get('tracks', [])
            if not tracks:
                raise ValidationError(f'Parallel stage {stage["id"]} must define tracks.')
            for track in tracks:
                owner = track.get('owner')
                if owner not in agents:
                    raise ValidationError(f'Track owner {owner} is not in agent list.')
                used_agents.add(owner)
        else:
            owner = stage.get('owner')
            if owner not in agents:
                raise ValidationError(f'Stage owner {owner} is not in agent list.')
            used_agents.add(owner)

    missing = agents - used_agents
    if missing:
        raise ValidationError(f'Agents not used in any stage: {sorted(missing)}')


def validate_workflow() -> None:
    flow = load_json(ROOT / 'workflow' / 'main-flow.json')
    validation_flow = load_json(ROOT / 'workflow' / 'validation-flow.json')
    validate_agents(flow)
    validate_stages(flow)
    validate_validation_policy(validation_flow)


def validate_validation_policy(validation_flow: dict) -> None:
    checks = {check.get('id'): check for check in validation_flow.get('checks', [])}
    screenshot_check = checks.get('screenshot-validation')
    if not screenshot_check or not screenshot_check.get('required'):
        raise ValidationError('screenshot-validation check must exist and be required.')

    policy = validation_flow.get('acceptance_policy', {})
    review = policy.get('screenshot_review', {})
    if not review.get('required'):
        raise ValidationError('screenshot_review.required must be true.')

    dims = review.get('dimensions', {})
    integrity = dims.get('ui_integrity', {}).get('min', 0)
    aesthetics = dims.get('ui_aesthetics', {}).get('min', 0)
    ux = dims.get('ux_rationality', {}).get('min', 0)

    if integrity < 9.5:
        raise ValidationError('ui_integrity minimum score must be >= 9.5.')
    if aesthetics < 9.0:
        raise ValidationError('ui_aesthetics minimum score must be >= 9.0.')
    if ux < 9.0:
        raise ValidationError('ux_rationality minimum score must be >= 9.0.')

    evidence = review.get('evidence', {})
    min_screenshots = evidence.get('min_screenshots', 0)
    if min_screenshots < 10:
        raise ValidationError('min_screenshots must be >= 10 for card/chess UI review.')

    required_scenes = evidence.get('required_scenes', [])
    if len(required_scenes) < 10:
        raise ValidationError('required_scenes must contain at least 10 scenarios.')

    required_scene_set = {
        'lobby-home',
        'room-list',
        'table-in-game',
        'hand-or-board-status',
        'settlement-result',
        'reconnect-state',
        'insufficient-balance',
        'network-latency-warning',
        'new-user-onboarding',
        'accessibility-high-contrast',
    }
    missing = required_scene_set - set(required_scenes)
    if missing:
        raise ValidationError(f'Missing required screenshot scenes: {sorted(missing)}')

    rubric = review.get('rubric', {})
    weights = rubric.get('weights', {})
    expected_weight_keys = {'ui_integrity', 'ui_aesthetics', 'ux_rationality'}
    if set(weights.keys()) != expected_weight_keys:
        raise ValidationError('rubric.weights keys must be ui_integrity/ui_aesthetics/ux_rationality.')
    if sum(weights.values()) != 100:
        raise ValidationError('rubric.weights must sum to 100.')


def main() -> int:
    try:
        validate_workflow()
        print('Workflow validation passed.')
        return 0
    except ValidationError as err:
        print(f'Workflow validation failed: {err}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

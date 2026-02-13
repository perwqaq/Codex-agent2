# Codex 多智能体协同工作流（9 Agents）

本仓库基于 `perwqaq/Codex-agent` 的目录理念重建，提供适用于 Codex 的可测试协同工作流。

## Agents

1. commander
2. product-manager
3. ui-ux-designer
4. frontend-engineer
5. backend-engineer
6. game-logic
7. qa-engineer
8. devops-security
9. data-analyst

每个 Agent 都包含：
- `agents/<agent>/role.md`
- `agents/<agent>/skills.json`
- `skills/<agent>/SKILL.md`

## 工作流

- 主流程：`workflow/main-flow.json`
- 验收流程：`workflow/validation-flow.json`
- 全局配置：`config/global.json`
- 技能目录：`config/skill-catalog.json`

## 技能来源策略

- 自建技能（本仓库 `skills/*/SKILL.md`）
- 可选外部来源：
  - https://github.com/openai/skills
  - https://skills.sh/

## npm 一键安装

```powershell
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install
```

默认安装到：
- Windows: `%USERPROFILE%\\.codex\\skills\\codex-agent-workflow`
- macOS/Linux: `~/.codex/skills/codex-agent-workflow`

可本地测试安装器：

```powershell
npm run install:local
```

## 测试与验证

```powershell
python scripts/workflow_validator.py
python -m unittest discover -s tests -p "test_*.py" -v
```

测试通过标准：
- Agent 数量 >= 8（当前为 9）
- 每个 Agent 有本地技能与配套技能清单
- 流程依赖可解析、阶段 owner 合法
- 验收门禁存在并满足最低阈值

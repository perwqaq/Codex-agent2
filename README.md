# 多 IDE 多智能体协同工作流（9 Agents）

本仓库基于 `perwqaq/Codex-agent` 的目录理念重建，提供适用于 `Codex`、`Trae`、`Cursor` 的可测试协同工作流。

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

## 多 IDE 一键安装（npm）

默认安装到 `Codex`：

```powershell
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install
```

指定安装到其他 IDE：

```powershell
# 安装到 Trae
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install --ide trae

# 安装到 Cursor
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install --ide cursor

# 同时安装到 Codex + Trae + Cursor
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install --ide all
```

默认目录：
- Codex: `%USERPROFILE%\\.codex\\skills\\codex-agent-workflow`
- Trae: `%USERPROFILE%\\.trae\\skills\\codex-agent-workflow`
- Cursor: `%USERPROFILE%\\.cursor\\skills\\codex-agent-workflow`

自定义目录：

```powershell
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install --dest "D:\\skills\\codex-agent-workflow"
```

可本地测试安装器：

```powershell
npm run install:local
npm run install:trae
npm run install:cursor
npm run install:all
```

## Trae 使用说明

1. 安装技能包到 Trae：
```powershell
npx -y github:perwqaq/Codex-agent2 codex-agent-workflow-install --ide trae
```
2. 重启 Trae，确保加载新的 skills。
3. 在 Trae 对话中直接使用触发词：
- `开始项目`
- `@commander 开始项目：开发一个棋牌类游戏大厅+对局+结算`
- `@commander 质量验收`

## 多 IDE 触发规则

- `Codex`、`Trae`、`Cursor` 使用同一套触发词。
- 触发顺序一致：`commander` 总控调度，子 Agent 分阶段执行。
- 验收标准一致：`workflow/validation-flow.json` + `validation/scoring-criteria.md`。

## 如何触发工作流

### 1) 触发总流程（推荐）

```text
开始项目
```

或

```text
@commander 开始项目：开发一个棋牌类游戏大厅+对局+结算
```

### 2) 按角色单独触发

- Commander：`开始项目`、`质量验收`、`检查交付`
- Product Manager：`写PRD`、`分析需求`、`产品规划`
- UI/UX Designer：`设计界面`、`出设计规范`、`做UI`
- Frontend Engineer：`写前端`、`React组件`、`WebSocket`
- Backend Engineer：`写后端`、`API开发`、`数据库设计`
- Game Logic：`写游戏逻辑`、`游戏规则`、`房间管理`
- QA Engineer：`写测试`、`测试用例`、`性能测试`
- DevOps/Security：`CI/CD`、`部署`、`安全审计`

### 3) 触发验收

```text
@commander 质量验收
```

验收依据：
- `workflow/validation-flow.json`
- `validation/scoring-criteria.md`

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
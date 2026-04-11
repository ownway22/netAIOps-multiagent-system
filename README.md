# {{PROJECT_NAME}}

> 此專案由 [repository-template](https://github.com/ownway22/repository-template) 初始化。

## 專案簡介

<!-- 在此描述你的專案目標與用途 -->

## 快速開始

```bash
# 1. Clone 此 repo（如果還沒有的話）
git clone https://github.com/ownway22/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}

# 2. 安裝依賴
# TODO: 根據你的技術棧填寫

# 3. 啟動開發環境
# TODO: 根據你的技術棧填寫
```

## Coding Agent 設定

本專案已預設以下 coding agent 的設定檔：

| Agent          | 設定位置                          | 說明                         |
| -------------- | --------------------------------- | ---------------------------- |
| GitHub Copilot | `.github/copilot-instructions.md` | 全域行為指引                 |
| GitHub Copilot | `.github/instructions/`           | 條件式指令（依檔案類型套用） |
| GitHub Copilot | `.github/prompts/`                | 自訂 Prompt 檔案             |
| GitHub Copilot | `.github/agents/`                 | 自訂 Agent 模式              |
| GitHub Copilot | `.github/skills/`                 | 自訂 Skills                  |
| Claude Code    | `CLAUDE.md`                       | Claude Code 專案指引         |
| Claude Code    | `CLAUDE.local.md`                 | 個人本地備註（不提交）       |
| Claude Code    | `.claude/settings.json`           | Claude 專案設定              |
| Claude Code    | `.claude/settings.local.json`     | 個人本地設定（不提交）       |
| Claude Code    | `.claude/commands/`               | 自訂 Slash Commands          |
| Claude Code    | `.claude/rules/`                  | 自訂規則檔案                 |
| Claude Code    | `.claude/skills/`                 | 自訂 Skills                  |
| Claude Code    | `.claude/agents/`                 | 自訂 Agents                  |
| Claude Code    | `AGENTS.md`                       | Agent 行為說明               |
| SpecKit        | `.specify/`                       | SpecKit 規格工作流程設定     |

## 專案結構

```
.
├── .github/
│   ├── copilot-instructions.md       # Copilot 全域指引
│   ├── instructions/                 # 條件式指令（依檔案類型套用）
│   ├── prompts/                      # 自訂 prompt 檔案
│   ├── agents/                       # 自訂 agent 模式
│   └── skills/                       # 自訂 skills
├── .claude/
│   ├── settings.json                 # Claude Code 專案設定
│   ├── settings.local.json           # 個人本地設定（不提交）
│   ├── commands/                     # Claude slash commands
│   ├── rules/                        # Claude 規則檔案
│   ├── skills/                       # Claude skills
│   └── agents/                       # Claude agents
├── .specify/                         # SpecKit 規格工作流程
│   ├── memory/
│   │   └── constitution.md           # 專案憲章與記憶
│   ├── scripts/                      # 自動化腳本
│   └── templates/                    # 範本檔案
├── .vscode/
│   ├── extensions.json               # 推薦擴充套件
│   ├── mcp.json                      # MCP 伺服器設定
│   └── settings.json                 # VS Code 推薦設定
├── AGENTS.md                         # Agent 行為文件
├── CLAUDE.md                         # Claude Code 專案指引
├── CLAUDE.local.md                   # 個人本地備註（不提交）
├── .gitignore
└── README.md
```

## 授權

<!-- 在此填寫授權方式 -->

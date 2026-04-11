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

| Agent | 設定位置 | 說明 |
|-------|----------|------|
| GitHub Copilot | `.github/copilot-instructions.md` | 全域行為指引 |
| GitHub Copilot | `.github/prompts/` | 自訂 Prompt 檔案 |
| GitHub Copilot | `.github/agents/` | 自訂 Agent 模式 |
| GitHub Copilot | `.github/skills/` | 自訂 Skills |
| Claude Code | `.claude/settings.json` | Claude 專案設定 |
| Claude Code | `.claude/commands/` | 自訂 Slash Commands |
| Claude Code | `AGENTS.md` | Agent 行為說明 |

## 專案結構

```
.
├── .github/
│   ├── copilot-instructions.md   # Copilot 全域指引
│   ├── prompts/                  # 自訂 prompt 檔案
│   ├── agents/                   # 自訂 agent 模式
│   └── skills/                   # 自訂 skills
├── .claude/
│   ├── settings.json             # Claude Code 設定
│   └── commands/                 # Claude slash commands
├── .vscode/
│   └── settings.json             # VS Code 推薦設定
├── AGENTS.md                     # Agent 行為文件
└── README.md
```

## 授權

<!-- 在此填寫授權方式 -->

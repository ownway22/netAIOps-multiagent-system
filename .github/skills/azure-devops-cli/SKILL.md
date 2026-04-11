````skill
---
name: azure-devops-cli
description: 透過 CLI 管理 Azure DevOps 資源，包括專案、存放庫、管線、建置、提取要求、工作項目、成品及服務端點。適用於使用 Azure DevOps、az 指令、DevOps 自動化、CI/CD，或使用者提及 Azure DevOps CLI 時。
---

# Azure DevOps CLI

此技能可協助使用 Azure CLI 搭配 Azure DevOps 擴充功能來管理 Azure DevOps 資源。

**CLI 版本：** 2.81.0（截至 2025 年為最新版）

## 先決條件

安裝 Azure CLI 和 Azure DevOps 擴充功能：

```bash
# 安裝 Azure CLI
brew install azure-cli  # macOS
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux
pip install azure-cli  # 透過 pip

# 驗證安裝
az --version

# 安裝 Azure DevOps 擴充功能
az extension add --name azure-devops
az extension show --name azure-devops
```

## CLI 結構

```
az devops          # 主要 DevOps 指令
├── admin          # 管理（橫幅）
├── extension      # 擴充功能管理
├── project        # 小組專案
├── security       # 安全性操作
│   ├── group      # 安全性群組
│   └── permission # 安全性權限
├── service-endpoint # 服務連線
├── team           # 小組
├── user           # 使用者
├── wiki           # Wiki
├── configure      # 設定預設值
├── invoke         # 呼叫 REST API
├── login          # 驗證
└── logout         # 清除認證

az pipelines       # Azure Pipelines
├── agent          # 代理程式
├── build          # 建置
├── folder         # 管線資料夾
├── pool           # 代理程式集區
├── queue          # 代理程式佇列
├── release        # 發行
├── runs           # 管線執行
├── variable       # 管線變數
└── variable-group # 變數群組

az boards          # Azure Boards
├── area           # 區域路徑
├── iteration      # 反覆運算
└── work-item      # 工作項目

az repos           # Azure Repos
├── import         # Git 匯入
├── policy         # 分支原則
├── pr             # 提取要求
└── ref            # Git 參考

az artifacts       # Azure Artifacts
└── universal      # 通用套件
    ├── download   # 下載套件
    └── publish    # 發佈套件
```

## 驗證

### 登入 Azure DevOps

```bash
# 互動式登入（提示輸入 PAT）
az devops login --organization https://dev.azure.com/{org}

# 使用 PAT 權杖登入
az devops login --organization https://dev.azure.com/{org} --token YOUR_PAT_TOKEN

# 登出
az devops logout --organization https://dev.azure.com/{org}
```

### 設定預設值

```bash
# 設定預設組織和專案
az devops configure --defaults organization=https://dev.azure.com/{org} project={project}

# 列出目前組態
az devops configure --list

# 啟用 Git 別名
az devops configure --use-git-aliases true
```

## 擴充功能管理

### 列出擴充功能

```bash
# 列出可用的擴充功能
az extension list-available --output table

# 列出已安裝的擴充功能
az extension list --output table
```

### 管理 Azure DevOps 擴充功能

```bash
# 安裝 Azure DevOps 擴充功能
az extension add --name azure-devops

# 更新 Azure DevOps 擴充功能
az extension update --name azure-devops

# 移除擴充功能
az extension remove --name azure-devops

# 從本機路徑安裝
az extension add --source ~/extensions/azure-devops.whl
```

## 專案

### 列出專案

```bash
az devops project list --organization https://dev.azure.com/{org}
az devops project list --top 10 --output table
```

### 建立專案

```bash
az devops project create \
  --name myNewProject \
  --organization https://dev.azure.com/{org} \
  --description "My new DevOps project" \
  --source-control git \
  --visibility private
```

### 顯示專案詳細資料

```bash
az devops project show --project {project-name} --org https://dev.azure.com/{org}
```

### 刪除專案

```bash
az devops project delete --id {project-id} --org https://dev.azure.com/{org} --yes
```

## 存放庫

### 列出存放庫

```bash
az repos list --org https://dev.azure.com/{org} --project {project}
az repos list --output table
```

### 顯示存放庫詳細資料

```bash
az repos show --repository {repo-name} --project {project}
```

### 建立存放庫

```bash
az repos create --name {repo-name} --project {project}
```

### 刪除存放庫

```bash
az repos delete --id {repo-id} --project {project} --yes
```

### 更新存放庫

```bash
az repos update --id {repo-id} --name {new-name} --project {project}
```

## 存放庫匯入

### 匯入 Git 存放庫

```bash
# 從公開 Git 存放庫匯入
az repos import create \
  --git-source-url https://github.com/user/repo \
  --repository {repo-name}

# 搭配驗證匯入
az repos import create \
  --git-source-url https://github.com/user/private-repo \
  --repository {repo-name} \
  --user {username} \
  --password {password-or-pat}
```

## 提取要求

### 建立提取要求

```bash
# 基本 PR 建立
az repos pr create \
  --repository {repo} \
  --source-branch {source-branch} \
  --target-branch {target-branch} \
  --title "PR Title" \
  --description "PR description" \
  --open

# 搭配工作項目的 PR
az repos pr create \
  --repository {repo} \
  --source-branch {source-branch} \
  --work-items 63 64

# 草稿 PR 搭配審閱者
az repos pr create \
  --repository {repo} \
  --source-branch feature/new-feature \
  --target-branch main \
  --title "Feature: New functionality" \
  --draft true \
  --reviewers user1@example.com user2@example.com \
  --required-reviewers lead@example.com \
  --labels "enhancement" "backlog"
```

### 列出提取要求

```bash
# 所有 PR
az repos pr list --repository {repo}

# 依狀態篩選
az repos pr list --repository {repo} --status active

# 依建立者篩選
az repos pr list --repository {repo} --creator {email}

# 以表格輸出
az repos pr list --repository {repo} --output table
```

### 顯示 PR 詳細資料

```bash
az repos pr show --id {pr-id}
az repos pr show --id {pr-id} --open  # 在瀏覽器中開啟
```

### 更新 PR（完成/放棄/草稿）

```bash
# 完成 PR
az repos pr update --id {pr-id} --status completed

# 放棄 PR
az repos pr update --id {pr-id} --status abandoned

# 設為草稿
az repos pr update --id {pr-id} --draft true

# 發佈草稿 PR
az repos pr update --id {pr-id} --draft false

# 原則通過時自動完成
az repos pr update --id {pr-id} --auto-complete true

# 設定標題和描述
az repos pr update --id {pr-id} --title "New title" --description "New description"
```

### 在本機簽出 PR

```bash
# 簽出 PR 分支
az repos pr checkout --id {pr-id}

# 使用特定遠端簽出
az repos pr checkout --id {pr-id} --remote-name upstream
```

### 對 PR 投票

```bash
az repos pr set-vote --id {pr-id} --vote approve
az repos pr set-vote --id {pr-id} --vote approve-with-suggestions
az repos pr set-vote --id {pr-id} --vote reject
az repos pr set-vote --id {pr-id} --vote wait-for-author
az repos pr set-vote --id {pr-id} --vote reset
```

### PR 審閱者

```bash
# 新增審閱者
az repos pr reviewer add --id {pr-id} --reviewers user1@example.com user2@example.com

# 列出審閱者
az repos pr reviewer list --id {pr-id}

# 移除審閱者
az repos pr reviewer remove --id {pr-id} --reviewers user1@example.com
```

### PR 工作項目

```bash
# 將工作項目新增至 PR
az repos pr work-item add --id {pr-id} --work-items {id1} {id2}

# 列出 PR 工作項目
az repos pr work-item list --id {pr-id}

# 從 PR 移除工作項目
az repos pr work-item remove --id {pr-id} --work-items {id1}
```

### PR 原則

```bash
# 列出 PR 的原則
az repos pr policy list --id {pr-id}

# 將 PR 的原則排入評估佇列
az repos pr policy queue --id {pr-id} --evaluation-id {evaluation-id}
```

## 管線

### 列出管線

```bash
az pipelines list --output table
az pipelines list --query "[?name=='myPipeline']"
az pipelines list --folder-path 'folder/subfolder'
```

### 建立管線

```bash
# 從本機存放庫上下文（自動偵測設定）
az pipelines create --name 'ContosoBuild' --description 'Pipeline for contoso project'

# 指定分支和 YAML 路徑
az pipelines create \
  --name {pipeline-name} \
  --repository {repo} \
  --branch main \
  --yaml-path azure-pipelines.yml \
  --description "My CI/CD pipeline"

# 用於 GitHub 存放庫
az pipelines create \
  --name 'GitHubPipeline' \
  --repository https://github.com/Org/Repo \
  --branch main \
  --repository-type github

# 跳過首次執行
az pipelines create --name 'MyPipeline' --skip-run true
```

### 顯示管線

```bash
az pipelines show --id {pipeline-id}
az pipelines show --name {pipeline-name}
```

### 更新管線

```bash
az pipelines update --id {pipeline-id} --name "New name" --description "Updated description"
```

### 刪除管線

```bash
az pipelines delete --id {pipeline-id} --yes
```

### 執行管線

```bash
# 依名稱執行
az pipelines run --name {pipeline-name} --branch main

# 依 ID 執行
az pipelines run --id {pipeline-id} --branch refs/heads/main

# 搭配參數
az pipelines run --name {pipeline-name} --parameters version=1.0.0 environment=prod

# 搭配變數
az pipelines run --name {pipeline-name} --variables buildId=123 configuration=release

# 在瀏覽器中開啟結果
az pipelines run --name {pipeline-name} --open
```

## 管線執行

### 列出執行

```bash
az pipelines runs list --pipeline {pipeline-id}
az pipelines runs list --name {pipeline-name} --top 10
az pipelines runs list --branch main --status completed
```

### 顯示執行詳細資料

```bash
az pipelines runs show --run-id {run-id}
az pipelines runs show --run-id {run-id} --open
```

### 管線成品

```bash
# 列出某次執行的成品
az pipelines runs artifact list --run-id {run-id}

# 下載成品
az pipelines runs artifact download \
  --artifact-name '{artifact-name}' \
  --path {local-path} \
  --run-id {run-id}

# 上傳成品
az pipelines runs artifact upload \
  --artifact-name '{artifact-name}' \
  --path {local-path} \
  --run-id {run-id}
```

### 管線執行標籤

```bash
# 為執行新增標籤
az pipelines runs tag add --run-id {run-id} --tags production v1.0

# 列出執行標籤
az pipelines runs tag list --run-id {run-id} --output table
```

## 建置

### 列出建置

```bash
az pipelines build list
az pipelines build list --definition {build-definition-id}
az pipelines build list --status completed --result succeeded
```

### 將建置排入佇列

```bash
az pipelines build queue --definition {build-definition-id} --branch main
az pipelines build queue --definition {build-definition-id} --parameters version=1.0.0
```

### 顯示建置詳細資料

```bash
az pipelines build show --id {build-id}
```

### 取消建置

```bash
az pipelines build cancel --id {build-id}
```

### 建置標籤

```bash
# 為建置新增標籤
az pipelines build tag add --build-id {build-id} --tags prod release

# 從建置刪除標籤
az pipelines build tag delete --build-id {build-id} --tag prod
```

## 建置定義

### 列出建置定義

```bash
az pipelines build definition list
az pipelines build definition list --name {definition-name}
```

### 顯示建置定義

```bash
az pipelines build definition show --id {definition-id}
```

## 發行

### 列出發行

```bash
az pipelines release list
az pipelines release list --definition {release-definition-id}
```

### 建立發行

```bash
az pipelines release create --definition {release-definition-id}
az pipelines release create --definition {release-definition-id} --description "Release v1.0"
```

### 顯示發行

```bash
az pipelines release show --id {release-id}
```

## 發行定義

### 列出發行定義

```bash
az pipelines release definition list
```

### 顯示發行定義

```bash
az pipelines release definition show --id {definition-id}
```

## 管線變數

### 列出變數

```bash
az pipelines variable list --pipeline-id {pipeline-id}
```

### 建立變數

```bash
# 非機密變數
az pipelines variable create \
  --name {var-name} \
  --value {var-value} \
  --pipeline-id {pipeline-id}

# 機密變數
az pipelines variable create \
  --name {var-name} \
  --secret true \
  --pipeline-id {pipeline-id}

# 搭配提示的機密變數
az pipelines variable create \
  --name {var-name} \
  --secret true \
  --prompt true \
  --pipeline-id {pipeline-id}
```

### 更新變數

```bash
az pipelines variable update \
  --name {var-name} \
  --value {new-value} \
  --pipeline-id {pipeline-id}

# 更新機密變數
az pipelines variable update \
  --name {var-name} \
  --secret true \
  --value "{new-secret-value}" \
  --pipeline-id {pipeline-id}
```

### 刪除變數

```bash
az pipelines variable delete --name {var-name} --pipeline-id {pipeline-id} --yes
```

## 變數群組

### 列出變數群組

```bash
az pipelines variable-group list
az pipelines variable-group list --output table
```

### 顯示變數群組

```bash
az pipelines variable-group show --id {group-id}
```

### 建立變數群組

```bash
az pipelines variable-group create \
  --name {group-name} \
  --variables key1=value1 key2=value2 \
  --authorize true
```

### 更新變數群組

```bash
az pipelines variable-group update \
  --id {group-id} \
  --name {new-name} \
  --description "Updated description"
```

### 刪除變數群組

```bash
az pipelines variable-group delete --id {group-id} --yes
```

### 變數群組變數

#### 列出變數

```bash
az pipelines variable-group variable list --group-id {group-id}
```

#### 建立變數

```bash
# 非機密變數
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name {var-name} \
  --value {var-value}

# 機密變數（如未提供值則會提示輸入）
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name {var-name} \
  --secret true

# 搭配環境變數的機密
export AZURE_DEVOPS_EXT_PIPELINE_VAR_MySecret=secretvalue
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name MySecret \
  --secret true
```

#### 更新變數

```bash
az pipelines variable-group variable update \
  --group-id {group-id} \
  --name {var-name} \
  --value {new-value} \
  --secret false
```

#### 刪除變數

```bash
az pipelines variable-group variable delete \
  --group-id {group-id} \
  --name {var-name}
```

## 管線資料夾

### 列出資料夾

```bash
az pipelines folder list
```

### 建立資料夾

```bash
az pipelines folder create --path 'folder/subfolder' --description "My folder"
```

### 刪除資料夾

```bash
az pipelines folder delete --path 'folder/subfolder'
```

### 更新資料夾

```bash
az pipelines folder update --path 'old-folder' --new-path 'new-folder'
```

## 代理程式集區

### 列出代理程式集區

```bash
az pipelines pool list
az pipelines pool list --pool-type automation
az pipelines pool list --pool-type deployment
```

### 顯示代理程式集區

```bash
az pipelines pool show --pool-id {pool-id}
```

## 代理程式佇列

### 列出代理程式佇列

```bash
az pipelines queue list
az pipelines queue list --pool-name {pool-name}
```

### 顯示代理程式佇列

```bash
az pipelines queue show --id {queue-id}
```

## 工作項目（Boards）

### 查詢工作項目

```bash
# WIQL 查詢
az boards query \
  --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] = 'Active'"

# 搭配輸出格式的查詢
az boards query --wiql "SELECT * FROM WorkItems" --output table
```

### 顯示工作項目

```bash
az boards work-item show --id {work-item-id}
az boards work-item show --id {work-item-id} --open
```

### 建立工作項目

```bash
# 基本工作項目
az boards work-item create \
  --title "Fix login bug" \
  --type Bug \
  --assigned-to user@example.com \
  --description "Users cannot login with SSO"

# 搭配區域和反覆運算
az boards work-item create \
  --title "New feature" \
  --type "User Story" \
  --area "Project\\Area1" \
  --iteration "Project\\Sprint 1"

# 搭配自訂欄位
az boards work-item create \
  --title "Task" \
  --type Task \
  --fields "Priority=1" "Severity=2"

# 搭配討論留言
az boards work-item create \
  --title "Issue" \
  --type Bug \
  --discussion "Initial investigation completed"

# 建立後在瀏覽器中開啟
az boards work-item create --title "Bug" --type Bug --open
```

### 更新工作項目

```bash
# 更新狀態、標題和指派對象
az boards work-item update \
  --id {work-item-id} \
  --state "Active" \
  --title "Updated title" \
  --assigned-to user@example.com

# 移動到不同區域
az boards work-item update \
  --id {work-item-id} \
  --area "{ProjectName}\\{Team}\\{Area}"

# 變更反覆運算
az boards work-item update \
  --id {work-item-id} \
  --iteration "{ProjectName}\\Sprint 5"

# 新增留言/討論
az boards work-item update \
  --id {work-item-id} \
  --discussion "Work in progress"

# 使用自訂欄位更新
az boards work-item update \
  --id {work-item-id} \
  --fields "Priority=1" "StoryPoints=5"
```

### 刪除工作項目

```bash
# 軟刪除（可還原）
az boards work-item delete --id {work-item-id} --yes

# 永久刪除
az boards work-item delete --id {work-item-id} --destroy --yes
```

### 工作項目關聯

```bash
# 列出關聯
az boards work-item relation list --id {work-item-id}

# 列出支援的關聯類型
az boards work-item relation list-type

# 新增關聯
az boards work-item relation add --id {work-item-id} --relation-type parent --target-id {parent-id}

# 移除關聯
az boards work-item relation remove --id {work-item-id} --relation-id {relation-id}
```

## 區域路徑

### 列出專案的區域

```bash
az boards area project list --project {project}
az boards area project show --path "Project\\Area1" --project {project}
```

### 建立區域

```bash
az boards area project create --path "Project\\NewArea" --project {project}
```

### 更新區域

```bash
az boards area project update \
  --path "Project\\OldArea" \
  --new-path "Project\\UpdatedArea" \
  --project {project}
```

### 刪除區域

```bash
az boards area project delete --path "Project\\AreaToDelete" --project {project} --yes
```

### 區域小組管理

```bash
# 列出小組的區域
az boards area team list --team {team-name} --project {project}

# 將區域新增至小組
az boards area team add \
  --team {team-name} \
  --path "Project\\NewArea" \
  --project {project}

# 從小組移除區域
az boards area team remove \
  --team {team-name} \
  --path "Project\\AreaToRemove" \
  --project {project}

# 更新小組區域
az boards area team update \
  --team {team-name} \
  --path "Project\\Area" \
  --project {project} \
  --include-sub-areas true
```

## 反覆運算

### 列出專案的反覆運算

```bash
az boards iteration project list --project {project}
az boards iteration project show --path "Project\\Sprint 1" --project {project}
```

### 建立反覆運算

```bash
az boards iteration project create --path "Project\\Sprint 1" --project {project}
```

### 更新反覆運算

```bash
az boards iteration project update \
  --path "Project\\OldSprint" \
  --new-path "Project\\NewSprint" \
  --project {project}
```

### 刪除反覆運算

```bash
az boards iteration project delete --path "Project\\OldSprint" --project {project} --yes
```

### 列出小組的反覆運算

```bash
az boards iteration team list --team {team-name} --project {project}
```

### 將反覆運算新增至小組

```bash
az boards iteration team add \
  --team {team-name} \
  --path "Project\\Sprint 1" \
  --project {project}
```

### 從小組移除反覆運算

```bash
az boards iteration team remove \
  --team {team-name} \
  --path "Project\\Sprint 1" \
  --project {project}
```

### 列出反覆運算中的工作項目

```bash
az boards iteration team list-work-items \
  --team {team-name} \
  --path "Project\\Sprint 1" \
  --project {project}
```

### 設定小組的預設反覆運算

```bash
az boards iteration team set-default-iteration \
  --team {team-name} \
  --path "Project\\Sprint 1" \
  --project {project}
```

### 顯示預設反覆運算

```bash
az boards iteration team show-default-iteration \
  --team {team-name} \
  --project {project}
```

### 設定小組的待辦項目反覆運算

```bash
az boards iteration team set-backlog-iteration \
  --team {team-name} \
  --path "Project\\Sprint 1" \
  --project {project}
```

### 顯示待辦項目反覆運算

```bash
az boards iteration team show-backlog-iteration \
  --team {team-name} \
  --project {project}
```

### 顯示目前反覆運算

```bash
az boards iteration team show --team {team-name} --project {project} --timeframe current
```

## Git 參考

### 列出參考（分支）

```bash
az repos ref list --repository {repo}
az repos ref list --repository {repo} --query "[?name=='refs/heads/main']"
```

### 建立參考（分支）

```bash
az repos ref create --name refs/heads/new-branch --object-type commit --object {commit-sha}
```

### 刪除參考（分支）

```bash
az repos ref delete --name refs/heads/old-branch --repository {repo} --project {project}
```

### 鎖定分支

```bash
az repos ref lock --name refs/heads/main --repository {repo} --project {project}
```

### 解除鎖定分支

```bash
az repos ref unlock --name refs/heads/main --repository {repo} --project {project}
```

## 存放庫原則

### 列出所有原則

```bash
az repos policy list --repository {repo-id} --branch main
```

### 使用組態檔建立原則

```bash
az repos policy create --config policy.json
```

### 更新/刪除原則

```bash
# 更新
az repos policy update --id {policy-id} --config updated-policy.json

# 刪除
az repos policy delete --id {policy-id} --yes
```

### 原則類型

#### 核准者數量原則

```bash
az repos policy approver-count create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id} \
  --minimum-approver-count 2 \
  --creator-vote-counts true
```

#### 建置原則

```bash
az repos policy build create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id} \
  --build-definition-id {definition-id} \
  --queue-on-source-update-only true \
  --valid-duration 720
```

#### 工作項目連結原則

```bash
az repos policy work-item-linking create \
  --blocking true \
  --branch main \
  --enabled true \
  --repository-id {repo-id}
```

#### 必要審閱者原則

```bash
az repos policy required-reviewer create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id} \
  --required-reviewers user@example.com
```

#### 合併策略原則

```bash
az repos policy merge-strategy create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id} \
  --allow-squash true \
  --allow-rebase true \
  --allow-no-fast-forward true
```

#### 大小寫強制原則

```bash
az repos policy case-enforcement create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id}
```

#### 必要留言原則

```bash
az repos policy comment-required create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id}
```

#### 檔案大小原則

```bash
az repos policy file-size create \
  --blocking true \
  --enabled true \
  --branch main \
  --repository-id {repo-id} \
  --maximum-file-size 10485760  # 10MB（位元組）
```

## 服務端點

### 列出服務端點

```bash
az devops service-endpoint list --project {project}
az devops service-endpoint list --project {project} --output table
```

### 顯示服務端點

```bash
az devops service-endpoint show --id {endpoint-id} --project {project}
```

### 建立服務端點

```bash
# 使用組態檔
az devops service-endpoint create --service-endpoint-configuration endpoint.json --project {project}
```

### 刪除服務端點

```bash
az devops service-endpoint delete --id {endpoint-id} --project {project} --yes
```

## 小組

### 列出小組

```bash
az devops team list --project {project}
```

### 顯示小組

```bash
az devops team show --team {team-name} --project {project}
```

### 建立小組

```bash
az devops team create \
  --name {team-name} \
  --description "Team description" \
  --project {project}
```

### 更新小組

```bash
az devops team update \
  --team {team-name} \
  --project {project} \
  --name "{new-team-name}" \
  --description "Updated description"
```

### 刪除小組

```bash
az devops team delete --team {team-name} --project {project} --yes
```

### 顯示小組成員

```bash
az devops team list-member --team {team-name} --project {project}
```

## 使用者

### 列出使用者

```bash
az devops user list --org https://dev.azure.com/{org}
az devops user list --top 10 --output table
```

### 顯示使用者

```bash
az devops user show --user {user-id-or-email} --org https://dev.azure.com/{org}
```

### 新增使用者

```bash
az devops user add \
  --email user@example.com \
  --license-type express \
  --org https://dev.azure.com/{org}
```

### 更新使用者

```bash
az devops user update \
  --user {user-id-or-email} \
  --license-type advanced \
  --org https://dev.azure.com/{org}
```

### 移除使用者

```bash
az devops user remove --user {user-id-or-email} --org https://dev.azure.com/{org} --yes
```

## 安全性群組

### 列出群組

```bash
# 列出專案中的所有群組
az devops security group list --project {project}

# 列出組織中的所有群組
az devops security group list --scope organization

# 搭配篩選列出
az devops security group list --project {project} --subject-types vstsgroup
```

### 顯示群組詳細資料

```bash
az devops security group show --group-id {group-id}
```

### 建立群組

```bash
az devops security group create \
  --name {group-name} \
  --description "Group description" \
  --project {project}
```

### 更新群組

```bash
az devops security group update \
  --group-id {group-id} \
  --name "{new-group-name}" \
  --description "Updated description"
```

### 刪除群組

```bash
az devops security group delete --group-id {group-id} --yes
```

### 群組成員管理

```bash
# 列出成員
az devops security group membership list --id {group-id}

# 新增成員
az devops security group membership add \
  --group-id {group-id} \
  --member-id {member-id}

# 移除成員
az devops security group membership remove \
  --group-id {group-id} \
  --member-id {member-id} --yes
```

## 安全性權限

### 列出命名空間

```bash
az devops security permission namespace list
```

### 顯示命名空間詳細資料

```bash
# 顯示命名空間中可用的權限
az devops security permission namespace show --namespace "GitRepositories"
```

### 列出權限

```bash
# 列出使用者/群組和命名空間的權限
az devops security permission list \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project}

# 列出特定權杖（存放庫）的權限
az devops security permission list \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}"
```

### 顯示權限

```bash
az devops security permission show \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}"
```

### 更新權限

```bash
# 授予權限
az devops security permission update \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" \
  --permission-mask "Pull,Contribute"

# 拒絕權限
az devops security permission update \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" \
  --permission-mask 0
```

### 重設權限

```bash
# 重設特定權限位元
az devops security permission reset \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" \
  --permission-mask "Pull,Contribute"

# 重設所有權限
az devops security permission reset-all \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" --yes
```

## Wiki

### 列出 Wiki

```bash
# 列出專案中的所有 Wiki
az devops wiki list --project {project}

# 列出組織中的所有 Wiki
az devops wiki list
```

### 顯示 Wiki

```bash
az devops wiki show --wiki {wiki-name} --project {project}
az devops wiki show --wiki {wiki-name} --project {project} --open
```

### 建立 Wiki

```bash
# 建立專案 Wiki
az devops wiki create \
  --name {wiki-name} \
  --project {project} \
  --type projectWiki

# 從存放庫建立程式碼 Wiki
az devops wiki create \
  --name {wiki-name} \
  --project {project} \
  --type codeWiki \
  --repository {repo-name} \
  --mapped-path /wiki
```

### 刪除 Wiki

```bash
az devops wiki delete --wiki {wiki-id} --project {project} --yes
```

### Wiki 頁面

```bash
# 列出頁面
az devops wiki page list --wiki {wiki-name} --project {project}

# 顯示頁面
az devops wiki page show \
  --wiki {wiki-name} \
  --path "/page-name" \
  --project {project}

# 建立頁面
az devops wiki page create \
  --wiki {wiki-name} \
  --path "/new-page" \
  --content "# New Page\n\nPage content here..." \
  --project {project}

# 更新頁面
az devops wiki page update \
  --wiki {wiki-name} \
  --path "/existing-page" \
  --content "# Updated Page\n\nNew content..." \
  --project {project}

# 刪除頁面
az devops wiki page delete \
  --wiki {wiki-name} \
  --path "/old-page" \
  --project {project} --yes
```

## 管理

### 橫幅管理

```bash
# 列出橫幅
az devops admin banner list

# 顯示橫幅詳細資料
az devops admin banner show --id {banner-id}

# 新增橫幅
az devops admin banner add \
  --message "System maintenance scheduled" \
  --level info  # info、warning、error

# 更新橫幅
az devops admin banner update \
  --id {banner-id} \
  --message "Updated message" \
  --level warning \
  --expiration-date "2025-12-31T23:59:59Z"

# 移除橫幅
az devops admin banner remove --id {banner-id}
```

## DevOps 擴充功能

管理安裝在 Azure DevOps 組織中的擴充功能（與 CLI 擴充功能不同）。

```bash
# 列出已安裝的擴充功能
az devops extension list --org https://dev.azure.com/{org}

# 搜尋市集擴充功能
az devops extension search --search-query "docker"

# 顯示擴充功能詳細資料
az devops extension show --ext-id {extension-id} --org https://dev.azure.com/{org}

# 安裝擴充功能
az devops extension install \
  --ext-id {extension-id} \
  --org https://dev.azure.com/{org} \
  --publisher {publisher-id}

# 啟用擴充功能
az devops extension enable \
  --ext-id {extension-id} \
  --org https://dev.azure.com/{org}

# 停用擴充功能
az devops extension disable \
  --ext-id {extension-id} \
  --org https://dev.azure.com/{org}

# 解除安裝擴充功能
az devops extension uninstall \
  --ext-id {extension-id} \
  --org https://dev.azure.com/{org} --yes
```

## 通用套件

### 發佈套件

```bash
az artifacts universal publish \
  --feed {feed-name} \
  --name {package-name} \
  --version {version} \
  --path {package-path} \
  --project {project}
```

### 下載套件

```bash
az artifacts universal download \
  --feed {feed-name} \
  --name {package-name} \
  --version {version} \
  --path {download-path} \
  --project {project}
```

## 代理程式

### 列出集區中的代理程式

```bash
az pipelines agent list --pool-id {pool-id}
```

### 顯示代理程式詳細資料

```bash
az pipelines agent show --agent-id {agent-id} --pool-id {pool-id}
```

## Git 別名

啟用 Git 別名後：

```bash
# 啟用 Git 別名
az devops configure --use-git-aliases true

# 使用 Git 指令進行 DevOps 操作
git pr create --target-branch main
git pr list
git pr checkout 123
```

## 輸出格式

所有指令皆支援多種輸出格式：

```bash
# 表格格式（方便人類閱讀）
az pipelines list --output table

# JSON 格式（預設，適合機器處理）
az pipelines list --output json

# JSONC（有色彩的 JSON）
az pipelines list --output jsonc

# YAML 格式
az pipelines list --output yaml

# YAMLC（有色彩的 YAML）
az pipelines list --output yamlc

# TSV 格式（定位字元分隔值）
az pipelines list --output tsv

# 無輸出
az pipelines list --output none
```

## JMESPath 查詢

篩選和轉換輸出：

```bash
# 依名稱篩選
az pipelines list --query "[?name=='myPipeline']"

# 取得特定欄位
az pipelines list --query "[].{Name:name, ID:id}"

# 鏈結查詢
az pipelines list --query "[?name.contains('CI')].{Name:name, ID:id}" --output table

# 取得第一筆結果
az pipelines list --query "[0]"

# 取得前 N 筆
az pipelines list --query "[0:5]"
```

## 全域引數

適用於所有指令：

- `--help` / `-h`：顯示說明
- `--output` / `-o`：輸出格式（json、jsonc、none、table、tsv、yaml、yamlc）
- `--query`：JMESPath 查詢字串
- `--verbose`：增加日誌詳細程度
- `--debug`：顯示所有偵錯日誌
- `--only-show-errors`：僅顯示錯誤，隱藏警告
- `--subscription`：訂用帳戶名稱或 ID

## 常用參數

| 參數                       | 說明                                                         |
| -------------------------- | ------------------------------------------------------------ |
| `--org` / `--organization` | Azure DevOps 組織 URL（例如 `https://dev.azure.com/{org}`）  |
| `--project` / `-p`         | 專案名稱或 ID                                                |
| `--detect`                 | 從 git 組態自動偵測組織                                       |
| `--yes` / `-y`             | 跳過確認提示                                                  |
| `--open`                   | 在網頁瀏覽器中開啟                                            |

## 常見工作流程

### 從目前分支建立 PR

```bash
CURRENT_BRANCH=$(git branch --show-current)
az repos pr create \
  --source-branch $CURRENT_BRANCH \
  --target-branch main \
  --title "Feature: $(git log -1 --pretty=%B)" \
  --open
```

### 在管線失敗時建立工作項目

```bash
az boards work-item create \
  --title "Build $BUILD_BUILDNUMBER failed" \
  --type bug \
  --org $SYSTEM_TEAMFOUNDATIONCOLLECTIONURI \
  --project $SYSTEM_TEAMPROJECT
```

### 下載最新的管線成品

```bash
RUN_ID=$(az pipelines runs list --pipeline {pipeline-id} --top 1 --query "[0].id" -o tsv)
az pipelines runs artifact download \
  --artifact-name 'webapp' \
  --path ./output \
  --run-id $RUN_ID
```

### 核准並完成 PR

```bash
# 投票核准
az repos pr set-vote --id {pr-id} --vote approve

# 完成 PR
az repos pr update --id {pr-id} --status completed
```

### 從本機存放庫建立管線

```bash
# 從本機 git 存放庫（自動偵測存放庫、分支等）
az pipelines create --name 'CI-Pipeline' --description 'Continuous Integration'
```

### 批次更新工作項目

```bash
# 查詢項目並在迴圈中更新
for id in $(az boards query --wiql "SELECT ID FROM WorkItems WHERE State='New'" -o tsv); do
  az boards work-item update --id $id --state "Active"
done
```

## 最佳實務

### 驗證與安全性

```bash
# 從環境變數使用 PAT（最安全）
export AZURE_DEVOPS_EXT_PAT=$MY_PAT
az devops login --organization $ORG_URL

# 安全地管道傳送 PAT（避免留在 shell 歷史記錄中）
echo $MY_PAT | az devops login --organization $ORG_URL

# 設定預設值以避免重複輸入
az devops configure --defaults organization=$ORG_URL project=$PROJECT

# 使用後清除認證
az devops logout --organization $ORG_URL
```

### 冪等操作

```bash
# 總是使用 --detect 進行自動偵測
az devops configure --defaults organization=$ORG_URL project=$PROJECT

# 建立前先檢查是否存在
if ! az pipelines show --id $PIPELINE_ID 2>/dev/null; then
  az pipelines create --name "$PIPELINE_NAME" --yaml-path azure-pipelines.yml
fi

# 使用 --output tsv 進行 shell 解析
PIPELINE_ID=$(az pipelines list --query "[?name=='MyPipeline'].id" --output tsv)

# 使用 --output json 進行程式化存取
BUILD_STATUS=$(az pipelines build show --id $BUILD_ID --query "status" --output json)
```

### 腳本安全輸出

```bash
# 隱藏警告和錯誤
az pipelines list --only-show-errors

# 無輸出（適用於只需要執行的指令）
az pipelines run --name "$PIPELINE_NAME" --output none

# TSV 格式用於 shell 腳本（乾淨、無格式化）
az repos pr list --output tsv --query "[].{ID:pullRequestId,Title:title}"

# 包含特定欄位的 JSON
az pipelines list --output json --query "[].{Name:name, ID:id, URL:url}"
```

### 管線編排

```bash
# 執行管線並等待完成
RUN_ID=$(az pipelines run --name "$PIPELINE_NAME" --query "id" -o tsv)

while true; do
  STATUS=$(az pipelines runs show --run-id $RUN_ID --query "status" -o tsv)
  if [[ "$STATUS" != "inProgress" && "$STATUS" != "notStarted" ]]; then
    break
  fi
  sleep 10
done

# 檢查結果
RESULT=$(az pipelines runs show --run-id $RUN_ID --query "result" -o tsv)
if [[ "$RESULT" == "succeeded" ]]; then
  echo "管線執行成功"
else
  echo "管線執行失敗，結果為：$RESULT"
  exit 1
fi
```

### 變數群組管理

```bash
# 冪等建立變數群組
VG_NAME="production-variables"
VG_ID=$(az pipelines variable-group list --query "[?name=='$VG_NAME'].id" -o tsv)

if [[ -z "$VG_ID" ]]; then
  VG_ID=$(az pipelines variable-group create \
    --name "$VG_NAME" \
    --variables API_URL=$API_URL API_KEY=$API_KEY \
    --authorize true \
    --query "id" -o tsv)
  echo "已建立變數群組，ID：$VG_ID"
else
  echo "變數群組已存在，ID：$VG_ID"
fi
```

### 服務連線自動化

```bash
# 使用組態檔建立服務連線
cat > service-connection.json <<'EOF'
{
  "data": {
    "subscriptionId": "$SUBSCRIPTION_ID",
    "subscriptionName": "My Subscription",
    "creationMode": "Manual",
    "serviceEndpointId": "$SERVICE_ENDPOINT_ID"
  },
  "url": "https://management.azure.com/",
  "authorization": {
    "parameters": {
      "tenantid": "$TENANT_ID",
      "serviceprincipalid": "$SP_ID",
      "authenticationType": "spnKey",
      "serviceprincipalkey": "$SP_KEY"
    },
    "scheme": "ServicePrincipal"
  },
  "type": "azurerm",
  "isShared": false,
  "isReady": true
}
EOF

az devops service-endpoint create \
  --service-endpoint-configuration service-connection.json \
  --project "$PROJECT"
```

### 提取要求自動化

```bash
# 建立搭配工作項目和審閱者的 PR
PR_ID=$(az repos pr create \
  --repository "$REPO_NAME" \
  --source-branch "$FEATURE_BRANCH" \
  --target-branch main \
  --title "Feature: $(git log -1 --pretty=%B)" \
  --description "$(git log -1 --pretty=%B)" \
  --work-items $WORK_ITEM_1 $WORK_ITEM_2 \
  --reviewers "$REVIEWER_1" "$REVIEWER_2" \
  --required-reviewers "$LEAD_EMAIL" \
  --labels "enhancement" "backlog" \
  --open \
  --query "pullRequestId" -o tsv)

# 原則通過時設定自動完成
az repos pr update --id $PR_ID --auto-complete true
```

## 錯誤處理與重試模式

### 暫時性失敗的重試邏輯

```bash
# 網路操作的重試函式
retry_command() {
  local max_attempts=3
  local attempt=1
  local delay=5

  while [[ $attempt -le $max_attempts ]]; do
    if "$@"; then
      return 0
    fi
    echo "第 $attempt 次嘗試失敗。${delay} 秒後重試..."
    sleep $delay
    ((attempt++))
    delay=$((delay * 2))
  done

  echo "所有 $max_attempts 次嘗試均失敗"
  return 1
}

# 使用方式
retry_command az pipelines run --name "$PIPELINE_NAME"
```

### 檢查並處理錯誤

```bash
# 操作前檢查管線是否存在
PIPELINE_ID=$(az pipelines list --query "[?name=='$PIPELINE_NAME'].id" -o tsv)

if [[ -z "$PIPELINE_ID" ]]; then
  echo "找不到管線。正在建立..."
  az pipelines create --name "$PIPELINE_NAME" --yaml-path azure-pipelines.yml
else
  echo "管線已存在，ID：$PIPELINE_ID"
fi
```

### 驗證輸入

```bash
# 驗證必要參數
if [[ -z "$PROJECT" || -z "$REPO" ]]; then
  echo "錯誤：必須設定 PROJECT 和 REPO"
  exit 1
fi

# 檢查分支是否存在
if ! az repos ref list --repository "$REPO" --query "[?name=='refs/heads/$BRANCH']" -o tsv | grep -q .; then
  echo "錯誤：分支 $BRANCH 不存在"
  exit 1
fi
```

### 處理權限錯誤

```bash
# 嘗試操作，處理權限錯誤
if az devops security permission update \
  --id "$USER_ID" \
  --namespace "GitRepositories" \
  --project "$PROJECT" \
  --token "repoV2/$PROJECT/$REPO_ID" \
  --allow-bit 2 \
  --deny-bit 0 2>&1 | grep -q "unauthorized"; then
  echo "錯誤：權限不足，無法更新存放庫權限"
  exit 1
fi
```

### 管線失敗通知

```bash
# 執行管線並檢查結果
RUN_ID=$(az pipelines run --name "$PIPELINE_NAME" --query "id" -o tsv)

# 等待完成
while true; do
  STATUS=$(az pipelines runs show --run-id $RUN_ID --query "status" -o tsv)
  if [[ "$STATUS" != "inProgress" && "$STATUS" != "notStarted" ]]; then
    break
  fi
  sleep 10
done

# 檢查結果，失敗時建立工作項目
RESULT=$(az pipelines runs show --run-id $RUN_ID --query "result" -o tsv)
if [[ "$RESULT" != "succeeded" ]]; then
  BUILD_NUMBER=$(az pipelines runs show --run-id $RUN_ID --query "buildNumber" -o tsv)

  az boards work-item create \
    --title "Build $BUILD_NUMBER failed" \
    --type Bug \
    --description "Pipeline run $RUN_ID failed with result: $RESULT\n\nURL: $ORG_URL/$PROJECT/_build/results?buildId=$RUN_ID"
fi
```

### 優雅降級

```bash
# 嘗試下載成品，失敗時退回替代來源
if ! az pipelines runs artifact download \
  --artifact-name 'webapp' \
  --path ./output \
  --run-id $RUN_ID 2>/dev/null; then
  echo "警告：從管線執行下載失敗。退回備份來源..."

  # 替代下載方式
  curl -L "$BACKUP_URL" -o ./output/backup.zip
fi
```

## 進階 JMESPath 查詢

### 篩選與排序

```bash
# 依多個條件篩選
az pipelines list --query "[?name.contains('CI') && enabled==true]"

# 依狀態和結果篩選
az pipelines runs list --query "[?status=='completed' && result=='succeeded']"

# 依日期排序（降序）
az pipelines runs list --query "sort_by([?status=='completed'], &finishTime | reverse(@))"

# 篩選後取得前 N 項
az pipelines runs list --query "[?result=='succeeded'] | [0:5]"
```

### 巢狀查詢

```bash
# 擷取巢狀屬性
az pipelines show --id $PIPELINE_ID --query "{Name:name, Repo:repository.{Name:name, Type:type}, Folder:folder}"

# 查詢建置詳細資料
az pipelines build show --id $BUILD_ID --query "{ID:id, Number:buildNumber, Status:status, Result:result, Requested:requestedFor.displayName}"
```

### 複雜篩選

```bash
# 尋找具有特定 YAML 路徑的管線
az pipelines list --query "[?process.type.name=='yaml' && process.yamlFilename=='azure-pipelines.yml']"

# 尋找特定審閱者的 PR
az repos pr list --query "[?contains(reviewers[?displayName=='John Doe'].displayName, 'John Doe')]"

# 尋找具有特定反覆運算和狀態的工作項目
az boards work-item show --id $WI_ID --query "{Title:fields['System.Title'], State:fields['System.State'], Iteration:fields['System.IterationPath']}"
```

### 彙總

```bash
# 依狀態計數項目
az pipelines runs list --query "groupBy([?status=='completed'], &[result]) | {Succeeded: [?key=='succeeded'][0].count, Failed: [?key=='failed'][0].count}"

# 取得唯一的審閱者
az repos pr list --query "unique_by(reviewers[], &displayName)"

# 加總值
az pipelines runs list --query "[?result=='succeeded'] | [].{Duration:duration} | [0].Duration"
```

### 條件式轉換

```bash
# 格式化日期
az pipelines runs list --query "[].{ID:id, Date:createdDate, Formatted:createdDate | format_datetime(@, 'yyyy-MM-dd HH:mm')}"

# 條件式輸出
az pipelines list --query "[].{Name:name, Status:(enabled ? 'Enabled' : 'Disabled')}"

# 擷取並包含預設值
az pipelines show --id $PIPELINE_ID --query "{Name:name, Folder:folder || 'Root', Description:description || 'No description'}"
```

### 複雜工作流程

```bash
# 找出最長執行時間的建置
az pipelines build list --query "sort_by([?result=='succeeded'], &queueTime) | reverse(@) | [0:3].{ID:id, Number:buildNumber, Duration:duration}"

# 取得每位審閱者的 PR 統計
az repos pr list --query "groupBy([], &reviewers[].displayName) | [].{Reviewer:@.key, Count:length(@)}"

# 找出具有多個子項目的工作項目
az boards work-item relation list --id $PARENT_ID --query "[?rel=='System.LinkTypes.Hierarchy-Forward'] | [].{ChildID:url | split('/', @) | [-1]}"
```

## 冪等操作的腳本模式

### 建立或更新模式

```bash
# 確保管線存在，如果不同則更新
ensure_pipeline() {
  local name=$1
  local yaml_path=$2

  PIPELINE=$(az pipelines list --query "[?name=='$name']" -o json)

  if [[ -z "$PIPELINE" ]]; then
    echo "正在建立管線：$name"
    az pipelines create --name "$name" --yaml-path "$yaml_path"
  else
    echo "管線已存在：$name"
  fi
}
```

### 確保變數群組存在

```bash
# 以冪等方式建立和更新變數群組
ensure_variable_group() {
  local vg_name=$1
  shift
  local variables=("$@")

  VG_ID=$(az pipelines variable-group list --query "[?name=='$vg_name'].id" -o tsv)

  if [[ -z "$VG_ID" ]]; then
    echo "正在建立變數群組：$vg_name"
    VG_ID=$(az pipelines variable-group create \
      --name "$vg_name" \
      --variables "${variables[@]}" \
      --authorize true \
      --query "id" -o tsv)
  else
    echo "變數群組已存在：$vg_name（ID：$VG_ID）"
  fi

  echo "$VG_ID"
}
```

### 確保服務連線存在

```bash
# 檢查服務連線是否存在，如不存在則建立
ensure_service_connection() {
  local name=$1
  local project=$2

  SC_ID=$(az devops service-endpoint list \
    --project "$project" \
    --query "[?name=='$name'].id" \
    -o tsv)

  if [[ -z "$SC_ID" ]]; then
    echo "找不到服務連線。正在建立..."
    # 此處放建立邏輯
  else
    echo "服務連線已存在：$name"
    echo "$SC_ID"
  fi
}
```

### 冪等工作項目建立

```bash
# 只在同標題的工作項目不存在時才建立
create_work_item_if_new() {
  local title=$1
  local type=$2

  WI_ID=$(az boards query \
    --wiql "SELECT ID FROM WorkItems WHERE [System.WorkItemType]='$type' AND [System.Title]='$title'" \
    --query "[0].id" -o tsv)

  if [[ -z "$WI_ID" ]]; then
    echo "正在建立工作項目：$title"
    WI_ID=$(az boards work-item create --title "$title" --type "$type" --query "id" -o tsv)
  else
    echo "工作項目已存在：$title（ID：$WI_ID）"
  fi

  echo "$WI_ID"
}
```

### 批次冪等操作

```bash
# 確保多個管線存在
declare -a PIPELINES=(
  "ci-pipeline:azure-pipelines.yml"
  "deploy-pipeline:deploy.yml"
  "test-pipeline:test.yml"
)

for pipeline in "${PIPELINES[@]}"; do
  IFS=':' read -r name yaml <<< "$pipeline"
  ensure_pipeline "$name" "$yaml"
done
```

### 組態同步

```bash
# 從組態檔同步變數群組
sync_variable_groups() {
  local config_file=$1

  while IFS=',' read -r vg_name variables; do
    ensure_variable_group "$vg_name" "$variables"
  done < "$config_file"
}

# config.csv 格式：
# prod-vars,API_URL=prod.com,API_KEY=secret123
# dev-vars,API_URL=dev.com,API_KEY=secret456
```

## 實際工作流程

### CI/CD 管線設定

```bash
# 設定完整的 CI/CD 管線
setup_cicd_pipeline() {
  local project=$1
  local repo=$2
  local branch=$3

  # 建立變數群組
  VG_DEV=$(ensure_variable_group "dev-vars" "ENV=dev API_URL=api-dev.com")
  VG_PROD=$(ensure_variable_group "prod-vars" "ENV=prod API_URL=api-prod.com")

  # 建立 CI 管線
  az pipelines create \
    --name "$repo-CI" \
    --repository "$repo" \
    --branch "$branch" \
    --yaml-path .azure/pipelines/ci.yml \
    --skip-run true

  # 建立 CD 管線
  az pipelines create \
    --name "$repo-CD" \
    --repository "$repo" \
    --branch "$branch" \
    --yaml-path .azure/pipelines/cd.yml \
    --skip-run true

  echo "CI/CD 管線設定完成"
}
```

### 自動化 PR 建立

```bash
# 從功能分支建立搭配自動化的 PR
create_automated_pr() {
  local branch=$1
  local title=$2

  # 取得分支資訊
  LAST_COMMIT=$(git log -1 --pretty=%B "$branch")
  COMMIT_SHA=$(git rev-parse "$branch")

  # 找出相關工作項目
  WORK_ITEMS=$(az boards query \
    --wiql "SELECT ID FROM WorkItems WHERE [System.ChangedBy] = @Me AND [System.State] = 'Active'" \
    --query "[].id" -o tsv)

  # 建立 PR
  PR_ID=$(az repos pr create \
    --source-branch "$branch" \
    --target-branch main \
    --title "$title" \
    --description "$LAST_COMMIT" \
    --work-items $WORK_ITEMS \
    --auto-complete true \
    --query "pullRequestId" -o tsv)

  # 設定必要審閱者
  az repos pr reviewer add \
    --id $PR_ID \
    --reviewers $(git log -1 --pretty=format:'%ae' "$branch") \
    --required true

  echo "已建立 PR #$PR_ID"
}
```

### 管線監控與警示

```bash
# 監控管線並在失敗時發出警示
monitor_pipeline() {
  local pipeline_name=$1
  local slack_webhook=$2

  while true; do
    # 取得最新的執行
    RUN_ID=$(az pipelines list --query "[?name=='$pipeline_name'] | [0].id" -o tsv)
    RUNS=$(az pipelines runs list --pipeline $RUN_ID --top 1)

    LATEST_RUN_ID=$(echo "$RUNS" | jq -r '.[0].id')
    RESULT=$(echo "$RUNS" | jq -r '.[0].result')

    # 檢查是否失敗且尚未處理
    if [[ "$RESULT" == "failed" ]]; then
      # 傳送 Slack 警示
      curl -X POST "$slack_webhook" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"管線 $pipeline_name 執行失敗！執行 ID：$LATEST_RUN_ID\"}"
    fi

    sleep 300 # 每 5 分鐘檢查一次
  done
}
```

### 批次工作項目管理

```bash
# 依查詢批次更新工作項目
bulk_update_work_items() {
  local wiql=$1
  local updates=("$@")

  # 查詢工作項目
  WI_IDS=$(az boards query --wiql "$wiql" --query "[].id" -o tsv)

  # 更新每個工作項目
  for wi_id in $WI_IDS; do
    az boards work-item update --id $wi_id "${updates[@]}"
    echo "已更新工作項目：$wi_id"
  done
}

# 使用方式：bulk_update_work_items "SELECT ID FROM WorkItems WHERE State='New'" --state "Active" --assigned-to "user@example.com"
```

### 分支原則自動化

```bash
# 將分支原則套用至所有存放庫
apply_branch_policies() {
  local branch=$1
  local project=$2

  # 取得所有存放庫
  REPOS=$(az repos list --project "$project" --query "[].id" -o tsv)

  for repo_id in $REPOS; do
    echo "正在將原則套用至存放庫：$repo_id"

    # 要求最少核准者
    az repos policy approver-count create \
      --blocking true \
      --enabled true \
      --branch "$branch" \
      --repository-id "$repo_id" \
      --minimum-approver-count 2 \
      --creator-vote-counts true

    # 要求工作項目連結
    az repos policy work-item-linking create \
      --blocking true \
      --branch "$branch" \
      --enabled true \
      --repository-id "$repo_id"

    # 要求建置驗證
    BUILD_ID=$(az pipelines list --query "[?name=='CI'].id" -o tsv | head -1)
    az repos policy build create \
      --blocking true \
      --enabled true \
      --branch "$branch" \
      --repository-id "$repo_id" \
      --build-definition-id "$BUILD_ID" \
      --queue-on-source-update-only true
  done
}
```

### 多環境部署

```bash
# 跨多個環境部署
deploy_to_environments() {
  local run_id=$1
  shift
  local environments=("$@")

  # 下載成品
  ARTIFACT_NAME=$(az pipelines runs artifact list --run-id $run_id --query "[0].name" -o tsv)
  az pipelines runs artifact download \
    --artifact-name "$ARTIFACT_NAME" \
    --path ./artifacts \
    --run-id $run_id

  # 部署至每個環境
  for env in "${environments[@]}"; do
    echo "正在部署至：$env"

    # 取得環境特定的變數
    VG_ID=$(az pipelines variable-group list --query "[?name=='$env-vars'].id" -o tsv)

    # 執行部署管線
    DEPLOY_RUN_ID=$(az pipelines run \
      --name "Deploy-$env" \
      --variables ARTIFACT_PATH=./artifacts ENV="$env" \
      --query "id" -o tsv)

    # 等待部署完成
    while true; do
      STATUS=$(az pipelines runs show --run-id $DEPLOY_RUN_ID --query "status" -o tsv)
      if [[ "$STATUS" != "inProgress" ]]; then
        break
      fi
      sleep 10
    done
  done
}
```

## 增強的全域引數

| 參數                 | 說明                                                 |
| -------------------- | ---------------------------------------------------- |
| `--help` / `-h`      | 顯示指令說明                                         |
| `--output` / `-o`    | 輸出格式（json、jsonc、none、table、tsv、yaml、yamlc）|
| `--query`            | 用於篩選輸出的 JMESPath 查詢字串                      |
| `--verbose`          | 增加日誌詳細程度                                      |
| `--debug`            | 顯示所有偵錯日誌                                      |
| `--only-show-errors` | 僅顯示錯誤，隱藏警告                                  |
| `--subscription`     | 訂用帳戶名稱或 ID                                     |
| `--yes` / `-y`       | 跳過確認提示                                          |

## 增強的常用參數

| 參數                       | 說明                                                         |
| -------------------------- | ------------------------------------------------------------ |
| `--org` / `--organization` | Azure DevOps 組織 URL（例如 `https://dev.azure.com/{org}`）  |
| `--project` / `-p`         | 專案名稱或 ID                                                |
| `--detect`                 | 從 git 組態自動偵測組織                                       |
| `--yes` / `-y`             | 跳過確認提示                                                  |
| `--open`                   | 在網頁瀏覽器中開啟資源                                        |
| `--subscription`           | Azure 訂用帳戶（用於 Azure 資源）                              |

## 取得說明

```bash
# 一般說明
az devops --help

# 特定指令群組的說明
az pipelines --help
az repos pr --help

# 特定指令的說明
az repos pr create --help

# 搜尋範例
az find "az repos pr create"
```

````

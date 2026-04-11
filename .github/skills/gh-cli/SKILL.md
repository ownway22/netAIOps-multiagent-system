````skill
---
name: gh-cli
description: GitHub CLI (gh) 完整參考手冊，涵蓋存放庫、議題、提取要求、Actions、專案、發行版本、Gist、Codespace、組織、擴充功能，以及所有可從命令列執行的 GitHub 操作。
---

# GitHub CLI (gh)

GitHub CLI (gh) 完整參考手冊 — 從命令列無縫操作 GitHub。

**版本：** 2.85.0（截至 2026 年 1 月為最新版）

## 先決條件

### 安裝

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Windows
winget install --id GitHub.cli

# 驗證安裝
gh --version
```

### 驗證

```bash
# 互動式登入（預設：github.com）
gh auth login

# 以特定主機名稱登入
gh auth login --hostname enterprise.internal

# 使用權杖登入
gh auth login --with-token < mytoken.txt

# 檢查驗證狀態
gh auth status

# 切換帳號
gh auth switch --hostname github.com --user username

# 登出
gh auth logout --hostname github.com --user username
```

### 設定 Git 整合

```bash
# 將 git 設定為使用 gh 作為認證輔助程式
gh auth setup-git

# 查看作用中的權杖
gh auth token

# 重新整理驗證範圍
gh auth refresh --scopes write:org,read:public_key
```

## CLI 結構

```
gh                          # 根指令
├── auth                    # 驗證
│   ├── login
│   ├── logout
│   ├── refresh
│   ├── setup-git
│   ├── status
│   ├── switch
│   └── token
├── browse                  # 在瀏覽器中開啟
├── codespace               # GitHub Codespace
│   ├── code
│   ├── cp
│   ├── create
│   ├── delete
│   ├── edit
│   ├── jupyter
│   ├── list
│   ├── logs
│   ├── ports
│   ├── rebuild
│   ├── ssh
│   ├── stop
│   └── view
├── gist                    # Gist
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   ├── list
│   ├── rename
│   └── view
├── issue                   # 議題
│   ├── create
│   ├── list
│   ├── status
│   ├── close
│   ├── comment
│   ├── delete
│   ├── develop
│   ├── edit
│   ├── lock
│   ├── pin
│   ├── reopen
│   ├── transfer
│   ├── unlock
│   └── view
├── org                     # 組織
│   └── list
├── pr                      # 提取要求
│   ├── create
│   ├── list
│   ├── status
│   ├── checkout
│   ├── checks
│   ├── close
│   ├── comment
│   ├── diff
│   ├── edit
│   ├── lock
│   ├── merge
│   ├── ready
│   ├── reopen
│   ├── revert
│   ├── review
│   ├── unlock
│   ├── update-branch
│   └── view
├── project                 # 專案
│   ├── close
│   ├── copy
│   ├── create
│   ├── delete
│   ├── edit
│   ├── field-create
│   ├── field-delete
│   ├── field-list
│   ├── item-add
│   ├── item-archive
│   ├── item-create
│   ├── item-delete
│   ├── item-edit
│   ├── item-list
│   ├── link
│   ├── list
│   ├── mark-template
│   ├── unlink
│   └── view
├── release                 # 發行版本
│   ├── create
│   ├── list
│   ├── delete
│   ├── delete-asset
│   ├── download
│   ├── edit
│   ├── upload
│   ├── verify
│   ├── verify-asset
│   └── view
├── repo                    # 存放庫
│   ├── create
│   ├── list
│   ├── archive
│   ├── autolink
│   ├── clone
│   ├── delete
│   ├── deploy-key
│   ├── edit
│   ├── fork
│   ├── gitignore
│   ├── license
│   ├── rename
│   ├── set-default
│   ├── sync
│   ├── unarchive
│   └── view
├── cache                   # Actions 快取
│   ├── delete
│   └── list
├── run                     # 工作流程執行
│   ├── cancel
│   ├── delete
│   ├── download
│   ├── list
│   ├── rerun
│   ├── view
│   └── watch
├── workflow                # 工作流程
│   ├── disable
│   ├── enable
│   ├── list
│   ├── run
│   └── view
├── agent-task              # 代理程式工作
├── alias                   # 指令別名
│   ├── delete
│   ├── import
│   ├── list
│   └── set
├── api                     # API 請求
├── attestation             # 成品證明
│   ├── download
│   ├── trusted-root
│   └── verify
├── completion              # Shell 自動補全
├── config                  # 組態
│   ├── clear-cache
│   ├── get
│   ├── list
│   └── set
├── extension               # 擴充功能
│   ├── browse
│   ├── create
│   ├── exec
│   ├── install
│   ├── list
│   ├── remove
│   ├── search
│   └── upgrade
├── gpg-key                 # GPG 金鑰
│   ├── add
│   ├── delete
│   └── list
├── label                   # 標籤
│   ├── clone
│   ├── create
│   ├── delete
│   ├── edit
│   └── list
├── preview                 # 預覽功能
├── ruleset                 # 規則集
│   ├── check
│   ├── list
│   └── view
├── search                  # 搜尋
│   ├── code
│   ├── commits
│   ├── issues
│   ├── prs
│   └── repos
├── secret                  # 機密
│   ├── delete
│   ├── list
│   └── set
├── ssh-key                 # SSH 金鑰
│   ├── add
│   ├── delete
│   └── list
├── status                  # 狀態概覽
└── variable                # 變數
    ├── delete
    ├── get
    ├── list
    └── set
```

## 組態

### 全域組態

```bash
# 列出所有組態
gh config list

# 取得特定組態值
gh config list git_protocol
gh config get editor

# 設定組態值
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt disabled
gh config set pager "less -R"

# 清除組態快取
gh config clear-cache
```

### 環境變數

```bash
# GitHub 權杖（用於自動化）
export GH_TOKEN=ghp_xxxxxxxxxxxx

# GitHub 主機名稱
export GH_HOST=github.com

# 停用提示
export GH_PROMPT_DISABLED=true

# 自訂編輯器
export GH_EDITOR=vim

# 自訂分頁程式
export GH_PAGER=less

# HTTP 逾時
export GH_TIMEOUT=30

# 自訂存放庫（覆寫預設值）
export GH_REPO=owner/repo

# 自訂 git 通訊協定
export GH_ENTERPRISE_HOSTNAME=hostname
```

## 驗證 (gh auth)

### 登入

```bash
# 互動式登入
gh auth login

# 網頁式驗證
gh auth login --web

# 搭配剪貼簿的 OAuth 代碼
gh auth login --web --clipboard

# 指定 git 通訊協定
gh auth login --git-protocol ssh

# 自訂主機名稱（GitHub Enterprise）
gh auth login --hostname enterprise.internal

# 從標準輸入使用權杖登入
gh auth login --with-token < token.txt

# 不安全的儲存（純文字）
gh auth login --insecure-storage
```

### 狀態

```bash
# 顯示所有驗證狀態
gh auth status

# 僅顯示作用中帳號
gh auth status --active

# 顯示特定主機名稱
gh auth status --hostname github.com

# 在輸出中顯示權杖
gh auth status --show-token

# JSON 輸出
gh auth status --json hosts

# 使用 jq 篩選
gh auth status --json hosts --jq '.hosts | add'
```

### 切換帳號

```bash
# 互動式切換
gh auth switch

# 切換至特定使用者/主機
gh auth switch --hostname github.com --user monalisa
```

### 權杖

```bash
# 列印驗證權杖
gh auth token

# 特定主機/使用者的權杖
gh auth token --hostname github.com --user monalisa
```

### 重新整理

```bash
# 重新整理認證
gh auth refresh

# 新增範圍
gh auth refresh --scopes write:org,read:public_key

# 移除範圍
gh auth refresh --remove-scopes delete_repo

# 重設為預設範圍
gh auth refresh --reset-scopes

# 搭配剪貼簿
gh auth refresh --clipboard
```

### 設定 Git

```bash
# 設定 git 認證輔助程式
gh auth setup-git

# 針對特定主機設定
gh auth setup-git --hostname enterprise.internal

# 即使主機未知也強制設定
gh auth setup-git --hostname enterprise.internal --force
```

## 瀏覽 (gh browse)

```bash
# 在瀏覽器中開啟存放庫
gh browse

# 開啟特定路徑
gh browse script/
gh browse main.go:312

# 開啟議題或 PR
gh browse 123

# 開啟提交
gh browse 77507cd94ccafcf568f8560cfecde965fcfa63

# 搭配特定分支開啟
gh browse main.go --branch bug-fix

# 開啟不同存放庫
gh browse --repo owner/repo

# 開啟特定頁面
gh browse --actions       # Actions 分頁
gh browse --projects      # 專案分頁
gh browse --releases      # 發行版本分頁
gh browse --settings      # 設定頁面
gh browse --wiki          # Wiki 頁面

# 列印 URL 而非開啟
gh browse --no-browser
```

## 存放庫 (gh repo)

### 建立存放庫

```bash
# 建立新存放庫
gh repo create my-repo

# 搭配描述建立
gh repo create my-repo --description "My awesome project"

# 建立公開存放庫
gh repo create my-repo --public

# 建立私人存放庫
gh repo create my-repo --private

# 搭配首頁建立
gh repo create my-repo --homepage https://example.com

# 搭配授權條款建立
gh repo create my-repo --license mit

# 搭配 gitignore 建立
gh repo create my-repo --gitignore python

# 初始化為範本存放庫
gh repo create my-repo --template

# 在組織中建立存放庫
gh repo create org/my-repo

# 建立但不在本機複製
gh repo create my-repo --source=.

# 停用議題
gh repo create my-repo --disable-issues

# 停用 Wiki
gh repo create my-repo --disable-wiki
```

### 複製存放庫

```bash
# 複製存放庫
gh repo clone owner/repo

# 複製到特定目錄
gh repo clone owner/repo my-directory

# 複製不同分支
gh repo clone owner/repo --branch develop
```

### 列出存放庫

```bash
# 列出所有存放庫
gh repo list

# 列出特定擁有者的存放庫
gh repo list owner

# 限制結果數量
gh repo list --limit 50

# 僅公開存放庫
gh repo list --public

# 僅原始碼存放庫（非分叉版本）
gh repo list --source

# JSON 輸出
gh repo list --json name,visibility,owner

# 表格輸出
gh repo list --limit 100 | tail -n +2

# 使用 jq 篩選
gh repo list --json name --jq '.[].name'
```

### 檢視存放庫

```bash
# 檢視存放庫詳細資料
gh repo view

# 檢視特定存放庫
gh repo view owner/repo

# JSON 輸出
gh repo view --json name,description,defaultBranchRef

# 在瀏覽器中檢視
gh repo view --web
```

### 編輯存放庫

```bash
# 編輯描述
gh repo edit --description "New description"

# 設定首頁
gh repo edit --homepage https://example.com

# 變更可見性
gh repo edit --visibility private
gh repo edit --visibility public

# 啟用/停用功能
gh repo edit --enable-issues
gh repo edit --disable-issues
gh repo edit --enable-wiki
gh repo edit --disable-wiki
gh repo edit --enable-projects
gh repo edit --disable-projects

# 設定預設分支
gh repo edit --default-branch main

# 重新命名存放庫
gh repo rename new-name

# 封存存放庫
gh repo archive
gh repo unarchive
```

### 刪除存放庫

```bash
# 刪除存放庫
gh repo delete owner/repo

# 跳過確認提示
gh repo delete owner/repo --yes
```

### 分叉存放庫

```bash
# 分叉存放庫
gh repo fork owner/repo

# 分叉到組織
gh repo fork owner/repo --org org-name

# 分叉後複製
gh repo fork owner/repo --clone

# 分叉的遠端名稱
gh repo fork owner/repo --remote-name upstream
```

### 同步分叉

```bash
# 同步分叉與上游
gh repo sync

# 同步特定分支
gh repo sync --branch feature

# 強制同步
gh repo sync --force
```

### 設定預設存放庫

```bash
# 設定目前目錄的預設存放庫
gh repo set-default

# 明確設定預設值
gh repo set-default owner/repo

# 取消設定預設值
gh repo set-default --unset
```

### 存放庫自動連結

```bash
# 列出自動連結
gh repo autolink list

# 新增自動連結
gh repo autolink add \
  --key-prefix JIRA- \
  --url-template https://jira.example.com/browse/<num>

# 刪除自動連結
gh repo autolink delete 12345
```

### 存放庫部署金鑰

```bash
# 列出部署金鑰
gh repo deploy-key list

# 新增部署金鑰
gh repo deploy-key add ~/.ssh/id_rsa.pub \
  --title "Production server" \
  --read-only

# 刪除部署金鑰
gh repo deploy-key delete 12345
```

### Gitignore 和授權條款

```bash
# 檢視 gitignore 範本
gh repo gitignore

# 檢視授權條款範本
gh repo license mit

# 搭配完整名稱的授權條款
gh repo license mit --fullname "John Doe"
```

## 議題 (gh issue)

### 建立議題

```bash
# 互動式建立議題
gh issue create

# 搭配標題建立
gh issue create --title "Bug: Login not working"

# 搭配標題和內文建立
gh issue create \
  --title "Bug: Login not working" \
  --body "Steps to reproduce..."

# 從檔案取得內文
gh issue create --body-file issue.md

# 搭配標籤建立
gh issue create --title "Fix bug" --labels bug,high-priority

# 搭配指派對象建立
gh issue create --title "Fix bug" --assignee user1,user2

# 在特定存放庫中建立
gh issue create --repo owner/repo --title "Issue title"

# 從網頁建立議題
gh issue create --web
```

### 列出議題

```bash
# 列出所有開啟的議題
gh issue list

# 列出所有議題（包含已關閉）
gh issue list --state all

# 列出已關閉的議題
gh issue list --state closed

# 限制結果數量
gh issue list --limit 50

# 依指派對象篩選
gh issue list --assignee username
gh issue list --assignee @me

# 依標籤篩選
gh issue list --labels bug,enhancement

# 依里程碑篩選
gh issue list --milestone "v1.0"

# 搜尋/篩選
gh issue list --search "is:open is:issue label:bug"

# JSON 輸出
gh issue list --json number,title,state,author

# 表格檢視
gh issue list --json number,title,labels --jq '.[] | [.number, .title, .labels[].name] | @tsv'

# 顯示留言數
gh issue list --json number,title,comments --jq '.[] | [.number, .title, .comments]'

# 排序方式
gh issue list --sort created --order desc
```

### 檢視議題

```bash
# 檢視議題
gh issue view 123

# 搭配留言檢視
gh issue view 123 --comments

# 在瀏覽器中檢視
gh issue view 123 --web

# JSON 輸出
gh issue view 123 --json title,body,state,labels,comments

# 檢視特定欄位
gh issue view 123 --json title --jq '.title'
```

### 編輯議題

```bash
# 互動式編輯
gh issue edit 123

# 編輯標題
gh issue edit 123 --title "New title"

# 編輯內文
gh issue edit 123 --body "New description"

# 新增標籤
gh issue edit 123 --add-label bug,high-priority

# 移除標籤
gh issue edit 123 --remove-label stale

# 新增指派對象
gh issue edit 123 --add-assignee user1,user2

# 移除指派對象
gh issue edit 123 --remove-assignee user1

# 設定里程碑
gh issue edit 123 --milestone "v1.0"
```

### 關閉/重新開啟議題

```bash
# 關閉議題
gh issue close 123

# 搭配留言關閉
gh issue close 123 --comment "Fixed in PR #456"

# 重新開啟議題
gh issue reopen 123
```

### 對議題留言

```bash
# 新增留言
gh issue comment 123 --body "This looks good!"

# 編輯留言
gh issue comment 123 --edit 456789 --body "Updated comment"

# 刪除留言
gh issue comment 123 --delete 456789
```

### 議題狀態

```bash
# 顯示議題狀態摘要
gh issue status

# 特定存放庫的狀態
gh issue status --repo owner/repo
```

### 釘選/取消釘選議題

```bash
# 釘選議題（釘選到存放庫面板）
gh issue pin 123

# 取消釘選議題
gh issue unpin 123
```

### 鎖定/解除鎖定議題

```bash
# 鎖定對話
gh issue lock 123

# 搭配原因鎖定
gh issue lock 123 --reason off-topic

# 解除鎖定
gh issue unlock 123
```

### 轉移議題

```bash
# 轉移至其他存放庫
gh issue transfer 123 --repo owner/new-repo
```

### 刪除議題

```bash
# 刪除議題
gh issue delete 123

# 跳過確認提示
gh issue delete 123 --yes
```

### 從議題開發（草稿 PR）

```bash
# 從議題建立草稿 PR
gh issue develop 123

# 在特定分支中建立
gh issue develop 123 --branch fix/issue-123

# 搭配基礎分支建立
gh issue develop 123 --base main
```

## 提取要求 (gh pr)

### 建立提取要求

```bash
# 互動式建立 PR
gh pr create

# 搭配標題建立
gh pr create --title "Feature: Add new functionality"

# 搭配標題和內文建立
gh pr create \
  --title "Feature: Add new functionality" \
  --body "This PR adds..."

# 從範本填入內文
gh pr create --body-file .github/PULL_REQUEST_TEMPLATE.md

# 設定基礎分支
gh pr create --base main

# 設定來源分支（預設：目前分支）
gh pr create --head feature-branch

# 建立草稿 PR
gh pr create --draft

# 新增指派對象
gh pr create --assignee user1,user2

# 新增審閱者
gh pr create --reviewer user1,user2

# 新增標籤
gh pr create --labels enhancement,feature

# 連結至議題
gh pr create --issue 123

# 在特定存放庫中建立
gh pr create --repo owner/repo

# 建立後在瀏覽器中開啟
gh pr create --web
```

### 列出提取要求

```bash
# 列出開啟的 PR
gh pr list

# 列出所有 PR
gh pr list --state all

# 列出已合併的 PR
gh pr list --state merged

# 列出已關閉（未合併）的 PR
gh pr list --state closed

# 依來源分支篩選
gh pr list --head feature-branch

# 依基礎分支篩選
gh pr list --base main

# 依作者篩選
gh pr list --author username
gh pr list --author @me

# 依指派對象篩選
gh pr list --assignee username

# 依標籤篩選
gh pr list --labels bug,enhancement

# 限制結果數量
gh pr list --limit 50

# 搜尋
gh pr list --search "is:open is:pr label:review-required"

# JSON 輸出
gh pr list --json number,title,state,author,headRefName

# 顯示檢查狀態
gh pr list --json number,title,statusCheckRollup --jq '.[] | [.number, .title, .statusCheckRollup[]?.status]'

# 排序方式
gh pr list --sort created --order desc
```

### 檢視提取要求

```bash
# 檢視 PR
gh pr view 123

# 搭配留言檢視
gh pr view 123 --comments

# 在瀏覽器中檢視
gh pr view 123 --web

# JSON 輸出
gh pr view 123 --json title,body,state,author,commits,files

# 檢視差異
gh pr view 123 --json files --jq '.files[].path'

# 搭配 jq 查詢檢視
gh pr view 123 --json title,state --jq '"\(.title): \(.state)"'
```

### 簽出提取要求

```bash
# 簽出 PR 分支
gh pr checkout 123

# 以特定分支名稱簽出
gh pr checkout 123 --branch name-123

# 強制簽出
gh pr checkout 123 --force
```

### 提取要求差異

```bash
# 檢視 PR 差異
gh pr diff 123

# 搭配色彩檢視差異
gh pr diff 123 --color always

# 輸出至檔案
gh pr diff 123 > pr-123.patch

# 僅顯示檔案名稱的差異
gh pr diff 123 --name-only
```

### 合併提取要求

```bash
# 合併 PR
gh pr merge 123

# 以特定方式合併
gh pr merge 123 --merge
gh pr merge 123 --squash
gh pr merge 123 --rebase

# 合併後刪除分支
gh pr merge 123 --delete-branch

# 搭配留言合併
gh pr merge 123 --subject "Merge PR #123" --body "Merging feature"

# 合併草稿 PR
gh pr merge 123 --admin

# 強制合併（跳過檢查）
gh pr merge 123 --admin
```

### 關閉提取要求

```bash
# 關閉 PR（作為草稿，不合併）
gh pr close 123

# 搭配留言關閉
gh pr close 123 --comment "Closing due to..."
```

### 重新開啟提取要求

```bash
# 重新開啟已關閉的 PR
gh pr reopen 123
```

### 編輯提取要求

```bash
# 互動式編輯
gh pr edit 123

# 編輯標題
gh pr edit 123 --title "New title"

# 編輯內文
gh pr edit 123 --body "New description"

# 新增標籤
gh pr edit 123 --add-label bug,enhancement

# 移除標籤
gh pr edit 123 --remove-label stale

# 新增指派對象
gh pr edit 123 --add-assignee user1,user2

# 移除指派對象
gh pr edit 123 --remove-assignee user1

# 新增審閱者
gh pr edit 123 --add-reviewer user1,user2

# 移除審閱者
gh pr edit 123 --remove-reviewer user1

# 標記為準備好接受審閱
gh pr edit 123 --ready
```

### 準備審閱

```bash
# 將草稿 PR 標記為準備就緒
gh pr ready 123
```

### 提取要求檢查

```bash
# 檢視 PR 檢查
gh pr checks 123

# 即時監看檢查
gh pr checks 123 --watch

# 監看間隔（秒）
gh pr checks 123 --watch --interval 5
```

### 對提取要求留言

```bash
# 新增留言
gh pr comment 123 --body "Looks good!"

# 對特定行留言
gh pr comment 123 --body "Fix this" \
  --repo owner/repo \
  --head-owner owner --head-branch feature

# 編輯留言
gh pr comment 123 --edit 456789 --body "Updated"

# 刪除留言
gh pr comment 123 --delete 456789
```

### 審閱提取要求

```bash
# 審閱 PR（開啟編輯器）
gh pr review 123

# 核准 PR
gh pr review 123 --approve \
  --approve-body "LGTM!"

# 要求變更
gh pr review 123 --request-changes \
  --body "Please fix these issues"

# 對 PR 留言
gh pr review 123 --comment --body "Some thoughts..."

# 駁回審閱
gh pr review 123 --dismiss
```

### 更新分支

```bash
# 使用最新基礎分支更新 PR 分支
gh pr update-branch 123

# 強制更新
gh pr update-branch 123 --force

# 使用合併策略
gh pr update-branch 123 --merge
```

### 鎖定/解除鎖定提取要求

```bash
# 鎖定 PR 對話
gh pr lock 123

# 搭配原因鎖定
gh pr lock 123 --reason off-topic

# 解除鎖定
gh pr unlock 123
```

### 還原提取要求

```bash
# 還原已合併的 PR
gh pr revert 123

# 搭配特定分支名稱還原
gh pr revert 123 --branch revert-pr-123
```

### 提取要求狀態

```bash
# 顯示 PR 狀態摘要
gh pr status

# 特定存放庫的狀態
gh pr status --repo owner/repo
```

## GitHub Actions

### 工作流程執行 (gh run)

```bash
# 列出工作流程執行
gh run list

# 列出特定工作流程的執行
gh run list --workflow "ci.yml"

# 列出特定分支的執行
gh run list --branch main

# 限制結果數量
gh run list --limit 20

# JSON 輸出
gh run list --json databaseId,status,conclusion,headBranch

# 檢視執行詳細資料
gh run view 123456789

# 搭配詳細日誌檢視執行
gh run view 123456789 --log

# 檢視特定工作
gh run view 123456789 --job 987654321

# 在瀏覽器中檢視
gh run view 123456789 --web

# 即時監看執行
gh run watch 123456789

# 搭配間隔監看
gh run watch 123456789 --interval 5

# 重新執行失敗項目
gh run rerun 123456789

# 重新執行特定工作
gh run rerun 123456789 --job 987654321

# 取消執行
gh run cancel 123456789

# 刪除執行
gh run delete 123456789

# 下載執行成品
gh run download 123456789

# 下載特定成品
gh run download 123456789 --name build

# 下載到目錄
gh run download 123456789 --dir ./artifacts
```

### 工作流程 (gh workflow)

```bash
# 列出工作流程
gh workflow list

# 檢視工作流程詳細資料
gh workflow view ci.yml

# 檢視工作流程 YAML
gh workflow view ci.yml --yaml

# 在瀏覽器中檢視
gh workflow view ci.yml --web

# 啟用工作流程
gh workflow enable ci.yml

# 停用工作流程
gh workflow disable ci.yml

# 手動執行工作流程
gh workflow run ci.yml

# 搭配輸入參數執行
gh workflow run ci.yml \
  --raw-field \
  version="1.0.0" \
  environment="production"

# 從特定分支執行
gh workflow run ci.yml --ref develop
```

### Actions 快取 (gh cache)

```bash
# 列出快取
gh cache list

# 列出特定分支的快取
gh cache list --branch main

# 搭配限制列出
gh cache list --limit 50

# 刪除快取
gh cache delete 123456789

# 刪除所有快取
gh cache delete --all
```

### Actions 機密 (gh secret)

```bash
# 列出機密
gh secret list

# 設定機密（提示輸入值）
gh secret set MY_SECRET

# 從環境設定機密
echo "$MY_SECRET" | gh secret set MY_SECRET

# 為特定環境設定機密
gh secret set MY_SECRET --env production

# 為組織設定機密
gh secret set MY_SECRET --org orgname

# 刪除機密
gh secret delete MY_SECRET

# 從環境中刪除
gh secret delete MY_SECRET --env production
```

### Actions 變數 (gh variable)

```bash
# 列出變數
gh variable list

# 設定變數
gh variable set MY_VAR "some-value"

# 為特定環境設定變數
gh variable set MY_VAR "value" --env production

# 為組織設定變數
gh variable set MY_VAR "value" --org orgname

# 取得變數值
gh variable get MY_VAR

# 刪除變數
gh variable delete MY_VAR

# 從環境中刪除
gh variable delete MY_VAR --env production
```

## 專案 (gh project)

```bash
# 列出專案
gh project list

# 列出特定擁有者的專案
gh project list --owner owner

# 開啟的專案
gh project list --open

# 檢視專案
gh project view 123

# 檢視專案項目
gh project view 123 --format json

# 建立專案
gh project create --title "My Project"

# 在組織中建立
gh project create --title "Project" --org orgname

# 搭配 README 建立
gh project create --title "Project" --readme "Description here"

# 編輯專案
gh project edit 123 --title "New Title"

# 刪除專案
gh project delete 123

# 關閉專案
gh project close 123

# 複製專案
gh project copy 123 --owner target-owner --title "Copy"

# 標記為範本
gh project mark-template 123

# 列出欄位
gh project field-list 123

# 建立欄位
gh project field-create 123 --title "Status" --datatype single_select

# 刪除欄位
gh project field-delete 123 --id 456

# 列出項目
gh project item-list 123

# 建立項目
gh project item-create 123 --title "New item"

# 將項目新增至專案
gh project item-add 123 --owner-owner --repo repo --issue 456

# 編輯項目
gh project item-edit 123 --id 456 --title "Updated title"

# 刪除項目
gh project item-delete 123 --id 456

# 封存項目
gh project item-archive 123 --id 456

# 連結項目
gh project link 123 --id 456 --link-id 789

# 解除連結項目
gh project unlink 123 --id 456 --link-id 789

# 在瀏覽器中檢視專案
gh project view 123 --web
```

## 發行版本 (gh release)

```bash
# 列出發行版本
gh release list

# 檢視最新發行版本
gh release view

# 檢視特定發行版本
gh release view v1.0.0

# 在瀏覽器中檢視
gh release view v1.0.0 --web

# 建立發行版本
gh release create v1.0.0 \
  --notes "Release notes here"

# 從檔案取得發行說明
gh release create v1.0.0 --notes-file notes.md

# 搭配目標建立發行版本
gh release create v1.0.0 --target main

# 建立草稿發行版本
gh release create v1.0.0 --draft

# 建立預先發行版本
gh release create v1.0.0 --prerelease

# 搭配標題建立發行版本
gh release create v1.0.0 --title "Version 1.0.0"

# 上傳資產至發行版本
gh release upload v1.0.0 ./file.tar.gz

# 上傳多個資產
gh release upload v1.0.0 ./file1.tar.gz ./file2.tar.gz

# 搭配標籤上傳（區分大小寫）
gh release upload v1.0.0 ./file.tar.gz --casing

# 刪除發行版本
gh release delete v1.0.0

# 刪除並清理標籤
gh release delete v1.0.0 --yes

# 刪除特定資產
gh release delete-asset v1.0.0 file.tar.gz

# 下載發行版本資產
gh release download v1.0.0

# 下載特定資產
gh release download v1.0.0 --pattern "*.tar.gz"

# 下載到目錄
gh release download v1.0.0 --dir ./downloads

# 下載壓縮檔（zip/tar）
gh release download v1.0.0 --archive zip

# 編輯發行版本
gh release edit v1.0.0 --notes "Updated notes"

# 驗證發行版本簽章
gh release verify v1.0.0

# 驗證特定資產
gh release verify-asset v1.0.0 file.tar.gz
```

## Gist (gh gist)

```bash
# 列出 Gist
gh gist list

# 列出所有 Gist（包含私人）
gh gist list --public

# 限制結果數量
gh gist list --limit 20

# 檢視 Gist
gh gist view abc123

# 檢視 Gist 檔案
gh gist view abc123 --files

# 建立 Gist
gh gist create script.py

# 搭配描述建立 Gist
gh gist create script.py --desc "My script"

# 建立公開 Gist
gh gist create script.py --public

# 建立多檔案 Gist
gh gist create file1.py file2.py

# 從標準輸入建立
echo "print('hello')" | gh gist create

# 編輯 Gist
gh gist edit abc123

# 刪除 Gist
gh gist delete abc123

# 重新命名 Gist 檔案
gh gist rename abc123 --filename old.py new.py

# 複製 Gist
gh gist clone abc123

# 複製到目錄
gh gist clone abc123 my-directory
```

## Codespace (gh codespace)

```bash
# 列出 Codespace
gh codespace list

# 建立 Codespace
gh codespace create

# 搭配特定存放庫建立
gh codespace create --repo owner/repo

# 搭配分支建立
gh codespace create --branch develop

# 搭配特定機器建立
gh codespace create --machine premiumLinux

# 檢視 Codespace 詳細資料
gh codespace view

# SSH 連線至 Codespace
gh codespace ssh

# 搭配特定指令 SSH 連線
gh codespace ssh --command "cd /workspaces && ls"

# 在瀏覽器中開啟 Codespace
gh codespace code

# 在 VS Code 中開啟
gh codespace code --codec

# 搭配特定路徑開啟
gh codespace code --path /workspaces/repo

# 停止 Codespace
gh codespace stop

# 刪除 Codespace
gh codespace delete

# 檢視日誌
gh codespace logs

--tail 100

# 檢視連接埠
gh codespace ports

# 轉送連接埠
gh codespace cp 8080:8080

# 重建 Codespace
gh codespace rebuild

# 編輯 Codespace
gh codespace edit --machine standardLinux

# Jupyter 支援
gh codespace jupyter

# 複製檔案至/從 Codespace
gh codespace cp file.txt :/workspaces/file.txt
gh codespace cp :/workspaces/file.txt ./file.txt
```

## 組織 (gh org)

```bash
# 列出組織
gh org list

# 列出特定使用者的組織
gh org list --user username

# JSON 輸出
gh org list --json login,name,description

# 檢視組織
gh org view orgname

# 檢視組織成員
gh org view orgname --json members --jq '.members[] | .login'
```

## 搜尋 (gh search)

```bash
# 搜尋程式碼
gh search code "TODO"

# 在特定存放庫中搜尋
gh search code "TODO" --repo owner/repo

# 搜尋提交
gh search commits "fix bug"

# 搜尋議題
gh search issues "label:bug state:open"

# 搜尋 PR
gh search prs "is:open is:pr review:required"

# 搜尋存放庫
gh search repos "stars:>1000 language:python"

# 限制結果數量
gh search repos "topic:api" --limit 50

# JSON 輸出
gh search repos "stars:>100" --json name,description,stargazers

# 排序結果
gh search repos "language:rust" --order desc --sort stars

# 搭配擴充功能搜尋
gh search code "import" --extension py

# 網頁搜尋（在瀏覽器中開啟）
gh search prs "is:open" --web
```

## 標籤 (gh label)

```bash
# 列出標籤
gh label list

# 建立標籤
gh label create bug --color "d73a4a" --description "Something isn't working"

# 搭配十六進位色碼建立
gh label create enhancement --color "#a2eeef"

# 編輯標籤
gh label edit bug --name "bug-report" --color "ff0000"

# 刪除標籤
gh label delete bug

# 從存放庫複製標籤
gh label clone owner/repo

# 複製到特定存放庫
gh label clone owner/repo --repo target/repo
```

## SSH 金鑰 (gh ssh-key)

```bash
# 列出 SSH 金鑰
gh ssh-key list

# 新增 SSH 金鑰
gh ssh-key add ~/.ssh/id_rsa.pub --title "My laptop"

# 搭配類型新增金鑰
gh ssh-key add ~/.ssh/id_ed25519.pub --type "authentication"

# 刪除 SSH 金鑰
gh ssh-key delete 12345

# 依標題刪除
gh ssh-key delete --title "My laptop"
```

## GPG 金鑰 (gh gpg-key)

```bash
# 列出 GPG 金鑰
gh gpg-key list

# 新增 GPG 金鑰
gh gpg-key add ~/.ssh/id_rsa.pub

# 刪除 GPG 金鑰
gh gpg-key delete 12345

# 依金鑰 ID 刪除
gh gpg-key delete ABCD1234
```

## 狀態 (gh status)

```bash
# 顯示狀態概覽
gh status

# 特定存放庫的狀態
gh status --repo owner/repo

# JSON 輸出
gh status --json
```

## 組態 (gh config)

```bash
# 列出所有組態
gh config list

# 取得特定值
gh config get editor

# 設定值
gh config set editor vim

# 設定 git 通訊協定
gh config set git_protocol ssh

# 清除快取
gh config clear-cache

# 設定提示行為
gh config set prompt disabled
gh config set prompt enabled
```

## 擴充功能 (gh extension)

```bash
# 列出已安裝的擴充功能
gh extension list

# 搜尋擴充功能
gh extension search github

# 安裝擴充功能
gh extension install owner/extension-repo

# 從分支安裝
gh extension install owner/extension-repo --branch develop

# 升級擴充功能
gh extension upgrade extension-name

# 移除擴充功能
gh extension remove extension-name

# 建立新擴充功能
gh extension create my-extension

# 瀏覽擴充功能
gh extension browse

# 執行擴充功能指令
gh extension exec my-extension --arg value
```

## 別名 (gh alias)

```bash
# 列出別名
gh alias list

# 設定別名
gh alias set prview 'pr view --web'

# 設定 Shell 別名
gh alias set co 'pr checkout' --shell

# 刪除別名
gh alias delete prview

# 匯入別名
gh alias import ./aliases.sh
```

## API 請求 (gh api)

```bash
# 發送 API 請求
gh api /user

# 搭配方法的請求
gh api --method POST /repos/owner/repo/issues \
  --field title="Issue title" \
  --field body="Issue body"

# 搭配標頭的請求
gh api /user \
  --header "Accept: application/vnd.github.v3+json"

# 搭配分頁的請求
gh api /user/repos --paginate

# 原始輸出（無格式化）
gh api /user --raw

# 在輸出中包含標頭
gh api /user --include

# 靜默模式（無進度輸出）
gh api /user --silent

# 從檔案輸入
gh api --input request.json

# 對回應執行 jq 查詢
gh api /user --jq '.login'

# 回應中的欄位
gh api /repos/owner/repo --jq '.stargazers_count'

# GitHub Enterprise
gh api /user --hostname enterprise.internal

# GraphQL 查詢
gh api graphql \
  -f query='
  {
    viewer {
      login
      repositories(first: 5) {
        nodes {
          name
        }
      }
    }
  }'
```

## 規則集 (gh ruleset)

```bash
# 列出規則集
gh ruleset list

# 檢視規則集
gh ruleset view 123

# 檢查規則集
gh ruleset check --branch feature

# 檢查特定存放庫
gh ruleset check --repo owner/repo --branch main
```

## 證明 (gh attestation)

```bash
# 下載證明
gh attestation download owner/repo \
  --artifact-id 123456

# 驗證證明
gh attestation verify owner/repo

# 取得受信任根憑證
gh attestation trusted-root
```

## 自動補全 (gh completion)

```bash
# 產生 Shell 自動補全
gh completion -s bash > ~/.gh-complete.bash
gh completion -s zsh > ~/.gh-complete.zsh
gh completion -s fish > ~/.gh-complete.fish
gh completion -s powershell > ~/.gh-complete.ps1

# Shell 特定說明
gh completion --shell=bash
gh completion --shell=zsh
```

## 預覽 (gh preview)

```bash
# 列出預覽功能
gh preview

# 執行預覽腳本
gh preview prompter
```

## 代理程式工作 (gh agent-task)

```bash
# 列出代理程式工作
gh agent-task list

# 檢視代理程式工作
gh agent-task view 123

# 建立代理程式工作
gh agent-task create --description "My task"
```

## 全域旗標

| 旗標                       | 說明                                 |
| -------------------------- | ------------------------------------ |
| `--help` / `-h`            | 顯示指令說明                          |
| `--version`                | 顯示 gh 版本                          |
| `--repo [HOST/]OWNER/REPO` | 選擇其他存放庫                        |
| `--hostname HOST`          | GitHub 主機名稱                       |
| `--jq EXPRESSION`          | 篩選 JSON 輸出                        |
| `--json FIELDS`            | 以指定欄位輸出 JSON                   |
| `--template STRING`        | 使用 Go 範本格式化 JSON               |
| `--web`                    | 在瀏覽器中開啟                        |
| `--paginate`               | 發出額外的 API 呼叫                   |
| `--verbose`                | 顯示詳細輸出                          |
| `--debug`                  | 顯示偵錯輸出                          |
| `--timeout SECONDS`        | 最大 API 請求持續時間                  |
| `--cache CACHE`            | 快取控制（default、force、bypass）     |

## 輸出格式化

### JSON 輸出

```bash
# 基本 JSON
gh repo view --json name,description

# 巢狀欄位
gh repo view --json owner,name --jq '.owner.login + "/" + .name'

# 陣列操作
gh pr list --json number,title --jq '.[] | select(.number > 100)'

# 複雜查詢
gh issue list --json number,title,labels \
  --jq '.[] | {number, title: .title, tags: [.labels[].name]}'
```

### 範本輸出

```bash
# 自訂範本
gh repo view \
  --template '{{.name}}: {{.description}}'

# 多行範本
gh pr view 123 \
  --template 'Title: {{.title}}
Author: {{.author.login}}
State: {{.state}}
'
```

## 常見工作流程

### 從議題建立 PR

```bash
# 從議題建立分支
gh issue develop 123 --branch feature/issue-123

# 進行變更、提交、推送
git add .
git commit -m "Fix issue #123"
git push

# 建立連結至議題的 PR
gh pr create --title "Fix #123" --body "Closes #123"
```

### 批次操作

```bash
# 關閉多個議題
gh issue list --search "label:stale" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh issue close {} --comment "Closing as stale"

# 為多個 PR 新增標籤
gh pr list --search "review:required" \
  --json number \
  --jq '.[].number' | \
  xargs -I {} gh pr edit {} --add-label needs-review
```

### 存放庫設定工作流程

```bash
# 建立具有初始設定的存放庫
gh repo create my-project --public \
  --description "My awesome project" \
  --clone \
  --gitignore python \
  --license mit

cd my-project

# 設定分支
git checkout -b develop
git push -u origin develop

# 建立標籤
gh label create bug --color "d73a4a" --description "Bug report"
gh label create enhancement --color "a2eeef" --description "Feature request"
gh label create documentation --color "0075ca" --description "Documentation"
```

### CI/CD 工作流程

```bash
# 執行工作流程並等待
RUN_ID=$(gh workflow run ci.yml --ref main --jq '.databaseId')

# 監看執行
gh run watch "$RUN_ID"

# 完成後下載成品
gh run download "$RUN_ID" --dir ./artifacts
```

### 分叉同步工作流程

```bash
# 分叉存放庫
gh repo fork original/repo --clone

cd repo

# 新增上游遠端
git remote add upstream https://github.com/original/repo.git

# 同步分叉
gh repo sync

# 或手動同步
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 環境設定

### Shell 整合

```bash
# 新增至 ~/.bashrc 或 ~/.zshrc
eval "$(gh completion -s bash)"  # 或 zsh/fish

# 建立實用的別名
alias gs='gh status'
alias gpr='gh pr view --web'
alias gir='gh issue view --web'
alias gco='gh pr checkout'
```

### Git 組態

```bash
# 使用 gh 作為認證輔助程式
gh auth setup-git

# 將 gh 設為存放庫操作的預設值
git config --global credential.helper 'gh !gh auth setup-git'

# 或手動設定
git config --global credential.helper github
```

## 最佳實務

1. **驗證**：在自動化中使用環境變數

   ```bash
   export GH_TOKEN=$(gh auth token)
   ```

2. **預設存放庫**：設定預設值以避免重複輸入

   ```bash
   gh repo set-default owner/repo
   ```

3. **JSON 解析**：使用 jq 進行複雜資料擷取

   ```bash
   gh pr list --json number,title --jq '.[] | select(.title | contains("fix"))'
   ```

4. **分頁**：對大量結果集使用 --paginate

   ```bash
   gh issue list --state all --paginate
   ```

5. **快取**：對經常存取的資料使用快取控制
   ```bash
   gh api /user --cache force
   ```

## 取得說明

```bash
# 一般說明
gh --help

# 指令說明
gh pr --help
gh issue create --help

# 說明主題
gh help formatting
gh help environment
gh help exit-codes
gh help accessibility
```

## 參考資料

- 官方手冊：https://cli.github.com/manual/
- GitHub 文件：https://docs.github.com/en/github-cli
- REST API：https://docs.github.com/en/rest
- GraphQL API：https://docs.github.com/en/graphql

````

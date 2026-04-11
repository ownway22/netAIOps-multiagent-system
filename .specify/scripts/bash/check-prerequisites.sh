#!/usr/bin/env bash

# 整合式先決條件檢查腳本
#
# 此腳本為規格驅動開發 (Spec-Driven Development) 工作流程提供統一的先決條件檢查。
# 它取代了先前分散在多個腳本中的功能。
#
# 用法：./check-prerequisites.sh [選項]
#
# 選項：
#   --json              以 JSON 格式輸出
#   --require-tasks     要求 tasks.md 必須存在（用於實作階段）
#   --include-tasks     在 AVAILABLE_DOCS 列表中包含 tasks.md
#   --paths-only        僅輸出路徑變數（不進行驗證）
#   --help, -h          顯示說明訊息
#
# 輸出：
#   JSON 模式：{"FEATURE_DIR":"...", "AVAILABLE_DOCS":["..."]}
#   文字模式：FEATURE_DIR:... \n AVAILABLE_DOCS: \n ✓/✗ file.md
#   僅路徑：REPO_ROOT: ... \n BRANCH: ... \n FEATURE_DIR: ... 等

set -e

# 解析命令列參數
JSON_MODE=false
REQUIRE_TASKS=false
INCLUDE_TASKS=false
PATHS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --require-tasks)
            REQUIRE_TASKS=true
            ;;
        --include-tasks)
            INCLUDE_TASKS=true
            ;;
        --paths-only)
            PATHS_ONLY=true
            ;;
        --help|-h)
            cat << 'EOF'
用法：check-prerequisites.sh [選項]

規格驅動開發 (Spec-Driven Development) 工作流程的整合式先決條件檢查。

選項：
  --json              以 JSON 格式輸出
  --require-tasks     要求 tasks.md 必須存在（用於實作階段）
  --include-tasks     在 AVAILABLE_DOCS 列表中包含 tasks.md
  --paths-only        僅輸出路徑變數（不進行先決條件驗證）
  --help, -h          顯示此說明訊息

範例：
  # 檢查任務先決條件（需要 plan.md）
  ./check-prerequisites.sh --json
  
  # 檢查實作先決條件（需要 plan.md + tasks.md）
  ./check-prerequisites.sh --json --require-tasks --include-tasks
  
  # 僅取得功能路徑（不進行驗證）
  ./check-prerequisites.sh --paths-only
  
EOF
            exit 0
            ;;
        *)
            echo "錯誤：未知選項 '$arg'。使用 --help 查看用法資訊。" >&2
            exit 1
            ;;
    esac
done

# 載入共用函式
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 取得功能路徑並驗證分支
eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# 如果是僅路徑模式，輸出路徑並結束（支援 JSON + paths-only 組合）
if $PATHS_ONLY; then
    if $JSON_MODE; then
        # 最小化 JSON 路徑負載（不執行驗證）
        printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","IMPL_PLAN":"%s","TASKS":"%s"}\n' \
            "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_DIR" "$FEATURE_SPEC" "$IMPL_PLAN" "$TASKS"
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_DIR: $FEATURE_DIR"
        echo "FEATURE_SPEC: $FEATURE_SPEC"
        echo "IMPL_PLAN: $IMPL_PLAN"
        echo "TASKS: $TASKS"
    fi
    exit 0
fi

# 驗證必要的目錄和檔案
if [[ ! -d "$FEATURE_DIR" ]]; then
    echo "錯誤：找不到功能目錄：$FEATURE_DIR" >&2
    echo "請先執行 /speckit.specify 以建立功能結構。" >&2
    exit 1
fi

if [[ ! -f "$IMPL_PLAN" ]]; then
    echo "錯誤：在 $FEATURE_DIR 中找不到 plan.md" >&2
    echo "請先執行 /speckit.plan 以建立實作計畫。" >&2
    exit 1
fi

# 如果需要則檢查 tasks.md
if $REQUIRE_TASKS && [[ ! -f "$TASKS" ]]; then
    echo "錯誤：在 $FEATURE_DIR 中找不到 tasks.md" >&2
    echo "請先執行 /speckit.tasks 以建立任務清單。" >&2
    exit 1
fi

# 建立可用文件列表
docs=()

# 始終檢查這些選用文件
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")

# 檢查契約目錄（僅當它存在且有檔案時）
if [[ -d "$CONTRACTS_DIR" ]] && [[ -n "$(ls -A "$CONTRACTS_DIR" 2>/dev/null)" ]]; then
    docs+=("contracts/")
fi

[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")

# 如果要求且存在則包含 tasks.md
if $INCLUDE_TASKS && [[ -f "$TASKS" ]]; then
    docs+=("tasks.md")
fi

# 輸出結果
if $JSON_MODE; then
    # 建立文件的 JSON 陣列
    if [[ ${#docs[@]} -eq 0 ]]; then
        json_docs="[]"
    else
        json_docs=$(printf '"%s",' "${docs[@]}")
        json_docs="[${json_docs%,}]"
    fi
    
    printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":%s}\n' "$FEATURE_DIR" "$json_docs"
else
    # 文字輸出
    echo "FEATURE_DIR:$FEATURE_DIR"
    echo "AVAILABLE_DOCS:"
    
    # 顯示每個潛在文件的狀態
    check_file "$RESEARCH" "research.md"
    check_file "$DATA_MODEL" "data-model.md"
    check_dir "$CONTRACTS_DIR" "contracts/"
    check_file "$QUICKSTART" "quickstart.md"
    
    if $INCLUDE_TASKS; then
        check_file "$TASKS" "tasks.md"
    fi
fi

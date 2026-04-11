#!/usr/bin/env bash
# 所有腳本的共用函式和變數

# 取得儲存庫根目錄，對於非 Git 儲存庫有備用方案
get_repo_root() {
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
    else
        # 對於非 Git 儲存庫，回退到腳本位置
        local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../../.." && pwd)
    fi
}

# 取得目前分支，對於非 Git 儲存庫有備用方案
get_current_branch() {
    # 首先檢查是否設定了 SPECIFY_FEATURE 環境變數
    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        echo "$SPECIFY_FEATURE"
        return
    fi

    # 然後檢查 git（如果可用）
    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
        git rev-parse --abbrev-ref HEAD
        return
    fi

    # 對於非 Git 儲存庫，嘗試尋找最新的功能目錄
    local repo_root=$(get_repo_root)
    local specs_dir="$repo_root/specs"

    if [[ -d "$specs_dir" ]]; then
        local latest_feature=""
        local highest=0

        for dir in "$specs_dir"/*; do
            if [[ -d "$dir" ]]; then
                local dirname=$(basename "$dir")
                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then
                    local number=${BASH_REMATCH[1]}
                    number=$((10#$number))
                    if [[ "$number" -gt "$highest" ]]; then
                        highest=$number
                        latest_feature=$dirname
                    fi
                fi
            fi
        done

        if [[ -n "$latest_feature" ]]; then
            echo "$latest_feature"
            return
        fi
    fi

    echo "main"  # 最終備用方案
}

# 檢查是否有 git 可用
has_git() {
    git rev-parse --show-toplevel >/dev/null 2>&1
}

check_feature_branch() {
    local branch="$1"
    local has_git_repo="$2"

    # 對於非 Git 儲存庫，我們無法強制分支命名，但仍提供輸出
    if [[ "$has_git_repo" != "true" ]]; then
        echo "[specify] 警告：未偵測到 Git 儲存庫；已跳過分支驗證" >&2
        return 0
    fi

    if [[ ! "$branch" =~ ^[0-9]{3}- ]]; then
        echo "錯誤：不在功能分支上。目前分支：$branch" >&2
        echo "功能分支應命名為：001-feature-name" >&2
        return 1
    fi

    return 0
}

get_feature_dir() { echo "$1/specs/$2"; }

# 透過數字前綴尋找功能目錄，而非精確分支匹配
# 這允許多個分支在同一規格上工作（例如 004-fix-bug、004-add-feature）
find_feature_dir_by_prefix() {
    local repo_root="$1"
    local branch_name="$2"
    local specs_dir="$repo_root/specs"

    # 從分支擷取數字前綴（例如從「004-whatever」擷取「004」）
    if [[ ! "$branch_name" =~ ^([0-9]{3})- ]]; then
        # 如果分支沒有數字前綴，回退到精確匹配
        echo "$specs_dir/$branch_name"
        return
    fi

    local prefix="${BASH_REMATCH[1]}"

    # 在 specs/ 目錄中搜尋以此前綴開頭的目錄
    local matches=()
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/"$prefix"-*; do
            if [[ -d "$dir" ]]; then
                matches+=("$(basename "$dir")")
            fi
        done
    fi

    # 處理結果
    if [[ ${#matches[@]} -eq 0 ]]; then
        # 未找到匹配 - 回傳分支名稱路徑（稍後會顯示明確錯誤）
        echo "$specs_dir/$branch_name"
    elif [[ ${#matches[@]} -eq 1 ]]; then
        # 恰好一個匹配 - 完美！
        echo "$specs_dir/${matches[0]}"
    else
        # 多個匹配 - 使用正確的命名規範不應發生此情況
        echo "錯誤：找到多個具有前綴 '$prefix' 的規格目錄：${matches[*]}" >&2
        echo "請確保每個數字前綴只存在一個規格目錄。" >&2
        echo "$specs_dir/$branch_name"  # 回傳某些值以避免中斷腳本
    fi
}

get_feature_paths() {
    local repo_root=$(get_repo_root)
    local current_branch=$(get_current_branch)
    local has_git_repo="false"

    if has_git; then
        has_git_repo="true"
    fi

    # 使用前綴查詢以支援每個規格多個分支
    local feature_dir=$(find_feature_dir_by_prefix "$repo_root" "$current_branch")

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$current_branch'
HAS_GIT='$has_git_repo'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/spec.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
RESEARCH='$feature_dir/research.md'
DATA_MODEL='$feature_dir/data-model.md'
QUICKSTART='$feature_dir/quickstart.md'
CONTRACTS_DIR='$feature_dir/contracts'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }


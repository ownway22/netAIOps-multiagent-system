#!/usr/bin/env bash

set -e

JSON_MODE=false
SHORT_NAME=""
BRANCH_NUMBER=""
ARGS=()
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --json) 
            JSON_MODE=true 
            ;;
        --short-name)
            if [ $((i + 1)) -gt $# ]; then
                echo '錯誤：--short-name 需要一個值' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            # 檢查下一個參數是否為另一個選項（以 -- 開頭）
            if [[ "$next_arg" == --* ]]; then
                echo '錯誤：--short-name 需要一個值' >&2
                exit 1
            fi
            SHORT_NAME="$next_arg"
            ;;
        --number)
            if [ $((i + 1)) -gt $# ]; then
                echo '錯誤：--number 需要一個值' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            if [[ "$next_arg" == --* ]]; then
                echo '錯誤：--number 需要一個值' >&2
                exit 1
            fi
            BRANCH_NUMBER="$next_arg"
            ;;
        --help|-h) 
            echo "用法：$0 [--json] [--short-name <名稱>] [--number N] <功能描述>"
            echo ""
            echo "選項："
            echo "  --json              以 JSON 格式輸出"
            echo "  --short-name <名稱> 提供自訂短名稱（2-4 個單詞）用於分支"
            echo "  --number N          手動指定分支編號（覆蓋自動偵測）"
            echo "  --help, -h          顯示此說明訊息"
            echo ""
            echo "範例："
            echo "  $0 'Add user authentication system' --short-name 'user-auth'"
            echo "  $0 'Implement OAuth2 integration for API' --number 5"
            exit 0
            ;;
        *) 
            ARGS+=("$arg") 
            ;;
    esac
    i=$((i + 1))
done

FEATURE_DESCRIPTION="${ARGS[*]}"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "用法：$0 [--json] [--short-name <名稱>] [--number N] <功能描述>" >&2
    exit 1
fi

# 透過搜尋現有專案標記來尋找儲存庫根目錄的函式
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# 從 specs 目錄取得最高編號的函式
get_highest_from_specs() {
    local specs_dir="$1"
    local highest=0
    
    if [ -d "$specs_dir" ]; then
        for dir in "$specs_dir"/*; do
            [ -d "$dir" ] || continue
            dirname=$(basename "$dir")
            number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
            number=$((10#$number))
            if [ "$number" -gt "$highest" ]; then
                highest=$number
            fi
        done
    fi
    
    echo "$highest"
}

# 從 Git 分支取得最高編號的函式
get_highest_from_branches() {
    local highest=0
    
    # 取得所有分支（本地和遠端）
    branches=$(git branch -a 2>/dev/null || echo "")
    
    if [ -n "$branches" ]; then
        while IFS= read -r branch; do
            # 清理分支名稱：移除前導標記和遠端前綴
            clean_branch=$(echo "$branch" | sed 's/^[* ]*//; s|^remotes/[^/]*/||')
            
            # 如果分支符合 ###-* 模式，擷取功能編號
            if echo "$clean_branch" | grep -q '^[0-9]\{3\}-'; then
                number=$(echo "$clean_branch" | grep -o '^[0-9]\{3\}' || echo "0")
                number=$((10#$number))
                if [ "$number" -gt "$highest" ]; then
                    highest=$number
                fi
            fi
        done <<< "$branches"
    fi
    
    echo "$highest"
}

# 檢查現有分支（本地和遠端）並回傳下一個可用編號的函式
check_existing_branches() {
    local specs_dir="$1"

    # 擷取所有遠端以取得最新分支資訊（如果沒有遠端則抑制錯誤）
    git fetch --all --prune 2>/dev/null || true

    # 從所有分支（不僅是匹配短名稱的分支）取得最高編號
    local highest_branch=$(get_highest_from_branches)

    # 從所有規格（不僅是匹配短名稱的規格）取得最高編號
    local highest_spec=$(get_highest_from_specs "$specs_dir")

    # 取兩者的最大值
    local max_num=$highest_branch
    if [ "$highest_spec" -gt "$max_num" ]; then
        max_num=$highest_spec
    fi

    # 回傳下一個編號
    echo $((max_num + 1))
}

# 清理和格式化分支名稱的函式
clean_branch_name() {
    local name="$1"
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//'
}

# 解析儲存庫根目錄。優先使用 Git 資訊，但回退到
# 搜尋儲存庫標記，以便工作流程在使用 --no-git 初始化的儲存庫中仍能運作。
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
    HAS_GIT=true
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        echo "錯誤：無法判斷儲存庫根目錄。請從儲存庫內執行此腳本。" >&2
        exit 1
    fi
    HAS_GIT=false
fi

cd "$REPO_ROOT"

SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

# 使用停用詞過濾和長度過濾產生分支名稱的函式
generate_branch_name() {
    local description="$1"
    
    # 要過濾掉的常見停用詞
    local stop_words="^(i|a|an|the|to|for|of|in|on|at|by|with|from|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might|must|shall|this|that|these|those|my|your|our|their|want|need|add|get|set)$"
    
    # 轉換為小寫並分割成單詞
    local clean_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/ /g')
    
    # 過濾單詞：移除停用詞和短於 3 個字元的單詞（除非它們在原文中是大寫縮寫）
    local meaningful_words=()
    for word in $clean_name; do
        # 跳過空單詞
        [ -z "$word" ] && continue
        
        # 保留非停用詞且（長度 >= 3 或為潛在縮寫）的單詞
        if ! echo "$word" | grep -qiE "$stop_words"; then
            if [ ${#word} -ge 3 ]; then
                meaningful_words+=("$word")
            elif echo "$description" | grep -q "\b${word^^}\b"; then
                # 如果短單詞在原文中以大寫出現則保留（可能是縮寫）
                meaningful_words+=("$word")
            fi
        fi
    done
    
    # 如果有有意義的單詞，使用前 3-4 個
    if [ ${#meaningful_words[@]} -gt 0 ]; then
        local max_words=3
        if [ ${#meaningful_words[@]} -eq 4 ]; then max_words=4; fi
        
        local result=""
        local count=0
        for word in "${meaningful_words[@]}"; do
            if [ $count -ge $max_words ]; then break; fi
            if [ -n "$result" ]; then result="$result-"; fi
            result="$result$word"
            count=$((count + 1))
        done
        echo "$result"
    else
        # 如果未找到有意義的單詞，回退到原始邏輯
        local cleaned=$(clean_branch_name "$description")
        echo "$cleaned" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//'
    fi
}

# 產生分支名稱
if [ -n "$SHORT_NAME" ]; then
    # 使用提供的短名稱，只進行清理
    BRANCH_SUFFIX=$(clean_branch_name "$SHORT_NAME")
else
    # 使用智慧過濾從描述產生
    BRANCH_SUFFIX=$(generate_branch_name "$FEATURE_DESCRIPTION")
fi

# 決定分支編號
if [ -z "$BRANCH_NUMBER" ]; then
    if [ "$HAS_GIT" = true ]; then
        # 檢查遠端的現有分支
        BRANCH_NUMBER=$(check_existing_branches "$SPECS_DIR")
    else
        # 回退到本地目錄檢查
        HIGHEST=$(get_highest_from_specs "$SPECS_DIR")
        BRANCH_NUMBER=$((HIGHEST + 1))
    fi
fi

# 強制以 10 進位解讀以防止八進位轉換（例如 010 → 八進位為 8，但應為十進位 10）
FEATURE_NUM=$(printf "%03d" "$((10#$BRANCH_NUMBER))")
BRANCH_NAME="${FEATURE_NUM}-${BRANCH_SUFFIX}"

# GitHub 強制分支名稱的 244 位元組限制
# 必要時驗證並截斷
MAX_BRANCH_LENGTH=244
if [ ${#BRANCH_NAME} -gt $MAX_BRANCH_LENGTH ]; then
    # 計算需要從後綴截斷多少
    # 考慮：功能編號 (3) + 連字符 (1) = 4 個字元
    MAX_SUFFIX_LENGTH=$((MAX_BRANCH_LENGTH - 4))
    
    # 如果可能，在單詞邊界截斷後綴
    TRUNCATED_SUFFIX=$(echo "$BRANCH_SUFFIX" | cut -c1-$MAX_SUFFIX_LENGTH)
    # 如果截斷產生尾隨連字符則移除
    TRUNCATED_SUFFIX=$(echo "$TRUNCATED_SUFFIX" | sed 's/-$//')
    
    ORIGINAL_BRANCH_NAME="$BRANCH_NAME"
    BRANCH_NAME="${FEATURE_NUM}-${TRUNCATED_SUFFIX}"
    
    >&2 echo "[specify] 警告：分支名稱超過 GitHub 的 244 位元組限制"
    >&2 echo "[specify] 原始：$ORIGINAL_BRANCH_NAME (${#ORIGINAL_BRANCH_NAME} 位元組)"
    >&2 echo "[specify] 已截斷為：$BRANCH_NAME (${#BRANCH_NAME} 位元組)"
fi

if [ "$HAS_GIT" = true ]; then
    git checkout -b "$BRANCH_NAME"
else
    >&2 echo "[specify] 警告：未偵測到 Git 儲存庫；已跳過 $BRANCH_NAME 的分支建立"
fi

FEATURE_DIR="$SPECS_DIR/$BRANCH_NAME"
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/.specify/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then cp "$TEMPLATE" "$SPEC_FILE"; else touch "$SPEC_FILE"; fi

# 為目前工作階段設定 SPECIFY_FEATURE 環境變數
export SPECIFY_FEATURE="$BRANCH_NAME"

if $JSON_MODE; then
    printf '{"BRANCH_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s"}\n' "$BRANCH_NAME" "$SPEC_FILE" "$FEATURE_NUM"
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "SPECIFY_FEATURE 環境變數已設定為：$BRANCH_NAME"
fi

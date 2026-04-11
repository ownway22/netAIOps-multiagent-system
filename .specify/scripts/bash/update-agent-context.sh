#!/usr/bin/env bash

# 使用 plan.md 的資訊更新代理程式上下文檔案
#
# 此腳本透過解析功能規格並使用專案資訊更新代理程式特定設定檔來維護 AI 代理程式上下文檔案。
#
# 主要功能：
# 1. 環境驗證
#    - 驗證 Git 儲存庫結構和分支資訊
#    - 檢查必要的 plan.md 檔案和範本
#    - 驗證檔案權限和可存取性
#
# 2. 計畫資料擷取
#    - 解析 plan.md 檔案以擷取專案中繼資料
#    - 識別語言/版本、框架、資料庫和專案類型
#    - 優雅處理遺失或不完整的規格資料
#
# 3. 代理程式檔案管理
#    - 需要時從範本建立新的代理程式上下文檔案
#    - 使用新的專案資訊更新現有代理程式檔案
#    - 保留手動新增和自訂設定
#    - 支援多種 AI 代理程式格式和目錄結構
#
# 4. 內容產生
#    - 產生語言特定的建置/測試命令
#    - 建立適當的專案目錄結構
#    - 更新技術堆疊和近期變更區段
#    - 維持一致的格式和時間戳記
#
# 5. 多代理程式支援
#    - 處理代理程式特定的檔案路徑和命名慣例
#    - 支援：Claude、Gemini、Copilot、Cursor、Qwen、opencode、Codex、Windsurf、Kilo Code、Auggie CLI、Roo Code、CodeBuddy CLI、Qoder CLI、Amp、SHAI 或 Amazon Q Developer CLI
#    - 可更新單一代理程式或所有現有代理程式檔案
#    - 如果沒有代理程式檔案存在，則建立預設 Claude 檔案
#
# 用法：./update-agent-context.sh [代理程式類型]
# 代理程式類型：claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|shai|q|bob|qoder
# 留空以更新所有現有代理程式檔案

set -e

# 啟用嚴格錯誤處理
set -u
set -o pipefail

#==============================================================================
# 設定和全域變數
#==============================================================================

# 取得腳本目錄並載入共用函式
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 從共用函式取得所有路徑和變數
eval $(get_feature_paths)

NEW_PLAN="$IMPL_PLAN"  # 與現有程式碼相容的別名
AGENT_TYPE="${1:-}"

# 代理程式特定檔案路徑
CLAUDE_FILE="$REPO_ROOT/CLAUDE.md"
GEMINI_FILE="$REPO_ROOT/GEMINI.md"
COPILOT_FILE="$REPO_ROOT/.github/agents/copilot-instructions.md"
CURSOR_FILE="$REPO_ROOT/.cursor/rules/specify-rules.mdc"
QWEN_FILE="$REPO_ROOT/QWEN.md"
AGENTS_FILE="$REPO_ROOT/AGENTS.md"
WINDSURF_FILE="$REPO_ROOT/.windsurf/rules/specify-rules.md"
KILOCODE_FILE="$REPO_ROOT/.kilocode/rules/specify-rules.md"
AUGGIE_FILE="$REPO_ROOT/.augment/rules/specify-rules.md"
ROO_FILE="$REPO_ROOT/.roo/rules/specify-rules.md"
CODEBUDDY_FILE="$REPO_ROOT/CODEBUDDY.md"
QODER_FILE="$REPO_ROOT/QODER.md"
AMP_FILE="$REPO_ROOT/AGENTS.md"
SHAI_FILE="$REPO_ROOT/SHAI.md"
Q_FILE="$REPO_ROOT/AGENTS.md"
BOB_FILE="$REPO_ROOT/AGENTS.md"

# 範本檔案
TEMPLATE_FILE="$REPO_ROOT/.specify/templates/agent-file-template.md"

# 解析計畫資料的全域變數
NEW_LANG=""
NEW_FRAMEWORK=""
NEW_DB=""
NEW_PROJECT_TYPE=""

#==============================================================================
# 工具函式
#==============================================================================

log_info() {
    echo "資訊：$1"
}

log_success() {
    echo "✓ $1"
}

log_error() {
    echo "錯誤：$1" >&2
}

log_warning() {
    echo "警告：$1" >&2
}

# 暫存檔案的清理函式
cleanup() {
    local exit_code=$?
    rm -f /tmp/agent_update_*_$$
    rm -f /tmp/manual_additions_$$
    exit $exit_code
}

# 設定清理陷阱
trap cleanup EXIT INT TERM

#==============================================================================
# 驗證函式
#==============================================================================

validate_environment() {
    # 檢查是否有目前分支/功能（Git 或非 Git）
    if [[ -z "$CURRENT_BRANCH" ]]; then
        log_error "無法判斷目前功能"
        if [[ "$HAS_GIT" == "true" ]]; then
            log_info "請確保您在功能分支上"
        else
            log_info "請設定 SPECIFY_FEATURE 環境變數或先建立功能"
        fi
        exit 1
    fi
    
    # 檢查 plan.md 是否存在
    if [[ ! -f "$NEW_PLAN" ]]; then
        log_error "在 $NEW_PLAN 找不到 plan.md"
        log_info "請確保您正在處理具有對應規格目錄的功能"
        if [[ "$HAS_GIT" != "true" ]]; then
            log_info "使用：export SPECIFY_FEATURE=your-feature-name 或先建立新功能"
        fi
        exit 1
    fi
    
    # 檢查範本是否存在（建立新檔案時需要）
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_warning "在 $TEMPLATE_FILE 找不到範本檔案"
        log_warning "建立新代理程式檔案將會失敗"
    fi
}

#==============================================================================
# 計畫解析函式
#==============================================================================

extract_plan_field() {
    local field_pattern="$1"
    local plan_file="$2"
    
    grep "^\*\*${field_pattern}\*\*: " "$plan_file" 2>/dev/null | \
        head -1 | \
        sed "s|^\*\*${field_pattern}\*\*: ||" | \
        sed 's/^[ \t]*//;s/[ \t]*$//' | \
        grep -v "NEEDS CLARIFICATION" | \
        grep -v "^N/A$" || echo ""
}

parse_plan_data() {
    local plan_file="$1"
    
    if [[ ! -f "$plan_file" ]]; then
        log_error "找不到計畫檔案：$plan_file"
        return 1
    fi
    
    if [[ ! -r "$plan_file" ]]; then
        log_error "計畫檔案不可讀取：$plan_file"
        return 1
    fi
    
    log_info "從 $plan_file 解析計畫資料"
    
    NEW_LANG=$(extract_plan_field "Language/Version" "$plan_file")
    NEW_FRAMEWORK=$(extract_plan_field "Primary Dependencies" "$plan_file")
    NEW_DB=$(extract_plan_field "Storage" "$plan_file")
    NEW_PROJECT_TYPE=$(extract_plan_field "Project Type" "$plan_file")
    
    # 記錄找到的內容
    if [[ -n "$NEW_LANG" ]]; then
        log_info "找到語言：$NEW_LANG"
    else
        log_warning "計畫中未找到語言資訊"
    fi
    
    if [[ -n "$NEW_FRAMEWORK" ]]; then
        log_info "找到框架：$NEW_FRAMEWORK"
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]]; then
        log_info "找到資料庫：$NEW_DB"
    fi
    
    if [[ -n "$NEW_PROJECT_TYPE" ]]; then
        log_info "找到專案類型：$NEW_PROJECT_TYPE"
    fi
}

format_technology_stack() {
    local lang="$1"
    local framework="$2"
    local parts=()
    
    # 新增非空部分
    [[ -n "$lang" && "$lang" != "NEEDS CLARIFICATION" ]] && parts+=("$lang")
    [[ -n "$framework" && "$framework" != "NEEDS CLARIFICATION" && "$framework" != "N/A" ]] && parts+=("$framework")
    
    # 以正確格式連接
    if [[ ${#parts[@]} -eq 0 ]]; then
        echo ""
    elif [[ ${#parts[@]} -eq 1 ]]; then
        echo "${parts[0]}"
    else
        # 以 " + " 連接多個部分
        local result="${parts[0]}"
        for ((i=1; i<${#parts[@]}; i++)); do
            result="$result + ${parts[i]}"
        done
        echo "$result"
    fi
}

#==============================================================================
# 範本和內容產生函式
#==============================================================================

get_project_structure() {
    local project_type="$1"
    
    if [[ "$project_type" == *"web"* ]]; then
        echo "backend/\\nfrontend/\\ntests/"
    else
        echo "src/\\ntests/"
    fi
}

get_commands_for_language() {
    local lang="$1"
    
    case "$lang" in
        *"Python"*)
            echo "cd src && pytest && ruff check ."
            ;;
        *"Rust"*)
            echo "cargo test && cargo clippy"
            ;;
        *"JavaScript"*|*"TypeScript"*)
            echo "npm test \\&\\& npm run lint"
            ;;
        *)
            echo "# 新增 $lang 的命令"
            ;;
    esac
}

get_language_conventions() {
    local lang="$1"
    echo "$lang: 遵循標準慣例"
}

create_new_agent_file() {
    local target_file="$1"
    local temp_file="$2"
    local project_name="$3"
    local current_date="$4"
    
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_error "在 $TEMPLATE_FILE 找不到範本"
        return 1
    fi
    
    if [[ ! -r "$TEMPLATE_FILE" ]]; then
        log_error "範本檔案不可讀取：$TEMPLATE_FILE"
        return 1
    fi
    
    log_info "從範本建立新代理程式上下文檔案..."
    
    if ! cp "$TEMPLATE_FILE" "$temp_file"; then
        log_error "複製範本檔案失敗"
        return 1
    fi
    
    # 取代範本佔位符
    local project_structure
    project_structure=$(get_project_structure "$NEW_PROJECT_TYPE")
    
    local commands
    commands=$(get_commands_for_language "$NEW_LANG")
    
    local language_conventions
    language_conventions=$(get_language_conventions "$NEW_LANG")
    
    # 使用更安全的方式進行替換並檢查錯誤
    # 透過使用不同分隔符或跳脫來跳脫 sed 的特殊字元
    local escaped_lang=$(printf '%s\n' "$NEW_LANG" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    local escaped_framework=$(printf '%s\n' "$NEW_FRAMEWORK" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    local escaped_branch=$(printf '%s\n' "$CURRENT_BRANCH" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    
    # 條件式建立技術堆疊和近期變更字串
    local tech_stack
    if [[ -n "$escaped_lang" && -n "$escaped_framework" ]]; then
        tech_stack="- $escaped_lang + $escaped_framework ($escaped_branch)"
    elif [[ -n "$escaped_lang" ]]; then
        tech_stack="- $escaped_lang ($escaped_branch)"
    elif [[ -n "$escaped_framework" ]]; then
        tech_stack="- $escaped_framework ($escaped_branch)"
    else
        tech_stack="- ($escaped_branch)"
    fi

    local recent_change
    if [[ -n "$escaped_lang" && -n "$escaped_framework" ]]; then
        recent_change="- $escaped_branch: Added $escaped_lang + $escaped_framework"
    elif [[ -n "$escaped_lang" ]]; then
        recent_change="- $escaped_branch: Added $escaped_lang"
    elif [[ -n "$escaped_framework" ]]; then
        recent_change="- $escaped_branch: Added $escaped_framework"
    else
        recent_change="- $escaped_branch: Added"
    fi

    local substitutions=(
        "s|\[PROJECT NAME\]|$project_name|"
        "s|\[DATE\]|$current_date|"
        "s|\[EXTRACTED FROM ALL PLAN.MD FILES\]|$tech_stack|"
        "s|\[ACTUAL STRUCTURE FROM PLANS\]|$project_structure|g"
        "s|\[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES\]|$commands|"
        "s|\[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE\]|$language_conventions|"
        "s|\[LAST 3 FEATURES AND WHAT THEY ADDED\]|$recent_change|"
    )
    
    for substitution in "${substitutions[@]}"; do
        if ! sed -i.bak -e "$substitution" "$temp_file"; then
            log_error "執行替換失敗：$substitution"
            rm -f "$temp_file" "$temp_file.bak"
            return 1
        fi
    done
    
    # 將 \n 序列轉換為實際換行
    newline=$(printf '\n')
    sed -i.bak2 "s/\\\\n/${newline}/g" "$temp_file"
    
    # 清理備份檔案
    rm -f "$temp_file.bak" "$temp_file.bak2"
    
    return 0
}




update_existing_agent_file() {
    local target_file="$1"
    local current_date="$2"
    
    log_info "更新現有代理程式上下文檔案..."
    
    # 使用單一暫存檔案進行原子更新
    local temp_file
    temp_file=$(mktemp) || {
        log_error "建立暫存檔案失敗"
        return 1
    }
    
    # 單次處理檔案
    local tech_stack=$(format_technology_stack "$NEW_LANG" "$NEW_FRAMEWORK")
    local new_tech_entries=()
    local new_change_entry=""
    
    # 準備新技術項目
    if [[ -n "$tech_stack" ]] && ! grep -q "$tech_stack" "$target_file"; then
        new_tech_entries+=("- $tech_stack ($CURRENT_BRANCH)")
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]] && [[ "$NEW_DB" != "NEEDS CLARIFICATION" ]] && ! grep -q "$NEW_DB" "$target_file"; then
        new_tech_entries+=("- $NEW_DB ($CURRENT_BRANCH)")
    fi
    
    # 準備新變更項目
    if [[ -n "$tech_stack" ]]; then
        new_change_entry="- $CURRENT_BRANCH: Added $tech_stack"
    elif [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]] && [[ "$NEW_DB" != "NEEDS CLARIFICATION" ]]; then
        new_change_entry="- $CURRENT_BRANCH: Added $NEW_DB"
    fi
    
    # 檢查檔案中是否存在各區段
    local has_active_technologies=0
    local has_recent_changes=0
    
    if grep -q "^## Active Technologies" "$target_file" 2>/dev/null; then
        has_active_technologies=1
    fi
    
    if grep -q "^## Recent Changes" "$target_file" 2>/dev/null; then
        has_recent_changes=1
    fi
    
    # 逐行處理檔案
    local in_tech_section=false
    local in_changes_section=false
    local tech_entries_added=false
    local changes_entries_added=false
    local existing_changes_count=0
    local file_ended=false
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        # 處理 Active Technologies 區段
        if [[ "$line" == "## Active Technologies" ]]; then
            echo "$line" >> "$temp_file"
            in_tech_section=true
            continue
        elif [[ $in_tech_section == true ]] && [[ "$line" =~ ^##[[:space:]] ]]; then
            # 在關閉區段前新增新技術項目
            if [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
                printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
                tech_entries_added=true
            fi
            echo "$line" >> "$temp_file"
            in_tech_section=false
            continue
        elif [[ $in_tech_section == true ]] && [[ -z "$line" ]]; then
            # 在技術區段的空行前新增新技術項目
            if [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
                printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
                tech_entries_added=true
            fi
            echo "$line" >> "$temp_file"
            continue
        fi
        
        # 處理 Recent Changes 區段
        if [[ "$line" == "## Recent Changes" ]]; then
            echo "$line" >> "$temp_file"
            # 在標題後立即新增新變更項目
            if [[ -n "$new_change_entry" ]]; then
                echo "$new_change_entry" >> "$temp_file"
            fi
            in_changes_section=true
            changes_entries_added=true
            continue
        elif [[ $in_changes_section == true ]] && [[ "$line" =~ ^##[[:space:]] ]]; then
            echo "$line" >> "$temp_file"
            in_changes_section=false
            continue
        elif [[ $in_changes_section == true ]] && [[ "$line" == "- "* ]]; then
            # 僅保留前 2 個現有變更
            if [[ $existing_changes_count -lt 2 ]]; then
                echo "$line" >> "$temp_file"
                ((existing_changes_count++))
            fi
            continue
        fi
        
        # 更新時間戳記
        if [[ "$line" =~ \*\*Last\ updated\*\*:.*[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] ]]; then
            echo "$line" | sed "s/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/$current_date/" >> "$temp_file"
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$target_file"
    
    # 迴圈後檢查：如果仍在 Active Technologies 區段且尚未新增新項目
    if [[ $in_tech_section == true ]] && [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
        printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
        tech_entries_added=true
    fi
    
    # 如果區段不存在，在檔案末尾新增
    if [[ $has_active_technologies -eq 0 ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
        echo "" >> "$temp_file"
        echo "## Active Technologies" >> "$temp_file"
        printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
        tech_entries_added=true
    fi
    
    if [[ $has_recent_changes -eq 0 ]] && [[ -n "$new_change_entry" ]]; then
        echo "" >> "$temp_file"
        echo "## Recent Changes" >> "$temp_file"
        echo "$new_change_entry" >> "$temp_file"
        changes_entries_added=true
    fi
    
    # 將暫存檔案原子移動到目標位置
    if ! mv "$temp_file" "$target_file"; then
        log_error "更新目標檔案失敗"
        rm -f "$temp_file"
        return 1
    fi
    
    return 0
}
#==============================================================================
# 主要代理程式檔案更新函式
#==============================================================================

update_agent_file() {
    local target_file="$1"
    local agent_name="$2"
    
    if [[ -z "$target_file" ]] || [[ -z "$agent_name" ]]; then
        log_error "update_agent_file 需要 target_file 和 agent_name 參數"
        return 1
    fi
    
    log_info "更新 $agent_name 上下文檔案：$target_file"
    
    local project_name
    project_name=$(basename "$REPO_ROOT")
    local current_date
    current_date=$(date +%Y-%m-%d)
    
    # 如果目錄不存在則建立
    local target_dir
    target_dir=$(dirname "$target_file")
    if [[ ! -d "$target_dir" ]]; then
        if ! mkdir -p "$target_dir"; then
            log_error "建立目錄失敗：$target_dir"
            return 1
        fi
    fi
    
    if [[ ! -f "$target_file" ]]; then
        # 從範本建立新檔案
        local temp_file
        temp_file=$(mktemp) || {
            log_error "建立暫存檔案失敗"
            return 1
        }
        
        if create_new_agent_file "$target_file" "$temp_file" "$project_name" "$current_date"; then
            if mv "$temp_file" "$target_file"; then
                log_success "已建立新的 $agent_name 上下文檔案"
            else
                log_error "移動暫存檔案到 $target_file 失敗"
                rm -f "$temp_file"
                return 1
            fi
        else
            log_error "建立新代理程式檔案失敗"
            rm -f "$temp_file"
            return 1
        fi
    else
        # 更新現有檔案
        if [[ ! -r "$target_file" ]]; then
            log_error "無法讀取現有檔案：$target_file"
            return 1
        fi
        
        if [[ ! -w "$target_file" ]]; then
            log_error "無法寫入現有檔案：$target_file"
            return 1
        fi
        
        if update_existing_agent_file "$target_file" "$current_date"; then
            log_success "已更新現有 $agent_name 上下文檔案"
        else
            log_error "更新現有代理程式檔案失敗"
            return 1
        fi
    fi
    
    return 0
}

#==============================================================================
# 代理程式選擇和處理
#==============================================================================

update_specific_agent() {
    local agent_type="$1"
    
    case "$agent_type" in
        claude)
            update_agent_file "$CLAUDE_FILE" "Claude Code"
            ;;
        gemini)
            update_agent_file "$GEMINI_FILE" "Gemini CLI"
            ;;
        copilot)
            update_agent_file "$COPILOT_FILE" "GitHub Copilot"
            ;;
        cursor-agent)
            update_agent_file "$CURSOR_FILE" "Cursor IDE"
            ;;
        qwen)
            update_agent_file "$QWEN_FILE" "Qwen Code"
            ;;
        opencode)
            update_agent_file "$AGENTS_FILE" "opencode"
            ;;
        codex)
            update_agent_file "$AGENTS_FILE" "Codex CLI"
            ;;
        windsurf)
            update_agent_file "$WINDSURF_FILE" "Windsurf"
            ;;
        kilocode)
            update_agent_file "$KILOCODE_FILE" "Kilo Code"
            ;;
        auggie)
            update_agent_file "$AUGGIE_FILE" "Auggie CLI"
            ;;
        roo)
            update_agent_file "$ROO_FILE" "Roo Code"
            ;;
        codebuddy)
            update_agent_file "$CODEBUDDY_FILE" "CodeBuddy CLI"
            ;;
        qoder)
            update_agent_file "$QODER_FILE" "Qoder CLI"
            ;;
        amp)
            update_agent_file "$AMP_FILE" "Amp"
            ;;
        shai)
            update_agent_file "$SHAI_FILE" "SHAI"
            ;;
        q)
            update_agent_file "$Q_FILE" "Amazon Q Developer CLI"
            ;;
        bob)
            update_agent_file "$BOB_FILE" "IBM Bob"
            ;;
        *)
            log_error "未知的代理程式類型 '$agent_type'"
            log_error "預期值：claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|roo|amp|shai|q|bob|qoder"
            exit 1
            ;;
    esac
}

update_all_existing_agents() {
    local found_agent=false
    
    # 檢查每個可能的代理程式檔案，如果存在則更新
    if [[ -f "$CLAUDE_FILE" ]]; then
        update_agent_file "$CLAUDE_FILE" "Claude Code"
        found_agent=true
    fi
    
    if [[ -f "$GEMINI_FILE" ]]; then
        update_agent_file "$GEMINI_FILE" "Gemini CLI"
        found_agent=true
    fi
    
    if [[ -f "$COPILOT_FILE" ]]; then
        update_agent_file "$COPILOT_FILE" "GitHub Copilot"
        found_agent=true
    fi
    
    if [[ -f "$CURSOR_FILE" ]]; then
        update_agent_file "$CURSOR_FILE" "Cursor IDE"
        found_agent=true
    fi
    
    if [[ -f "$QWEN_FILE" ]]; then
        update_agent_file "$QWEN_FILE" "Qwen Code"
        found_agent=true
    fi
    
    if [[ -f "$AGENTS_FILE" ]]; then
        update_agent_file "$AGENTS_FILE" "Codex/opencode"
        found_agent=true
    fi
    
    if [[ -f "$WINDSURF_FILE" ]]; then
        update_agent_file "$WINDSURF_FILE" "Windsurf"
        found_agent=true
    fi
    
    if [[ -f "$KILOCODE_FILE" ]]; then
        update_agent_file "$KILOCODE_FILE" "Kilo Code"
        found_agent=true
    fi

    if [[ -f "$AUGGIE_FILE" ]]; then
        update_agent_file "$AUGGIE_FILE" "Auggie CLI"
        found_agent=true
    fi
    
    if [[ -f "$ROO_FILE" ]]; then
        update_agent_file "$ROO_FILE" "Roo Code"
        found_agent=true
    fi

    if [[ -f "$CODEBUDDY_FILE" ]]; then
        update_agent_file "$CODEBUDDY_FILE" "CodeBuddy CLI"
        found_agent=true
    fi

    if [[ -f "$SHAI_FILE" ]]; then
        update_agent_file "$SHAI_FILE" "SHAI"
        found_agent=true
    fi

    if [[ -f "$QODER_FILE" ]]; then
        update_agent_file "$QODER_FILE" "Qoder CLI"
        found_agent=true
    fi

    if [[ -f "$Q_FILE" ]]; then
        update_agent_file "$Q_FILE" "Amazon Q Developer CLI"
        found_agent=true
    fi
    
    if [[ -f "$BOB_FILE" ]]; then
        update_agent_file "$BOB_FILE" "IBM Bob"
        found_agent=true
    fi
    
    # 如果沒有代理程式檔案存在，建立預設 Claude 檔案
    if [[ "$found_agent" == false ]]; then
        log_info "找不到現有代理程式檔案，建立預設 Claude 檔案..."
        update_agent_file "$CLAUDE_FILE" "Claude Code"
    fi
}
print_summary() {
    echo
    log_info "變更摘要："
    
    if [[ -n "$NEW_LANG" ]]; then
        echo "  - 新增語言：$NEW_LANG"
    fi
    
    if [[ -n "$NEW_FRAMEWORK" ]]; then
        echo "  - 新增框架：$NEW_FRAMEWORK"
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]]; then
        echo "  - 新增資料庫：$NEW_DB"
    fi
    
    echo

    log_info "用法：$0 [claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|codebuddy|shai|q|bob|qoder]"
}

#==============================================================================
# 主要執行
#==============================================================================

main() {
    # 在繼續之前驗證環境
    validate_environment
    
    log_info "=== 正在更新功能 $CURRENT_BRANCH 的代理程式上下文檔案 ==="
    
    # 解析計畫檔案以擷取專案資訊
    if ! parse_plan_data "$NEW_PLAN"; then
        log_error "解析計畫資料失敗"
        exit 1
    fi
    
    # 根據代理程式類型參數進行處理
    local success=true
    
    if [[ -z "$AGENT_TYPE" ]]; then
        # 未提供特定代理程式 - 更新所有現有代理程式檔案
        log_info "未指定代理程式，更新所有現有代理程式檔案..."
        if ! update_all_existing_agents; then
            success=false
        fi
    else
        # 提供特定代理程式 - 僅更新該代理程式
        log_info "更新特定代理程式：$AGENT_TYPE"
        if ! update_specific_agent "$AGENT_TYPE"; then
            success=false
        fi
    fi
    
    # 列印摘要
    print_summary
    
    if [[ "$success" == true ]]; then
        log_success "代理程式上下文更新成功完成"
        exit 0
    else
        log_error "代理程式上下文更新完成但有錯誤"
        exit 1
    fi
}

# 如果腳本直接執行則執行 main 函式
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi


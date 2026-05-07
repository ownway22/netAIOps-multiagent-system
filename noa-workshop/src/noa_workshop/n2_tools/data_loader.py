"""共用的資料載入工具，讓 ``n2_tools/`` 下的 ``@tool`` 能讀到 ``n3_data/`` 下的擬真資料集。

關鍵設計
--------
- ``load_json`` / ``load_text`` 都加了 ``lru_cache``，同一份資料只讀一次、走 in-memory。
- ``_resolve_data_dir()`` 處理各種部署 layout，改變檔案位置也不會一下子壞掉。
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


def _resolve_data_dir() -> Path:
    """定位 workshop 的資料根目錄，適應不同部署情境。

    資料差不多與 package 一起裝（``src/noa_workshop/n3_data/``），所以不管是 wheel 還是
    容器都能跟著走。

    判斷順序：
      1. ``NOA_DATA_DIR`` 環境變數（顯式覆寫，給測試與容器用）。
      2. 與模組同層的位置：``.../noa_workshop/n3_data/``。
      3. 從本檔位置往上走，找任何含 ``n3_data/`` 的祖先資料夾（對不常見的 install layout 是防護措施）。
      4. 總設不到時就回預設位置，讓 ``load_json`` 抓不到檔案時能醒你到哪裡去找。
    """
    override = os.getenv("NOA_DATA_DIR")
    if override:
        path = Path(override).resolve()
        if (path / "telemetry").is_dir() or path.is_dir():
            return path

    here = Path(__file__).resolve()
    # 與模組同層的資料位置，改名 n0x_ 後的正式位置。
    candidate = here.parents[1] / "n3_data"
    if candidate.is_dir():
        return candidate

    for parent in here.parents:
        candidate = parent / "n3_data"
        if candidate.is_dir():
            return candidate
        candidate = parent / "data"
        if candidate.is_dir():
            return candidate

    # 接不到任何 hit，仍回一個合理路徑，讓下游的錯誤訊息能顯示清楚位置。
    return here.parents[1] / "n3_data"


_DATA_DIR = _resolve_data_dir()


@lru_cache(maxsize=32)
def load_json(relative_path: str) -> Any:
    """從 n3_data 讀一份 JSON；同一個 ``relative_path`` 只會讀一次。"""
    path = _DATA_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=8)
def load_text(relative_path: str) -> str:
    """從 n3_data 讀一份純文本 / markdown；同一個路徑只會讀一次。"""
    path = _DATA_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    return path.read_text(encoding="utf-8")

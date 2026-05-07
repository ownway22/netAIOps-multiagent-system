# SOP-SEC-001：核心 PoP 異常南向流量處理程序

## 適用情境

- 核心節點（如 CORE-POP1-EDGE）egress throughput 相對週基線 +50% 以上、持續 5 分鐘。
- 並伴隨 IOC 簽章命中（SIG-BOT-\* 系列）或可疑 destination IP。

## 步驟

1. **遙測佐證**：telemetry agent 取得 5 分鐘 throughput / latency / packet_loss 數值，標示異常起點。
2. **威脅情資**：security agent 用 `lookup_threat_intel` 比對 destination IP / 簽章。
3. **策略檢查**：使用 `check_security_policy` 確認異常流量是否違反 egress allow-list。
4. **判定**：
   - 若**確認**為安全事件：建議啟動 P1 incident response，凍結相關帳號並隔離節點（**只能建議，不可自動執行**）。
   - 若**疑似但未確認**：建議切到觀察模式，加密記錄、不立即阻擋。
   - 若**否決**為安全事件：交還 NOC Manager，重新檢視是否是計畫性流量（例如備份視窗、CDN 預載）。
5. **field-ops**：本 SOP 通常**不**需要派工，但若需要更換被入侵節點的硬體，再開派工單。

## 注意事項

- 任何 mitigation（封鎖、隔離、阻擋 IP）都**必須**經安全主管批准，agent 只能產生建議文字。
- 過去類似事件參見 TT-2025-10110。

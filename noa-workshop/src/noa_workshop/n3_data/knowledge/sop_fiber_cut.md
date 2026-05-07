# SOP-FIBER-001：傳輸環光纖中斷處理程序

## 適用情境

- 收到 P1 link_down 告警，且伴隨 packet_loss_pct > 5% 與 latency_ms 相對 baseline 上升 2 倍以上。
- 同一鏈路兩端節點（例如 RTR-N1 與 RTR-N2）皆觀測到丟包飆升。

## 步驟

1. **快速確認**：呼叫 telemetry agent 比對 baseline，確認異常並非短暫抖動（≥ 60 秒）。
2. **排除安全因素**：呼叫 security agent 確認非 DDoS、非設定漂移。
3. **拓撲定位**：在 topology 中找出對應 link 的 cable_id 與兩端站點。
4. **派工**：依 cable_id 與站點，由 field-ops 找最近的 fiber-splicing 工程師。預估 SLA：MTTR ≤ 4 小時。
5. **臨時繞徑**：在現場修復期間，網管先把流量切到備援路徑（北環的備援是 LINK-N4-N1）。
6. **修復後驗證**：派工結束後再跑一次 baseline 比對，確認 KPI 回穩 15 分鐘以上。

## 注意事項

- 北環的施工熱點是新莊—板橋段，CABLE-NB-007 過去 12 個月有兩次施工導致光纖被挖斷的紀錄。
- 若同時兩條 ring 鏈路 down，視為 P0，立刻通報區網主管。

````skill
---
name: copilot-sdk
description: 使用 GitHub Copilot SDK 建構代理式應用程式。適用於在應用程式中嵌入 AI 代理、建立自訂工具、實作串流回應、管理工作階段、連線至 MCP 伺服器或建立自訂代理時使用。觸發關鍵字：Copilot SDK、GitHub SDK、代理式應用程式、嵌入 Copilot、可程式化代理、MCP 伺服器、自訂代理。
---

# GitHub Copilot SDK

使用 Python、TypeScript、Go 或 .NET 將 Copilot 的代理式工作流程嵌入任何應用程式。

## 概述

GitHub Copilot SDK 公開了 Copilot CLI 背後的同一引擎：一個經過正式環境驗證的代理執行階段，可供程式化呼叫。無需自行建構協調機制——您定義代理行為，Copilot 負責規劃、工具呼叫、檔案編輯等作業。

## 先決條件

1. **GitHub Copilot CLI** 已安裝並完成驗證（[安裝指南](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)）
2. **語言執行階段**：Node.js 18+、Python 3.8+、Go 1.21+ 或 .NET 8.0+

驗證 CLI：`copilot --version`

## 安裝

### Node.js/TypeScript
```bash
mkdir copilot-demo && cd copilot-demo
npm init -y --init-type module
npm install @github/copilot-sdk tsx
```

### Python
```bash
pip install github-copilot-sdk
```

### Go
```bash
mkdir copilot-demo && cd copilot-demo
go mod init copilot-demo
go get github.com/github/copilot-sdk/go
```

### .NET
```bash
dotnet new console -n CopilotDemo && cd CopilotDemo
dotnet add package GitHub.Copilot.SDK
```

## 快速入門

### TypeScript
```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({ model: "gpt-4.1" });

const response = await session.sendAndWait({ prompt: "What is 2 + 2?" });
console.log(response?.data.content);

await client.stop();
process.exit(0);
```

執行：`npx tsx index.ts`

### Python
```python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})

    print(response.data.content)
    await client.stop()

asyncio.run(main())
```

### Go
```go
package main

import (
    "fmt"
    "log"
    "os"
    copilot "github.com/github/copilot-sdk/go"
)

func main() {
    client := copilot.NewClient(nil)
    if err := client.Start(); err != nil {
        log.Fatal(err)
    }
    defer client.Stop()

    session, err := client.CreateSession(&copilot.SessionConfig{Model: "gpt-4.1"})
    if err != nil {
        log.Fatal(err)
    }

    response, err := session.SendAndWait(copilot.MessageOptions{Prompt: "What is 2 + 2?"}, 0)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(*response.Data.Content)
    os.Exit(0)
}
```

### .NET (C#)
```csharp
using GitHub.Copilot.SDK;

await using var client = new CopilotClient();
await using var session = await client.CreateSessionAsync(new SessionConfig { Model = "gpt-4.1" });

var response = await session.SendAndWaitAsync(new MessageOptions { Prompt = "What is 2 + 2?" });
Console.WriteLine(response?.Data.Content);
```

執行：`dotnet run`

## 串流回應

啟用即時輸出以提升使用者體驗：

### TypeScript
```typescript
import { CopilotClient, SessionEvent } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    streaming: true,
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
    if (event.type === "session.idle") {
        console.log(); // 完成時換行
    }
});

await session.sendAndWait({ prompt: "Tell me a short joke" });

await client.stop();
process.exit(0);
```

### Python
```python
import asyncio
import sys
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
    })

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        if event.type == SessionEventType.SESSION_IDLE:
            print()

    session.on(handle_event)
    await session.send_and_wait({"prompt": "Tell me a short joke"})
    await client.stop()

asyncio.run(main())
```

### Go
```go
session, err := client.CreateSession(&copilot.SessionConfig{
    Model:     "gpt-4.1",
    Streaming: true,
})

session.On(func(event copilot.SessionEvent) {
    if event.Type == "assistant.message_delta" {
        fmt.Print(*event.Data.DeltaContent)
    }
    if event.Type == "session.idle" {
        fmt.Println()
    }
})

_, err = session.SendAndWait(copilot.MessageOptions{Prompt: "Tell me a short joke"}, 0)
```

### .NET
```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = "gpt-4.1",
    Streaming = true,
});

session.On(ev =>
{
    if (ev is AssistantMessageDeltaEvent deltaEvent)
        Console.Write(deltaEvent.Data.DeltaContent);
    if (ev is SessionIdleEvent)
        Console.WriteLine();
});

await session.SendAndWaitAsync(new MessageOptions { Prompt = "Tell me a short joke" });
```

## 自訂工具

定義 Copilot 在推理過程中可呼叫的工具。定義工具時，您需要告訴 Copilot：
1. **工具的功能**（描述）
2. **需要哪些參數**（結構描述）
3. **要執行的程式碼**（處理函式）

### TypeScript（JSON Schema）
```typescript
import { CopilotClient, defineTool, SessionEvent } from "@github/copilot-sdk";

const getWeather = defineTool("get_weather", {
    description: "Get the current weather for a city",
    parameters: {
        type: "object",
        properties: {
            city: { type: "string", description: "The city name" },
        },
        required: ["city"],
    },
    handler: async (args: { city: string }) => {
        const { city } = args;
        // 在實際應用中，此處會呼叫天氣 API
        const conditions = ["sunny", "cloudy", "rainy", "partly cloudy"];
        const temp = Math.floor(Math.random() * 30) + 50;
        const condition = conditions[Math.floor(Math.random() * conditions.length)];
        return { city, temperature: `${temp}°F`, condition };
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    streaming: true,
    tools: [getWeather],
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
});

await session.sendAndWait({
    prompt: "What's the weather like in Seattle and Tokyo?",
});

await client.stop();
process.exit(0);
```

### Python（Pydantic）
```python
import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": [get_weather],
    })

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)

    await session.send_and_wait({
        "prompt": "What's the weather like in Seattle and Tokyo?"
    })

    await client.stop()

asyncio.run(main())
```

### Go
```go
type WeatherParams struct {
    City string `json:"city" jsonschema:"The city name"`
}

type WeatherResult struct {
    City        string `json:"city"`
    Temperature string `json:"temperature"`
    Condition   string `json:"condition"`
}

getWeather := copilot.DefineTool(
    "get_weather",
    "Get the current weather for a city",
    func(params WeatherParams, inv copilot.ToolInvocation) (WeatherResult, error) {
        conditions := []string{"sunny", "cloudy", "rainy", "partly cloudy"}
        temp := rand.Intn(30) + 50
        condition := conditions[rand.Intn(len(conditions))]
        return WeatherResult{
            City:        params.City,
            Temperature: fmt.Sprintf("%d°F", temp),
            Condition:   condition,
        }, nil
    },
)

session, _ := client.CreateSession(&copilot.SessionConfig{
    Model:     "gpt-4.1",
    Streaming: true,
    Tools:     []copilot.Tool{getWeather},
})
```

### .NET（Microsoft.Extensions.AI）
```csharp
using GitHub.Copilot.SDK;
using Microsoft.Extensions.AI;
using System.ComponentModel;

var getWeather = AIFunctionFactory.Create(
    ([Description("The city name")] string city) =>
    {
        var conditions = new[] { "sunny", "cloudy", "rainy", "partly cloudy" };
        var temp = Random.Shared.Next(50, 80);
        var condition = conditions[Random.Shared.Next(conditions.Length)];
        return new { city, temperature = $"{temp}°F", condition };
    },
    "get_weather",
    "Get the current weather for a city"
);

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = "gpt-4.1",
    Streaming = true,
    Tools = [getWeather],
});
```

## 工具運作原理

當 Copilot 決定呼叫您的工具時：
1. Copilot 傳送包含參數的工具呼叫請求
2. SDK 執行您的處理函式
3. 結果回傳給 Copilot
4. Copilot 將結果納入其回應中

Copilot 會依據使用者的問題和您的工具描述，來決定何時呼叫您的工具。

## 互動式 CLI 助手

建構完整的互動式助手：

### TypeScript
```typescript
import { CopilotClient, defineTool, SessionEvent } from "@github/copilot-sdk";
import * as readline from "readline";

const getWeather = defineTool("get_weather", {
    description: "Get the current weather for a city",
    parameters: {
        type: "object",
        properties: {
            city: { type: "string", description: "The city name" },
        },
        required: ["city"],
    },
    handler: async ({ city }) => {
        const conditions = ["sunny", "cloudy", "rainy", "partly cloudy"];
        const temp = Math.floor(Math.random() * 30) + 50;
        const condition = conditions[Math.floor(Math.random() * conditions.length)];
        return { city, temperature: `${temp}°F`, condition };
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    streaming: true,
    tools: [getWeather],
});

session.on((event: SessionEvent) => {
    if (event.type === "assistant.message_delta") {
        process.stdout.write(event.data.deltaContent);
    }
});

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

console.log("天氣助手（輸入 'exit' 離開）");
console.log("試試看：'What's the weather in Paris?'\n");

const prompt = () => {
    rl.question("您：", async (input) => {
        if (input.toLowerCase() === "exit") {
            await client.stop();
            rl.close();
            return;
        }

        process.stdout.write("助手：");
        await session.sendAndWait({ prompt: input });
        console.log("\n");
        prompt();
    });
};

prompt();
```

### Python
```python
import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": params.city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": [get_weather],
    })

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)

    print("天氣助手（輸入 'exit' 離開）")
    print("試試看：'What's the weather in Paris?'\n")

    while True:
        try:
            user_input = input("您：")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("助手：")
        await session.send_and_wait({"prompt": user_input})
        print("\n")

    await client.stop()

asyncio.run(main())
```

## MCP 伺服器整合

連線至 MCP（Model Context Protocol）伺服器以使用預建工具。連線至 GitHub 的 MCP 伺服器以存取存放庫、議題和 PR：

### TypeScript
```typescript
const session = await client.createSession({
    model: "gpt-4.1",
    mcpServers: {
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
        },
    },
});
```

### Python
```python
session = await client.create_session({
    "model": "gpt-4.1",
    "mcp_servers": {
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
        },
    },
})
```

### Go
```go
session, _ := client.CreateSession(&copilot.SessionConfig{
    Model: "gpt-4.1",
    MCPServers: map[string]copilot.MCPServerConfig{
        "github": {
            Type: "http",
            URL:  "https://api.githubcopilot.com/mcp/",
        },
    },
})
```

### .NET
```csharp
await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = "gpt-4.1",
    McpServers = new Dictionary<string, McpServerConfig>
    {
        ["github"] = new McpServerConfig
        {
            Type = "http",
            Url = "https://api.githubcopilot.com/mcp/",
        },
    },
});
```

## 自訂代理

為特定任務定義專業化的 AI 角色：

### TypeScript
```typescript
const session = await client.createSession({
    model: "gpt-4.1",
    customAgents: [{
        name: "pr-reviewer",
        displayName: "PR Reviewer",
        description: "Reviews pull requests for best practices",
        prompt: "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
});
```

### Python
```python
session = await client.create_session({
    "model": "gpt-4.1",
    "custom_agents": [{
        "name": "pr-reviewer",
        "display_name": "PR Reviewer",
        "description": "Reviews pull requests for best practices",
        "prompt": "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
})
```

## 系統訊息

自訂 AI 的行為和風格：

### TypeScript
```typescript
const session = await client.createSession({
    model: "gpt-4.1",
    systemMessage: {
        content: "You are a helpful assistant for our engineering team. Always be concise.",
    },
});
```

### Python
```python
session = await client.create_session({
    "model": "gpt-4.1",
    "system_message": {
        "content": "You are a helpful assistant for our engineering team. Always be concise.",
    },
})
```

## 外部 CLI 伺服器

以伺服器模式另外執行 CLI，並將 SDK 連線至該伺服器。適用於偵錯、資源共享或自訂環境。

### 以伺服器模式啟動 CLI
```bash
copilot --server --port 4321
```

### 將 SDK 連線至外部伺服器

#### TypeScript
```typescript
const client = new CopilotClient({
    cliUrl: "localhost:4321"
});

const session = await client.createSession({ model: "gpt-4.1" });
```

#### Python
```python
client = CopilotClient({
    "cli_url": "localhost:4321"
})
await client.start()

session = await client.create_session({"model": "gpt-4.1"})
```

#### Go
```go
client := copilot.NewClient(&copilot.ClientOptions{
    CLIUrl: "localhost:4321",
})

if err := client.Start(); err != nil {
    log.Fatal(err)
}

session, _ := client.CreateSession(&copilot.SessionConfig{Model: "gpt-4.1"})
```

#### .NET
```csharp
using var client = new CopilotClient(new CopilotClientOptions
{
    CliUrl = "localhost:4321"
});

await using var session = await client.CreateSessionAsync(new SessionConfig { Model = "gpt-4.1" });
```

**注意：** 當提供 `cliUrl` 時，SDK 不會啟動或管理 CLI 程序——僅連線至現有伺服器。

## 事件類型

| 事件 | 說明 |
|-------|------|
| `user.message` | 使用者輸入已加入 |
| `assistant.message` | 完整模型回應 |
| `assistant.message_delta` | 串流回應片段 |
| `assistant.reasoning` | 模型推理（依模型而異） |
| `assistant.reasoning_delta` | 串流推理片段 |
| `tool.execution_start` | 工具呼叫已開始 |
| `tool.execution_complete` | 工具執行已完成 |
| `session.idle` | 無進行中的處理 |
| `session.error` | 發生錯誤 |

## 用戶端組態

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `cliPath` | Copilot CLI 執行檔路徑 | 系統 PATH |
| `cliUrl` | 連線至現有伺服器（例如 "localhost:4321"） | 無 |
| `port` | 伺服器通訊連接埠 | 隨機 |
| `useStdio` | 使用 stdio 傳輸而非 TCP | true |
| `logLevel` | 日誌詳細程度 | "info" |
| `autoStart` | 自動啟動伺服器 | true |
| `autoRestart` | 當機時自動重啟 | true |
| `cwd` | CLI 程序的工作目錄 | 繼承 |

## 工作階段組態

| 選項 | 說明 |
|------|------|
| `model` | 使用的 LLM（"gpt-4.1"、"claude-sonnet-4.5" 等） |
| `sessionId` | 自訂工作階段識別碼 |
| `tools` | 自訂工具定義 |
| `mcpServers` | MCP 伺服器連線 |
| `customAgents` | 自訂代理角色 |
| `systemMessage` | 覆寫預設系統提示 |
| `streaming` | 啟用增量回應片段 |
| `availableTools` | 允許的工具白名單 |
| `excludedTools` | 停用的工具黑名單 |

## 工作階段持久化

跨重啟保存和恢復對話：

### 使用自訂 ID 建立
```typescript
const session = await client.createSession({
    sessionId: "user-123-conversation",
    model: "gpt-4.1"
});
```

### 恢復工作階段
```typescript
const session = await client.resumeSession("user-123-conversation");
await session.send({ prompt: "What did we discuss earlier?" });
```

### 列出與刪除工作階段
```typescript
const sessions = await client.listSessions();
await client.deleteSession("old-session-id");
```

## 錯誤處理

```typescript
try {
    const client = new CopilotClient();
    const session = await client.createSession({ model: "gpt-4.1" });
    const response = await session.sendAndWait(
        { prompt: "Hello!" },
        30000 // 逾時時間（毫秒）
    );
} catch (error) {
    if (error.code === "ENOENT") {
        console.error("Copilot CLI 未安裝");
    } else if (error.code === "ECONNREFUSED") {
        console.error("無法連線至 Copilot 伺服器");
    } else {
        console.error("錯誤：", error.message);
    }
} finally {
    await client.stop();
}
```

## 優雅關閉

```typescript
process.on("SIGINT", async () => {
    console.log("正在關閉...");
    await client.stop();
    process.exit(0);
});
```

## 常見模式

### 多輪對話
```typescript
const session = await client.createSession({ model: "gpt-4.1" });

await session.sendAndWait({ prompt: "My name is Alice" });
await session.sendAndWait({ prompt: "What's my name?" });
// 回應："Your name is Alice"
```

### 檔案附件
```typescript
await session.send({
    prompt: "Analyze this file",
    attachments: [{
        type: "file",
        path: "./data.csv",
        displayName: "Sales Data"
    }]
});
```

### 中止長時間操作
```typescript
const timeoutId = setTimeout(() => {
    session.abort();
}, 60000);

session.on((event) => {
    if (event.type === "session.idle") {
        clearTimeout(timeoutId);
    }
});
```

## 可用模型

在執行階段查詢可用模型：

```typescript
const models = await client.getModels();
// 回傳：["gpt-4.1", "gpt-4o", "claude-sonnet-4.5", ...]
```

## 最佳實務

1. **務必清理資源**：使用 `try-finally` 或 `defer` 確保呼叫 `client.stop()`
2. **設定逾時**：對長時間操作使用 `sendAndWait` 搭配逾時設定
3. **處理事件**：訂閱錯誤事件以進行穩健的錯誤處理
4. **使用串流**：為長回應啟用串流以提升使用者體驗
5. **持久化工作階段**：為多輪對話使用自訂工作階段 ID
6. **定義清晰的工具**：撰寫具描述性的工具名稱和說明

## 架構

```
您的應用程式
       |
  SDK 用戶端
       | JSON-RPC
  Copilot CLI（伺服器模式）
       |
  GitHub（模型、驗證）
```

SDK 自動管理 CLI 程序的生命週期。所有通訊透過 stdio 或 TCP 上的 JSON-RPC 進行。

## 資源

- **GitHub 存放庫**：https://github.com/github/copilot-sdk
- **入門教學課程**：https://github.com/github/copilot-sdk/blob/main/docs/tutorials/first-app.md
- **GitHub MCP 伺服器**：https://github.com/github/github-mcp-server
- **MCP 伺服器目錄**：https://github.com/modelcontextprotocol/servers
- **範例食譜**：https://github.com/github/copilot-sdk/tree/main/cookbook
- **範例程式碼**：https://github.com/github/copilot-sdk/tree/main/samples

## 狀態

此 SDK 目前為**技術預覽版**，可能會有破壞性變更。尚不建議用於正式環境。

````

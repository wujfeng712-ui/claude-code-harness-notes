# 图示资源 · Diagrams

本目录每张图都是一对文件：

| 文件 | 用途 |
|---|---|
| `*.svg` | 在文档/GitHub 里**显示**的矢量图（采用 draw.io 标准配色，手工绘制） |
| `*.drawio` | 对应的 **draw.io 源文件**，可编辑、可二次创作 |

## 用 [next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) 编辑

`.drawio` 是标准 draw.io（diagrams.net）格式，可以：

1. 直接在 [app.diagrams.net](https://app.diagrams.net) 或 VS Code 的 *Draw.io Integration* 插件里打开编辑；
2. 用 **next-ai-draw-io** 的 MCP server 让 AI 帮你改：
   ```sh
   claude mcp add drawio -- npx @next-ai-drawio/mcp-server@latest
   ```
   之后把某个 `.drawio` 的 XML 交给 agent，用自然语言描述要改什么即可。

> 改完 `.drawio` 后，如需更新显示用的 `.svg`，在 draw.io 里 **File → Export as → SVG** 覆盖同名文件即可。

## 清单

| 图 | 说明 |
|---|---|
| `01-core-loop` | 永不改变的核心循环 |
| `02-evolution` | 20 课分五篇的演进路线 |
| `03-context` | 上下文工程五层 |
| `04-memory` | 记忆三环节 |
| `05-teams` | 多 Agent 协作（MessageBus） |

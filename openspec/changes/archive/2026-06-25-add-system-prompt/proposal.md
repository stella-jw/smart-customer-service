## Why

目前每个智能体只能通过 `personality` 和 `response_tone` 有限参数配置机器人行为，无法定义具体的角色设定、回答逻辑和知识范围。系统提示词（System Prompt）允许管理员为每个机器人配置专属的指令，使 LLM 能够扮演特定角色并提供针对性的回答。

## What Changes

- 在 `BotConfiguration` 表添加 `system_prompt` 字段（Text 类型）
- 在管理后台"智能体配置"界面添加系统提示词输入框
- 在调用 LLM 时将 `system_prompt` 作为 `system` 参数传入
- 支持多行文本输入，提供默认提示词模板

## Capabilities

### New Capabilities

- **system-prompt**: 智能体系统提示词配置，允许为每个机器人定义专属的角色设定和行为指令

### Modified Capabilities

- (无)

## Impact

- **数据库**: `BotConfiguration` 表新增 `system_prompt` 字段
- **后端 API**: `BotConfigRequest` 添加 `system_prompt` 字段
- **LLM 调用**: LangGraph generate 节点接收 `system_prompt` 参数
- **前端**: BotConfigPage 添加系统提示词输入框

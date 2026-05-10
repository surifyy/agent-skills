# TRTC AI Integration Framework

帮助开发者通过 AI 快速集成和排障 [TRTC](https://trtc.io)（腾讯实时音视频）SDK。

本项目将 TRTC 的产品知识拆解为**原子能力片段（Slice）**，并通过 **Claude Code Skills** 提供智能搜索、代码校验、场景引导和新手入门等交互能力，让开发者在对话中完成从零到上线的集成过程。

## 核心理念

```
用户提问 → Skill 路由 → 知识库检索 → 结构化回答 + 代码示例
```

传统文档是"被动阅读"，本框架是"主动交互"：
- **按需加载**：只返回用户当前需要的知识片段，不信息过载
- **代码生成与校验**：基于 Slice 知识生成生产级代码，并通过约束规则 + 编译验证自我校验
- **渐进引导**：通过场景（Scenario）按步骤引导完整功能集成
- **智能兜底**：7 层搜索策略 + 4 级 Fallback，确保用户总能得到有效回答

## 项目结构

```
ai-integration/
├── .claude/skills/trtc/          # Claude Code Skills（用户交互层）
│   ├── SKILL.md                  #   路由入口 — 识别产品/平台，分发到子 skill
│   ├── onboarding/SKILL.md       #   新手引导 — Demo 运行 / 集成教程 / 排障 / 扩展
│   ├── search/SKILL.md           #   智能搜索 — 7 策略匹配 + 4 级 Fallback
│   ├── apply/SKILL.md            #   代码生成与校验 — 生成生产级代码 + 自我校验
│   └── topic/SKILL.md            #   场景引导 — Checkpoint 式分步教程
│
├── knowledge-base/                # 结构化知识层
│   ├── index.yaml                #   全量索引（产品/Slice/场景/跨产品关系）
│   ├── slice-spec.md             #   Slice 编写规范
│   ├── slices/                   #   原子能力片段（按产品 → 平台组织）
│   │   ├── live/                 #     Live 产品（15 个 slice，iOS 平台已完成）
│   │   ├── chat/                 #     Chat 产品（规划中）
│   │   ├── call/                 #     Call 产品（规划中）
│   │   ├── rtc-engine/           #     RTC Engine 产品（规划中）
│   │   └── room/                 #     Room 产品（规划中）
│   └── scenarios/                #   场景组合（多 Slice 串联的完整流程）
│       └── entertainment-live-room.md
│
├── llms/                          # llms.txt 模板（供外部 LLM 发现文档）
├── llms.txt                       # 产品索引入口
└── .claude/skills/trtc-eval/      # 评测工具 skill（含 scripts / tests / templates / bootstrap.sh）
```

## 核心概念

### Slice（原子能力片段）

一个 Slice 对应一个原子能力（如"登录认证"、"弹幕"、"美颜"），是知识库的最小单元。

每个 Slice 分两层：
- **产品级概览**（`slices/live/barrage.md`）— 跨平台通用的功能说明、核心概念、最佳实践、排障指南
- **平台实现细节**（`slices/live/ios/barrage.md`）— 具体 API 调用、代码示例、平台特有注意事项

Slice 有两类来源：
- **主线 Slice**：按 SDK 能力域系统规划，覆盖核心功能
- **反馈 Slice**：从用户高频问题中提炼，补充真实场景的坑和边缘情况

### Scenario（场景组合）

一个完整的使用场景，串联多个 Slice 并定义执行顺序。例如「秀场直播间」场景包含 15 个 Slice，从登录认证到连麦互动。

### llms.txt（LLM 文档发现）

遵循 [llms.txt 标准](https://llmstxt.org/) 的三级渐进式文档：

`llms.txt`（产品索引）→ `{product}.txt`（产品概述）→ `{product}-{platform}.txt`（平台详情）

## TRTC 产品矩阵

| 产品 | 说明 | 当前状态 |
|------|------|---------|
| **Live** | 直播（推流/拉流/连麦/弹幕/礼物/美颜） | ✅ iOS 平台 15 个 Slice 已完成 |
| **Chat** | 即时通信（消息/会话/群组） | 📋 规划中 |
| **Call** | 音视频通话（1v1/群组） | 📋 规划中 |
| **RTC Engine** | 实时音视频引擎（进房/推流/拉流） | 📋 规划中 |
| **Room** | 房间管理（创建/销毁/成员管理） | 📋 规划中 |

**支持平台**：Web / Android / iOS / Flutter / Electron / Unity

## Skills 功能说明

### 路由（SKILL.md）

入口 Skill，识别用户意图中的产品和平台，分发到对应的子 Skill。

### 新手引导（onboarding）

为首次接触 TRTC 的开发者提供四条路径：
- **跑通 Demo**：下载 → 配置 → 运行，最快体验产品能力
- **集成教程**：从零将 SDK 集成到自有项目
- **排障指南**：遇到问题时的诊断和解决流程
- **功能扩展**：在已有集成基础上添加新能力

### 智能搜索（search）

7 层匹配策略按优先级执行：

1. 错误码精确匹配
2. Slice ID 精确匹配
3. 标签精确匹配
4. 产品 + 模糊匹配
5. 跨产品关系匹配
6. 场景匹配
7. 模糊 + 关键词映射（中英互转）

无匹配时进入 4 级 Fallback 链，确保有效回答。

### 代码生成与校验（apply）

基于 Slice 和 Scenario 知识生成生产级示例代码，并通过多层验证确保代码可直接使用。有两种工作模式：

- **生成模式**：读取 Slice 的 API 签名、代码示例和约束规则，生成符合最佳实践的生产级代码
- **审查模式**：用户贴入自己的代码，基于知识库规则进行校验和修复

两种模式共享同一条验证管线：

1. **约束合规检查** — 逐条校验 ALWAYS/NEVER（产品级）和 MUST/MUST NOT（平台级）规则
2. **跨 Slice 检查** — 前置状态验证、跨产品依赖、平台生命周期、清理对称性
3. **编译验证** — 在实际项目环境中编译，以证据而非推测确认代码正确性
4. **集成安全检查** — 确保代码不破坏已有项目（SDK 初始化冲突、依赖冲突、回归测试）

核心原则：**没有编译证据，不声称代码正确；每个 issue 必须附带可直接替换的修复代码。**

### 场景引导（topic）

基于 Scenario 文件，通过 Checkpoint 机制分步引导用户完成完整功能集成，每一步都会确认用户是否成功再继续。

## 三层架构

```
┌─────────────────────────────────────────────────────┐
│  Layer 3: Skills（用户交互层）                        │
│  trtc → onboarding / search / apply / topic          │
├─────────────────────────────────────────────────────┤
│  Layer 2: Knowledge Base（结构化知识层）               │
│  index.yaml → slices/ + scenarios/                   │
├─────────────────────────────────────────────────────┤
│  Layer 1: Claude Code Runtime                        │
│  .claude/skills/ + CLAUDE.md                         │
└─────────────────────────────────────────────────────┘
```
# Topic state-machine tests

> ⚪ **内部 — 不对外发布**。这些测试只供 TRTC 知识库维护者使用。
> 跟项目根 `tests/` 的定位一致，不会随 skill 包分发到用户机器；
> 发布脚本应当排除整个 `tests/` 目录。end user 不会跑、也不应跑这些测试。

这套测试守护 topic skill 的 slice-loop 状态机、PreToolUse / Stop 守门员
与 `apply.py` 的契约——也就是阻止 AI 批量读 slice、批量生成代码、跳过 `apply`
这三类坏行为的那一层硬约束。每次改动 `scripts/`、`scripts/lib/`、
`guardrails/` 下任何一个文件都应跑一遍这套测试。

## 运行

```bash
# 在 repo 根
python3 -m pytest .claude/skills/trtc-topic/tests/

# 看详细
python3 -m pytest .claude/skills/trtc-topic/tests/ -v

# 单文件
python3 -m pytest .claude/skills/trtc-topic/tests/test_state_machine.py -v

# 单 case
python3 -m pytest \
  .claude/skills/trtc-topic/tests/test_apply_cli.py::TestAutoAdvanceOnPass::test_pause_on_failure_pass_advances_to_next_slice -v
```

依赖：pytest 8+ 与 PyYAML（项目已有）。

## 覆盖矩阵（85 cases）

| 文件 | cases | 守护对象 | 关键场景 |
|---|---|---|---|
| `test_state_machine.py` | 25 | `scripts/lib/state_machine.py` | `init_queue` / `current_slice` / `advance` 全部合法 transition；非法 transition 抛错；apply_failed → 重试；user_confirmed 后清理 evidence；queue 末尾 → all_done |
| `test_gates.py` | 19 | `guardrails/gate_slice_read.py`、`guardrails/gate_slice_write.py` | session 缺失/queue 未初始化静默放行；只放行 cursor 当前 slice 的 .md；`not_started`/`apply_passed` 状态拦 Write；`slice_read`/`code_written`/`apply_failed` 放行 Edit |
| `test_apply_cli.py` | 16 | `scripts/apply.py` | pass + fail + static-only + 4 类 usage error；`auto_advance_policy` 五种值；apply 失败永远 pause；最后一个 slice → all_done；demo-test-2 三条 regression（注释/字符串塞 pattern / fail 输出不泄漏 patterns）|
| `test_stop_require_apply.py` | 8 | `guardrails/stop_require_apply_evidence.py` | session/queue 缺失放行；`not_started` / `slice_read` / `apply_passed` / `all_done` 放行；`code_written` / `apply_failed` 拦截 |
| `test_end_to_end.py` | 3 | 全链路 | 手动 confirm 完整循环；apply 失败路径；`pause_on_failure` 自动推进路径 |
| `test_topic_skill_invariants.py` | 4 | `topic/SKILL.md` 结构不变量 | Apply Evidence Block 已删；STATE-MACHINE-GUIDE.md 存在且被引用；topic/SKILL.md 不超过 480 行；Calling apply 段保持紧凑 |
| `test_session_resolver.py` | 10 | 三个 CLI 共享的 session 路径解析 | 4 级解析链（`--session` flag → `$TRTC_SESSION_PATH` → `$CLAUDE_PROJECT_DIR/.trtc-session.yaml` → cwd）；找不到时给 actionable 提示；三个 CLI 行为一致 |

## Fixtures（`conftest.py`）

- `session_factory(**overrides)` — 在 `tmp_path` 写一个 `.trtc-session.yaml`。
  默认仿真"general-conference / web 集成中"的状态。`overrides` 可换 `confirmed_plan`、
  `auto_advance_policy` 等任意根级字段。
- `project_factory()` — 在 `tmp_path/user-project/src/` 造空项目骨架，
  测试可以往里写 .vue / .ts。

## 依赖的目录布局（已对齐 apply skill）

```
topic/
├── guardrails/                ← Claude Code 注册的 hook
│   ├── gate_slice_read.py
│   ├── gate_slice_write.py
│   └── stop_require_apply_evidence.py
├── scripts/                   ← AI 通过 Bash 调用的 runtime CLI
│   ├── apply.py
│   ├── init_slice_queue.py
│   ├── next_slice.py
│   └── lib/
│       └── state_machine.py   ← 被 import 的库（不直接跑）
└── tests/                     ← ⚪ 本目录
```

如果你 git mv 了 `scripts/` 或 `scripts/lib/` 下的任何文件，这套测试里的
`sys.path.insert` / `parents[N]` / 命令行路径都需要同步更新——跑全套就能
立刻发现哪些路径断了。

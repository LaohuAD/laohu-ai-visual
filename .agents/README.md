# 项目 Skill 自动发现

Codex 的项目级入口为 `.agents/skills/`，不是 `.agent/`。本目录的22个相对符号链接指向 `../../skills/laohu-*`；`skills/` 仍是唯一正文来源，修改任一入口读取的是同一文件，不复制、不另建版本。

```text
.agents/skills/laohu-video-prompt → ../../skills/laohu-video-prompt
skills/laohu-video-prompt/SKILL.md
skills/laohu-video-prompt/skills/laohu-action-design/SKILL.md
```

## 使用与维护

- 在本仓库或其子目录启动 Codex，主入口及嵌套专业能力可进入技能列表；描述匹配决定隐式调用，明确指定技能可用于核查入口。
- 子 Skill 保持原嵌套及父级调度。Codex 会递归发现它们，列表可见不改变主责、交接和内容权限。
- 新增或删除主入口时，同步本目录链接、能力注册表及发现测试；内部专业不另建顶层链接。
- 符号链接必须为仓库内相对路径，随 Git 保存；不使用指向本机绝对目录的链接，不创建第二份 Skill 正文。
- 已打开会话的技能列表若未刷新，重新打开项目或新建会话核对。磁盘检索成功不代表当前窗口已经刷新。
- 本轮仅验证 Codex；其他 Agent 是否使用同一目录、递归扫描及支持符号链接，应按其实际运行时核验。

## 验证证据

2026-09-11，本机 Codex `app-server` 的 `skills/list` 在项目目录执行 `forceReload=true`，返回110个项目技能（22主入口＋88内部专业）、零解析错误。此操作仅检索技能，不启动模型任务或生成媒体。

维护检查：`python3 -m unittest discover -s tests -p 'test_skill_discovery.py'`。

目录依据：[OpenAI Skill 文档](https://learn.chatgpt.com/docs/build-skills)。

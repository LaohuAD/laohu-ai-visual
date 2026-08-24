# laohu Skills 能力生长规范（兼容入口）

> 本文件保留旧路径兼容，不再维护第二套能力进化方法。当前唯一负责人是 [`laohu-capability-evolution`](../../skills/laohu-capability-evolution/SKILL.md)。

## 迁移箴言

### 先把能力接过去，再把旧路指清楚

旧入口可以继续被找到，但所有原则发现、四层重编译、行为验证、保真迁移和回退判断都只在新 Skill 及其 Reference 维护。不要在本文件补写新规则，否则同一能力会再次出现两个负责人。

## 当前入口

遇到以下任务，读取 [`skills/laohu-capability-evolution/SKILL.md`](../../skills/laohu-capability-evolution/SKILL.md)：

- 重复反馈或跨作品经验需要进入长期能力。
- 外部 Skill、论文、案例、专家方法或平台资料需要被选择性吸收。
- 项目需要反思、自查、修复冲突或重构成熟能力。
- 平台、模型、接口、字符、路径或格式发生变化。
- 新建或修改 Skill 时，需要把灵魂、筋骨、血肉、表皮编译成领域自己的规则。

## 已迁移能力

| 旧内容 | 当前唯一负责人 |
|---|---|
| 高水平与相邻水平对照、取舍、因果、原则发现 | [`01_证据吸收与根因判断.md`](../../skills/laohu-capability-evolution/references/01_证据吸收与根因判断.md) |
| 箴言、章法、技法、法度及载体分工 | [`02_四层能力重编译.md`](../../skills/laohu-capability-evolution/references/02_四层能力重编译.md) |
| 成熟项目语义迁移、外部依赖保真、行为验证和回退 | [`03_保真迁移回归与回退.md`](../../skills/laohu-capability-evolution/references/03_保真迁移回归与回退.md) |
| 跨任务记忆、证据重开和新能力出生门槛 | [`04_进化记忆与能力生长.md`](../../skills/laohu-capability-evolution/references/04_进化记忆与能力生长.md) |
| 进入方式、任务契约、写回位置、权限与返回总控 | [`laohu-capability-evolution/SKILL.md`](../../skills/laohu-capability-evolution/SKILL.md) |

## 兼容规则

任何仍指向本文件的旧调用，都应立即转到新 Skill。迁移完成前保留本路径，避免旧链接失效；确认没有调用者后，是否删除由能力进化 Skill 按迁移证据决定。

本文件不直接修改业务 Skill，不给一次反馈立永久禁令，也不执行 `git commit` 或 `git push`。

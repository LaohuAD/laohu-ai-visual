# 《不想长大》片尾主题曲 Style Prompt 与演唱控制

## 风格提示词

```text
Mandarin nostalgic family end-credit ballad, 70 BPM, 4/4, intimate bittersweet childhood memory, light folk-pop warmth, warm felt piano, nylon acoustic guitar, soft brushed drums, subtle upright bass, recurring music-box wooden-wheel motif, thin low strings entering after second chorus, mature male Mandarin baritone vocal, low-mid range, slightly husky dry timbre, close-mic storytelling, restrained chest voice, clear natural consonants, short dry phrase endings, verses sparse and narrative, pre-choruses gently rising with shorter breaths, choruses vocal-forward with controlled emotional lift, bridge stripped to piano and music box, final chorus wider with low strings bloom and one soft harmony tail, dry intimate room, vocal forward, clear hook space, long fading piano outro
```

## 带演唱控制的歌词

```text
[Intro ｜ felt piano ｜ music-box wooden-wheel motif ｜ old room air]

[Verse 1 ｜ close dry male vocal ｜ sparse piano and nylon guitar ｜ clear consonants]
回老家的车窗上
雾气被我画了又擦
老家没玩具 只有红灯笼
挂在门框摇摇晃晃

你把药碗推到一旁
笑着搬出木马车
我只顾问它跑不跑
没听见你把咳声藏

[Pre-Chorus ｜ vocal closer ｜ music-box motif returns ｜ gentle tension lift]
木轮咕噜咕噜过院坝
我笑得忘了回家
那时我把你的叮咛
听成哄小孩的话

[Chorus 1 ｜ vocal forward ｜ soft drums enter ｜ controlled emotional lift]
我不想长大
不是怕谁催我回家
是怕木轮停下
[(hold final vowel on "话", short dry fall)]
才听懂你没说完的话

我不想长大
怕再也没人等我回家
那枚硬币握到发麻
[(rhyme handoff, gentle chest voice, keep "挂" clear)]
才懂好运是你的牵挂

[Verse 2 ｜ warm return ｜ light brush groove ｜ close narrative phrasing]
我把汤圆戳碎找硬币
偏说好运一定在碗底
你把掌心摊到我眼里
说好运都归你

白布系在额上
奶奶低头理衣裳
她说吃饭别挑 夜里关窗
我低着头不敢答腔

[Pre-Chorus 2 ｜ tighter breath ｜ low strings barely enter ｜ inward tension]
后来补丁磨着手腕
针线密密缝了几圈
没听完的话在耳边
[(slight pause, softer onset, solo dry lead)]
一针一针疼到今天

[Chorus 2 ｜ fuller low end ｜ vocal still close ｜ hook repeated clearly]
我不想长大
不是怕谁催我回家
是怕木轮停下
才听懂你没说完的话

我不想长大
怕再也没人等我回家
那枚硬币握到发麻
才懂好运是你的牵挂

[Bridge ｜ stripped piano and music box ｜ close dry vocal ｜ emotional turn]
如果那天我再慢一点哭
如果那晚我没那么倔强
如果我早些听懂
你把心疼藏得不声不响

若长大真有答案
会不会藏在木轮旁
可我学会说谢谢
[(short breath before line, small downward fall)]
已经隔着一座院墙

[Final Chorus ｜ warm final lift ｜ low strings bloom ｜ soft harmony tail]
[(half-beat breath, piano dips before hook)]
我不想长大
不是怕谁催我回家
是怕木轮停下
才明白你没说完的话

我不想长大
怕再回头只剩牵挂
那辆木车停在墙下
[(chest voice, hold "家", harmony answers softly)]
等不到你喊我回家

[Outro ｜ energy falls ｜ solo piano and music box ｜ dry vocal tail]
木轮轻轻转一圈
像你喊我回家
我终于不再顶嘴
[(soft final line, short dry ending, leave silence)]
可你听不见我回答
```

## 演唱控制评审报告

```text
评审模式：本地诊断评分。未调用独立 Agent，不能冒充正式隔离评审。
评审对象：02_Style Prompt + 03_Lyrics / Custom Lyrics
评审结论：允许进入生成测试。
最终得分：95 / 100
等级：顶级定制化配乐提示
```

| 模块 | 满分 | 得分 | 失分说明 |
|---|---:|---:|---|
| A1 曲风/BPM/律动/氛围适配 | 18 | 17 | 70 BPM、片尾亲情慢歌、轻民谣流行贴合歌词；轻微风险是整体偏稳，需要生成时听副歌是否足够抬起。 |
| A2 配器编排/乐器音色精准度 | 16 | 15 | 钢琴、尼龙吉他、木轮 music-box、轻鼓、低弦乐分工清楚；可再细化 bass 进入时机。 |
| A3 全局人声参数 | 14 | 14 | 成年男声、低中音、近麦、轻微沙哑、克制胸声、咬字和尾句都明确。 |
| A4 混音空间/动态/声场规划 | 12 | 11 | 近麦干声、chorus 前置、bridge stripped、final wider 清楚；混响干湿比例未量化，但不影响投喂。 |
| A模块小计 | 60 | 57 |  |
| B1 分段乐器分层适配 | 12 | 11 | Intro/Verse/Pre/Chorus/Bridge/Final/Outro 都有收放；Verse 2 与 Verse 1 区分可以更强一点。 |
| B2 分段人声/呼吸/张力控制 | 12 | 12 | 关键段落有人声距离、呼吸、咬字和张力；行级控制收紧到关键句，避免过控。 |
| B3 hook/和声/尾句特殊处理 | 10 | 9 | “我不想长大”“话”“牵挂”“回家”“回答”均有让位或尾音处理；Final Chorus 和声控制足够克制。 |
| B4 段落过渡/衔接细节 | 6 | 6 | Hook 前半拍呼吸、bridge 前后减配器、outro 留白完整。 |
| B模块小计 | 40 | 38 |  |

基础总分：95 / 100

| AI专项倒扣 | 最高扣减 | 实际扣减 | 证据 |
|---|---:|---:|---|
| 通用模板堆砌 | -4 | 0 | 有木轮 music-box、补丁针线、片尾亲情场景等本歌定制。 |
| 分段控制复制粘贴 | -3 | 0 | 各段落控制有不同距离、配器和动态。 |
| 配器无动态增减 | -2 | 0 | Bridge 减配器，Final Chorus 加低弦乐，Outro 回落。 |
| 缺失气口/和声/长音精控 | -1 | 0 | 核心 hook、尾句、和声、半拍呼吸已标注。 |
| AI专项总扣减 | -10 | 0 |  |

最终得分 = 95 - 0 = 95

不应误扣：
- 钢琴、木吉他、轻鼓、低弦乐是本题材正常选择，不因为通俗就扣分。
- 控制没有逐行铺满，是为了保留歌词呼吸，不属于控制不足。

真实核心短板：
- Verse 2 的编曲返回可以在实际生成时检查是否和 Verse 1 太像。
- 若生成结果副歌抬升不够，可增强 Chorus 2 / Final Chorus 的鼓和弦乐进入，但不建议先把 prompt 写得过满。

给 writer 的交接：
保留：成年男声、近麦、木轮 music-box、克制片尾慢歌、Final Chorus 低弦乐和轻和声。
必须修：本轮已修，无需再打回。
禁止路线：大合唱、宣传片弦乐、spoken 念白控制、过度 R&B 转音、重鼓摇滚化。
是否允许作为最终投喂结果：允许。
```

# 《不想长大》片尾主题曲男女合唱版 Style Prompt 与演唱控制

## 风格提示词

```text
Mandarin nostalgic family end-credit duet ballad, 70 BPM, 4/4, intimate bittersweet childhood memory, light folk-pop warmth, warm felt piano, nylon acoustic guitar, soft brushed drums, subtle upright bass, recurring music-box wooden-wheel motif, thin low strings entering after second chorus, mature male Mandarin baritone and mature female Mandarin mezzo-soprano duet, low-mid vocal ranges, close-mic storytelling, male voice slightly husky and dry, female voice warm slightly breathy and dry, restrained chest voice and chest-mix blend, clear natural consonants, short dry phrase endings, verses alternate lead vocals like two adults remembering the same childhood, pre-choruses tighten with closer solo lead and shorter breaths, choruses open into gentle unison then soft two-part harmony on hook endings, bridge stripped to piano and music box with alternating single-line leads, final chorus wider with low strings bloom, male-female unison on main hook, one soft harmony tail after final "回家", dry intimate room, vocal forward, delicate dynamics, clear hook space, long fading piano outro
```

## 带演唱控制的歌词

```text
[Intro ｜ felt piano ｜ music-box wooden-wheel motif ｜ old room air ｜ no vocal]

[Verse 1 ｜ male lead close dry vocal ｜ sparse piano and nylon guitar ｜ clear consonants]
回老家的车窗上
雾气被我画了又擦
老家没玩具 只有红灯笼
挂在门框摇摇晃晃

[Verse 1B ｜ female lead enters close and soft ｜ same sparse groove ｜ keep narrative plain]
你把药碗推到一旁
笑着搬出木马车
我只顾问它跑不跑
没听见你把咳声藏

[Pre-Chorus ｜ male lead closer ｜ music-box motif returns ｜ gentle tension lift]
木轮咕噜咕噜过院坝
我笑得忘了回家
那时我把你的叮咛
[(short breath, clear consonants on "话")]
听成哄小孩的话

[Chorus 1 ｜ duet unison on hook ｜ soft drums enter ｜ controlled emotional lift]
我不想长大
不是怕谁催我回家
是怕木轮停下
[(duet holds final vowel on "话", short dry fall)]
才听懂你没说完的话

[Chorus 1B ｜ female lead with male low harmony tail ｜ vocal forward ｜ keep hook clear]
我不想长大
怕再也没人等我回家
那枚硬币握到发麻
[(rhyme handoff, female lead clear, male harmony answers softly)]
才懂好运是你的牵挂

[Verse 2 ｜ female lead close narrative vocal ｜ light brush groove ｜ warmer guitar pulse]
我把汤圆戳碎找硬币
偏说好运一定在碗底
你把掌心摊到我眼里
说好运都归你

[Verse 2B ｜ male lead lower and restrained ｜ low strings barely prepare ｜ dry room]
白布系在额上
奶奶低头理衣裳
她说吃饭别挑 夜里关窗
我低着头不敢答腔

[Pre-Chorus 2 ｜ female lead tighter breath ｜ male low pad-like harmony only after line endings ｜ inward tension]
后来补丁磨着手腕
针线密密缝了几圈
没听完的话在耳边
[(slight pause, softer onset, no harmony over the words)]
一针一针疼到今天

[Chorus 2 ｜ duet fuller low end ｜ main hook in unison ｜ harmony only on tail words]
我不想长大
不是怕谁催我回家
是怕木轮停下
[(unison, hold "话", harmony blooms after the word)]
才听懂你没说完的话

[Chorus 2B ｜ male lead first half ｜ female harmony tail ｜ vocal still forward]
我不想长大
怕再也没人等我回家
那枚硬币握到发麻
[(male lead keeps "挂" open, female harmony answers softly)]
才懂好运是你的牵挂

[Bridge ｜ stripped piano and music box ｜ alternating single-line leads ｜ emotional turn]
[Male lead]
如果那天我再慢一点哭
[Female lead]
如果那晚我没那么倔强
[Male lead]
如果我早些听懂
[Female lead ｜ close dry voice, small downward fall]
你把心疼藏得不声不响

[Bridge 2 ｜ both voices closer ｜ no drums ｜ leave air between lines]
[Male lead]
若长大真有答案
[Female lead]
会不会藏在木轮旁
[Male lead]
可我学会说谢谢
[Duet ｜ very soft unison, short breath before line]
已经隔着一座院墙

[Final Chorus ｜ warm final lift ｜ low strings bloom ｜ duet unison with soft two-part harmony tail]
[(half-beat breath, piano dips before hook)]
我不想长大
不是怕谁催我回家
是怕木轮停下
[(duet holds "话", male low harmony stays under female lead)]
才明白你没说完的话

[Final Chorus B ｜ duet wider but restrained ｜ harmony tail after hook lines ｜ clear final rhyme]
我不想长大
怕再回头只剩牵挂
那辆木车停在墙下
[(duet softens, hold "家", one harmony answer after the line)]
等不到你喊我回家

[Outro ｜ energy falls ｜ solo piano and music box ｜ male then female dry vocal tail]
[Male lead]
木轮轻轻转一圈
[Female lead]
像你喊我回家
[Duet ｜ very close, almost whispered singing is not used, keep sung tone]
我终于不再顶嘴
[(soft final line, short dry ending, leave silence)]
可你听不见我回答
```

## 演唱控制评审报告

```text
评审模式：本地诊断评分。按第三阶段小循环执行；未调用独立 Agent，不能冒充正式隔离评审。
评审对象：男女合唱版风格提示词 + 带演唱控制的歌词
评审结论：允许作为第三阶段通过版本。
最终得分：94 / 100
等级：顶级定制化配乐提示
```

| 模块 | 满分 | 得分 | 失分说明 |
|---|---:|---:|---|
| A1 曲风/BPM/律动/氛围适配 | 18 | 17 | 70 BPM、片尾亲情慢歌、轻民谣流行仍适配；合唱版没有改变作品根气质。轻微风险是 duet ballad 容易被模型生成得偏“大”，已用 intimate / restrained 压住。 |
| A2 配器编排/乐器音色精准度 | 16 | 15 | 钢琴、尼龙吉他、木轮 music-box、轻鼓、低弦乐分工清楚；合唱版保留人声空间。Bass 进入点仍未精确到小节级。 |
| A3 人声全局参数 | 14 | 14 | 男中低音与女中低音区分明确，音色、距离、唱法、合唱关系都有约束；没有出现 tenor/mezzo 冲突。 |
| A4 混音空间/动态/声场规划 | 12 | 11 | 近麦干声、尾句和声、Final Chorus 扩宽明确；混响比例仍未量化。 |
| A模块小计 | 60 | 57 |  |
| B1 分段乐器分层适配 | 12 | 11 | Verse 轮唱、Pre 收紧、Chorus 合、Bridge 减配器、Final 扩宽完整；个别段落拆成 Verse 1B/Chorus 1B，平台理解可能略有风险。 |
| B2 分段人声/呼吸/张力控制 | 12 | 12 | 男女主唱分工清楚，Bridge 单句轮唱，Final unison + harmony tail；气口和人声距离有控制。 |
| B3 hook/和声/尾句特殊处理 | 10 | 9 | “话 / 牵挂 / 回家 / 回答”尾音处理清楚；合唱和声只放尾字后，避免遮挡歌词。 |
| B4 段落过渡/衔接细节 | 6 | 5 | Hook 前半拍呼吸、Bridge 留白、Outro 分声部收尾完整；但合唱标签较多，生成稳定性略低于单人版。 |
| B模块小计 | 40 | 37 |  |

基础总分：94 / 100

| AI专项倒扣 | 最高扣减 | 实际扣减 | 证据 |
|---|---:|---:|---|
| 通用模板堆砌 | -4 | 0 | 合唱关系绑定本歌：木轮、回家、迟懂、尾句和声，不是 generic duet。 |
| 分段控制复制粘贴 | -3 | 0 | 男声、女声、合唱、Bridge 轮唱、Outro 收束均有差异。 |
| 配器无动态增减 | -2 | 0 | Bridge 减配器，Final Chorus 加低弦乐，Outro 回落。 |
| 缺失气口/和声/长音精控 | -1 | 0 | Hook 前呼吸、尾音 hold、harmony tail 已标注。 |
| AI专项总扣减 | -10 | 0 |  |

最终得分 = 94 - 0 = 94

不应误扣：
- 男女合唱本身不是“更商业化”的缺点，只要合唱不遮挡核心句，就能增加片尾情绪的公共认领感。
- 钢琴、木吉他、轻鼓和低弦乐仍是本题材正常选择，不因为常见而扣分。

核心缺点：
1. 合唱标签比单人版更多，Suno / 同类模型可能偶尔忽略声部分配。生成后若男女分配不稳，应减少 Verse 1B / Chorus 1B 的标签复杂度。
2. Final Chorus 容易被模型做成大合唱。当前已用 restrained / close-mic / dry intimate room 压住，但生成时仍要听是否过宽。

给 laohu_sing_control_writer 的交接单：
保留：男女低中音区、近麦、主歌轮唱、副歌轻合、Bridge 单句轮唱、Final Chorus 尾句和声。
必须修：本轮已修，无需打回。
禁止路线：晚会合唱、大合唱、男高女高飙音、spoken / almost spoken、过度 R&B 转音、厚弦乐宣传片化。
是否允许作为最终投喂结果：允许。
```

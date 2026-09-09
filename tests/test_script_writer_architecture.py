from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptWriterArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def combined(self, *relatives: str) -> str:
        return "\n".join(self.writer_with_routed_methods() if relative == 'skills/laohu-script-writer/SKILL.md' else self.read(relative) for relative in relatives)

    def writer_with_routed_methods(self) -> str:
        """Behavior anchors belong to the actual routed owners, not all to the router body."""
        from scripts.validate_capability_architecture import reachable_documents
        entry = ROOT / 'skills/laohu-script-writer/SKILL.md'
        return '\n'.join(p.read_text() for p in sorted(reachable_documents(entry)))

    def test_script_writer_routes_story_gaps_to_component_search(self) -> None:
        writer = self.writer_with_routed_methods()
        for anchor in (
            "故事构件查询合同",
            "story_component_library.py",
            "stats → search → get",
            "允许零采用并继续原创",
            "构件调用回执",
        ):
            self.assertIn(anchor, writer)

    def test_material_atoms_and_story_components_have_separate_owners(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-story-material/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
        )
        self.assertIn("素材原子提供生活证据，故事构件提供状态变化方式", text)
        self.assertIn("source / atom / usage", text)
        self.assertIn("不改变素材库", text)
        self.assertIn("不保存私人原话", text)

    def test_component_candidates_require_causal_edges_and_character_intention(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md"
        )
        for anchor in (
            "前置条件 → 人物行动 → 状态变化 → 观众更新 → 下一压力",
            "人物行动理由",
            "三个因果真正不同",
            "已锁定人物、高潮和结尾只比较剩余因果实现",
            "替换职业、地点和道具不算因果不同",
            "并排堆叠",
        ):
            self.assertIn(anchor, reference)

    def test_expectation_contract_tracks_evidence_prediction_pressure_and_payoff(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/04_叙事视角命名与故事因果.md",
        )
        self.assertIn(
            "可见证据 → 暂时判断 → 可预见压力 → 未揭变量 → 部分兑现",
            text,
        )
        for anchor in ("主要注意入口", "承诺—兑现账本", "完成 / 扩大 / 推翻 / 重新解释"):
            self.assertIn(anchor, text)

    def test_scene_fusion_requires_one_bearing_action_and_one_primary_result(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md"
        )
        for anchor in (
            "场景融合",
            "同一承重行动",
            "一个主要状态结果",
            "争夺主结果",
            "拆场或淘汰",
        ):
            self.assertIn(anchor, reference)

    def test_formal_screenplay_separates_body_from_production_evidence(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
        )
        for anchor in (
            "剧本正文",
            "生产证据账本",
            "【声音：声源、发生方式和对行动的影响】",
            "【场次结果】",
            "出现前状态",
            "出现后状态",
            "连续性风险",
        ):
            self.assertIn(anchor, text)

    def test_formal_screenplay_contains_readable_brief_and_numbered_shots(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
        )
        for anchor in (
            "【剧本说明】",
            "【作品信息】",
            "【故事说明】",
            "【E01-S01-C01｜中景｜运镜：固定镜头｜机位：圆台南侧，朝北看向双人关系轴｜构图：Luna左侧、老胡右侧｜约4秒】",
            "所有观众会看到或听到的正文必须归入一个镜号",
            "景别是镜头属性，不是编号",
        ):
            self.assertIn(anchor, text)
        self.assertNotIn("【镜1｜E01-S01-C01", text)
        self.assertNotIn("普通正式剧本不强制焦段、景别和机位", text)

    def test_scene_local_shot_ids_replace_redundant_global_shot_labels(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
        )
        for anchor in (
            "Episode",
            "Scene",
            "Camera Shot",
            "进入新场后从 `C01` 重新编号",
            "不再额外添加全片连续",
        ):
            self.assertIn(anchor, text)

    def test_screenplay_body_keeps_visible_prose_and_video_owns_camera_execution(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "偏小说性的可见结果语言",
            "不重复编译摄影机路径",
            "详细摄影机执行",
            "laohu-video-prompt",
        ):
            self.assertIn(anchor, text)

    def test_multi_character_action_paragraphs_anchor_names_before_pronouns(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "人物指代锚点",
            "第一次出现人物时先写具体名称",
            "叙述主体切换",
            "重新写具体名称",
        ):
            self.assertIn(anchor, text)

    def test_comedy_mishearing_selects_phonetic_and_non_phonetic_methods(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/skills/laohu-dialogue/references/喜剧场面与传播.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "自然同音或近音",
            "现场发音与句法",
            "双重语义",
            "断句换义",
            "对象偷换",
            "字面执行",
            "改变下一动作",
        ):
            self.assertIn(anchor, text)

    def test_teaching_comedy_protects_learning_and_human_reaction(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/喜剧场面与传播.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "知识线是不可补偿的主任务",
            "教学喜剧的对白场景合同",
            "本段唯一主喜剧引擎",
            "已确认的 3–8 句原话",
            "纯对白盲听",
            "悬空机灵",
            "作者腹语",
            "不是配额",
            "不得把结构测试通过",
        ):
            self.assertIn(anchor, text)

    def test_screen_relationship_maps_world_camera_and_screen_without_numeric_rigging(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md"
        )
        for anchor in (
            "世界层",
            "摄影机层",
            "画面层",
            "世界位置 → 摄影机观看侧 / 视轴 → 画面左中右与前中后景",
            "画面位置",
            "身体朝向",
            "视线对象",
            "遮挡",
            "关系距离",
            "设备坐标",
            "POV",
            "过肩",
        ):
            self.assertIn(anchor, reference)
        self.assertIn("不自动等于", reference)
        self.assertIn("不能只靠“左前景 / 右后景”假定机位已经成立", reference)

    def test_script_shot_header_exposes_viewpoint_and_composition_before_body(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "编号｜景别｜运镜｜机位 / 视轴｜构图｜参考时长",
            "机位是原因，构图是画面结果",
            "摄影机从哪里朝哪里看",
            "不重复方头已经锁定的静态机位",
        ):
            self.assertIn(anchor, text)

    def test_comedy_can_recur_as_varied_relationship_engine_without_becoming_a_quota(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/喜剧场面与传播.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "明知原义、故意换义",
            "先让观众听懂知识原义",
            "变奏式回声",
            "禁止机械排班",
            "不能因一次过量失败就被一刀切删除",
        ):
            self.assertIn(anchor, text)

    def test_emotion_handoff_carries_state_trigger_and_playable_evidence(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
            "skills/laohu-video-prompt/references/01_文戏对白与人物表演.md",
        )
        for anchor in (
            "情绪交接合同",
            "情绪阶段",
            "关系目的",
            "精确触发",
            "可见泄露",
            "禁止提前反应",
            "声音放低、句子很短",
            "笑意开始发虚",
            "返回编剧",
        ):
            self.assertIn(anchor, text)

    def test_spoken_performance_contract_allows_explicit_scene_baseline(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "每句有声台词",
            "声源位置不等于表演状态",
            "声源 / 情绪阶段 / 关系目的 / 可听语气",
            "本场基线",
            "不得只写 `O.S. / V.O. / 远处`",
        ):
            self.assertIn(anchor, text)

    def test_bearing_action_hands_off_cause_process_environment_and_result(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
            "skills/laohu-video-prompt/references/02_动作打斗追逐与力量奇观.md",
        )
        for anchor in (
            "动作因果交接合同",
            "世界能力基线",
            "起始条件",
            "发力来源",
            "能力触发",
            "运动路径",
            "环境交互",
            "接触点",
            "受力结果",
            "镜尾把手",
            "剧本锁因果，提示词扩颗粒",
        ):
            self.assertIn(anchor, text)

    def test_public_performance_example_has_no_bare_dialogue_or_source_only_cue(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md"
        )
        # Public regression tests must remain runnable without local work files.
        section = reference.split("括号保持短", 1)[1]
        script = section.split("```text\n", 1)[1].split("```", 1)[0]
        dialogue = re.findall(r"(?m)^(?:Luna|老胡)（[^\n]+）：.+$", script)
        self.assertEqual(2, len(dialogue), "performance example must contain both speakers")
        bare_dialogue = re.findall(r"(?m)^(?:Luna|老胡)：.+$", script)
        source_only = re.findall(
            r"(?m)^(?:Luna|老胡)（(?:O\.S\.|V\.O\.|远处)）：.+$",
            script,
        )
        self.assertEqual([], bare_dialogue)
        self.assertEqual([], source_only)

    def test_confirmed_wordplay_survives_into_the_action_it_promises(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "语言机关兑现合同",
            "已确认原词",
            "人物故意换义",
            "下一动作",
            "动作结果",
            "跨镜头保留项",
            "下一镜不得退回普通招式名",
        ):
            self.assertIn(anchor, text)

    def test_fixed_closeup_cannot_gain_an_unintroduced_background_actor(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md"
        )
        for anchor in (
            "固定镜头、人物入画与景别证据边界",
            "人物从开镜起已经可见",
            "人物由画外进入",
            "人物始终不入画",
            "固定近景先说",
            "保持助手 O.S.",
            "新双人镜头",
        ):
            self.assertIn(anchor, reference)

    def test_script_owns_shot_facts_assets_stabilize_and_video_compiles(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-set-design/SKILL.md",
            "skills/laohu-visual-assets/SKILL.md",
            "skills/laohu-video-prompt/SKILL.md",
        )
        for anchor in (
            "镜头化内容母版",
            "稳定视觉形态",
            "镜头继承合同",
            "组成 E-S-B 批次",
            "三段式执行语言",
            "不第一次发明",
        ):
            self.assertIn(anchor, text)

    def test_video_capabilities_are_recompiled_upstream_without_turning_script_into_prompt(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md"
        )
        for anchor in (
            "镜头原子与观看任务",
            "世界—摄影机—画面空间",
            "信息拓扑 → 视窗 / 版式观看范围 → 屏幕层级与焦点",
            "动作与道具因果",
            "人物表演",
            "声音与必要特效",
            "光线变化",
            "相邻镜头交接",
            "以下内容不迁入剧本正文",
            "E-S-B 批次组合",
            "正式三段式",
            "VC 提纯",
        ):
            self.assertIn(anchor, reference)
        self.assertIn("不能为了统一术语，给二维内容强造摄影机", reference)

    def test_performable_psychology_supports_but_never_replaces_screen_evidence(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md"
        )
        self.assertNotIn("不写心理描写，只写能被看见或听见的内容", reference)
        for anchor in (
            "可表演的心理解释",
            "不能代替画面",
            "可见或可听证据",
            "行动后果",
            "每句有声台词",
            "本场基线",
        ):
            self.assertIn(anchor, reference)

    def test_storyboard_is_integrated_and_video_prompt_preserves_source_mapping(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md",
            "skills/laohu-video-prompt/SKILL.md",
        )
        for anchor in (
            "文字分镜并入正式剧本",
            "取消独立分镜宏观表",
            "剧本镜号来源映射",
            "拆镜、并镜",
            "返回编剧",
        ):
            self.assertIn(anchor, text)

    def test_complete_lighting_sample_uses_shots_as_the_only_body_container(self) -> None:
        sample = self.read(
            "04_诊断与系统日志/2026-09-05_镜头化剧本完整验证样例.md"
        )
        first_shot = sample.index("【E01-S01-C01")
        first_action = sample.index("△")
        self.assertLess(first_shot, first_action)
        self.assertNotRegex(sample, r"【镜\d+｜E\d+-S\d+-C\d+")
        ids = re.findall(r"E01-S01-C(\d{2})", sample)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, [f"{number:02d}" for number in range(1, len(ids) + 1)])
        for anchor in (
            "遥控器一直在露娜右手里",
            "老胡空手",
            "测试摄影机",
            "节目镜头",
            "监视器",
            "三角油光",
            "【场次结果】",
        ):
            self.assertIn(anchor, sample)
        self.assertNotIn("镜头作用：", sample)
        self.assertNotRegex(sample, r"摄影机.{0,12}(45度|\d+(?:\.\d+)?米)")

    def test_low_intensity_story_may_reject_component_stacking(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        self.assertIn("低烈度", text)
        self.assertIn("等待、距离、误解、表演", text)
        self.assertIn("不为连续反转强行堆叠", text)

    def test_empty_or_unfit_component_results_allow_original_writing(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
        )
        self.assertIn("允许零采用并继续原创", text)
        self.assertIn("构件库为空", text)
        self.assertIn("不得自动网络搜索", text)

    def test_character_voice_starts_with_perception_and_interpretation(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
        )
        for anchor in (
            "人物声音合同",
            "他优先注意什么",
            "他会怎样解释证据",
            "他最不愿直接说出什么",
            "未说出的普通愿望",
        ):
            self.assertIn(anchor, text)
        self.assertIn("口头禅、方言词和金句都不能单独证明人物", text)

    def test_professional_perception_requires_grounded_expertise(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md"
        )
        for anchor in (
            "职业化感知",
            "前史、训练或当场证据",
            "普通人不会优先注意",
            "不可信的超能力",
        ):
            self.assertIn(anchor, reference)

    def test_related_words_change_meaning_without_random_metaphor_stacking(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md"
        )
        for anchor in (
            "同组词语换义",
            "同一条人物矛盾",
            "新指向",
            "随机更换漂亮意象",
        ):
            self.assertIn(anchor, reference)

    def test_voiceover_adds_information_and_stylish_prose_must_change_scene_state(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/skills/laohu-dialogue/references/本地对白与表演补充.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "补充 / 对位 / 反差",
            "不同义复述画面",
            "感知证据 → 人物解释 → 当场行动 → 可见后果",
            "删掉漂亮独白",
            "人物选择和场次状态不变",
        ):
            self.assertIn(anchor, text)


if __name__ == "__main__":
    unittest.main()

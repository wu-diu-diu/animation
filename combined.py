"""
天线阻抗失配导致功放烧毁 — 工程科普动画（完整版）
使用 Manim CE v0.20.1, 1920x1080 @ 60fps

渲染命令：manim render -q h combined.py AntennaMismatchCombined
"""

from manim import *
import numpy as np

# ═══════════════════════════════════════════════════════════════
# 画面配置
# ═══════════════════════════════════════════════════════════════
config.background_color = "#080c1a"
config.frame_rate = 60
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_height = 8.0
config.frame_width = 14.222

# ═══════════════════════════════════════════════════════════════
# 颜色调色板
# ═══════════════════════════════════════════════════════════════
BG_COLOR          = "#080c1a"
FORWARD_COLOR     = "#00e5cc"
REFLECTED_COLOR   = "#ff4060"
STANDING_COLOR    = "#b066ff"
PA_BODY_COLOR     = "#1a2a3a"
PA_ACCENT         = "#336699"
ANTENNA_OK        = "#22cc66"
ANTENNA_BAD       = "#cc2244"
LINE_COLOR        = "#335577"
LINE_GLOW         = "#5588bb"
TEXT_PRIMARY      = "#ddeeff"
TEXT_SECONDARY    = "#8899bb"
WARNING_COLOR     = "#ff7733"
DANGER_COLOR      = "#ff2222"
WHITE_HOT         = "#ffffff"
PANEL_BG          = "#0d1225"
PANEL_BORDER      = "#1a3050"

# ═══════════════════════════════════════════════════════════════
# 画面布局
# ═══════════════════════════════════════════════════════════════
PA_X         = -4.8
PA_W, PA_H  = 1.8, 2.4
TL_LEFT      = -3.0
TL_RIGHT     = 3.0
TL_Y         = 0.0
ANT_X        = 4.8
ANT_W, ANT_H = 1.4, 2.8
TOP_Y        = 2.9
BOT_Y        = -3.0

# 波动物理参数
K      = 2.2
OMEGA  = 4.0
AMP    = 1.05
N_WAVE_PTS = 300

# ═══════════════════════════════════════════════════════════════
# 波形绘制：发光效果
# ═══════════════════════════════════════════════════════════════

def glow_wave_layers(x_min, x_max, wave_fn, color, glow_count=3):
    layers_def = [
        (14, 0.06),
        (8,  0.14),
        (4,  0.30),
        (2,  0.75),
    ]
    layers = []
    for stroke_w, opacity in layers_def[:glow_count + 1]:
        def make_layer(sw=stroke_w, op=opacity):
            return always_redraw(lambda:
                FunctionGraph(
                    lambda x: wave_fn(x),
                    x_range=[x_min, x_max],
                    color=color,
                    stroke_width=sw,
                    stroke_opacity=op,
                )
            )
        layers.append(make_layer())
    return VGroup(*layers)


def single_wave(x_min, x_max, wave_fn, color, stroke_w=3, opacity=0.85):
    def make_single(sw=stroke_w, op=opacity):
        return always_redraw(lambda:
            FunctionGraph(
                lambda x: wave_fn(x),
                x_range=[x_min, x_max],
                color=color,
                stroke_width=sw,
                stroke_opacity=op,
            )
        )
    return make_single()

# ═══════════════════════════════════════════════════════════════
# UI 组件
# ═══════════════════════════════════════════════════════════════

def build_pa_module():
    body = RoundedRectangle(
        width=PA_W, height=PA_H,
        fill_color=PA_BODY_COLOR, fill_opacity=0.85,
        stroke_color=PA_ACCENT, stroke_width=1.5,
        corner_radius=0.15,
    )
    label = Text("功放", font="sans-serif", font_size=28, color=TEXT_PRIMARY)
    mos_label = Text("MOSFET", font="sans-serif", font_size=14,
                     color=TEXT_SECONDARY).next_to(label, DOWN, buff=0.1)
    title_group = VGroup(label, mos_label)
    title_group.move_to(body.get_center())
    group = VGroup(body, title_group)
    group.move_to([PA_X, 0, 0])
    return group, body, label


def build_antenna():
    body = RoundedRectangle(
        width=ANT_W, height=ANT_H,
        fill_color=ANTENNA_OK, fill_opacity=0.7,
        stroke_color=ANTENNA_OK, stroke_width=1.5,
        corner_radius=0.15,
    )
    label = Text("天线", font="sans-serif", font_size=22, color=TEXT_PRIMARY)
    z_label = Text("50Ω", font="sans-serif", font_size=16,
                   color=TEXT_SECONDARY).next_to(label, DOWN, buff=0.1)
    title_group = VGroup(label, z_label)
    title_group.move_to(body.get_center())
    group = VGroup(body, title_group)
    group.move_to([ANT_X, 0, 0])
    return group, body, label, z_label


def build_transmission_line():
    TL_GAP = 0.65
    top_line = Line(
        [TL_LEFT - 0.3, TL_Y + TL_GAP, 0],
        [TL_RIGHT + 0.3, TL_Y + TL_GAP, 0],
        color=LINE_GLOW, stroke_width=1.8,
    )
    bot_line = Line(
        [TL_LEFT - 0.3, TL_Y - TL_GAP, 0],
        [TL_RIGHT + 0.3, TL_Y - TL_GAP, 0],
        color=LINE_GLOW, stroke_width=1.8,
    )
    fill_rect = Rectangle(
        width=TL_RIGHT - TL_LEFT, height=TL_GAP * 2,
        fill_color=LINE_COLOR, fill_opacity=0.12,
        stroke_width=0,
    )
    fill_rect.move_to([(TL_LEFT + TL_RIGHT) / 2, TL_Y, 0])
    ticks = VGroup()
    for i in range(7):
        x = TL_LEFT + i * (TL_RIGHT - TL_LEFT) / 6
        tick = Line([x, TL_Y + TL_GAP, 0], [x, TL_Y - TL_GAP, 0],
                    color=LINE_GLOW, stroke_width=0.5, stroke_opacity=0.35)
        ticks.add(tick)
    z0_label = Text("Z₀ = 50Ω", font="sans-serif", font_size=14,
                    color=TEXT_SECONDARY)
    z0_label.next_to([TL_LEFT + 3, TL_Y + TL_GAP + 0.3, 0], LEFT, buff=0.15)
    return VGroup(fill_rect, top_line, bot_line, ticks, z0_label)


def build_param_panel():
    panel_w = 12.0
    panel_h = 0.9
    panel = RoundedRectangle(
        width=panel_w, height=panel_h,
        fill_color=PANEL_BG, fill_opacity=0.7,
        stroke_color=PANEL_BORDER, stroke_width=0.8,
        corner_radius=0.1,
    )
    panel.move_to([0, TOP_Y, 0])
    z0    = Tex(r"$Z_0 = 50\Omega$", font_size=28, color=TEXT_SECONDARY)
    zl    = Tex(r"$Z_L = 50\Omega$", font_size=28, color=TEXT_SECONDARY)
    gamma = Tex(r"$\Gamma = 0.00$", font_size=28, color=TEXT_SECONDARY)
    vswr  = Tex(r"$\mathrm{VSWR} = 1.00$", font_size=28, color=TEXT_SECONDARY)
    params = VGroup(z0, zl, gamma, vswr)
    params.arrange(RIGHT, buff=0.7)
    params.move_to(panel.get_center())
    group = VGroup(panel, params)
    return group, {"z0": z0, "zl": zl, "gamma": gamma, "vswr": vswr}


def build_status_line():
    txt = Text("", font="sans-serif", font_size=22, color=TEXT_PRIMARY)
    txt.move_to([0, BOT_Y, 0])
    return txt


# ═══════════════════════════════════════════════════════════════
# 波动物理函数
# ═══════════════════════════════════════════════════════════════

def wave_forward(x, t, amp=AMP, k=K, omega=OMEGA):
    return amp * np.sin(k * x - omega * t)


def wave_reflected(x, t, gamma, amp=AMP, k=K, omega=OMEGA, boundary=TL_RIGHT):
    return gamma * amp * np.sin(k * (2 * boundary - x) - omega * t)


def wave_total(x, t, gamma, amp=AMP, k=K, omega=OMEGA, boundary=TL_RIGHT):
    return wave_forward(x, t, amp, k, omega) + wave_reflected(x, t, gamma, amp, k, omega, boundary)


# ═══════════════════════════════════════════════════════════════
# 完整动画（8 个场景连续播放）
# ═══════════════════════════════════════════════════════════════

class AntennaMismatchCombined(MovingCameraScene):
    def construct(self):
        # ── 全局 tracker ──
        self.time_tracker = ValueTracker(0)
        self.gamma_tracker = ValueTracker(0.0)
        self.forward_amp = ValueTracker(AMP)
        self.collapse_tracker = ValueTracker(1.0)
        self._time_updater_added = False

        # ── 播放所有场景 ──
        self.scene_01_title()
        self.scene_02_normal_match()
        self.scene_03_mismatch()
        self.scene_04_reflected_wave()
        self.scene_05_standing_wave()
        self.scene_06_overvoltage()
        self.scene_07_failure()
        self.scene_08_summary()

    # ═══════════════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════════════

    def _current_gamma(self):
        return self.gamma_tracker.get_value()

    def _fwd_fn(self):
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_forward(x, self.time_tracker.get_value(), amp=amp)

    def _ref_fn(self):
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_reflected(x, self.time_tracker.get_value(),
                                              gamma=self._current_gamma(), amp=amp)

    def _tot_fn(self):
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_total(x, self.time_tracker.get_value(),
                                          gamma=self._current_gamma(), amp=amp)

    def _start_wave_time(self):
        if not self._time_updater_added:
            self.time_tracker.add_updater(lambda m, dt: m.increment_value(dt))
            self._time_updater_added = True

    def _update_param_texts(self, z0_str, zl_str, gamma_str, vswr_str):
        """以面板中心为锚点更新参数，避免漂移。"""
        new_z0    = Tex(z0_str,    font_size=28, color=TEXT_SECONDARY)
        new_zl    = Tex(zl_str,    font_size=28, color=TEXT_SECONDARY)
        new_gamma = Tex(gamma_str, font_size=28, color=TEXT_SECONDARY)
        new_vswr  = Tex(vswr_str,  font_size=28, color=TEXT_SECONDARY)
        new_group = VGroup(new_z0, new_zl, new_gamma, new_vswr)
        new_group.arrange(RIGHT, buff=0.7)
        new_group.move_to([0, TOP_Y, 0])  # 固定锚点
        self.play(
            Transform(self.params["z0"], new_z0, replace_mobject_with_target_in_scene=True),
            Transform(self.params["zl"], new_zl, replace_mobject_with_target_in_scene=True),
            Transform(self.params["gamma"], new_gamma, replace_mobject_with_target_in_scene=True),
            Transform(self.params["vswr"], new_vswr, replace_mobject_with_target_in_scene=True),
            run_time=1.5,
        )
        self.params["z0"]    = new_z0
        self.params["zl"]    = new_zl
        self.params["gamma"] = new_gamma
        self.params["vswr"]  = new_vswr

    def _make_status_math(self, ch_text, math_str, color):
        """创建「中文 + LaTeX 公式」组合状态栏。"""
        ch = Text(ch_text, font="sans-serif", font_size=20, color=color)
        m = MathTex(math_str, font_size=28, color=color)
        return VGroup(ch, m).arrange(RIGHT, buff=0.15)

    # ═══════════════════════════════════════════════════════════
    # 场景1：标题
    # ═══════════════════════════════════════════════════════════

    def scene_01_title(self):
        title = Text("为什么天线失配会烧毁功放？",
                     font="sans-serif", font_size=48, color=TEXT_PRIMARY)
        title.set_stroke(BLUE_D, width=0.5, opacity=0.5)
        sub = Text("传输线反射与功放失效", font="sans-serif", font_size=24,
                   color=TEXT_SECONDARY)
        sub.next_to(title, DOWN, buff=0.3)
        glow = title.copy().set_stroke(BLUE_C, width=8, opacity=0.25)
        group = VGroup(glow, title, sub)
        group.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.3), FadeIn(sub, shift=UP * 0.2),
                  FadeIn(glow, shift=UP * 0.3), run_time=1.5)
        self.play(
            title.animate.scale(1.03).set_stroke(BLUE_C, width=1.5, opacity=0.5),
            glow.animate.scale(1.03).set_stroke(BLUE_C, width=10, opacity=0.3),
            rate_func=there_and_back, run_time=2.0,
        )
        self.wait(0.5)
        self.play(FadeOut(group), run_time=0.6)

    # ═══════════════════════════════════════════════════════════
    # 场景2：正常匹配
    # ═══════════════════════════════════════════════════════════

    def scene_02_normal_match(self):
        # 构建所有 UI
        self.pa_group, self.pa_body, _ = build_pa_module()
        self.ant_group, self.ant_body, _, self.ant_z = build_antenna()
        self.tl_group = build_transmission_line()
        self.panel_group, self.params = build_param_panel()
        self.status_mob = build_status_line()

        self.play(
            FadeIn(self.pa_group), FadeIn(self.ant_group),
            FadeIn(self.tl_group), FadeIn(self.panel_group),
            run_time=1.0,
        )
        status_text = Text("所有功率被天线吸收并辐射", font="sans-serif",
                           font_size=20, color=TEXT_PRIMARY)
        status_text.move_to([0, BOT_Y, 0])
        self.play(FadeIn(status_text), run_time=0.5)
        self.status_mob = status_text

        # 前向波
        self._start_wave_time()
        fwd_wave = glow_wave_layers(TL_LEFT, TL_RIGHT, self._fwd_fn(), FORWARD_COLOR)
        self.add(fwd_wave)
        self.wait(5.5)

        # 天线辐射波纹
        ripple_circles = VGroup()
        for i in range(4):
            c = Circle(radius=0.25 + i * 0.35,
                       stroke_color=ANTENNA_OK, stroke_width=3.5,
                       stroke_opacity=0.7 - i * 0.15, fill_opacity=0)
            c.move_to(self.ant_body.get_center())
            ripple_circles.add(c)
        self.play(LaggedStart(
            *[GrowFromCenter(c) for c in ripple_circles], lag_ratio=0.3,
        ), run_time=2.0)
        self.play(FadeOut(ripple_circles), run_time=0.5)
        self.wait(0.5)
        self.remove(fwd_wave)

    # ═══════════════════════════════════════════════════════════
    # 场景3：发生失配
    # ═══════════════════════════════════════════════════════════

    def scene_03_mismatch(self):
        # 天线变红 + 警告
        warn = Text("⚠", font="sans-serif", font_size=36, color=WARNING_COLOR)
        warn.move_to(self.ant_body.get_center() + UP * 1.0)
        self.play(
            self.ant_body.animate.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD),
            Transform(self.ant_z, Tex(r"$Z_L = \infty\Omega$", font_size=22,
                                      color=WARNING_COLOR),
                      replace_mobject_with_target_in_scene=True),
            FadeIn(warn, scale=1.5),
            run_time=1.5,
        )

        # 底部状态
        new_status = self._make_status_math("天线阻抗失配！", r"Z_L \to \infty", WARNING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status_mob, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.8)
        self.status_mob = new_status

        # 反射系数公式
        gamma_formula = MathTex(
            r"\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}",
            font_size=36, color=TEXT_PRIMARY,
        )
        gamma_formula.move_to([0, TOP_Y - 1.0, 0])
        self.play(Write(gamma_formula), run_time=1.0)

        self.play(self.gamma_tracker.animate.set_value(1.0),
                  run_time=2.0, rate_func=smooth)

        self._update_param_texts(
            r"$Z_0 = 50\Omega$", r"$Z_L = \infty\Omega$",
            r"$\Gamma = 1.00$", r"$\mathrm{VSWR} = \infty$",
        )
        self.wait(0.5)
        self.play(FadeOut(gamma_formula), run_time=0.5)

    # ═══════════════════════════════════════════════════════════
    # 场景4：反射波形成
    # ═══════════════════════════════════════════════════════════

    def scene_04_reflected_wave(self):
        # 前向波
        self._start_wave_time()
        fwd = glow_wave_layers(TL_LEFT, TL_RIGHT, self._fwd_fn(), FORWARD_COLOR)
        self.add(fwd)
        self.wait(1.5)

        # 反射波
        ref = glow_wave_layers(TL_LEFT, TL_RIGHT, self._ref_fn(), REFLECTED_COLOR)
        self.play(FadeIn(ref), run_time=1.0)

        # 方向箭头
        fwd_arrow = Arrow(LEFT * 1.5, RIGHT * 1.5,
                          color=FORWARD_COLOR, stroke_width=3,
                          max_tip_length_to_length_ratio=0.15)
        fwd_arrow.next_to([TL_LEFT + 1.0, TL_Y + 1.6, 0], RIGHT, buff=0)
        fwd_label = Text("入射波", font="sans-serif", font_size=16,
                          color=FORWARD_COLOR).next_to(fwd_arrow, UP, buff=0.1)

        ref_arrow = Arrow(RIGHT * 1.5, LEFT * 1.5,
                          color=REFLECTED_COLOR, stroke_width=3,
                          max_tip_length_to_length_ratio=0.15)
        ref_arrow.next_to([TL_RIGHT - 1.0, TL_Y + 1.6, 0], LEFT, buff=0)
        ref_label = Text("反射波", font="sans-serif", font_size=16,
                          color=REFLECTED_COLOR).next_to(ref_arrow, UP, buff=0.1)

        self.play(FadeIn(fwd_arrow), FadeIn(fwd_label),
                  FadeIn(ref_arrow), FadeIn(ref_label), run_time=0.8)

        # 功率显示：入射靠左，反射靠右
        pf_math = MathTex(r"P_f = ", font_size=28, color=FORWARD_COLOR)
        pf_text = Text("入射功率", font="sans-serif", font_size=24, color=FORWARD_COLOR)
        pf_combined = VGroup(pf_math, pf_text).arrange(RIGHT, buff=0.1)
        pf_combined.move_to([TL_LEFT - 0.5, TOP_Y - 1.2, 0])

        pr_math = MathTex(r"P_r = ", font_size=28, color=REFLECTED_COLOR)
        pr_text = Text("反射功率", font="sans-serif", font_size=24, color=REFLECTED_COLOR)
        pr_combined = VGroup(pr_math, pr_text).arrange(RIGHT, buff=0.1)
        pr_combined.move_to([TL_RIGHT + 0.5, TOP_Y - 1.2, 0])

        self.play(Write(pf_combined), run_time=0.5)
        self.play(Write(pr_combined), run_time=0.5)

        new_status = Text("Pr 增加中... 反射功率返回功放", font="sans-serif",
                          font_size=20, color=WARNING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status_mob, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)
        self.status_mob = new_status

        self.wait(4.0)

        self.play(FadeOut(fwd_arrow), FadeOut(fwd_label),
                  FadeOut(ref_arrow), FadeOut(ref_label),
                  FadeOut(pf_combined), FadeOut(pr_combined), run_time=0.5)
        self.remove(fwd, ref)

    # ═══════════════════════════════════════════════════════════
    # 场景5：驻波形成
    # ═══════════════════════════════════════════════════════════

    def scene_05_standing_wave(self):
        standing_formula = MathTex(
            r"V(z,t) = V_f \cos(\omega t - \beta z) + V_r \cos(\omega t + \beta z)",
            font_size=30, color=TEXT_PRIMARY,
        )
        standing_formula.move_to([0, TOP_Y - 1.2, 0])
        self.play(Write(standing_formula), run_time=1.0)

        self._start_wave_time()
        sw = glow_wave_layers(TL_LEFT, TL_RIGHT, self._tot_fn(),
                              STANDING_COLOR, glow_count=4)
        self.play(FadeIn(sw), run_time=1.0)

        new_status = Text("驻波形成 — 节点与腹点", font="sans-serif",
                          font_size=20, color=STANDING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status_mob, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)
        self.status_mob = new_status

        # 节点
        nodes_x = []
        for n in range(-3, 4):
            xn = n * np.pi / K
            if TL_LEFT <= xn <= TL_RIGHT:
                nodes_x.append(xn)

        node_dots = VGroup()
        antinode_dots = VGroup()
        node_labels = VGroup()
        anti_labels = VGroup()

        for xn in nodes_x:
            d = Dot([xn, TL_Y, 0], color="#111122", radius=0.08,
                   stroke_color=STANDING_COLOR, stroke_width=1.0)
            node_dots.add(d)
            nl = Text("节点", font="sans-serif", font_size=10,
                      color=TEXT_SECONDARY).next_to(d, DOWN, buff=0.15)
            node_labels.add(nl)

        for i in range(len(nodes_x) - 1):
            xa = (nodes_x[i] + nodes_x[i + 1]) / 2
            d = Dot([xa, TL_Y, 0], color=STANDING_COLOR, radius=0.1,
                   stroke_color=WHITE, stroke_width=0.8)
            antinode_dots.add(d)
            al = Text("腹点", font="sans-serif", font_size=10,
                      color=STANDING_COLOR).next_to(d, UP, buff=0.15)
            anti_labels.add(al)

        self.play(FadeIn(node_dots), FadeIn(antinode_dots),
                  FadeIn(node_labels), FadeIn(anti_labels), run_time=1.0)

        self._update_param_texts(
            r"$Z_0 = 50\Omega$", r"$Z_L = \infty\Omega$",
            r"$\Gamma = 1.00$", r"$\mathrm{VSWR} \to \infty$",
        )
        self.wait(2.0)

        self.play(FadeOut(standing_formula), FadeOut(node_dots),
                  FadeOut(antinode_dots), FadeOut(node_labels),
                  FadeOut(anti_labels), run_time=0.5)
        self.remove(sw)

    # ═══════════════════════════════════════════════════════════
    # 场景6：功放端过压
    # ═══════════════════════════════════════════════════════════

    def scene_06_overvoltage(self):
        # 驻波
        self._start_wave_time()
        sw = glow_wave_layers(TL_LEFT, TL_RIGHT, self._tot_fn(),
                              STANDING_COLOR, glow_count=4)
        self.add(sw)

        # 镜头 zoom 到功放
        self.play(
            self.camera.frame.animate.scale(0.55).move_to([PA_X + 0.5, TL_Y, 0]),
            run_time=2.0,
        )

        vmax_formula = MathTex(
            r"V_{\mathrm{max}} = V_0 (1 + |\Gamma|)",
            font_size=32, color=TEXT_PRIMARY,
        )
        vmax_formula.move_to([PA_X + 0.5, TOP_Y - 1.0, 0])
        self.play(Write(vmax_formula), run_time=0.8)

        voltage_tex = MathTex("V_{\mathrm{peak}} = 100\,\mathrm{V}",
                              font_size=42, color=TEXT_PRIMARY)
        voltage_tex.move_to([PA_X + 0.5, TL_Y - 1.8, 0])
        self.play(Write(voltage_tex), run_time=0.5)

        breakdown_tex = MathTex(
            r"\mathrm{MOSFET\ Breakdown} = 150\,\mathrm{V}",
            font_size=28, color=WARNING_COLOR,
        )
        breakdown_tex.next_to(voltage_tex, DOWN, buff=0.3)

        pa_glow = self.pa_body.copy()
        pa_glow.set_fill_color(DANGER_COLOR).set_fill_opacity(0)
        pa_glow.set_stroke_color(DANGER_COLOR).set_stroke_width(4).set_stroke_opacity(0)
        self.add(pa_glow)

        breakdown_v = 150
        for v in [100, 120, 160, 200, 240]:
            new_vtex = MathTex(
                f"V_{{\\mathrm{{peak}}}} = {v}\\,\\mathrm{{V}}",
                font_size=42,
                color=DANGER_COLOR if v > breakdown_v else TEXT_PRIMARY,
            )
            new_vtex.move_to([PA_X + 0.5, TL_Y - 1.8, 0])
            self.play(Transform(voltage_tex, new_vtex,
                               replace_mobject_with_target_in_scene=True),
                      run_time=0.7)
            voltage_tex = new_vtex

            if v == 160:
                self.play(Write(breakdown_tex), run_time=0.5)
                self.play(pa_glow.animate.set_fill_opacity(0.3).set_stroke_opacity(0.6),
                          run_time=0.5)
            if v >= 200:
                original_pos = self.pa_group.get_center()
                for _ in range(6):
                    self.play(self.pa_group.animate.shift(np.random.randn(3) * 0.04),
                              run_time=0.05)
                self.play(self.pa_group.animate.move_to(original_pos), run_time=0.1)
                self.play(pa_glow.animate.set_fill_opacity(0.5).set_stroke_opacity(0.8),
                          run_time=0.4)

        new_status = Text("电压超过MOSFET击穿极限！", font="sans-serif",
                          font_size=20, color=DANGER_COLOR)
        new_status.move_to([PA_X + 0.5, BOT_Y - 0.5, 0])
        self.play(Transform(self.status_mob, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)
        self.status_mob = new_status
        self.wait(1.5)

    # ═══════════════════════════════════════════════════════════
    # 场景7：功放烧毁
    # ═══════════════════════════════════════════════════════════

    def scene_07_failure(self):
        # 电弧
        arcs = VGroup()
        for _ in range(8):
            pts = [
                self.pa_body.get_center() + np.array([
                    np.random.uniform(-0.6, 0.6),
                    np.random.uniform(-0.8, 0.8), 0
                ])
                for _ in range(4)
            ]
            arc = VMobject(color=WHITE_HOT, stroke_width=2)
            arc.set_points_as_corners(pts)
            arcs.add(arc)

        flash = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color=WHITE_HOT, fill_opacity=0, stroke_width=0,
        )
        flash.move_to(ORIGIN)

        pa_fail = Text("功放烧毁", font="sans-serif", font_size=48,
                       color=DANGER_COLOR, weight=BOLD)
        pa_fail.set_stroke(WHITE_HOT, width=1, opacity=0.5)
        pa_fail.move_to(self.pa_body.get_center())
        pa_fail.scale(1.2)

        self.play(LaggedStart(*[Create(a) for a in arcs],
                              lag_ratio=0.05), run_time=0.8)

        self.play(flash.animate.set_fill_opacity(0.8), run_time=0.3)
        self.play(
            flash.animate.set_fill_opacity(0),
            self.collapse_tracker.animate.set_value(0.0),
            run_time=1.0,
        )

        self.play(Write(pa_fail), run_time=0.8)

        p_vi = MathTex(r"P = VI", font_size=36, color=DANGER_COLOR)
        # p_loss = MathTex(r"P_{\mathrm{loss}} = I^2 R", font_size=36, color=DANGER_COLOR)
        p_group = VGroup(p_vi)
        p_group.arrange(DOWN, buff=0.3)
        p_group.next_to(pa_fail, DOWN, buff=0.5)
        self.play(Write(p_group), run_time=0.8)

        new_status = Text("功放烧毁！输出归零", font="sans-serif",
                          font_size=20, color=DANGER_COLOR)
        new_status.move_to([PA_X + 0.5, BOT_Y - 0.5, 0])
        self.play(Transform(self.status_mob, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.5)

        dark_overlay = Rectangle(
            width=config.frame_width * 2, height=config.frame_height * 2,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        dark_overlay.move_to(self.camera.frame.get_center())
        self.add(dark_overlay)
        self.play(dark_overlay.animate.set_fill_opacity(0.85), run_time=1.5)
        self.wait(1.0)

    # ═══════════════════════════════════════════════════════════
    # 场景8：总结
    # ═══════════════════════════════════════════════════════════

    def scene_08_summary(self):
        # 镜头拉回全景
        self.play(
            self.camera.frame.animate.scale(1 / 0.55).move_to(ORIGIN),
            run_time=1.0,
        )

        conclusion = Text(
            "阻抗失配 → 反射 → 驻波 → 过压/过流 → 功放烧毁",
            font="sans-serif", font_size=34, color=TEXT_PRIMARY,
        )
        conclusion.set_stroke(BLUE_D, width=0.5, opacity=0.4)
        conclusion.move_to([0, 1.8, 0])
        self.play(Write(conclusion), run_time=1.5)

        bg_wave = always_redraw(lambda:
            FunctionGraph(
                lambda x: 0.4 * np.sin(K * x) * np.cos(OMEGA * self.time_tracker.get_value()),
                x_range=[TL_LEFT, TL_RIGHT],
                color=STANDING_COLOR, stroke_width=2, stroke_opacity=0.2,
            )
        )
        self.add(bg_wave)
        self.wait(4.0)
        self.play(FadeOut(VGroup(conclusion, bg_wave)), run_time=1.5)

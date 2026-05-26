"""
天线阻抗失配导致功放烧毁 — 工程科普动画
使用 Manim CE v0.20.1, 1920x1080 @ 60fps

视频共 10 个场景：
  场景1：标题
  场景2：正常匹配（前向波传播，天线吸收）
  场景3：复数负载失配（ZL=25+j25Ω，Γ=0.447∠116.57°）
  场景4：反射波（前向波 + 反射波同时存在）
  场景5：驻波形成（节点与腹点）
  场景6：功放过压（电压飙升超过MOSFET击穿极限）
  场景7：功放烧毁（电弧、白闪、波形崩塌）
  场景8：总结与保护方法
  场景9：基础布局（功放 + 传输线 + 天线）
  场景10：λ/4 阻抗变换器匹配
"""

from manim import *
import numpy as np

# ═══════════════════════════════════════════════════════════════
# 画面配置
# ═══════════════════════════════════════════════════════════════
config.background_color = "#080c1a"  # 深蓝黑背景（科技感）
config.frame_rate = 60               # 60fps 流畅动画
config.pixel_height = 1080           # 1920x1080 全高清
config.pixel_width = 1920
config.frame_height = 8.0            # Manim 内部坐标高度
config.frame_width = 14.222          # Manim 内部坐标宽度（16:9）

# ═══════════════════════════════════════════════════════════════
# 颜色调色板 — 深色科技工程风格
# ═══════════════════════════════════════════════════════════════
BG_COLOR          = "#080c1a"  # 背景深蓝黑
FORWARD_COLOR     = "#00e5cc"  # 前向波：亮青绿色
REFLECTED_COLOR   = "#ff4060"  # 反射波：红色
STANDING_COLOR    = "#b066ff"  # 驻波：紫色
PA_BODY_COLOR     = "#1a2a3a"  # 功放模块底色
PA_ACCENT         = "#336699"  # 功放模块边框
ANTENNA_OK        = "#22cc66"  # 天线正常：绿色
ANTENNA_BAD       = "#cc2244"  # 天线失配：红色
LINE_COLOR        = "#335577"  # 传输线填充色
LINE_GLOW         = "#5588bb"  # 传输线发光色
TEXT_PRIMARY      = "#ddeeff"  # 主文字：浅蓝白
TEXT_SECONDARY    = "#8899bb"  # 辅助文字：灰蓝
WARNING_COLOR     = "#ff7733"  # 警告：橙色
DANGER_COLOR      = "#ff2222"  # 危险/烧毁：红色
WHITE_HOT         = "#ffffff"  # 白闪光（电弧/击穿瞬间）
PANEL_BG          = "#0d1225"  # 顶部参数面板背景
PANEL_BORDER      = "#1a3050"  # 顶部参数面板边框

# ═══════════════════════════════════════════════════════════════
# 画面布局（坐标以画面中心为原点）
# ═══════════════════════════════════════════════════════════════
# 屏幕结构：
#   左侧：功放模块（PA）
#   中间：传输线（Transmission Line）
#   右侧：天线（Antenna）


PA_X         = -4.8      # 功放 X 坐标（画面左侧）
PA_W, PA_H  = 1.8, 2.4   # 功放 宽, 高
TL_LEFT      = -3.0      # 传输线左端 X
TL_RIGHT     = 3.0       # 传输线右端 X
TL_Y         = 0.0       # 传输线 Y（画面正中间）
ANT_X        = 4.8       # 天线 X 坐标（画面右侧）
ANT_W, ANT_H = 1.4, 2.8  # 天线 宽, 高
TOP_Y        = 2.9       # 顶部参数面板 Y
BOT_Y        = -3.0      # 底部状态文字 Y

# 波动物理参数
K      = 2.2        # 波数（传输线上约显示 3 个波长）
OMEGA  = 4.0        # 角频率（控制波传播速度）
AMP    = 1.05       # 前向波基础振幅
N_WAVE_PTS = 300    # 波形采样点数（越高越平滑）
MISMATCH_GAMMA_MAG = 0.447
MISMATCH_GAMMA_PHASE_DEG = 116.57
MISMATCH_GAMMA_PHASE_RAD = np.deg2rad(MISMATCH_GAMMA_PHASE_DEG)

# ═══════════════════════════════════════════════════════════════
# 波形绘制工具：发光效果
# ═══════════════════════════════════════════════════════════════
# 发光原理：同一波形用不同粗细、不同透明度的线叠加绘制
#   外层：粗、很透明 → 模拟光晕扩散
#   内层：细、不透明   → 波形主体

def glow_wave_layers(x_min, x_max, wave_fn, color, glow_count=3, reverse=False):
    """绘制带发光效果的波形。
    wave_fn(x) 接收位置 x，返回该点的电压值（y 坐标）。
    每帧通过 always_redraw 自动重绘，实现连续动画。"""
    layers_def = [
        (14, 0.06),   # 最外层光晕：粗线宽、极透明
        (8,  0.14),   # 第二层
        (4,  0.30),   # 第三层
        (2,  0.75),   # 核心波形：细线宽、高不透明
    ]
    layers = []
    for stroke_w, opacity in layers_def[:glow_count + 1]:
        def make_layer(sw=stroke_w, op=opacity):
            def build_graph():
                graph = FunctionGraph(
                    lambda x: wave_fn(x),
                    x_range=[x_min, x_max],
                    color=color,
                    stroke_width=sw,
                    stroke_opacity=op,
                )
                if reverse:
                    graph.reverse_points()
                return graph
            return always_redraw(build_graph)
        layers.append(make_layer())
    return VGroup(*layers)


def single_wave(x_min, x_max, wave_fn, color, stroke_w=3, opacity=0.85):
    """绘制单层波形（无发光，用于叠加或背景）。"""
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
# UI 组件构建函数
# ═══════════════════════════════════════════════════════════════

def build_pa_module():
    """构建功放模块（画面左侧）。
    返回 (整体VGroup, 矩形本体, 标签文字)"""
    body = RoundedRectangle(
        width=PA_W, height=PA_H,
        fill_color=PA_BODY_COLOR, fill_opacity=0.85,
        stroke_color=PA_ACCENT, stroke_width=1.5,
        corner_radius=0.15,
    )
    label = Text("功放", font="sans-serif", font_size=28,
                 color=TEXT_PRIMARY)
    mos_label = Text("MOSFET", font="sans-serif", font_size=14,
                     color=TEXT_SECONDARY).next_to(label, DOWN, buff=0.1)
    title_group = VGroup(label, mos_label)
    title_group.move_to(body.get_center())
    group = VGroup(body, title_group)
    group.move_to([PA_X, 0, 0])
    return group, body, label


def build_antenna():
    """构建天线模块（画面右侧）。
    返回 (整体VGroup, 矩形本体, 标签文字, 阻抗文字)"""
    body = RoundedRectangle(
        width=ANT_W, height=ANT_H,
        fill_color=ANTENNA_OK, fill_opacity=0.7,
        stroke_color=ANTENNA_OK, stroke_width=1.5,
        corner_radius=0.15,
    )
    label = Text("天线", font="sans-serif", font_size=22,
                 color=TEXT_PRIMARY)
    z_label = Text("50Ω", font="sans-serif", font_size=16,
                   color=TEXT_SECONDARY).next_to(label, DOWN, buff=0.1)
    title_group = VGroup(label, z_label)
    title_group.move_to(body.get_center())
    group = VGroup(body, title_group)
    group.move_to([ANT_X, 0, 0])
    return group, body, label, z_label


def build_transmission_line():
    """构建传输线（画面中间）—— 上下两条平行导体。
    两导体间有半透明填充和竖线刻度，左侧标注特征阻抗 Z₀=50Ω。
    波形在两条导体之间振荡传播。"""
    TL_GAP = 0.65  # 导体间距的一半
    # 上导体
    top_line = Line(
        [TL_LEFT - 0.3, TL_Y + TL_GAP, 0],
        [TL_RIGHT + 0.3, TL_Y + TL_GAP, 0],
        color=LINE_GLOW, stroke_width=1.8,
    )
    # 下导体
    bot_line = Line(
        [TL_LEFT - 0.3, TL_Y - TL_GAP, 0],
        [TL_RIGHT + 0.3, TL_Y - TL_GAP, 0],
        color=LINE_GLOW, stroke_width=1.8,
    )
    # 两导体间的半透明填充
    fill_rect = Rectangle(
        width=TL_RIGHT - TL_LEFT, height=TL_GAP * 2,
        fill_color=LINE_COLOR, fill_opacity=0.12,
        stroke_width=0,
    )
    fill_rect.move_to([(TL_LEFT + TL_RIGHT) / 2, TL_Y, 0])
    # 竖线刻度（连接两导体）
    ticks = VGroup()
    for i in range(7):
        x = TL_LEFT + i * (TL_RIGHT - TL_LEFT) / 6
        tick = Line([x, TL_Y + TL_GAP, 0], [x, TL_Y - TL_GAP, 0],
                    color=LINE_GLOW, stroke_width=0.5, stroke_opacity=0.35)
        ticks.add(tick)
    # 特性阻抗标注
    z0_label = Text("Z₀ = 50Ω", font="sans-serif", font_size=14,
                    color=TEXT_SECONDARY)
    z0_label.next_to([TL_LEFT + 3, TL_Y + TL_GAP + 0.3, 0], LEFT, buff=0.15)
    return VGroup(fill_rect, top_line, bot_line, ticks, z0_label)


def connected_transmission_line_range():
    """返回连接功放右边缘与天线左边缘的传输线 x 范围。"""
    return PA_X + PA_W / 2, ANT_X - ANT_W / 2


def build_simple_transmission_line(stroke_width=5.0):
    """构建简化传输线：仅保留上下两条较粗导体。"""
    TL_GAP = 0.65
    x_start, x_end = connected_transmission_line_range()
    top_line = Line(
        [x_start, TL_Y + TL_GAP, 0],
        [x_end, TL_Y + TL_GAP, 0],
        color=LINE_GLOW, stroke_width=stroke_width,
    )
    bot_line = Line(
        [x_start, TL_Y - TL_GAP, 0],
        [x_end, TL_Y - TL_GAP, 0],
        color=LINE_GLOW, stroke_width=stroke_width,
    )
    return VGroup(top_line, bot_line)


def build_param_panel():
    """构建顶部参数面板。
    显示四个实时参数：Z₀, Z_L, Γ, VSWR。
    返回 (面板VGroup, 参数dict)，参数dict用于后续动态更新。"""
    panel_w = 13.4
    panel_h = 0.9
    panel = RoundedRectangle(
        width=panel_w, height=panel_h,
        fill_color=PANEL_BG, fill_opacity=0.7,
        stroke_color=PANEL_BORDER, stroke_width=0.8,
        corner_radius=0.1,
    )
    panel.move_to([0, TOP_Y, 0])

    # 初始参数（匹配状态：Γ=0, VSWR=1）
    z0 = Tex(r"$Z_0 = 50\Omega$", font_size=28, color=TEXT_SECONDARY)    # 特征阻抗
    zl = Tex(r"$Z_L = 50\Omega$", font_size=28, color=TEXT_SECONDARY)    # 负载阻抗
    gamma = Tex(r"$\Gamma = 0.00$", font_size=28, color=TEXT_SECONDARY)  # 反射系数
    vswr = Tex(r"$\mathrm{VSWR} = 1.00$", font_size=28, color=TEXT_SECONDARY)  # 驻波比

    z0.move_to([-5.25, TOP_Y, 0])
    zl.move_to([-1.75, TOP_Y, 0])
    gamma.move_to([2.15, TOP_Y, 0])
    vswr.move_to([5.45, TOP_Y, 0])
    params = VGroup(z0, zl, gamma, vswr)

    group = VGroup(panel, params)
    return group, {"z0": z0, "zl": zl, "gamma": gamma, "vswr": vswr}


def build_status_line():
    """构建底部状态栏（空文本占位，后续各场景替换内容）。"""
    txt = Text("", font="sans-serif", font_size=22, color=TEXT_PRIMARY)
    txt.move_to([0, BOT_Y, 0])
    return txt


# ═══════════════════════════════════════════════════════════════
# 波动物理函数
# ═══════════════════════════════════════════════════════════════
# 三个核心函数对应视频中的三种波：
#   wave_forward  → 入射波（青绿色，向右传播）
#   wave_reflected → 反射波（红色，向左传播）
#   wave_total    → 驻波（紫色，前向+反射叠加）


def wave_forward(x, t, amp=AMP, k=K, omega=OMEGA):
    """前向波（入射波）：Vf(x,t) = A·sin(kx - ωt)
    沿 +x 方向（从左到右，功放→天线）传播。"""
    return amp * np.sin(k * x - omega * t)


def wave_reflected(x, t, gamma, amp=AMP, k=K, omega=OMEGA,
                   boundary=TL_RIGHT):
    """反射波：Vr(x,t) = Γ·A·sin(k(2L-x) - ωt)
    在天线端(x=boundary)反射，沿 -x 方向（从右到左）传回功放。
    反射系数 Γ 决定反射强度：0=无反射, 1=全反射。"""
    return gamma * amp * np.sin(k * (2 * boundary - x) - omega * t)


def wave_reflected_mismatch(x, t, amp=AMP, k=K, omega=OMEGA):
    """复数负载下的反射波，幅度为 0.447A，相位为 116.57°。"""
    return MISMATCH_GAMMA_MAG * amp * np.cos(
        omega * t + k * x + MISMATCH_GAMMA_PHASE_RAD
    )


def wave_total(x, t, gamma, amp=AMP, k=K, omega=OMEGA,
               boundary=TL_RIGHT):
    """总波（驻波）：V(x,t) = Vf + Vr
    前向波与反射波叠加。当 Γ=1 时形成纯驻波，
    节点（振幅为0）和腹点（振幅最大）固定不动。"""
    fwd = wave_forward(x, t, amp, k, omega)
    ref = wave_reflected(x, t, gamma, amp, k, omega, boundary)
    return fwd + ref


# ═══════════════════════════════════════════════════════════════
# 主场景类
# ═══════════════════════════════════════════════════════════════
# 继承 MovingCameraScene 以支持镜头推拉（场景6 zoom 到功放）

class AntennaMismatch(MovingCameraScene):
    def construct(self):
        # ── 全局共享的 ValueTracker ──
        # ValueTracker 是 Manim 中驱动动画的核心机制
        # 通过 .get_value() 读取当前值，.animate.set_value() 平滑过渡到新值
        self.time_tracker = ValueTracker(0)        # 时间（驱动波形连续运动）
        self.gamma_tracker = ValueTracker(0.0)     # 反射系数 Γ（0→1 表示失配程度）
        self.vswr_tracker = ValueTracker(1.0)      # 驻波比 VSWR
        self.forward_amp = ValueTracker(AMP)       # 前向波振幅（场景5/6可调）
        self.collapse_tracker = ValueTracker(1.0)  # 波形崩塌系数（1=正常, 0=崩塌）

        # 按顺序播放所有8个场景
        self.scene_01_title()           # 场景1：标题
        self.scene_02_normal_match()    # 场景2：正常匹配
        self.scene_03_mismatch()        # 场景3：发生失配
        self.scene_04_reflected_wave()  # 场景4：反射波形成
        self.scene_05_standing_wave()   # 场景5：驻波形成
        self.scene_06_overvoltage()     # 场景6：功放端过压
        self.scene_07_failure()         # 场景7：功放烧毁
        self.scene_08_summary()         # 场景8：总结

    # ── 内部辅助方法 ─────────────────────────────────────────

    def _current_gamma(self):
        """读取当前反射系数 Γ"""
        return self.gamma_tracker.get_value()

    def _fwd_fn(self):
        """返回前向波函数 f(x) = Vf(x, t)。
        每次调用都从 time_tracker 实时读取时间，确保 always_redraw 每帧更新。"""
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_forward(x, self.time_tracker.get_value(),
                                            amp=amp)

    def _ref_fn(self):
        """返回反射波函数 f(x) = Vr(x, t)。
        同时实时读取 Γ 和时间，保证反射波随参数变化。"""
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_reflected(x, self.time_tracker.get_value(),
                                              gamma=self._current_gamma(),
                                              amp=amp)

    def _tot_fn(self):
        """返回总波函数 f(x) = Vf + Vr（驻波）。
        场景5核心：前向波+反射波叠加形成驻波。"""
        amp = self.forward_amp.get_value()
        col = self.collapse_tracker.get_value()
        return lambda x: col * wave_total(x, self.time_tracker.get_value(),
                                          gamma=self._current_gamma(),
                                          amp=amp)

    def _start_wave_time(self):
        """启动时间追踪器，让波形开始连续运动。
        使用 updater 机制：每帧自动累加 dt，保证动画平滑。"""
        if not hasattr(self, '_time_updater_added'):
            self.time_tracker.add_updater(lambda m, dt: m.increment_value(dt))
            self._time_updater_added = True

    def _update_param_texts(self, params, z0_str, zl_str, gamma_str, vswr_str):
        """动态更新顶部参数面板的四个数值。
        通过 Transform 动画从旧值平滑过渡到新值。"""
        new_z0 = Tex(z0_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["z0"].get_center())
        new_zl = Tex(zl_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["zl"].get_center())
        new_gamma = Tex(gamma_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["gamma"].get_center())
        new_vswr = Tex(vswr_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["vswr"].get_center())
        self.play(
            Transform(params["z0"], new_z0, replace_mobject_with_target_in_scene=True),
            Transform(params["zl"], new_zl, replace_mobject_with_target_in_scene=True),
            Transform(params["gamma"], new_gamma, replace_mobject_with_target_in_scene=True),
            Transform(params["vswr"], new_vswr, replace_mobject_with_target_in_scene=True),
            run_time=1.5,
        )
        params["z0"] = new_z0
        params["zl"] = new_zl
        params["gamma"] = new_gamma
        params["vswr"] = new_vswr

    # ═══════════════════════════════════════════════════════════
    # 场景1：标题（约 3 秒）
    # 画面：深蓝背景 + 标题文字蓝色辉光呼吸动画
    # ═══════════════════════════════════════════════════════════

    def scene_01_title(self):
        # 主标题
        title = Text("为什么天线失配会烧毁功放？",
                     font="sans-serif", font_size=48,
                     color=TEXT_PRIMARY)
        title.set_stroke(BLUE_D, width=0.5, opacity=0.5)  # 文字描边

        # 副标题
        sub = Text("传输线反射与功放失效", font="sans-serif", font_size=24,
                   color=TEXT_SECONDARY)
        sub.next_to(title, DOWN, buff=0.3)

        # 标题后面的辉光副本（模糊光晕效果）
        glow = title.copy().set_stroke(BLUE_C, width=8, opacity=0.25)

        group = VGroup(glow, title, sub)
        group.move_to(ORIGIN)  # 居中

        # 淡入
        self.play(FadeIn(title, shift=UP * 0.3), FadeIn(sub, shift=UP * 0.2),
                  FadeIn(glow, shift=UP * 0.3), run_time=1.5)
        # 呼吸效果：文字微微放大再缩小
        self.play(
            title.animate.scale(1.03).set_stroke(BLUE_C, width=1.5, opacity=0.5),
            glow.animate.scale(1.03).set_stroke(BLUE_C, width=10, opacity=0.3),
            rate_func=there_and_back, run_time=2.0,
        )
        self.wait(0.5)
        self.play(FadeOut(group), run_time=0.6)

    # ═══════════════════════════════════════════════════════════
    # 场景2：正常匹配（约 6 秒）
    # 画面：功放 → 50Ω传输线 → 50Ω天线
    # 前向波（青绿色）沿传输线向右传播，到达天线后被吸收
    # 天线出现辐射波纹，表示功率被辐射出去
    # 顶部：Z₀=50Ω, Z_L=50Ω, Γ=0, VSWR=1.0
    # ═══════════════════════════════════════════════════════════

    def scene_02_normal_match(self):
        # ── 构建所有 UI 组件并存入 self 供后续场景使用 ──
        self.pa_group, pa_body, pa_label = build_pa_module()
        self.ant_group, self.ant_body, self.ant_label, self.ant_z = build_antenna()
        self.tl_group = build_simple_transmission_line()
        self.panel_group, self.params = build_param_panel()
        self.status = build_status_line()

        # 所有 UI 组件同时淡入
        self.play(
            FadeIn(self.pa_group),
            FadeIn(self.ant_group),
            FadeIn(self.tl_group),
            FadeIn(self.panel_group),
            run_time=1.0,
        )
        fwd_formula = MathTex(
            r"V(z,t) = A\cos(\omega t - \beta z)",
            font_size=34, color=FORWARD_COLOR,
        )
        fwd_formula.move_to([0, TL_Y + 1.55, 0])
        self._fwd_formula = fwd_formula
        self.play(Write(fwd_formula), run_time=0.8)
        self.wait(1.0)

        # ── 启动前向波（青绿色发光，沿传输线向右传播）──
        self._start_wave_time()
        tl_x_start, tl_x_end = connected_transmission_line_range()
        fwd_wave = glow_wave_layers(tl_x_start, tl_x_end, self._fwd_fn(),
                                    FORWARD_COLOR)
        self.play(
            LaggedStart(
                *[Create(layer) for layer in fwd_wave],
                lag_ratio=0.08,
            ),
            run_time=1.5,
        )

        # 让波形连续运动约 5 秒
        self.wait(1.0)

        # ── 天线辐射波纹（绿色同心圆扩散）──
        ripple_circles = VGroup()
        for i in range(4):
            c = Circle(radius=0.25 + i * 0.35,
                       stroke_color=ANTENNA_OK, stroke_width=3.5,
                       stroke_opacity=0.7 - i * 0.15, fill_opacity=0)
            c.move_to(self.ant_body.get_center())
            ripple_circles.add(c)
        self.play(LaggedStart(
            *[GrowFromCenter(c) for c in ripple_circles],
            lag_ratio=0.3,
        ), run_time=2.0)
        self.play(FadeOut(ripple_circles), run_time=0.5)
        self.wait(0.5)

        # 移除波形，准备进入下一场景
        self.remove(fwd_wave)

    # ═══════════════════════════════════════════════════════════
    # 场景3：复数负载失配
    # 画面：ZL 变为 25+j25Ω，Γ 变为 0.447∠116.57°
    # 保留前向波，加入带相位差的红色反射波
    # 依次显示总电压波公式和最大电压公式
    # ═══════════════════════════════════════════════════════════

    def scene_03_mismatch(self):
        tl_x_start, tl_x_end = connected_transmission_line_range()
        self._start_wave_time()

        fwd = glow_wave_layers(tl_x_start, tl_x_end, self._fwd_fn(), FORWARD_COLOR)
        self.add(fwd)

        self.play(FadeOut(self.ant_z), run_time=0.4)

        self.play(self.gamma_tracker.animate.set_value(MISMATCH_GAMMA_MAG),
                  run_time=1.0, rate_func=smooth)
        self._update_param_texts(
            self.params,
            r"$Z_0 = 50\Omega$",
            r"$Z_L = 25 + j25\,\Omega$",
            r"$\Gamma = 0.447\angle 116.57^\circ$",
            r"$\mathrm{VSWR} = 2.62$",
        )

        ref = glow_wave_layers(
            tl_x_start, tl_x_end,
            lambda x: wave_reflected_mismatch(x, self.time_tracker.get_value()),
            REFLECTED_COLOR,
            reverse=True,
        )
        self.play(
            LaggedStart(
                *[Create(layer) for layer in ref],
                lag_ratio=0.08,
            ),
            run_time=1.5,
        )

        if hasattr(self, "_fwd_formula"):
            self.play(FadeOut(self._fwd_formula), run_time=0.5)

        total_formula = MathTex(
            r"V_{total}(z,t) = A\cos(\omega t - \beta z)"
            r" + 0.447A\cos(\omega t + \beta z + 116.57^\circ)",
            font_size=26, color=TEXT_PRIMARY,
        )
        total_formula.move_to([0, TL_Y + 1.55, 0])
        if total_formula.width > 12.4:
            total_formula.scale(12.4 / total_formula.width)
        self.play(Write(total_formula), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(total_formula), run_time=0.5)

        vmax_formula = MathTex(
            r"V_{max} = A + |\Gamma|A = A(1 + 0.447) = 1.447A",
            font_size=32, color=WARNING_COLOR,
        )
        vmax_formula.move_to([0, TL_Y + 1.55, 0])
        if vmax_formula.width > 12.4:
            vmax_formula.scale(12.4 / vmax_formula.width)
        self.play(Write(vmax_formula), run_time=1.0)
        self.wait(1.5)

        self._scene3_waves = VGroup(fwd, ref)
        self._scene3_formula = vmax_formula

    # ═══════════════════════════════════════════════════════════
    # 场景4：反射波形成（约 8 秒）
    # 画面：前向波（青绿）到达天线后被全反射
    # 反射波（红色）沿传输线向左传播，返回功放
    # 方向箭头标注"入射波"和"反射波"
    # 显示 P_f（入射功率）和 P_r（反射功率）
    # 底部：Pr 增加中... 反射功率返回功放
    # ═══════════════════════════════════════════════════════════

    def scene_04_reflected_wave(self):
        # ── 重新显示前向波 ──
        self._start_wave_time()
        fwd = glow_wave_layers(TL_LEFT, TL_RIGHT, self._fwd_fn(),
                               FORWARD_COLOR)
        self.add(fwd)

        # 等波到达天线端...
        self.wait(1.5)

        # ── 反射波（红色发光）淡入，沿传输线向左传播 ──
        ref = glow_wave_layers(TL_LEFT, TL_RIGHT, self._ref_fn(),
                               REFLECTED_COLOR)
        self.play(FadeIn(ref), run_time=1.0)

        # ── 方向箭头 + 标签 ──
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

        # ── 功率显示：入射靠左，反射靠右 ──
        pf_math = MathTex(r"P_f = ", font_size=28, color=FORWARD_COLOR)
        pf_text = Text("入射功率", font="sans-serif", font_size=24,
                       color=FORWARD_COLOR)
        pf_combined = VGroup(pf_math, pf_text).arrange(RIGHT, buff=0.1)
        pf_combined.move_to([TL_LEFT + 1.5, TOP_Y - 1.2, 0])

        pr_math = MathTex(r"P_r = ", font_size=28, color=REFLECTED_COLOR)
        pr_text = Text("反射功率", font="sans-serif", font_size=24,
                       color=REFLECTED_COLOR)
        pr_combined = VGroup(pr_math, pr_text).arrange(RIGHT, buff=0.1)
        pr_combined.move_to([TL_RIGHT - 1.5, TOP_Y - 1.2, 0])

        self.play(Write(pf_combined), run_time=0.5)
        self.play(Write(pr_combined), run_time=0.5)

        new_status = Text("Pr 增加中... 反射功率返回功放",
                          font="sans-serif", font_size=20,
                          color=WARNING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True),
                  run_time=0.6)
        self.status = new_status

        self.wait(4.0)

        # 清理箭头和功率显示
        self.play(FadeOut(fwd_arrow), FadeOut(fwd_label),
                  FadeOut(ref_arrow), FadeOut(ref_label),
                  FadeOut(pf_combined), FadeOut(pr_combined), run_time=0.5)
        self.remove(fwd, ref)

    # ═══════════════════════════════════════════════════════════
    # 场景5：驻波形成（约 10 秒）—— 核心场景
    # 画面：前向波与反射波叠加形成驻波（紫色发光）
    # 驻波公式：V(z,t) = Vf·cos(ωt-βz) + Vr·cos(ωt+βz)
    # 节点（振幅恒为0，深色圆点）和腹点（振幅最大，紫色圆点）固定不动
    # 标注 Vmax、Vmin，显示 VSWR = Vmax/Vmin
    # 顶部参数：Γ=1.00, VSWR→∞
    # ═══════════════════════════════════════════════════════════

    def scene_05_standing_wave(self):
        # Show formula briefly
        standing_formula = MathTex(
            r"V(z,t) = V_f \cos(\omega t - \beta z) + V_r \cos(\omega t + \beta z)",
            font_size=30, color=TEXT_PRIMARY,
        )
        standing_formula.move_to([0, TOP_Y - 1.2, 0])
        self.play(Write(standing_formula), run_time=1.0)

        # Draw standing wave (total wave) in purple glow
        self._start_wave_time()
        sw = glow_wave_layers(TL_LEFT, TL_RIGHT, self._tot_fn(),
                              STANDING_COLOR, glow_count=4)
        self.play(FadeIn(sw), run_time=1.0)

        new_status = Text("驻波形成 — 节点与腹点", font="sans-serif",
                          font_size=20, color=STANDING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True),
                  run_time=0.6)
        self.status = new_status

        # node / antinode markers
        # For k=2.2, nodes at kx = nπ → x = nπ/k ≈ n*1.428
        # In range [-3, 3]: nodes at -2.86, -1.43, 0, 1.43, 2.86
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

        # Antinodes midway between nodes
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

        # Vmax / Vmin display
        vmax_tex = MathTex(r"V_{\mathrm{max}}", font_size=26,
                           color=DANGER_COLOR)
        vmin_tex = MathTex(r"V_{\mathrm{min}}", font_size=26,
                           color=TEXT_SECONDARY)
        vswr_eq = MathTex(
            r"\mathrm{VSWR} = \frac{V_{\mathrm{max}}}{V_{\mathrm{min}}}",
            font_size=26, color=TEXT_PRIMARY,
        )
        vm_group = VGroup(vmax_tex, vmin_tex, vswr_eq)
        vm_group.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        vm_group.move_to([TL_RIGHT + 1.8, TL_Y, 0])
        self.play(Write(vm_group), run_time=1.0)

        # Update param display
        self._update_param_texts(
            self.params,
            r"$Z_0 = 50\Omega$",
            r"$Z_L = \infty\Omega$",
            r"$\Gamma = 1.00$",
            r"$\mathrm{VSWR} \to \infty$",
        )

        self.wait(5.0)

        # Cleanup
        self.play(FadeOut(standing_formula), FadeOut(node_dots),
                  FadeOut(antinode_dots), FadeOut(node_labels),
                  FadeOut(anti_labels), FadeOut(vm_group), run_time=0.5)
        self.remove(sw)

    # ═══════════════════════════════════════════════════════════
    # 场景6：功放端过压（约 8 秒）
    # 画面：镜头 zoom 到左侧功放模块
    # 显示 Vmax = V₀(1+|Γ|) 公式
    # 电压数字动态攀升：100V → 120V → 160V → 200V → 240V
    # MOSFET 击穿电压 = 150V（超过后数字变红）
    # 功放模块出现红色辉光、震动效果
    # 底部：电压超过MOSFET击穿极限！
    # ═══════════════════════════════════════════════════════════

    def scene_06_overvoltage(self):
        pa_group = self.pa_group
        pa_body = pa_group[0]

        # Zoom camera towards PA
        self.play(
            self.camera.frame.animate.scale(0.55).move_to([PA_X + 0.5, TL_Y, 0]),
            run_time=2.0,
        )

        # Show voltage build-up formula
        vmax_formula = MathTex(
            r"V_{\mathrm{max}} = V_0 (1 + |\Gamma|)",
            font_size=32, color=TEXT_PRIMARY,
        )
        vmax_formula.move_to([PA_X + 0.5, TOP_Y - 0.8, 0])
        self.play(Write(vmax_formula), run_time=0.8)

        # Voltage display that climbs
        voltage_values = [100, 120, 160, 200, 240]
        breakdown_v = 150
        voltage_tex = MathTex("V_{\mathrm{peak}} = 100\,\mathrm{V}",
                              font_size=42, color=TEXT_PRIMARY)
        voltage_tex.move_to([PA_X + 0.5, TL_Y - 1.8, 0])
        self.play(Write(voltage_tex), run_time=0.5)

        breakdown_tex = MathTex(
            r"\mathrm{MOSFET\ Breakdown} = 150\,\mathrm{V}",
            font_size=28, color=WARNING_COLOR,
        )
        breakdown_tex.next_to(voltage_tex, DOWN, buff=0.3)

        pa_glow = pa_body.copy()
        pa_glow.set_fill_color(DANGER_COLOR).set_fill_opacity(0)
        pa_glow.set_stroke_color(DANGER_COLOR).set_stroke_width(4).set_stroke_opacity(0)

        self.add(pa_glow)

        for v in voltage_values:
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

            if v > breakdown_v and v == 160:
                self.play(Write(breakdown_tex), run_time=0.5)
                # Start PA glow
                self.play(
                    pa_glow.animate.set_fill_opacity(0.3).set_stroke_opacity(0.6),
                    run_time=0.5,
                )

            if v >= 200:
                # Shaking
                original_pos = pa_group.get_center()
                for _ in range(6):
                    self.play(
                        pa_group.animate.shift((np.random.randn(3)) * 0.04),
                        run_time=0.05,
                    )
                self.play(pa_group.animate.move_to(original_pos), run_time=0.1)

                # Increase glow
                self.play(
                    pa_glow.animate.set_fill_opacity(0.5).set_stroke_opacity(0.8),
                    run_time=0.4,
                )

        new_status = Text("电压超过MOSFET击穿极限！",
                          font="sans-serif", font_size=20,
                          color=DANGER_COLOR)
        new_status.move_to([PA_X + 0.5, BOT_Y - 0.5, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True),
                  run_time=0.6)
        self.status = new_status

        self.wait(1.5)

        # Store for next scene
        self._pa_glow = pa_glow
        self._voltage_tex = voltage_tex
        self._breakdown_tex = breakdown_tex
        self._vmax_formula = vmax_formula

    # ═══════════════════════════════════════════════════════════
    # 场景7：功放烧毁（约 6 秒）
    # 画面：雪崩击穿（Avalanche Breakdown）
    # 功放内部出现随机电弧（白色锯齿线）
    # 瞬间白闪覆盖全屏
    # 波形崩塌（collapse_tracker → 0，波形归零）
    # 显示"功放烧毁"大字 + P=VI、P_loss=I²R 公式
    # 整个系统暗化（黑色半透明遮罩）
    # ═══════════════════════════════════════════════════════════

    def scene_07_failure(self):
        pa_body = self.pa_group[0]

        # Arc effect — random zigzag lines inside PA
        arcs = VGroup()
        for _ in range(8):
            pts = [
                pa_body.get_center() + np.array([np.random.uniform(-0.6, 0.6),
                                                  np.random.uniform(-0.8, 0.8), 0])
                for _ in range(4)
            ]
            arc = VMobject(color=WHITE_HOT, stroke_width=2)
            arc.set_points_as_corners(pts)
            arcs.add(arc)

        # White flash overlay
        flash = Rectangle(
            width=config.frame_width, height=config.frame_height,
            fill_color=WHITE_HOT, fill_opacity=0,
            stroke_width=0,
        )
        flash.move_to(ORIGIN)

        pa_fail = Text("功放烧毁", font="sans-serif", font_size=48,
                       color=DANGER_COLOR, weight=BOLD)
        pa_fail.set_stroke(WHITE_HOT, width=1, opacity=0.5)
        pa_fail.move_to(pa_body.get_center())

        # Show arcs
        self.play(LaggedStart(*[Create(a) for a in arcs],
                              lag_ratio=0.05), run_time=0.8)

        # Flash
        self.play(
            flash.animate.set_fill_opacity(0.8),
            run_time=0.3,
        )
        self.play(
            flash.animate.set_fill_opacity(0),
            self.collapse_tracker.animate.set_value(0.0),
            run_time=1.0,
        )

        # Show failure text
        pa_fail.scale(1.2)
        self.play(Write(pa_fail), run_time=0.8)

        # Power formulas
        p_vi = MathTex(r"P = VI", font_size=36, color=DANGER_COLOR)
        p_loss = MathTex(r"P_{\mathrm{loss}} = I^2 R",
                         font_size=36, color=DANGER_COLOR)
        p_group = VGroup(p_vi, p_loss)
        p_group.arrange(DOWN, buff=0.3)
        p_group.next_to(pa_fail, DOWN, buff=0.5)
        self.play(Write(p_group), run_time=0.8)

        new_status = Text("功放烧毁！输出归零", font="sans-serif",
                          font_size=20, color=DANGER_COLOR)
        new_status.move_to([PA_X + 0.5, BOT_Y - 0.5, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True),
                  run_time=0.5)
        self.status = new_status

        # Everything dims via a dark overlay
        dark_overlay = Rectangle(
            width=config.frame_width * 2, height=config.frame_height * 2,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        dark_overlay.move_to(self.camera.frame.get_center())
        self.add(dark_overlay)
        self.play(dark_overlay.animate.set_fill_opacity(0.85), run_time=1.5)
        self.wait(1.0)

    # ═══════════════════════════════════════════════════════════
    # 场景8：总结（约 6 秒）
    # 画面：镜头拉回全景
    # 核心结论：阻抗失配 → 反射 → 驻波 → 过压/过流 → 功放烧毁
    # 四种保护方法：VSWR保护、环形器/隔离器、假负载、自动功率回退
    # 背景缓慢显示驻波图样作为装饰
    # 最终淡出
    # ═══════════════════════════════════════════════════════════

    def scene_08_summary(self):
        # Reset camera
        self.play(
            self.camera.frame.animate.scale(1 / 0.55).move_to(ORIGIN),
            run_time=1.0,
        )

        # Main takeaway
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

        # Final fade out
        self.play(FadeOut(VGroup(conclusion, bg_wave)),
                  run_time=1.5)


# ═══════════════════════════════════════════════════════════════
# 独立场景类 —— 每个场景可单独渲染，方便调试
# ═══════════════════════════════════════════════════════════════
# 用法：
#   manim render -q l main.py Scene01Title        # 只渲染标题
#   manim render -q l main.py Scene02NormalMatch  # 只渲染正常匹配
#   manim render -q l main.py AntennaMismatch     # 渲染全部


class _BaseScene(MovingCameraScene):
    """基类：提供所有场景共用的 tracker 初始化、UI 构建和波形辅助方法。
    不实现 construct()，仅供子类继承。"""

    def _setup_trackers(self, gamma=0.0):
        """初始化 ValueTracker。子类可指定 gamma 初始值。"""
        self.time_tracker = ValueTracker(0)
        self.gamma_tracker = ValueTracker(gamma)
        self.vswr_tracker = ValueTracker(1.0)
        self.forward_amp = ValueTracker(AMP)
        self.collapse_tracker = ValueTracker(1.0)
        self._time_updater_added = False

    def _setup_ui(self, simple_transmission_line=False, animate=True):
        """构建画面中所有 UI 组件（功放、天线、传输线、面板、状态栏）。
        存入 self，相当于场景2中的布局初始化。"""
        self.pa_group, self.pa_body, self.pa_label = build_pa_module()
        self.ant_group, self.ant_body, self.ant_label, self.ant_z = build_antenna()
        if simple_transmission_line:
            self.tl_group = build_simple_transmission_line()
        else:
            self.tl_group = build_transmission_line()
        self.panel_group, self.params = build_param_panel()
        self.status = build_status_line()

        if not animate:
            self.add(self.pa_group, self.ant_group, self.tl_group,
                     self.panel_group)
            return

        # 一次性淡入所有 UI
        self.play(
            FadeIn(self.pa_group),
            FadeIn(self.ant_group),
            FadeIn(self.tl_group),
            FadeIn(self.panel_group),
            run_time=1.0,
        )

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

    def _update_param_texts(self, params, z0_str, zl_str, gamma_str, vswr_str):
        new_z0 = Tex(z0_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["z0"].get_center())
        new_zl = Tex(zl_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["zl"].get_center())
        new_gamma = Tex(gamma_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["gamma"].get_center())
        new_vswr = Tex(vswr_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["vswr"].get_center())
        self.play(
            Transform(params["z0"], new_z0, replace_mobject_with_target_in_scene=True),
            Transform(params["zl"], new_zl, replace_mobject_with_target_in_scene=True),
            Transform(params["gamma"], new_gamma, replace_mobject_with_target_in_scene=True),
            Transform(params["vswr"], new_vswr, replace_mobject_with_target_in_scene=True),
            run_time=1.5,
        )
        params["z0"] = new_z0
        params["zl"] = new_zl
        params["gamma"] = new_gamma
        params["vswr"] = new_vswr

    def _set_antenna_mismatched(self):
        """将天线设为失配状态（变红 + ZL=∞ + 警告图标）。"""
        warn = Text("⚠", font="sans-serif", font_size=36, color=WARNING_COLOR)
        warn.move_to(self.ant_body.get_center() + UP * 1.0)
        self.play(
            self.ant_body.animate.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD),
            Transform(self.ant_z, Tex(r"$Z_L = \infty\Omega$", font_size=22,
                                      color=WARNING_COLOR),
                      replace_mobject_with_target_in_scene=True),
            FadeIn(warn, scale=1.5),
            run_time=1.0,
        )
        return warn


# ═══════════════════════════════════════════════════════════════
# 场景1：标题
# ═══════════════════════════════════════════════════════════════

class Scene01Title(Scene):
    def construct(self):
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


# ═══════════════════════════════════════════════════════════════
# 场景2：正常匹配
# ═══════════════════════════════════════════════════════════════

class Scene02NormalMatch(_BaseScene):
    def construct(self):
        self._setup_trackers()
        self._setup_ui(simple_transmission_line=True)

        fwd_formula = MathTex(
            r"V(z,t) = A\cos(\omega t - \beta z)",
            font_size=34, color=FORWARD_COLOR,
        )
        fwd_formula.move_to([0, TL_Y + 1.55, 0])
        self.play(Write(fwd_formula), run_time=0.8)

        # 前向波
        self._start_wave_time()
        tl_x_start, tl_x_end = connected_transmission_line_range()
        fwd_wave = glow_wave_layers(tl_x_start, tl_x_end, self._fwd_fn(), FORWARD_COLOR)
        self.play(
            LaggedStart(
                *[Create(layer) for layer in fwd_wave],
                lag_ratio=0.08,
            ),
            run_time=1.5,
        )
        self.wait(0.5)

        # 天线辐射波纹
        ripple_circles = VGroup()
        for i in range(4):
            c = Circle(radius=0.25 + i * 0.35,
                       stroke_color=ANTENNA_OK, stroke_width=4.5,
                       stroke_opacity=0.7 - i * 0.15, fill_opacity=0)
            c.move_to(self.ant_body.get_center())
            ripple_circles.add(c)
        self.play(LaggedStart(
            *[GrowFromCenter(c) for c in ripple_circles], lag_ratio=0.3,
        ), run_time=2.0)


# ═══════════════════════════════════════════════════════════════
# 场景3：复数负载失配
# ═══════════════════════════════════════════════════════════════

class Scene03Mismatch(_BaseScene):
    def construct(self):
        self._setup_trackers(gamma=0.0)
        self._setup_ui(simple_transmission_line=True, animate=False)

        tl_x_start, tl_x_end = connected_transmission_line_range()
        fwd_formula = MathTex(
            r"V(z,t) = A\cos(\omega t - \beta z)",
            font_size=34, color=FORWARD_COLOR,
        )
        fwd_formula.move_to([0, TL_Y + 1.55, 0])

        self._start_wave_time()
        fwd = glow_wave_layers(tl_x_start, tl_x_end, self._fwd_fn(), FORWARD_COLOR)
        ripple_circles = VGroup()
        for i in range(4):
            c = Circle(radius=0.25 + i * 0.35,
                       stroke_color=ANTENNA_OK, stroke_width=4.5,
                       stroke_opacity=0.7 - i * 0.15, fill_opacity=0)
            c.move_to(self.ant_body.get_center())
            ripple_circles.add(c)
        self.add(fwd_formula, fwd, ripple_circles)
        self.wait(1.0)

        self.play(FadeOut(self.ant_z), run_time=0.4)

        self.play(self.gamma_tracker.animate.set_value(MISMATCH_GAMMA_MAG),
                  run_time=1.0, rate_func=smooth)
        self._update_param_texts(
            self.params,
            r"$Z_0 = 50\Omega$",
            r"$Z_L = 25 + j25\,\Omega$",
            r"$\Gamma = 0.447\angle 116.57^\circ$",
            r"$\mathrm{VSWR} = 2.62$",
        )

        ref = glow_wave_layers(
            tl_x_start, tl_x_end,
            lambda x: wave_reflected_mismatch(x, self.time_tracker.get_value()),
            REFLECTED_COLOR,
            reverse=True,
        )
        self.play(
            LaggedStart(
                *[Create(layer) for layer in ref],
                lag_ratio=0.08,
            ),
            run_time=1.5,
        )
        self.play(FadeOut(fwd_formula), run_time=0.5)

        total_formula = MathTex(
            r"V_{total}(z,t) = A\cos(\omega t - \beta z)"
            r" + 0.447A\cos(\omega t + \beta z + 116.57^\circ)",
            font_size=26, color=TEXT_PRIMARY,
        )
        total_formula.move_to([0, TL_Y + 1.55, 0])
        if total_formula.width > 12.4:
            total_formula.scale(12.4 / total_formula.width)
        self.play(Write(total_formula), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(total_formula), run_time=0.5)

        vmax_formula = MathTex(
            r"V_{max} = A + |\Gamma|A = A(1 + 0.447) = 1.447A",
            font_size=32, color=WARNING_COLOR,
        )
        vmax_formula.move_to([0, TL_Y + 1.55, 0])
        if vmax_formula.width > 12.4:
            vmax_formula.scale(12.4 / vmax_formula.width)
        self.play(Write(vmax_formula), run_time=1.0)
        self.wait(1.5)


# ═══════════════════════════════════════════════════════════════
# 场景4：反射波形成
# ═══════════════════════════════════════════════════════════════

class Scene04ReflectedWave(_BaseScene):
    def construct(self):
        self._setup_trackers(gamma=1.0)  # 已是失配状态
        self._setup_ui()

        # 天线直接显示为失配状态
        self.ant_body.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD)
        new_zl = Tex(r"$Z_L = \infty\Omega$", font_size=22, color=WARNING_COLOR)
        new_zl.move_to(self.ant_z.get_center())
        self.ant_z = new_zl
        self.ant_group[1][1] = new_zl

        status_ch = Text("天线阻抗失配！", font="sans-serif",
                         font_size=20, color=WARNING_COLOR)
        status_math = MathTex(r"Z_L \to \infty", font_size=28, color=WARNING_COLOR)
        status_text = VGroup(status_ch, status_math).arrange(RIGHT, buff=0.15)
        status_text.move_to([0, BOT_Y, 0])
        self.status = status_text

        # 直接显示（不播放动画，因为场景开始就是失配状态）
        self.add(self.pa_group, self.ant_group, self.tl_group, self.panel_group, status_text)
        self.play(FadeIn(self.pa_group), FadeIn(self.ant_group),
                  FadeIn(self.tl_group), FadeIn(self.panel_group),
                  FadeIn(status_text), run_time=0.5)

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
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)

        self.wait(4.0)

        self.play(FadeOut(fwd_arrow), FadeOut(fwd_label),
                  FadeOut(ref_arrow), FadeOut(ref_label),
                  FadeOut(pf_combined), FadeOut(pr_combined), run_time=0.5)
        self.remove(fwd, ref)


# ═══════════════════════════════════════════════════════════════
# 场景5：驻波形成
# ═══════════════════════════════════════════════════════════════

class Scene05StandingWave(_BaseScene):
    def _update_param_texts(self, params, z0_str, zl_str, gamma_str, vswr_str):
        """覆盖基类方法：每个字段在原位置替换，避免整组漂移。"""
        new_z0 = Tex(z0_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["z0"].get_center())
        new_zl = Tex(zl_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["zl"].get_center())
        new_gamma = Tex(gamma_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["gamma"].get_center())
        new_vswr = Tex(vswr_str, font_size=28, color=TEXT_SECONDARY).move_to(
            params["vswr"].get_center())
        self.play(
            Transform(params["z0"], new_z0, replace_mobject_with_target_in_scene=True),
            Transform(params["zl"], new_zl, replace_mobject_with_target_in_scene=True),
            Transform(params["gamma"], new_gamma, replace_mobject_with_target_in_scene=True),
            Transform(params["vswr"], new_vswr, replace_mobject_with_target_in_scene=True),
            run_time=1.5,
        )
        params["z0"] = new_z0
        params["zl"] = new_zl
        params["gamma"] = new_gamma
        params["vswr"] = new_vswr

    def construct(self):
        self._setup_trackers(gamma=1.0)
        self._setup_ui()

        # 天线直接设为失配状态（不播动画）
        self.ant_body.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD)
        new_zl = Tex(r"$Z_L = \infty\Omega$", font_size=22, color=WARNING_COLOR)
        new_zl.move_to(self.ant_z.get_center())
        self.ant_z = new_zl

        status_ch = Text("天线阻抗失配！", font="sans-serif",
                         font_size=20, color=WARNING_COLOR)
        status_math = MathTex(r"Z_L \to \infty", font_size=28, color=WARNING_COLOR)
        status_text = VGroup(status_ch, status_math).arrange(RIGHT, buff=0.15)
        status_text.move_to([0, BOT_Y, 0])
        self.status = status_text

        self.add(self.pa_group, self.ant_group, self.tl_group, self.panel_group, status_text)
        self.play(FadeIn(self.pa_group), FadeIn(self.ant_group),
                  FadeIn(self.tl_group), FadeIn(self.panel_group),
                  FadeIn(status_text), run_time=0.5)

        # 驻波公式
        standing_formula = MathTex(
            r"V(z,t) = V_f \cos(\omega t - \beta z) + V_r \cos(\omega t + \beta z)",
            font_size=30, color=TEXT_PRIMARY,
        )
        standing_formula.move_to([0, TOP_Y - 1.2, 0])
        self.play(Write(standing_formula), run_time=1.0)

        # 驻波
        self._start_wave_time()
        sw = glow_wave_layers(TL_LEFT, TL_RIGHT, self._tot_fn(),
                              STANDING_COLOR, glow_count=4)
        self.play(FadeIn(sw), run_time=1.0)

        new_status = Text("驻波形成 — 节点与腹点", font="sans-serif",
                          font_size=20, color=STANDING_COLOR)
        new_status.move_to([0, BOT_Y, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)

        # 节点标记
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
            self.params,
            r"$Z_0 = 50\Omega$", r"$Z_L = \infty\Omega$",
            r"$\Gamma = 1.00$", r"$\mathrm{VSWR} \to \infty$",
        )
        self.wait(2.0)

        self.play(FadeOut(standing_formula), FadeOut(node_dots),
                  FadeOut(antinode_dots), FadeOut(node_labels),
                  FadeOut(anti_labels), run_time=0.5)
        self.remove(sw)


# ═══════════════════════════════════════════════════════════════
# 场景6：功放端过压
# ═══════════════════════════════════════════════════════════════

class Scene06Overvoltage(_BaseScene):
    def construct(self):
        self._setup_trackers(gamma=1.0)
        self._setup_ui()

        # 天线直接显示失配
        self.ant_body.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD)
        new_zl = Tex(r"$Z_L = \infty\Omega$", font_size=22, color=WARNING_COLOR)
        new_zl.move_to(self.ant_z.get_center())
        self.ant_z = new_zl

        status_text = Text("驻波形成 — 节点与腹点", font="sans-serif",
                           font_size=20, color=STANDING_COLOR)
        status_text.move_to([0, BOT_Y, 0])
        self.status = status_text

        self.add(self.pa_group, self.ant_group, self.tl_group, self.panel_group, status_text)
        self.play(FadeIn(self.pa_group), FadeIn(self.ant_group),
                  FadeIn(self.tl_group), FadeIn(self.panel_group),
                  FadeIn(status_text), run_time=0.5)

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

        # Vmax 公式
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
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.6)
        self.wait(1.5)


# ═══════════════════════════════════════════════════════════════
# 场景7：功放烧毁
# ═══════════════════════════════════════════════════════════════

class Scene07Failure(_BaseScene):
    def construct(self):
        self._setup_trackers(gamma=1.0)
        self._setup_ui()

        # 天线失配状态
        self.ant_body.set_fill_color(ANTENNA_BAD).set_stroke_color(ANTENNA_BAD)
        new_zl = Tex(r"$Z_L = \infty\Omega$", font_size=22, color=WARNING_COLOR)
        new_zl.move_to(self.ant_z.get_center())
        self.ant_z = new_zl

        status_text = Text("电压超过MOSFET击穿极限！", font="sans-serif",
                           font_size=20, color=DANGER_COLOR)
        status_text.move_to([0, BOT_Y, 0])
        self.status = status_text

        self.add(self.pa_group, self.ant_group, self.tl_group, self.panel_group, status_text)
        self.play(FadeIn(self.pa_group), FadeIn(self.ant_group),
                  FadeIn(self.tl_group), FadeIn(self.panel_group),
                  FadeIn(status_text), run_time=0.5)

        # 驻波
        self._start_wave_time()
        sw = glow_wave_layers(TL_LEFT, TL_RIGHT, self._tot_fn(),
                              STANDING_COLOR, glow_count=4)
        self.add(sw)

        # 镜头已在功放附近
        self.camera.frame.scale(0.55).move_to([PA_X + 0.5, TL_Y, 0])

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
        p_loss = MathTex(r"P_{\mathrm{loss}} = I^2 R", font_size=36, color=DANGER_COLOR)
        p_group = VGroup(p_vi, p_loss)
        p_group.arrange(DOWN, buff=0.3)
        p_group.next_to(pa_fail, DOWN, buff=0.5)
        self.play(Write(p_group), run_time=0.8)

        new_status = Text("功放烧毁！输出归零", font="sans-serif",
                          font_size=20, color=DANGER_COLOR)
        new_status.move_to([PA_X + 0.5, BOT_Y - 0.5, 0])
        self.play(Transform(self.status, new_status,
                           replace_mobject_with_target_in_scene=True), run_time=0.5)

        dark_overlay = Rectangle(
            width=config.frame_width * 2, height=config.frame_height * 2,
            fill_color=BLACK, fill_opacity=0, stroke_width=0,
        )
        dark_overlay.move_to(self.camera.frame.get_center())
        self.add(dark_overlay)
        self.play(dark_overlay.animate.set_fill_opacity(0.85), run_time=1.5)
        self.wait(1.0)


# ═══════════════════════════════════════════════════════════════
# 场景8：总结
# ═══════════════════════════════════════════════════════════════

class Scene08Summary(Scene):
    def construct(self):
        time_tracker = ValueTracker(0)
        time_tracker.add_updater(lambda m, dt: m.increment_value(dt))

        conclusion = Text(
            "阻抗失配 → 反射 → 驻波 → 过压/过流 → 功放烧毁",
            font="sans-serif", font_size=34, color=TEXT_PRIMARY,
        )
        conclusion.set_stroke(BLUE_D, width=0.5, opacity=0.4)
        conclusion.move_to([0, 1.8, 0])
        self.play(Write(conclusion), run_time=1.5)

        bg_wave = always_redraw(lambda:
            FunctionGraph(
                lambda x: 0.4 * np.sin(K * x) * np.cos(OMEGA * time_tracker.get_value()),
                x_range=[TL_LEFT, TL_RIGHT],
                color=STANDING_COLOR, stroke_width=2, stroke_opacity=0.2,
            )
        )
        self.add(bg_wave)
        self.wait(4.0)
        self.play(FadeOut(VGroup(conclusion, bg_wave)),
                  run_time=1.5)


# ═══════════════════════════════════════════════════════════════
# 场景9：基础布局
# ═══════════════════════════════════════════════════════════════

class Scene09SimpleLayout(Scene):
    def construct(self):
        pa_group, _, _ = build_pa_module()
        ant_group, _, _, _ = build_antenna()
        tl_group = build_simple_transmission_line(stroke_width=5.0)

        self.play(
            FadeIn(pa_group),
            FadeIn(tl_group),
            FadeIn(ant_group),
            run_time=1.0,
        )
        self.wait(4.0)


# ═══════════════════════════════════════════════════════════════
# 场景10：λ/4 阻抗变换器匹配
# ═══════════════════════════════════════════════════════════════

class Scene10ImpedanceTransformer(MovingCameraScene):
    def _two_wire_segment(self, x_start, x_end, color, stroke_width=5.0,
                          opacity=1.0):
        gap = 0.65
        top = Line([x_start, TL_Y + gap, 0], [x_end, TL_Y + gap, 0],
                   color=color, stroke_width=stroke_width,
                   stroke_opacity=opacity)
        bot = Line([x_start, TL_Y - gap, 0], [x_end, TL_Y - gap, 0],
                   color=color, stroke_width=stroke_width,
                   stroke_opacity=opacity)
        return VGroup(top, bot)

    def _formula_at_top(self, tex, color=TEXT_PRIMARY, font_size=30,
                        y_offset=0.35, x_offset=0):
        formula = MathTex(tex, font_size=font_size, color=color)
        frame = self.camera.frame
        formula.move_to([
            frame.get_center()[0] + x_offset,
            frame.get_center()[1] + frame.height / 2 - y_offset,
            0,
        ])
        max_width = frame.width * 0.9
        if formula.width > max_width:
            formula.scale(max_width / formula.width)
        return formula

    def construct(self):
        time_tracker = ValueTracker(0)
        time_tracker.add_updater(lambda m, dt: m.increment_value(dt))

        pa_group, _, _ = build_pa_module()
        ant_group, ant_body, _, ant_z = build_antenna()
        new_ant_z = MathTex(r"25+j25\,\Omega",
                            font_size=18, color=TEXT_SECONDARY)
        new_ant_z.move_to(ant_z.get_center())
        if new_ant_z.width > ANT_W * 1.1:
            new_ant_z.scale((ANT_W * 1.1) / new_ant_z.width)
        ant_group[1][1] = new_ant_z
        x_start, x_end = connected_transmission_line_range()
        full_line = build_simple_transmission_line(stroke_width=5.0)

        self.play(
            FadeIn(pa_group),
            FadeIn(full_line),
            FadeIn(ant_group),
            run_time=1.0,
        )
        self.wait(0.5)

        antenna_focus = [3.0, 0.0, 0]
        self.play(
            self.camera.frame.animate.set_width(6.2).move_to(antenna_focus),
            run_time=1.4,
        )

        cut_x = 2.45
        min_dot = Dot([cut_x, TL_Y, 0], radius=0.08, color=WARNING_COLOR)
        min_line = DashedLine([cut_x, TL_Y - 0.9, 0], [cut_x, TL_Y + 0.9, 0],
                              color=WARNING_COLOR, stroke_width=2.5)
        min_label = Text("电压最小点", font="sans-serif", font_size=18,
                         color=WARNING_COLOR)
        min_label.next_to(min_dot, UP, buff=0.25)
        min_label.shift(RIGHT*0.7)
        self.play(Create(min_line), FadeIn(min_dot), FadeIn(min_label),
                  run_time=0.8)

        r_min_formula = self._formula_at_top(
            r"R_{min} = \frac{Z_0}{\rho} = \frac{50}{2.618}"
            r" \approx 19.1\,\Omega",
            color=WARNING_COLOR,
            font_size=30,
            y_offset=0.5,
            x_offset=-0.8
        )
        self.wait(0.5)
        self.play(Write(r_min_formula), run_time=1.0)
        self.wait(1.1)

        left_stub = self._two_wire_segment(x_start, cut_x - 0.08, LINE_GLOW,
                                           stroke_width=5.0, opacity=0.35)
        antenna_side = self._two_wire_segment(cut_x, x_end, ANTENNA_OK,
                                              stroke_width=5.0)
        cut_mark_1 = Line([cut_x - 0.08, TL_Y + 0.85, 0],
                          [cut_x + 0.08, TL_Y + 0.45, 0],
                          color=WARNING_COLOR, stroke_width=4)
        cut_mark_2 = Line([cut_x - 0.08, TL_Y - 0.45, 0],
                          [cut_x + 0.08, TL_Y - 0.85, 0],
                          color=WARNING_COLOR, stroke_width=4)
        self.play(
            FadeOut(full_line),
            FadeIn(left_stub),
            FadeIn(antenna_side),
            Create(cut_mark_1),
            Create(cut_mark_2),
            run_time=0.9,
        )

        zt_formula = self._formula_at_top(
            r"Z_T = \sqrt{R_{min}\cdot Z_0}"
            r" = \sqrt{19.1 \times 50} = \sqrt{955}"
            r" \approx 30.9\,\Omega",
            color=TEXT_PRIMARY,
            font_size=28,
        )
        self.play(FadeOut(r_min_formula), run_time=1.0)

        transformer_len = 1.25
        transformer_start = cut_x - transformer_len
        transformer = self._two_wire_segment(transformer_start, cut_x,
                                             WARNING_COLOR, stroke_width=7.0)
        transformer_label = MathTex(r"\lambda/4,\ Z_T=30.9\Omega",
                                    font_size=22, color=WARNING_COLOR)
        transformer_label.next_to(transformer, DOWN, buff=0.18)
        standard_left = self._two_wire_segment(x_start, transformer_start,
                                               FORWARD_COLOR, stroke_width=5.0)

        self.play(
            FadeOut(left_stub),
            FadeOut(cut_mark_1),
            FadeOut(cut_mark_2),
            FadeIn(transformer),
            run_time=1.2,
        )
        self.wait(1.0)

        self.play(Write(zt_formula), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(zt_formula), run_time=0.5)
        self.play(
            self.camera.frame.animate.set_width(config.frame_width).move_to(ORIGIN),
            run_time=1.4,
        )
        self.wait(0.5)
        self.play(Write(transformer_label), FadeOut(min_label), FadeOut(min_dot), FadeOut(min_line), run_time=0.5)

        zin_formula = self._formula_at_top(
            r"Z_{in} = \frac{Z_T^2}{R_{min}}"
            r" = \frac{30.9^2}{19.1} \approx 50\,\Omega",
            color=FORWARD_COLOR,
            font_size=30,
            y_offset=0.8,
        )
        self.play(Write(zin_formula), run_time=1.0)
        self.wait(1.0)

        match_formula = self._formula_at_top(
            r"Z_L = Z_0 = 50\,\Omega",
            color=FORWARD_COLOR,
            font_size=34,
            y_offset=0.8,
        )
        self.play(
            FadeOut(zin_formula),
            run_time=1.0,
        )
        self.wait(1.0)
        self.play(FadeIn(standard_left),run_time=1.0)
        self.wait(1.0)
        self.play(Write(match_formula), run_time=1.0)

        fwd_wave = glow_wave_layers(
            x_start, x_end,
            lambda x: AMP * np.cos(OMEGA * time_tracker.get_value() - K * x),
            FORWARD_COLOR,
        )
        self.wait(1.0)
        self.play(
            LaggedStart(
                *[Create(layer) for layer in fwd_wave],
                lag_ratio=0.08,
            ),
            FadeOut(transformer_label),
            run_time=1.5,
        )
        self.wait(1.0)
        # 天线辐射波纹
        ripple_circles = VGroup()
        for i in range(4):
            c = Circle(radius=0.25 + i * 0.35,
                       stroke_color=ANTENNA_OK, stroke_width=4.5,
                       stroke_opacity=0.7 - i * 0.15, fill_opacity=0)
            c.move_to(ant_body.get_center())
            ripple_circles.add(c)
        self.play(LaggedStart(
            *[GrowFromCenter(c) for c in ripple_circles], lag_ratio=0.3,
        ), run_time=2.0)
        self.wait(1.5)

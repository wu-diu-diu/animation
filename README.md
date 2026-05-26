# animation

本项目使用 [Manim Community Edition](https://www.manim.community/) 制作“天线阻抗失配导致功放烧毁”的工程科普动画。仓库中主要有两个 Python 脚本：`main.py` 和 `combined.py`。

## 两个 Python 文件的作用

### `main.py`

`main.py` 是分场景版本，包含完整动画所需的公共绘图函数、布局参数、波形函数，以及多个独立场景类。

适合用于：

- 单独渲染某一个场景，便于调试和修改。
- 渲染完整动画类 `AntennaMismatch`。
- 查看每一段动画的具体实现逻辑。

主要场景类包括：

```text
Scene01Title
Scene02NormalMatch
Scene03Mismatch
Scene04ReflectedWave
Scene05StandingWave
Scene06Overvoltage
Scene07Failure
Scene08Summary
AntennaMismatch
```

### `combined.py`

`combined.py` 是合并版本，把完整动画组织成一个连续场景类：

```text
AntennaMismatchCombined
```

适合用于：

- 一次性渲染完整视频。
- 输出最终成片。
- 避免逐个场景拼接。

## 环境准备

项目依赖写在 `pyproject.toml` 中，建议使用 `uv` 安装：

```bash
uv sync
```

如果你已经在虚拟环境中安装好依赖，也可以直接使用 `manim` 命令。

## 生成低清晰度视频

低清晰度适合快速预览，渲染速度更快。

渲染完整分场景版本：

```bash
uv run manim render -q l main.py AntennaMismatch
```

渲染完整合并版本：

```bash
uv run manim render -q l combined.py AntennaMismatchCombined
```

## 生成高清晰度视频

高清晰度适合最终输出，但渲染时间更长。

渲染完整分场景版本：

```bash
uv run manim render -q h main.py AntennaMismatch
```

渲染完整合并版本：

```bash
uv run manim render -q h combined.py AntennaMismatchCombined
```

## 只生成单个场景视频

如果只想生成某一个场景，请使用 `main.py` 中的单个场景类名。

例如，只渲染标题场景：

```bash
uv run manim render -q l main.py Scene01Title
```

例如，只渲染“正常匹配”场景：

```bash
uv run manim render -q l main.py Scene02NormalMatch
```

例如，只渲染“驻波形成”场景：

```bash
uv run manim render -q l main.py Scene05StandingWave
```

需要高清晰度时，把 `-q l` 改成 `-q h`：

```bash
uv run manim render -q h main.py Scene05StandingWave
```

## 输出文件位置

Manim 生成的视频通常会输出到 `media/videos/` 目录下。该目录是渲染产物，不需要提交到 Git。

## 清晰度参数说明

常用参数如下：

```text
-q l    低清晰度，适合快速预览
-q h    高清晰度，适合最终输出
```

开发时建议先使用低清晰度确认动画效果，最终导出时再使用高清晰度。

## Manim 简易入门

### 1. 构建场景类

Manim 的视频由“场景类”组成。每个场景类通常继承 `Scene` 或 `MovingCameraScene`，并在 `construct()` 方法中编写画面内容和动画流程。

最简单的结构如下：

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        title = Text("Hello Manim")
        self.play(Write(title))
        self.wait(1)
```

本项目中，`Scene02NormalMatch`、`Scene03Mismatch`、`Scene10ImpedanceTransformer` 都是独立场景类，可以用类名单独渲染。

### 2. 构建方块、线段和公式

常用图形对象包括：

```python
box = RoundedRectangle(
    width=1.8,
    height=2.4,
    fill_color="#1a2a3a",
    fill_opacity=0.85,
    stroke_color="#336699",
    stroke_width=1.5,
)

line = Line(
    start=[-3, 0.65, 0],
    end=[3, 0.65, 0],
    color="#5588bb",
    stroke_width=5,
)

formula = MathTex(
    r"Z_L = Z_0 = 50\,\Omega",
    font_size=34,
    color="#00e5cc",
)
```

中文说明文字可使用 `Text()`：

```python
label = Text("电压最小点", font="sans-serif", font_size=18)
```

LaTeX 公式使用 `MathTex()` 或 `Tex()`，字符串前建议加 `r`，例如 `r"\lambda/4"`，避免反斜杠转义问题。

### 3. 设置和调整元素位置

Manim 坐标以画面中心为原点，`x` 向右，`y` 向上，`z` 通常写 `0`。

直接放到指定坐标：

```python
formula.move_to([0, 2.5, 0])
dot.move_to([2.45, 0, 0])
```

相对移动：

```python
label.shift(DOWN * 0.3)
box.shift(RIGHT * 1.0)
```

放到另一个元素旁边：

```python
label.next_to(dot, UP, buff=0.35)
formula.next_to(box, DOWN, buff=0.2)
```

常用方向包括 `UP`、`DOWN`、`LEFT`、`RIGHT`。`buff` 表示间距，数值越大距离越远。

### 4. 播放动画

创建元素后，可以用 `self.add()` 直接显示，或用 `self.play()` 播放动画。

```python
self.add(box)
self.play(FadeIn(box))
self.play(Write(formula))
self.play(Create(line))
self.wait(1.0)
```

如果要让线条或波形从左到右出现，可以用 `Create()`：

```python
self.play(Create(line), run_time=1.5)
```

如果是多个发光波形图层，可以用 `LaggedStart()`：

```python
self.play(
    LaggedStart(
        *[Create(layer) for layer in wave_group],
        lag_ratio=0.08,
    ),
    run_time=1.5,
)
```

### 5. 镜头移动

需要镜头拉近或拉远时，场景类应继承 `MovingCameraScene`：

```python
class MyZoomScene(MovingCameraScene):
    def construct(self):
        self.play(
            self.camera.frame.animate.set_width(6.2).move_to([3, 0, 0]),
            run_time=1.4,
        )
```

恢复到默认全景：

```python
self.play(
    self.camera.frame.animate.set_width(config.frame_width).move_to(ORIGIN),
    run_time=1.4,
)
```

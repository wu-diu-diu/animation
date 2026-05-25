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

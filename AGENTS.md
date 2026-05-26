# Repository Guidelines

## Project Structure & Module Organization

This repository contains Manim-based Python animation scripts for an antenna impedance mismatch explainer. `main.py` is the primary source file and includes reusable drawing helpers plus individual scene classes such as `Scene01Title`, `Scene02NormalMatch`, and `AntennaMismatch`. `combined.py` contains a full combined scene, `AntennaMismatchCombined`, intended for rendering the complete animation in one pass. `pyproject.toml` and `uv.lock` define the Python 3.11+ environment and dependencies.

Generated Manim outputs are written under `media/` and should stay uncommitted. The `test/` directory currently exists as a placeholder and has no committed test files. Project notes may live in Markdown files such as `动画制作.md`.

## Build, Test, and Development Commands

Use `uv sync` to install the locked dependencies into the local environment. Run `uv run python main.py` only for basic import/runtime checks; rendering is done through Manim.

Common render commands:

```bash
uv run manim render -q l main.py Scene01Title
uv run manim render -q l main.py AntennaMismatch
uv run manim render -q h combined.py AntennaMismatchCombined
```

Use low quality (`-q l`) while iterating and high quality (`-q h`) for final output.

## Coding Style & Naming Conventions

Follow standard Python style with 4-space indentation. Keep scene classes in `PascalCase`, helper functions in `snake_case`, and shared layout/color constants in `UPPER_SNAKE_CASE`. Prefer small helper functions for reusable Manim objects, as shown by `build_pa_module()` and `glow_wave_layers()`.

The existing scripts use Chinese labels and comments for animation content; keep new user-facing scene text consistent with that style. Avoid committing generated cache folders such as `__pycache__/`.

## Testing Guidelines

There is no configured test framework yet. For changes to scene logic, run at least one low-quality Manim render of the affected scene and confirm it completes without errors. If adding tests, place them under `test/`, name files `test_*.py`, and use `pytest` so they can run with:

```bash
uv run pytest
```

## Commit & Pull Request Guidelines

The repository currently has no commit history, so no project-specific commit convention is established. Use short imperative commit messages such as `Add reflected wave scene` or `Fix antenna mismatch labels`.

Pull requests should describe the changed scenes, list render commands used for verification, and include screenshots or video clips when visuals change. Link related issues when available and keep generated `media/` artifacts out of the diff.

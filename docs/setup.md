# 開発環境構築 (Setup)

## 共通

```bash
git clone <this repo>
cd Vertical_Multi-Joint_Robot
git lfs install && git lfs pull
```

## 上位ソフト (robot_core)

```bash
cd software/robot_core
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## ROS 2

> TBD: ディストリビューション (Humble / Jazzy) を決めてから記載。

```bash
cd software/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## ファームウェア

> TBD: PlatformIO / STM32CubeIDE など、ツールチェーン決定後に記載。

## CAD・基板

- CAD: TBD (Fusion 360 / SolidWorks / FreeCAD)
- 基板: KiCad 8 以降。共通ライブラリは `electrical/pcb/lib/` をプロジェクトに登録する。

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

## ドキュメントサイト (GitHub Pages)

本サイトは MkDocs Material で生成し、デフォルトブランチへの push で自動デプロイされる。

```bash
pip install -r requirements-docs.txt
mkdocs serve                  # http://127.0.0.1:8000 でプレビュー
mkdocs build --strict         # CI と同じチェック (リンク切れで失敗する)
```

- 設定: `mkdocs.yml` (ナビゲーションはここに手で追加する)
- ワークフロー: `.github/workflows/docs.yml`
- 公開URL: <https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/>

新しいドキュメントを追加したら `mkdocs.yml` の `nav:` にも追記すること。
`--strict` を付けているので、nav から漏れたページやリンク切れは CI で失敗する。

### 初回のみ必要な手動設定

リポジトリの **Settings → Pages** で **Source** を **GitHub Actions** に設定する。
`GITHUB_TOKEN` には Pages サイトを新規作成する権限がないため、
この操作だけはワークフローから自動化できない (一度設定すれば以降は不要)。

# VMJR — 3軸 垂直多関節ロボット

3自由度 (旋回・肩・肘) の垂直多関節ロボットを、**機構・電装・ファーム・上位ソフト**
まとめて開発するためのリポジトリ。

## リポジトリ構成

| ディレクトリ | 内容 |
|---|---|
| `docs/` | 要求仕様・機体諸元・システム構成・運動学の導出 |
| `mechanical/` | CAD (ネイティブ + STEP/STL/DXF)、2D図面、構造解析、機械BOM |
| `electrical/` | KiCad 基板プロジェクト、回路図、ガーバー、ハーネス図、電気BOM |
| `firmware/` | 関節制御MCU のファームウェア、通信プロトコル定義 |
| `software/` | 運動学・軌道生成ライブラリ、ROS 2 パッケージ、GUI |
| `simulation/` | Gazebo モデル、作業領域・トルク検討ノート |
| `config/` | リンク長・減速比・可動範囲・キャリブレーション値 (**全ての正本**) |
| `tests/` | ユニット / 結合 / HIL テスト |
| `tools/` | パラメータ生成・メッシュ同期・BOM統合スクリプト |

詳細な責務と運用ルールは **[docs/project_structure.md](docs/project_structure.md)** を参照。

## 設計資料

**📖 <https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/>** — GitHub Pages で公開中

| ドキュメント | 内容 |
|---|---|
| [設計計算書](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/design_calculations/) | 可搬質量・速度性能・位置決め精度の試算 (計算過程つき) |
| [要求仕様](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/requirements/) | 可搬質量・リーチ・繰返し精度の目標値 |
| [機体諸元](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/specifications/) | 確定値・質量内訳・機体番号との対応 |
| [システム構成](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/architecture/) | ブロック図・責務分担・通信仕様 |
| [運動学](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/kinematics/) | 座標系・DHパラメータ・逆運動学・特異点 |
| [安全設計](https://suke-toudara.github.io/Vertical_Multi-Joint_Robot/safety/) | 非常停止・リミットの三重化 |

設計計算書の数値は `tools/calc_payload.py` の出力。前提を変えたら再実行して更新する。

### サイトのローカル確認

```bash
pip install -r requirements-docs.txt
mkdocs serve          # http://127.0.0.1:8000
```

`docs/` 以下を更新してデフォルトブランチに push すると、
`.github/workflows/docs.yml` が自動でビルド・デプロイする。

> **初回のみ手動設定が必要**: GitHub の
> [Settings → Pages](https://github.com/suke-toudara/Vertical_Multi-Joint_Robot/settings/pages)
> で **Source** を **GitHub Actions** に設定する。
> `GITHUB_TOKEN` には Pages サイトを新規作成する権限がないため、
> この1ステップだけはワークフローから自動化できない。

## 設計上の原則

1. **パラメータは `config/` に集約** — リンク長や減速比を CAD・URDF・ファームに
   重複して書かない。`tools/gen_params.py` で生成する。
2. **運動学は ROS 非依存** — `software/robot_core/` に実装し、ROS 2 からは import
   するだけにする。実機・ROS なしでテストできる状態を保つ。
3. **バイナリCADは STEP を併置** — ネイティブCADは差分が取れないので、
   レビューと共有は STEP で行う。
4. **基板のガーバーはリビジョン単位で保存** — 製造した実物と一対一で追跡する。

## はじめに

```bash
git clone <this repo>
cd Vertical_Multi-Joint_Robot
git lfs install && git lfs pull      # CAD・PDF は Git LFS 管理
```

開発環境の構築手順は `docs/setup.md`、開発の進め方は
`docs/project_structure.md` の「開発の進め方」を参照。

## ステータス

構成定義と、手持ちアクチュエータ (AK80-64 ×2 + EduLite 05) での性能試算まで。
現時点の試算では **リーチ 370 mm / 可搬質量 0.62 kg / 手先速度 1.86 m/s** が
成立見込み (詳細と前提は `docs/design_calculations.md`)。
未決定事項は `docs/project_structure.md` 末尾のリストを参照。

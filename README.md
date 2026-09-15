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

構成定義のみ。仕様の未決定事項は `docs/project_structure.md` 末尾のリストを参照。

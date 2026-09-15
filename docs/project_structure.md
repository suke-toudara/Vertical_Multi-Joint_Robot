# プロジェクト構成 (Project Structure)

3軸垂直多関節ロボット `VMJR` (Vertical Multi-Joint Robot) の、
**機構 (CAD) / 電装 (基板) / ファームウェア / 上位ソフトウェア** を
1つのリポジトリで管理するための構成定義。

---

## 1. 前提とスコープ

| 項目 | 想定 |
|---|---|
| 自由度 | 3軸 (J1: 旋回 / J2: 肩 / J3: 肘)、手先はオプションのエンドエフェクタ |
| 駆動 | ステッピング or BLDC + 減速機 (ハーモニック / サイクロイド / ベルト) |
| 制御構成 | 上位PC (ROS 2) ── CAN / シリアル ── 関節コントローラMCU |
| CAD | Fusion 360 / SolidWorks などのネイティブ + STEP / STL 中間形式 |
| 基板 | KiCad プロジェクト (回路図・PCB・ガーバー) |
| 言語 | ファーム: C/C++ (STM32 or ESP32) / 上位: Python + C++ |

> これらは初期仮定。確定した値は `docs/specifications.md` と
> `config/robot_params.yaml` を**唯一の正**とし、他はそこを参照する。

---

## 2. リポジトリ全体像

```
Vertical_Multi-Joint_Robot/
├── README.md                   # プロジェクト概要・入口
├── LICENSE
├── .gitattributes              # Git LFS 対象 (CAD/STEP/STL/PDF など)
├── .gitignore
│
├── docs/                       # 設計ドキュメント一式
├── mechanical/                 # 機構設計 (CAD・図面・BOM)
├── electrical/                 # 電装設計 (基板・配線・BOM)
├── firmware/                   # MCU ファームウェア
├── software/                   # 上位ソフト (ライブラリ・ROS 2・GUI)
├── simulation/                 # シミュレーション環境
├── config/                     # 機体パラメータ・キャリブレーション値
├── tests/                      # 結合 / HIL テスト
├── tools/                      # 開発補助スクリプト
└── .github/workflows/          # CI
```

設計思想は **「層ごとに分け、層をまたぐ値は `config/` に集約する」**。
リンク長・減速比・可動範囲といった値は CAD・URDF・ファーム・上位ソフトの
4箇所に散らばりがちなので、`config/robot_params.yaml` を単一の情報源とし、
URDF やファームのヘッダは**そこから生成**する (`tools/gen_params.py`)。

---

## 3. 各ディレクトリの責務

### 3.1 `docs/` — ドキュメント

```
docs/
├── project_structure.md   # 本書
├── requirements.md        # 要求仕様 (可搬質量・リーチ・繰返し精度・速度)
├── specifications.md      # 機体諸元 (確定値・リンク長・減速比・質量特性)
├── architecture.md        # システム構成図・信号フロー・通信仕様
├── kinematics.md          # DHパラメータ、順/逆運動学の導出と解の分岐
├── setup.md               # 開発環境構築 (ROS 2・ツールチェーン・CAD)
├── safety.md              # 非常停止・ソフトリミット・リスクアセスメント
├── adr/                   # Architecture Decision Record (設計判断の記録)
│   └── 0001-example.md
└── images/                # 図版 (構成図・座標系定義)
```

`adr/` には「なぜハーモニックではなくベルト減速にしたか」のような
**後から理由を思い出せない判断**を1件1ファイルで残す。

### 3.2 `mechanical/` — 機構

```
mechanical/
├── cad/
│   ├── source/            # ネイティブCAD (.f3d / .sldprt / .FCStd) ★LFS
│   ├── parts/             # 部品単位の中間ファイル
│   ├── assembly/          # アセンブリ
│   └── export/
│       ├── step/          # STEP (AP214) — 外部共有・解析用の正本
│       ├── stl/           # 3Dプリント用 / URDF メッシュ元データ
│       └── dxf/           # 板金・レーザーカット用
├── drawings/              # 2D図面 PDF (公差・加工指示)
├── fea/                   # 構造解析 (たわみ・固有振動数) の結果とレポート
└── bom/
    └── mechanical_bom.csv # 機械部品表 (型番・メーカ・数量・単価・入手先)
```

**運用ルール**
- ネイティブCADはバイナリで差分が取れないため、必ず **STEP を同時にコミット**する。
  レビュー・外部共有・履歴確認は STEP 側で行う。
- URDF 用メッシュは `stl/` を正本とし、`software/ros2_ws/src/vmjr_description/meshes/`
  へはコピーではなくエクスポートスクリプト (`tools/export_meshes.py`) で同期する。
- ファイル名は `VMJR-M-001_link1_base.step` のように
  `<プロジェクト>-<M/E>-<連番>_<名称>` で統一。

### 3.3 `electrical/` — 電装

```
electrical/
├── pcb/
│   ├── main_controller/   # メイン制御基板 (KiCad プロジェクト一式)
│   ├── motor_driver/      # モータドライバ基板
│   ├── io_breakout/       # センサ・I/O 中継基板
│   └── lib/               # 共通シンボル・フットプリント・3Dモデル
├── schematics/            # 回路図 PDF (レビュー用エクスポート)
├── fab/                   # 製造データ (Gerber / ドリル / 実装用 Pick&Place) ★LFS
├── wiring/                # ハーネス図・結線表・コネクタピンアサイン
├── datasheets/            # 採用部品のデータシート ★LFS
└── bom/
    └── electrical_bom.csv # 電子部品表 (リファレンス・型番・実装区分)
```

**運用ルール**
- KiCad の `.kicad_sch` / `.kicad_pcb` はテキストなので **LFS に入れず**、差分レビュー可能に保つ。
- ガーバーは `fab/<基板名>/rev<N>/` に**リビジョンごと**に保存し、上書きしない
  (製造済み基板と一対一で追跡できるようにするため)。
- コネクタのピンアサインは `wiring/pinout.md` に集約し、
  ファームの `firmware/common/include/pinmap.h` と一致させる。

### 3.4 `firmware/` — ファームウェア

```
firmware/
├── joint_controller/      # 関節制御MCU (電流/速度/位置ループ、原点復帰)
│   ├── src/
│   ├── include/
│   ├── test/              # ホスト上で走るユニットテスト
│   └── platformio.ini     # or CMakeLists.txt
├── common/
│   └── include/
│       ├── protocol.h     # 上位⇔MCU 通信プロトコル定義 (★上位ソフトと共有)
│       └── pinmap.h       # ピン配置 (electrical/wiring と対応)
└── tools/                 # 書き込み・キャリブレーション・ログ取得スクリプト
```

`protocol.h` は上位ソフト (`software/robot_core/vmjr/comm/`) と
**同じ定義を共有する唯一の接点**。ここを変更したら双方のバージョンを上げる。

### 3.5 `software/` — 上位ソフトウェア

```
software/
├── robot_core/            # ROS 非依存の純Pythonライブラリ (単体で使える)
│   ├── vmjr/
│   │   ├── kinematics/    # 順運動学・逆運動学・ヤコビアン
│   │   ├── trajectory/    # 台形/S字速度、ジョイント空間・直交空間補間
│   │   ├── control/       # 上位制御ロジック
│   │   └── comm/          # シリアル/CAN 通信 (protocol.h に対応)
│   ├── tests/
│   └── pyproject.toml
├── ros2_ws/src/
│   ├── vmjr_description/  # URDF/xacro + メッシュ (RViz・MoveIt の基盤)
│   ├── vmjr_hardware/     # ros2_control ハードウェアインタフェース
│   ├── vmjr_bringup/      # launch ファイル・実機起動一式
│   ├── vmjr_moveit_config/# MoveIt 設定 (動作計画)
│   └── vmjr_msgs/         # 独自メッセージ・サービス定義
├── gui/                   # ティーチング/ジョグ操作 GUI
└── examples/              # 最小サンプル (pick & place など)
```

**ポイント**: 運動学は `robot_core` にだけ実装し、ROS 2 パッケージからは
それを import する。ROS を入れずにテスト・検証できる状態を保つことで、
ユニットテストと CI が軽くなる。

### 3.6 `simulation/` — シミュレーション

```
simulation/
├── gazebo/
│   ├── worlds/            # 作業環境モデル
│   └── models/            # ワーク・治具
└── notebooks/             # 作業領域・特異点・トルク見積りの検討ノート
```

実機が無い段階での逆運動学検証・可搬質量の見積りはここで行う。

### 3.7 `config/` — 機体パラメータ (単一の情報源)

```
config/
├── robot_params.yaml      # リンク長・質量・重心・減速比 ★すべての正本
├── joint_limits.yaml      # 可動範囲・最大速度・最大加速度・トルク上限
├── controllers.yaml       # ros2_control / ゲイン設定
└── calibration/
    └── offsets_<機体番号>.yaml  # 個体ごとの原点オフセット
```

`calibration/` は**機体固有**の値なので、機体番号でファイルを分ける。
`robot_params.yaml` は共通設計値で、ここを変えたら
`tools/gen_params.py` で URDF とファームのヘッダを再生成する。

### 3.8 `tests/` · `tools/` · `.github/`

```
tests/
├── unit/                  # 純粋なロジック (運動学・軌道生成)
├── integration/           # ROS 2 ノード間の結合
└── hil/                   # 実機接続テスト (手動実行、CIからは除外)

tools/
├── gen_params.py          # config/ → URDF・ファームヘッダ生成
├── export_meshes.py       # CAD STL → vmjr_description/meshes 同期
└── bom_merge.py           # 機械+電気 BOM の統合・発注リスト生成

.github/workflows/
├── ci.yml                 # lint + robot_core のユニットテスト
└── ros2.yml               # ROS 2 パッケージのビルド確認
```

---

## 4. Git 運用

### 4.1 Git LFS

CAD・データシート・製造データはバイナリで肥大するため LFS を使う。
`.gitattributes` の設定:

```
*.f3d   filter=lfs diff=lfs merge=lfs -text
*.sldprt filter=lfs diff=lfs merge=lfs -text
*.step  filter=lfs diff=lfs merge=lfs -text
*.stl   filter=lfs diff=lfs merge=lfs -text
*.pdf   filter=lfs diff=lfs merge=lfs -text
*.zip   filter=lfs diff=lfs merge=lfs -text
```

**LFS に入れないもの**: KiCad のソース (`.kicad_sch` / `.kicad_pcb`)、
YAML、URDF/xacro。テキストとして差分レビューする価値があるため。

### 4.2 リビジョン管理

| 対象 | 方法 |
|---|---|
| 機構部品 | 図面のリビジョン欄 + ファイル名 `_revB` |
| 基板 | `fab/<基板名>/rev<N>/` のディレクトリで固定、上書き禁止 |
| ソフト | Git タグ `v0.1.0` (SemVer) |
| 機体一台 | `docs/specifications.md` に「機体番号 ⇔ 各リビジョン」の対応表 |

実機は「機構revB + 基板rev2 + ファームv0.3.0」のような**組み合わせ**で
成立するので、その対応表を残すことが後の再現性を決める。

### 4.3 ブランチ

- `main` — 動作確認済み
- `feature/<領域>-<内容>` — 例: `feature/mech-j2-gearbox`, `feature/sw-ik-solver`
- CAD/基板は同一ファイルの並行編集ができないため、
  着手前に Issue でロックする運用にする。

---

## 5. 開発の進め方 (推奨順)

1. `docs/requirements.md` — 可搬質量・リーチ・繰返し精度を数値で決める
2. `config/robot_params.yaml` — リンク長・減速比の初期値を置く
3. `simulation/notebooks/` — 作業領域と必要トルクを検算し、上の値を確定
4. `mechanical/` — 確定値で CAD、STEP/STL をエクスポート
5. `electrical/` — 選定したモータに合わせてドライバ基板を設計
6. `firmware/` — 単軸で回す → 原点復帰 → 3軸同期
7. `software/robot_core/` — 運動学・軌道生成 (実機なしでテスト可能)
8. `software/ros2_ws/` — URDF・ros2_control で実機と接続
9. `tests/hil/` — 実機での繰返し精度測定、`docs/specifications.md` に記録

---

## 6. 未決定事項 (要確認)

- [ ] 駆動方式: ステッピング / BLDC + エンコーダ のどちらか
- [ ] 通信: CAN (拡張性重視) / RS-485 / USB-CDC のどれか
- [ ] MCU: STM32 / ESP32 / RP2040
- [ ] CAD ツール: Fusion 360 / SolidWorks / FreeCAD (`.gitattributes` の拡張子に影響)
- [ ] ROS 2 を使うか、自前の上位ソフトのみにするか
- [ ] エンドエフェクタを 4軸目として扱うか、独立系として扱うか

決まり次第、本書と `.gitattributes` を更新する。

# 機構設計

## ファイル配置

| 置き場所 | 入れるもの |
|---|---|
| `cad/source/` | ネイティブCAD (編集用の原本) — Git LFS |
| `cad/export/step/` | STEP — レビュー・外部共有・解析の正本 |
| `cad/export/stl/` | STL — 3Dプリント / URDF メッシュ元データ |
| `cad/export/dxf/` | DXF — 板金・レーザーカット |
| `drawings/` | 2D図面 PDF (公差・表面処理・加工指示) |
| `fea/` | 構造解析の入力条件と結果レポート |
| `bom/` | 機械部品表 CSV |

## ルール

- ネイティブCADを更新したら **STEP も同時にコミット**する (差分が追えないため)。
- ファイル名: `VMJR-M-<連番>_<名称>[_rev<X>].<ext>`
- URDF 用メッシュは `tools/export_meshes.py` で同期する。手でコピーしない。
- 同一ファイルの並行編集はできないので、着手前に Issue でロックする。

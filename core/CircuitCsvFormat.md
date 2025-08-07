# PyPlc Ver3 Circuit CSV File Format Specification

作成日: 2025-08-07  
対象バージョン: PyPlc Ver3  
管理クラス: core.circuit_csv_manager.CircuitCsvManager  

## 目的

PyPlc Ver3で使用する回路保存・読み込み用CSVファイルフォーマットの完全仕様書。  
将来的に機能が削除されても、この仕様書により確実に復元可能とする。

---

## ファイル命名規則

### 自動保存時
```
circuit_YYYYMMDD_HHMMSS.csv
```

例: circuit_20250807_184743.csv

### ファイル名構成要素
- circuit_: 固定プレフィックス
- YYYYMMDD: 年月日（8桁）
- HHMMSS: 時分秒（6桁）
- .csv: 拡張子

---

## CSVファイル構造

### ヘッダー行（必須）
```csv
Row,Col,DeviceType,DeviceID,IsEnergized,State
```

### データ行フォーマット
```csv
{Row},{Col},{DeviceType},{DeviceID},{IsEnergized},{State}
```

---

## フィールド仕様

| フィールド名 | データ型 | 必須 | 説明 | 値の範囲・形式 |
|-------------|---------|------|------|---------------|
| Row | int | 必須 | グリッド行番号（Y座標） | 0-14 (15行グリッド) |
| Col | int | 必須 | グリッド列番号（X座標） | 1-18 (バスバー除外範囲) |
| DeviceType | str | 必須 | デバイス種別識別子 | DeviceType enum値 |
| DeviceID | str | 必須 | デバイスアドレス | PLC標準準拠アドレス |
| IsEnergized | bool | 必須 | 通電状態 | True/False |
| State | bool | 必須 | デバイス論理状態 | True/False |

---

## DeviceType値一覧

### 保存対象デバイス
| DeviceType値 | 説明 | 例 |
|-------------|------|-----|
| CONTACT_A | A接点（ノーマルオープン） | -[]-  |
| CONTACT_B | B接点（ノーマルクローズ） | -[/]- |
| COIL_STD | 標準コイル | -(○)- |
| COIL_REV | 反転コイル | -(/)- |
| LINK_HORZ | 水平配線 | ----- |
| LINK_BRANCH | 分岐配線（3方向） | 右・上・下分配 |
| LINK_VIRT | 垂直配線（双方向） | 上下伝播 |

### 保存除外デバイス
| DeviceType値 | 説明 | 除外理由 |
|-------------|------|---------|
| L_SIDE | 左バスバー | システム自動生成 |
| R_SIDE | 右バスバー | システム自動生成 |
| EMPTY | 空デバイス | 保存不要 |

---

## DeviceID仕様（PLC標準準拠）

### 入力接点（X系）
- 形式: X000-X377 (8進数)
- 例: X000, X001, X010, X377

### 出力（Y系）
- 形式: Y000-Y377 (8進数)
- 例: Y000, Y001, Y010, Y377

### 内部リレー（M系）
- 形式: M0-M7999 (10進数)
- 例: M0, M100, M7999

### タイマー（T系）※将来実装
- 形式: T000-T255 (10進数)
- 例: T000, T001, T255

### カウンター（C系）※将来実装
- 形式: C000-C255 (10進数)
- 例: C000, C001, C255

---

## 実際のファイル例

### サンプル回路CSV
```csv
Row,Col,DeviceType,DeviceID,IsEnergized,State
1,1,CONTACT_A,X11,False,False
1,2,LINK_HORZ,X12,False,False
1,3,LINK_HORZ,X13,False,False
1,4,COIL_STD,X14,False,False
2,1,CONTACT_B,X21,False,True
2,2,LINK_BRANCH,X22,False,False
2,3,LINK_VIRT,X23,False,False
2,4,COIL_REV,X24,False,False
```

### 各行の解説
```csv
1,1,CONTACT_A,X11,False,False
# 1行1列にA接点X11、非通電、OFF状態

1,2,LINK_HORZ,X12,False,False  
# 1行2列に水平配線、非通電

2,2,LINK_BRANCH,X22,False,False
# 2行2列に分岐配線、右・上・下方向分配可能
```

---

## 実装上の重要な注意点

### 1. 座標系統一
```python
# 必ず [row][col] = [Y座標][X座標] の順序で統一
grid[row][col]  # [y座標][x座標]
```

### 2. バスバー除外処理
```python
# 保存時に除外すべきデバイス
exclude_types = [DeviceType.L_SIDE, DeviceType.R_SIDE, DeviceType.EMPTY]
```

### 3. Boolean値処理
```python
# CSV読み込み時のboolean変換
is_energized = row_data['IsEnergized'].lower() == 'true'
state = row_data['State'].lower() == 'true'
```

### 4. ファイル検索パターン
```python
# ファイル検索・最新選択
csv_files = glob.glob("circuit_*.csv")
latest_file = max(csv_files, key=os.path.getctime)
```

---

## 復元用実装ガイド

### 必須インポート
```python
import csv
import os  
import glob
from datetime import datetime
from typing import Optional
from config import DeviceType
```

### 保存処理の骨格
```python
def save_circuit_to_csv(self, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"circuit_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Row', 'Col', 'DeviceType', 'DeviceID', 'IsEnergized', 'State'])
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                device = get_device(row, col)
                if device and device.device_type not in [DeviceType.L_SIDE, DeviceType.R_SIDE]:
                    writer.writerow([row, col, device.device_type.value, 
                                   device.address, device.is_energized, device.state])
```

### 読み込み処理の骨格  
```python
def load_circuit_from_csv(self, filename=None):
    if filename is None:
        csv_files = glob.glob("circuit_*.csv")
        filename = max(csv_files, key=os.path.getctime)
    
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row_data in reader:
            row = int(row_data['Row'])
            col = int(row_data['Col'])
            device_type = DeviceType(row_data['DeviceType'])
            address = row_data['DeviceID']
            is_energized = row_data['IsEnergized'].lower() == 'true'
            state = row_data['State'].lower() == 'true'
            
            # デバイス配置・状態復元
            place_device(row, col, device_type, address)
            device = get_device(row, col)
            device.is_energized = is_energized
            device.state = state
```

---

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|----------|------|---------|
| 1.0 | 2025-08-07 | 初版作成・基本仕様確定 |

---

重要: このフォーマット仕様は PyPlc Ver3 の回路データ永続化における最重要ドキュメントです。  
機能削除や実装変更時も、必ずこの仕様に準拠した復元を行ってください。
# PyPlc Ver3 - PLC標準準拠ラダー図シミュレーター

## 概要

PyPlc Ver3は、工場検証用途と教育目的を兼ねたPLC標準準拠のラダー図シミュレーターです。実際のPLCプログラミングと同等の操作感を提供し、接点・コイル・タイマー・カウンター等の基本機能を完全実装しています。

**⚠️ アルファ版について**: このソフトウェアは現在アルファ段階です。一部機能が未完成または変更される可能性があります。本格運用での使用は推奨しません。

## 特徴

- **PLC標準完全準拠**: 教育用として、可能な限りのデバイス体系・動作仕様を目指す
- **リアルタイム回路解析**: 30FPS高速動作での電力フロー可視化  
- **教育的価値**: 実PLC移行時の違和感なし
- **モジュラーアーキテクチャ**: 責任分離原則に基づくクリーン実装

## インストール・実行

```bash
# 依存関係インストール
pip install pyxel

# 通常実行
pyxel run main.py
```

## 基本操作

- **1-0キー**: デバイス選択（A/B接点、コイル、タイマー等）
- **マウス左クリック**: デバイス配置
- **マウス右クリック**: デバイスID編集
- **F5**: 回路実行開始/停止
- **Shift+X**: 入力デバイス操作（X001-X004）
- **TAB**: EDIT/RUNモード切り替え

## 技術仕様

- **解像度**: 384×384ピクセル
- **グリッドシステム**: 15行×20列
- **対応デバイス**: X接点、Y出力、M内部、T/Cタイマー/カウンター
- **アーキテクチャ**: モジュール化設計、責任分離原則
- **パフォーマンス**: 30FPSリアルタイム動作
- **規格準拠**: 三菱PLCアドレス形式準拠

## PLCデバイス番号体系

### 入力デバイス (X)
- **範囲**: X0 ～ X377
- **説明**: 物理的な入力デバイス（スイッチ、センサーなど）
- **例**: X001, X002, ..., X377

### 出力デバイス (Y)
- **範囲**: Y0 ～ Y377
- **説明**: 物理的な出力デバイス（ランプ、リレーなど）
- **例**: Y000, Y001, ..., Y377

### 内部リレー (M)
- **範囲**: M0 ～ M7999
- **説明**: プログラム内で使用する内部リレー（補助リレー）
- **例**: M0, M1, ..., M7999

### タイマー (T)
- **範囲**: T0 ～ T255
- **説明**: タイマー用デバイス
- **プリセット値**: 0～32767ms
- **例**: T0, T1, ..., T255

### カウンター (C)
- **範囲**: C0 ～ C255
- **説明**: カウンター用デバイス
- **プリセット値**: 0～65535
- **例**: C0, C1, ..., C255

### データレジスタ (D)
- **範囲**: D0 ～ D7999
- **説明**: データ保持用レジスタ
- **例**: D0, D1, ..., D7999

### アドレス表記ルール
- すべてのデバイスは3桁のゼロパディングで表記
  - 例: X001, Y020, M100, T010, C005, D1000

## デバイス一覧

| キー | デバイス | 説明 |
|------|----------|------|
| 1 | A接点 | ノーマルオープン接点 -\| \|- |
| 2 | B接点 | ノーマルクローズ接点 -\|/\|- |
| 3 | コイル | 出力コイル -( )- |
| 4 | タイマー | タイマーデバイス（TON） |
| 5 | カウンター | カウンターデバイス（CTU） |
| 6-9 | 配線 | 垂直/水平接続 |
| 0 | 削除 | デバイス除去 |

## 開発履歴

- **Ver1**: プロトタイプ実装
- **Ver2**: モジュール化・安定化
- **Ver3**: PLC標準準拠・教育効果最大化（現在のアルファ版）

## 動作環境

- Python 3.8以上
- Pyxel 1.9.0以上
- 対応OS: Windows/Linux/macOS

## 現在の制限事項（アルファ版）

- 一部の高度なPLC機能は未実装
- 回路保存・読み込み機能は開発中
- 複雑な並列回路解析は改良中

## プロジェクト構造

```
PyPlc/
├── main.py                    # メインアプリケーション
├── config.py                  # 設定定数
├── core/                      # コアモジュール
│   ├── grid_system.py         # グリッド管理
│   ├── circuit_analyzer.py    # 回路解析
│   ├── device_base.py         # デバイス基底クラス
│   └── input_handler.py       # 入力処理
├── dialogs/                   # ダイアログシステム
└── venv/                      # Python仮想環境
```

## ライセンス

このプロジェクトはアルファ版として開発中です。ライセンス条項は正式版リリース時に決定予定です。

---

# PyPlc Ver3 - PLC Standard-Compliant Ladder Diagram Simulator

[![Version](https://img.shields.io/badge/Version-3.0--alpha-orange)]() 
[![Python](https://img.shields.io/badge/Python-3.8+-green)]() 
[![Pyxel](https://img.shields.io/badge/Pyxel-1.9.0+-red)]()
[![Status](https://img.shields.io/badge/Status-Alpha-yellow)]()

## Overview

PyPlc Ver3 is a PLC (Programmable Logic Controller) standard-compliant ladder diagram simulator designed for industrial verification and educational purposes. This alpha version provides the same operational experience as real PLC programming, with complete implementation of basic functions including contacts, coils, timers, and counters.

**⚠️ Alpha Version Notice**: This software is currently in alpha stage. Some features may be incomplete or subject to change. Use for production purposes is not recommended.

## Features

- **Full PLC Standard Compliance**: Device system and operation specifications equivalent to actual PLCs (Mitsubishi PLC compatible)
- **Real-time Circuit Analysis**: High-speed 30FPS power flow visualization
- **Educational Value**: Seamless transition to real PLC programming
- **Commercial-grade Quality**: Achieved A+ rating from WindSurf AI Assistant code review
- **Modular Architecture**: Clean implementation with separation of concerns

## Installation & Execution

```bash
# Install dependencies
pip install pyxel

# Alternative execution
pyxel run main.py
```

## Basic Operations

- **1-0 Keys**: Device selection (A/B contacts, coils, timers, etc.)
- **Left Click**: Place device on grid
- **Right Click**: Edit device ID
- **F5**: Start/stop circuit execution
- **Shift+X**: Operate input devices (X001-X004)
- **TAB**: Switch between EDIT/RUN modes

## Technical Specifications

- **Resolution**: 384×384 pixels
- **Grid System**: 15 rows × 20 columns
- **Supported Devices**: X contacts, Y outputs, M internal relays, T/C timers/counters
- **Architecture**: Modular design with responsibility separation
- **Performance**: 30FPS real-time operation
- **Standards**: Mitsubishi PLC address format compliance

## Device Types

| Key | Device | Description |
|-----|--------|-------------|
| 1 | A Contact | Normally Open Contact -\| \|- |
| 2 | B Contact | Normally Closed Contact -\|/\|- |
| 3 | Coil | Output Coil -( )- |
| 4 | Timer | Timer Device (TON) |
| 5 | Counter | Counter Device (CTU) |
| 6-9 | Links | Vertical/Horizontal connections |
| 0 | Delete | Remove device |

## Development History

- **Ver1**: Prototype implementation
- **Ver2**: Modularization and stabilization  
- **Ver3**: PLC standard compliance and educational optimization (Current Alpha)

## System Requirements

- Python 3.8 or higher
- Pyxel 1.9.0 or higher
- Operating System: Windows/Linux/macOS

## Current Limitations (Alpha)

- Some advanced PLC functions not yet implemented
- Circuit save/load functionality under development
- Complex parallel circuit analysis in progress



---

**Development Status**: Active development in progress  
**Last Updated**: 2025-08-09  
**Target Audience**: PLC engineers, automation students, industrial education
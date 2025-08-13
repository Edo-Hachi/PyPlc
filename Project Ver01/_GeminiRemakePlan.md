# Project: PLC Simulator Remake Plan

This document outlines the plan for recreating the PLC Simulator, incorporating insights from previous development and aiming for a simplified, robust system. It is structured for clarity for both human and AI understanding.

## 1. Core Components (コアコンポーネント)

Based on the existing file structure and requirements, the application will consist of the following core components:

既存のファイル構造と要件に基づき、アプリケーションは以下のコアコンポーネントで構成されます。

*   **Grid System (`grid.py`):** Manages the 2D grid, including its dimensions and the placement of devices.
    *   2Dグリッド（寸法、デバイス配置）を管理します。
*   **Device Management (`devices.py`):** Defines the `LogicElement` class and its subclasses for different device types (e.g., `ContactA`, `ContactB`, `OutCoil`).
    *   `LogicElement`クラスとそのサブクラス（`ContactA`, `ContactB`, `OutCoil`など）を定義します。
*   **PLC Logic (`plc_logic.py`):** Implements the core PLC simulation logic, including the scan cycle and evaluation of device states.
    *   スキャンサイクルとデバイスの状態評価を含む、コアPLCシミュレーションロジックを実装します。
*   **User Interface (`ui.py`):** Handles all UI elements, including the main grid display, device palette, and user interactions.
    *   メイングリッド表示、デバイスパレット、ユーザーインタラクションを含むすべてのUI要素を処理します。
*   **Main Application (`main.py`):** The entry point of the application, responsible for initializing the game loop and managing the overall application state.
    *   アプリケーションのエントリポイントであり、ゲームループの初期化とアプリケーション全体の状態管理を担当します。
*   **Configuration (`config.py`):** Manages settings and constants for the application, such as grid dimensions and colors.
    *   グリッドの寸法や色など、アプリケーションの設定と定数を管理します。
*   **Assets (`assets/`):** Contains all static assets, such as sprites and images.
    *   スプライトや画像などのすべての静的アセットが含まれます。

## 2. Implementation Steps (実装ステップ)

Implementation will proceed in the following manageable steps:

実装は以下の管理しやすいステップで進行します。

### Step 1: Project Setup & Basic Grid (ステップ1：プロジェクトセットアップと基本グリッド)

1.  **Initialize Project:** Create the directory structure and initial empty Python files (`main.py`, `grid.py`, `devices.py`, `plc_logic.py`, `ui.py`, `config.py`).
    *   プロジェクトの初期化：ディレクトリ構造と初期の空のPythonファイルを作成します。
2.  **Setup Pyxel Window:** In `main.py`, initialize a Pyxel window with a specified title and dimensions.
    *   Pyxelウィンドウのセットアップ：`main.py`で、指定されたタイトルと寸法でPyxelウィンドウを初期化します。
3.  **Define Grid Constants:** In `config.py`, define constants for `GRID_WIDTH`, `GRID_HEIGHT`, `GRID_CELL_SIZE`, and colors.
    *   グリッド定数の定義：`config.py`で、`GRID_WIDTH`、`GRID_HEIGHT`、`GRID_CELL_SIZE`、および色の定数を定義します。
4.  **Implement Grid Drawing:** In `grid.py`, create a `Grid` class that can draw the grid lines on the screen based on the constants from `config.py`.
    *   グリッド描画の実装：`grid.py`で、`config.py`の定数に基づいて画面にグリッド線を描画できる`Grid`クラスを作成します。
5.  **Render Grid in Main Loop:** In `main.py`, create an instance of the `Grid` and call its `draw()` method within the main game loop.
    *   メインループでのグリッドのレンダリング：`main.py`で、`Grid`のインスタンスを作成し、メインゲームループ内でその`draw()`メソッドを呼び出します。

### Step 2: Device Representation (ステップ2：デバイス表現)

1.  **Device Class:** In `devices.py`, create a base `Device` class with common attributes like `x`, `y`, `device_type`, and an abstract `draw()` method.
    *   デバイスクラス：`devices.py`で、`x`、`y`、`device_type`などの共通属性と抽象的な`draw()`メソッドを持つ基本`Device`クラスを作成します。
2.  **Device Subclasses:** Create subclasses for each device type (e.g., `ContactA`, `ContactB`, `OutCoil`) that inherit from the `Device` class.
    *   デバイスサブクラス：`Device`クラスを継承する各デバイスタイプ（例：`ContactA`、`ContactB`、`OutCoil`）のサブクラスを作成します。
3.  **Sprite Loading:** In `main.py`, load the sprites from `sprites.json` and the image from `my_resource.pyxres`.
    *   スプライトの読み込み：`main.py`で、`sprites.json`からスプライトを、`my_resource.pyxres`から画像を読み込みます。
4.  **Device Sprites:** In `devices.py`, assign the appropriate sprite to each device subclass.
    *   デバイススプライト：`devices.py`で、各デバイスサブクラスに適切なスプライトを割り当てます。
5.  **Device Drawing:** Implement the `draw()` method in each device subclass to draw the device's sprite at its grid position.
    *   デバイスの描画：各デバイスサブクラスの`draw()`メソッドを実装し、グリッド位置にデバイスのスプライトを描画します。

### Step 3: Device Palette and Placement (ステップ3：デバイスパレットと配置)

1.  **UI Directory:** Create a `ui/` directory for UI-related components.
    *   UIディレクトリ：UI関連のコンポーネント用に`ui/`ディレクトリを作成します。
2.  **Palette Class:** In `ui/palette.py`, create a `Palette` class to display available devices.
    *   パレットクラス：`ui/palette.py`で、利用可能なデバイスを表示するための`Palette`クラスを作成します。
3.  **Device Selection:** Implement logic to handle mouse clicks on the palette to select a device.
    *   デバイス選択：パレットでのマウスクリックを処理してデバイスを選択するロジックを実装します。
4.  **Grid Placement:** In `main.py`, handle mouse clicks on the grid. If a device is selected from the palette, create an instance of that device and add it to a list of devices at the clicked grid position.
    *   グリッド配置：`main.py`で、グリッドでのマウスクリックを処理します。パレットからデバイスが選択されている場合、そのデバイスのインスタンスを作成し、クリックされたグリッド位置のデバイスリストに追加します。
5.  **Render Devices:** In `main.py`, iterate through the list of devices and call their `draw()` methods in the main game loop.
    *   デバイスのレンダリング：`main.py`で、デバイスのリストを反復処理し、メインゲームループ内でそれらの`draw()`メソッドを呼び出します。

### Step 4: PLC Simulation Logic (ステップ4：PLCシミュレーションロジック)

1.  **PLC Class:** In `plc_logic.py`, create a `PLC` class to manage the simulation.
    *   PLCクラス：`plc_logic.py`で、シミュレーションを管理するための`PLC`クラスを作成します。
2.  **Grid State:** The `PLC` class should have access to the grid and all placed devices.
    *   グリッドの状態：`PLC`クラスは、グリッドと配置されたすべてのデバイスにアクセスできる必要があります。
3.  **Scan Cycle:** Implement a `scan()` method in the `PLC` class that iterates through the grid from top-to-bottom and left-to-right.
    *   スキャンサイクル：`PLC`クラスに、グリッドを上から下、左から右に反復処理する`scan()`メソッドを実装します。
4.  **Device Evaluation:** For each device, implement an `evaluate()` method that determines its state based on the state of its neighbors.
    *   デバイス評価：各デバイスについて、隣接するデバイスの状態に基づいてその状態を決定する`evaluate()`メソッドを実装します。
5.  **Update State:** The `scan()` method should update the state of each device based on the evaluation results. This should be repeated until the grid state stabilizes.
    *   状態の更新：`scan()`メソッドは、評価結果に基づいて各デバイスの状態を更新する必要があります。これは、グリッドの状態が安定するまで繰り返されます。
6.  **Visual Feedback:** Update the `Device.draw()` method to visually represent the device's state (e.g., using different sprites for "on" and "off").
    *   視覚的フィードバック：`Device.draw()`メソッドを更新して、デバイスの状態を視覚的に表現します（例：「オン」と「オフ」で異なるスプライトを使用）。

### Step 5: Interactivity and Refinements (ステップ5：インタラクティブ性と改善)

1.  **Device Removal:** Implement a way to remove devices from the grid (e.g., right-clicking).
    *   デバイスの削除：グリッドからデバイスを削除する方法（例：右クリック）を実装します。
2.  **Device Configuration:** For devices like timers, implement a way to configure their settings (e.g., a dialog box on double-click).
    *   デバイスの設定：タイマーなどのデバイスの場合、設定を構成する方法（例：ダブルクリックでダイアログボックス）を実装します。
3.  **Grid Panning and Zooming:** Add controls for panning and zooming the grid to allow for larger circuits.
    *   グリッドのパンとズーム：より大きな回路を可能にするために、グリッドのパンとズームのコントロールを追加します。
4.  **Save/Load Functionality:** Implement a way to save and load the grid state to a file.
    *   保存/読み込み機能：グリッドの状態をファイルに保存および読み込む方法を実装します。
5.  **Code Refactoring:** Refactor the code to improve its structure, readability, and performance.
    *   コードのリファクタリング：コードをリファクタリングして、構造、可読性、パフォーマンスを向上させます。

## 3. Next Steps (次のステップ)

I will proceed with **Step 1: Project Setup & Basic Grid**. This involves creating the necessary directories and files, and then setting up the basic Pyxel window and grid drawing.

**ステップ1：プロジェクトセットアップと基本グリッド**の実装から開始します。これには、必要なディレクトリとファイルの作成、および基本的なPyxelウィンドウとグリッド描画のセットアップが含まれます。
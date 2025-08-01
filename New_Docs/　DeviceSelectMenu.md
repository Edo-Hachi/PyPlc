

**DEVICE SELECT MENU**


[____]は未定義です

---------------------------------
#UP MENU

ID, 
[_A_] ,  0:A接点
[_B_] ,  1:B接点
[COIL],  2:コイル
[____],  3:未定義
[LINE],  4:ライン
[_UP_],  5:上方向へ接続ライン ↑
[DOWN],  6:下方向へ接続するライン↓
[____],  7:未定義
[____],  8:未定義
[DEL],   9:デリート（削除コマンド）
---------------------------------

#DOWN MENU
[STD]   0:標準
[REV]   1:反転
[____]  2:未定義
[____]  3:未定義
[____]  4:未定義
[____]  5:未定義
[____]  6:未定義
[____]  7:未定義
[____]  8:未定義
[____]  9:未定義
---------------------------------


---------------------------------


デバイス名,定義名,スプライト名,ステート,Note
A接点,TYPE_A,TYPE_A_ON,作動時,作動時　導通ON
A接点,TYPE_A,TYPE_A_OFF,待機時,待機時　導通OFF
,,,,
B接点,TYPE_B,TYPE_B_ON,待機時,待機時　導通ON
B接点,TYPE_B,TYPE_B_OFF,作動時,作動時　導通OFF
,,,,
入力 コイル,INCOIL,INCOIL_ON,作動時,作動時　導通ON
入力 コイル,INCOIL,INCOIL_OFF,待機時,待機時　導通OFF
,,,,
リンク,LINK,LINK_UP,なし,ラインから上向きにのアイコン
リンク,LINK,LINK_DOWN,なし,ラインから下向きのアイコン
,,,,
削除,DEL,DEL,なし,編集画面での削除機能
,,,,
タイマ,TIMER,TIMER_STANBY,待機中,待機時　導通OFF
タイマ,TIMER,TIMER_CNTUP,カウントアップ中,待機時　導通OFF
タイマ,TIMER,TIMER_ON,作動時,作動時　導通ON
,,,,
出力コイル,OUTCOIL_NML,OUTCOIL_NML_ON,作動時,作動時　導通ON
出力コイル,OUTCOIL_NML,OUTCOIL_NML_OFF,待機時,待機時　導通OFF
,,,,
出力コイル,OUTCOIL_REV,OUTCOIL_REV_ON,作動時,待機時　導通OFF
出力コイル,OUTCOIL_REV,OUTCOIL_REV_OFF,待機時,作動時　導通ON

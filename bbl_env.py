import pandas as pd
from typing import Dict

class BBLDataLoader:
    def __init__(self, csv_path: str) -> None:
        self.csv_path: str = csv_path
        self.matrix: pd.DataFrame = pd.DataFrame()
        self.growth_patterns: pd.DataFrame = pd.DataFrame()
        
        self.load_data()

    def load_data(self) -> None:
        """CSVのパース"""
        # CSVを読み込む
        df = pd.read_csv(self.csv_path, header=0)
        
        # 1. 練習メニューごとの期待値マトリクスを抽出 (停滞期00〜衰え等、20行分)
        self.matrix = df.iloc[0:19].copy()
        self.matrix.set_index("パターン", inplace=True)
        
        # 2. 年齢ごとの成長型マッピングを抽出 (21行目以降)
        # 成長型テーブル部分
        growth_df = df.iloc[19:].copy()

        # 先頭行(成長型,18歳,19歳...)を列名にする
        growth_df.columns = growth_df.iloc[0]

        # ヘッダー化した行を削除
        growth_df = growth_df.iloc[1:]

        # インデックス設定
        growth_df.set_index("成長型", inplace=True)

        self.growth_patterns = growth_df
        
        print("【システム】: 成長型メモをシステムに同期しました。")
        print(f"  - 読み込んだ成長パターン数: {len(self.matrix)} 種類")
        print(f"  - 登録された成長型: {list(self.growth_patterns.index)} の全 {len(self.growth_patterns)} 型")

    def get_phase(self, growth_type: str, age: int) -> str:
        age_col = f"{age}歳"
        
        if growth_type in self.growth_patterns.index and age_col in self.growth_patterns.columns:
            phase_value = self.growth_patterns.loc[growth_type, age_col]
            return str(phase_value).strip().split('\n')[0]

        return "不明"


    def get_gain(self, phase: str, menu: str) -> float:
        """特定の期（パターン）と練習メニューから、基礎上昇量の期待値を引っ張ってくる"""
        if phase in self.matrix.index and menu in self.matrix.columns:
            try:
                return float(self.matrix.loc[phase, menu])
            except (ValueError, TypeError):
                return 0.0
        return 0.0

# --- テスト実行 ---
if __name__ == "__main__":
    # CSVのパス
    csv_file = "resources/bbl_expect.csv"
    
    try:
        loader = BBLDataLoader(csv_file)
        
        test_growth = "早熟"
        test_age = 18
        test_menu = "パワーAP大"
        
        # 18歳の早熟が何期か調べる
        current_phase = loader.get_phase(test_growth, test_age)
        # その期のパワーAP大の数値を引っ張る
        gain_expect = loader.get_gain(current_phase, test_menu)
        
        print(f"\n【検算結果】")
        print(f"  {test_age}歳・{test_growth} の現在のフェーズ ⇒ {current_phase}")
        print(f"  その状態で 『{test_menu.replace('\n', ' ')}』 を叩いた時の上昇期待値 ⇒ {gain_expect}")
        
    except FileNotFoundError:
        print(f"【エラー】: '{csv_file}' が見つかりません。ファイルパスを確認してください。")
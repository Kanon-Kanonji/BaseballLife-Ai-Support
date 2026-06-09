import pandas as pd
from typing import Dict
from bbl_rules import BBLRules, Ability

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
class BBLPlayer:
    def __init__(self, name: str, growth_type: str, appeal: str) -> None:
        self.name: str = name
        self.growth_type: str = growth_type
        self.appeal_point: str = appeal
        self.age: int = 18
        self.max_age: int = 37
        
        # 経験値タンク
        self.abilities_exp: Dict[str, float] = {}
        self.reset()
        
    def reset(self) -> None:
        self.age = 18
        # ルールモジュールから、AP補正込みの初期値をもらう
        self.abilities_exp = BBLRules.get_initial_exps(self.appeal_point)

    def show_status(self) -> None:
        print(f"--- 【{self.name}】 {self.age}歳 ({self.growth_type} / AP:{self.appeal_point}) ---")
        for abi, exp in self.abilities_exp.items():
            # 経験値から、実数値とランク(文字)に変換して表示！
            val, rank = BBLRules.exp_to_status(abi, exp)
            print(f"  {abi}: {rank} ({val})  [現在の経験値: {exp:.1f}]")


class BBLSimulator:
    def __init__(self, csv_path: str) -> None:
        self.data_loader = BBLDataLoader(csv_path)
        self.player = BBLPlayer("テスト選手", "普通", Ability.POWER)
        self.turns_left_this_year: int = 30
        
    def reset(self) -> None:
        self.player.reset()
        self.turns_left_this_year = 30
        
    def step(self, menu: str) -> bool:
        if self.player.age >= self.player.max_age:
            return True
            
        phase = self.data_loader.get_phase(self.player.growth_type, self.player.age)
        base_gain = self.data_loader.get_gain(phase, menu)
        
        # ルールモジュールを使って、最終的な全能力の増減値を計算してもらう
        gains, _ = BBLRules.calculate_gains(base_gain, menu, self.player.appeal_point)
        
        # プレイヤーの経験値タンクに反映
        for abi, gain_val in gains.items():
            self.player.abilities_exp[abi] += gain_val
                
        self.turns_left_this_year -= 1
        
        if self.turns_left_this_year <= 0:
            print(f"\n【システム】: {self.player.age}歳のシーズンが終了しました。(30ターン消化)")
            self.player.age += 1
            self.turns_left_this_year = 30
            
        if self.player.age >= self.player.max_age:
            print("\n【システム】: 選手が引退年齢に達しました。")
            return True
        return False

if __name__ == "__main__":
    expect_csv = "resources/bbl_expect.csv"
    table_csv = "resources/経験値対照表_野手.csv"
    
    try:
        BBLRules.load_exp_table(table_csv)
        sim = BBLSimulator(expect_csv)
        sim.reset()
        
        print("\n=== 18歳のシーズン開幕 ===")
        for i in range(30):
            sim.step("パワーAP大")
            
        sim.player.show_status()
            
    except FileNotFoundError as e:
        print(f"【エラー】: ファイルが見つかりません。パスを確認してください。\n詳細: {e}")
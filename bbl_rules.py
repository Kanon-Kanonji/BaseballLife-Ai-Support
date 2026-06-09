import pandas as pd
from typing import Dict, Tuple

class Ability:
    MEET = "ミート"
    POWER = "パワー"
    SORYOKU = "走力"
    SHUBI = "守備"
    KOWAZA = "小技"
    SEISHIN = "精神"

class BBLRules:
    _exp_table: pd.DataFrame = pd.DataFrame()

    @classmethod
    def load_exp_table(cls, csv_path: str) -> None:
        """「経験値対照表_野手」の読み込み"""
        cls._exp_table = pd.read_csv(csv_path)
        print(f"【システム】: 野手用経験値対照表（全 {len(cls._exp_table)} 段階）を完全同期しました。")

    @classmethod
    def exp_to_status(cls, ability_name: str, exp: float) -> Tuple[int, str]:
        """能力名に合わせて参照列を切り替え、実数値とランクを正確に返す"""
        if cls._exp_table.empty:
            return 0, "G"

        # 1. 能力名によって、CSVのどの列（累積経験値）を見るか判定する
        if ability_name in [Ability.MEET, Ability.POWER]:
            target_col = "ミート経験値"
        elif ability_name in [Ability.POWER]:
            target_col = "パワー経験値"
        else:
            target_col = "その他経験値"

        current_val = 0
        current_rank = "G"

        # 2. ユーザーの経験値が、CSVの累積経験値を超えている最大の行を探す
        for _, row in cls._exp_table.iterrows():
            # CSVの空行（NaN）対策
            if pd.isna(row[target_col]):
                break
                
            if exp >= float(row[target_col]):
                current_val = int(row["実数値"])
                current_rank = str(row["ランク"])
            else:
                break
                
        return current_val, current_rank

    @staticmethod
    def get_initial_exps(appeal_point: str) -> Dict[str, float]:
        """初期能力。仮処理でF15とする"""
        #TODO: 別モジュールの関数としてランダムでの初期能力決定処理を実装
        initial_exps = {
            Ability.MEET: 420.0,
            Ability.POWER: 420.0,
            Ability.SORYOKU: 280.0,
            Ability.SHUBI: 280.0,
            Ability.KOWAZA: 280.0,
            Ability.SEISHIN: 280.0
        }
        # AP補正（一旦E30とする)
        if appeal_point in [Ability.MEET, Ability.POWER]:
            initial_exps[appeal_point] += 450.0  # ミパ：870
        else:
            initial_exps[appeal_point] += 300.0  # それ以外：580
            
        return initial_exps

    @staticmethod
    def calculate_gains(base_gain: float, menu: str, appeal_point: str) -> Tuple[Dict[str, float], float]:
        """練習による獲得経験値の計算"""
        gains = {
            Ability.MEET: 0.0, Ability.POWER: 0.0, Ability.SORYOKU: 0.0, 
            Ability.SHUBI: 0.0, Ability.KOWAZA: 0.0, Ability.SEISHIN: 0.0
        }
        injury_gain = 0.0
        
        for abi in gains:
            if abi in menu:
                gains[abi] = base_gain
                
        return gains, injury_gain
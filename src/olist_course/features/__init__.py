"""特徵群組。每個模組提供 build(base, tables) -> DataFrame（與 base 同 index、只含新欄位）。

規則：純函式、不修改輸入；只能使用 T0（下單當下）已知的資訊。
"""

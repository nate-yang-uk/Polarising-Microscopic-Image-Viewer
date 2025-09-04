import argparse
import sys
from pathlib import Path


from pathlib import Path
import pandas as pd


script_dir = Path(__file__).resolve().parent   # app/ folder if your script lives there
repo_root  = script_dir if (script_dir / "images").exists() else script_dir.parent

print(repo_root)

df = pd.read_csv(repo_root / "metadata.csv")
df["full_path"] = (repo_root / "images" / df["rel_path"]).astype(str)

# 3. Load your CSV
# csv_path = script_dir / "metadata.csv"
# print(csv_path)

# df = pd.read_csv(csv_path)

# # 4. Turn relative paths into full paths
# df["full_path"] = df["rel_path"].apply(lambda x: str(root / x))

print(df.head())

# print('lol')
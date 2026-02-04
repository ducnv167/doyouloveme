import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Vote automation")
parser.add_argument(
    "--file",
    type=str,
    default="account",
    help="Đường dẫn file account CSV"
)
args = parser.parse_args()

def reset_is_done(csv_path: str):
    df = pd.read_csv(csv_path)

    if "is_done" not in df.columns:
        raise ValueError("Column 'is_done' not found")

    df["is_done"] = df["is_done"].replace(1, 0)

    df.to_csv(csv_path, index=False)

reset_is_done(csv_path=str(args.file + ".csv"))
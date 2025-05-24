import pandas as pd

# === 1. 读取原始 CSV 文件 ===
input_file = "data3_using.csv"              # 原始文件名
output_file = "data3_with_description.csv"  # 输出文件名

# 加载数据
df = pd.read_csv(input_file)

# === 2. 构造 song_description 字段===
def merge_description(row):
    song_des = str(row.get("song_des", "")).strip()
    songDes_add = str(row.get("songDes_add", "")).strip()
    genres = str(row.get("genres", "")).strip()

    if (songDes_add != "nan"):
        return f"{song_des} {songDes_add}. genre is {genres}."
    else:
        return f"{song_des} genre is {genres}."

df["song_description"] = df.apply(merge_description, axis=1)

df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"已成功生成 song_description 字段，保存为：{output_file}")

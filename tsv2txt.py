# tsv_to_line.py
input_file = "input.tsv"
output_file = "output.txt"

with open(input_file, "r", encoding="shift-jis") as f:
    lines = f.readlines()

# 各行の末尾の改行を削除し、タブ文字はそのまま残す
lines = [line.rstrip("\n") for line in lines]

# \t と \n を文字列として使う
single_line = "\\t".join(lines[0].split("\t"))  # 1行目
for line in lines[1:]:
    single_line += "\\n" + "\\t".join(line.split("\t"))

with open(output_file, "w", encoding="utf-8") as f:
    f.write(single_line)

print("変換完了！")

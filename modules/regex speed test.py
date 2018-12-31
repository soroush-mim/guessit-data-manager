import re

ans = re.findall(r"(sub.*?) ", "this subject has a submarine as a subsequence" * 1000000)
print(len(ans))

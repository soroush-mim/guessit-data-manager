import re

ans = re.findall(r"(sub.*?) ", "this subject has a submarine as a subsequence" * 10000)
#print(ans)

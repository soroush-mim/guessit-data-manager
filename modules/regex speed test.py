import re

ans = re.findall(r"\\b(sub)([^ ]*)", "this subject has a submarine as a subsequence" * 10 ** 5)
print(len(ans))


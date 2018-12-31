import re

ans = re.search(r"(.*?) ", "this subject has a submarine as a subsequence").groups()
print(ans)

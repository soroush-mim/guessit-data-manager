import re

ans = re.search(r"(sub[^ ]*) ", "this subject has a submarine as a subsequence")
print(ans.groups())

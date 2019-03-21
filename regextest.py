import re

regex = "^Grade PK[3-4]$"
teststring = "Grade PK3"

result = re.match(regex, teststring)

if (result):
    print("Match!")
else:
    print("No Match")

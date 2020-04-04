import csv
from difflib import Differ

file_a = "covidar_2020-04-01.csv"
file_b = "covidar_2020-04-04.csv"


def csv2dict(filepath):
    data = {}
    with open(filepath, newline='') as csvfile:
        csveader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csveader:
            data[row[1]] = row[2]
    return data


dict_a = csv2dict(file_a)
dict_b = csv2dict(file_b)

for url in dict_a:
    if dict_a[url] != dict_b[url]:
        print("\n\ndiff")
        print(url)
        d = Differ()
        diff = d.compare(dict_a[url], dict_b[url])
        print("\nDIFF")
        result = {}
        action = ""
        for character in list(diff):
            if character[:2] in ["+ ", "- "]:
                new_action = character[:2]
                #if action != new_action:
                #    result += new_action
                if new_action not in result:
                    result[new_action] = ""
                result[new_action] += character[-1]
                action = new_action
        print(result)

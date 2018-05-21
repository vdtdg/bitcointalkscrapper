import json
import os
import re

#  GLOBAL VAR
if os.name == "nt":
    PATH_DATA = os.getcwd() + "\\..\\data\\"
elif os.name == "posix":
    PATH_DATA = os.getcwd() + "/../data/"

# Nettoyage du JSON, on supprime tout ce qui ne passe pas la regex
with open(PATH_DATA + os.listdir(PATH_DATA)[0], "r+") as file:
    dict1 = json.loads(file.read())
    clear = dict()
    exp = re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')
    for key in dict1:
        m = exp.search(key)
        if m is not None:
            clear[key] = dict1[key]
    # clear est le dict "propre"
    print("# of previous entry : " + str(len(dict1)))
    print("# of clear entry :  " + str(len(clear)))
    file.seek(0, 0)  # On repositionne le pointeur de lecture/écriture au début du fichier
    file.write(json.dumps(clear))
    file.truncate()

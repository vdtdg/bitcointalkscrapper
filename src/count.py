import json
import os

#  GLOBAL VAR
if os.name == "nt":
    PATH_DATA = os.getcwd() + "\\..\\data\\"
elif os.name == "posix":
    PATH_DATA = os.getcwd() + "/../data/"

# On compte le nombre d'entrée dans le fichier json du dossier.
with open(PATH_DATA + os.listdir(PATH_DATA)[0], "r") as file:
    dict1 = json.loads(file.read())
    # for key in dict1:
    #     print(key)
    print("# of entry : " + str(len(dict1)))

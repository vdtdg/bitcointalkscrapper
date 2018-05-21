import json
import os

#  GLOBAL VAR
if os.name == "nt":
    PATH_DATA = os.getcwd() + "\\..\\data\\"
elif os.name == "posix":
    PATH_DATA = os.getcwd() + "/../data/"

# On fabrique une liste de tuple (begin, end), ils representent les fichiers.
list_file = os.listdir(PATH_DATA)
print("Nombre de fichier restant : " + str(len(list_file)))
tuple_file = []
for file in list_file:
    begin, endt = file.split('-')
    end = endt.split('.')[0]
    tuple_file.append((int(begin), int(end)))

# On va d'abord attraper le fichier avec le plus petit begin, on sauvegarde aussi la valeur de son end.
begin_min = 1
end_min = 1
for tuple_i in tuple_file:
    if tuple_i[0] <= begin_min:
        begin_min = tuple_i[0]
        end_min = tuple_i[1]


# Puis, on attrape le fichier de la liste tq begin2 = end OR end-1.
begin_next = 0
end_next = 0
for tuple_i in tuple_file:
    if tuple_i[0] == end_min:
        begin_next = tuple_i[0]
        end_next = tuple_i[1]
    elif tuple_i[0] == end_min + 1:
        begin_next = tuple_i[0]
        end_next = tuple_i[1]

print(begin_min, end_min)
print(begin_next, end_next)


# On merge les deux fichiers. Le nouveau fichier se nommera begin-end2.json. Et on boucle !
with open(PATH_DATA + str(begin_min) + "-" + str(end_min) + ".json", "r") as file_min:
    with open(PATH_DATA + str(begin_next) + "-" + str(end_next) + ".json", "r") as file_next:
        dict1 = json.loads(file_min.read())
        dict2 = json.loads(file_next.read())
        dict2.update(dict1)
        with open(PATH_DATA + str(begin_min) + "-" + str(end_next) + ".json", "w+") as file_new:
            file_new.write(json.dumps(dict2))  # We then write the new whole dict to json into the file.


# On supprime les deux anciens fichiers
os.remove(PATH_DATA + str(begin_min) + "-" + str(end_min) + ".json")
os.remove(PATH_DATA + str(begin_next) + "-" + str(end_next) + ".json")


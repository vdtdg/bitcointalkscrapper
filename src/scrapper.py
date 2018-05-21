# By Valérian de THEZAN de GAUSSAN
# UCBL - Lyon 1
import json
import os
import re
import time
from multiprocessing import Process

import bs4
import cfscrape  # Kudos to this guy. https://github.com/Anorov/cloudflare-scrape
import requests  # For exception

#  GLOBAL VAR
if os.name == "nt":
    PATH_DATA = os.getcwd() + "\\..\\data\\"
elif os.name == "posix":
    PATH_DATA = os.getcwd() + "/../data/"
NUMBER_OF_PROCESS = 5
TIME_BETWEEN_PULL = NUMBER_OF_PROCESS
BTC_REGEX = re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')


# Vérifie qu'une clé appartienne bien à un dict avant de la supprimer
def check_and_del(dict1, key):
    if key in dict1:
        del dict1[key]


# Fonction classique de wrapper de log, inscrit la date et l'heure en début de message.
def log(string):
    print(str(time.strftime("%d/%m/%Y-%H:%M:%S")) + "  " + str(string))


# Fonction de transformation de la "soup" en data
# Cette "soup" est le code HTML traité par BeautifulSoup de la page d'un utilisateur.
# La data de sortie est un couple de valeur : (adresse btc, info de l'utilisateur)
# Dans le cas où l'utilisateur n'a pas renseigné son adresse btc, l'adresse vaut -1 et les infos utilisateur ne seront
# pas retenues.
def soup_to_data(soup):
    user_data = dict()
    try:
        tr = soup.find_all("table").pop(6).find_all("tr")
    except IndexError:
        print("Got a IndexError while scrapping the data.")
        return -1, dict()
    for i in tr:
        if i.find_all("table"):  # So we avoid signature.
            continue
        td = i.find_all('td', attrs={"style": ""})  # No style is another trick to avoid signature.
        if len(td) == 2 and td[0] is not None and td[1] is not None and len(td[1]) != 0:
            if td[0].text.partition(':')[0].strip() == "Website":
                user_data[td[0].text.partition(':')[0].strip()] = td[1].a["href"]
            elif td[0].text.partition(':')[0].strip()[:9] == "Summary -":
                continue
            elif td[0].text.partition(':')[0].strip()[:9] == "Age" and td[1].text == "N/A":
                continue
            else:
                user_data[td[0].text.partition(':')[0].strip()] = td[1].text.strip()

    # Cleaning the user_data dict.
    try:
        if "Email" in user_data:
            if user_data["Email"] == "hidden":
                del user_data["Email"]
        check_and_del(user_data, "Activity")
        check_and_del(user_data, "Current Status")
        check_and_del(user_data, "Date Registered")
        check_and_del(user_data, "Local Time")
        check_and_del(user_data, "Last Active")
        check_and_del(user_data, "Merit")
        check_and_del(user_data, "Position")
        check_and_del(user_data, "Posts")
        if len(user_data["Website"]) == 0:
            del user_data["Website"]
    except KeyError:
        print("Got a KeyError while cleaning the data.")
    finally:
        print("  Data scraped.")
    # Get the bitcoin address field and if it doesn't exist, we return -1
    return user_data.get("Bitcoin address", -1), user_data


# Scrap les id de l'intervalle [n_from, n_to] en respectant les contraintes d'appel du site web et gérant tous les cas
# d'erreurs envisageables.
# Renvoie la data scrappé et l'id ou la fonction s'est arrêtée.
def scrap(n_from, n_to, proxies):
    scraper = cfscrape.create_scraper(delay=3)
    data = dict()  # Data is the dictionary that receive every user data with the bitcoin address as a key.
    t0 = time.time()
    log_i = n_from
    i = n_from
    while i < n_to + 1:
        while time.time() <= (t0 + (i - n_from) * TIME_BETWEEN_PULL):
            time.sleep(.1)
        try:
            page = scraper.get("https://bitcointalk.org/index.php?action=profile;u=" + str(i), proxies=proxies)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects):
            log("Can't load page with UID = " + str(i) + ", retrying...")
            time.sleep(1)
            i -= 1
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        if page.status_code == 503:
            log("Got 503 code from " + page.url + ", retrying...")
            time.sleep(5)  # Small security.
            i -= 1
        elif page.status_code == 200:
            if soup.title.string == "An Error Has Occurred!":
                log("Got 404 HTML code from uid " + str(i) + ".")
            else:
                log("Got 200 HTML code from uid " + str(i) + ". Scraping...")
                key, user_data = soup_to_data(soup)
                if key != -1:
                    m = BTC_REGEX.search(user_data["Bitcoin address"])
                    if m is not None:
                        del user_data["Bitcoin address"]  # Not useful anymore because its the key of the dict.
                        data[key] = user_data  # data and user_data are dict.
        else:
            log("Unknown case when pull from " + page.url + " got code " + str(page.status_code) + ", retrying...")
            time.sleep(5)
            i -= 1
        log_i = i
        i += 1
    # end for
    return data, log_i


# Crée un fichier avec pour nom "start-stop.json"
def create_file(start, stop):
    name = PATH_DATA + str(start) + "-" + str(stop) + ".json"
    file = "notopen"
    try:
        file = open(name, "w+")
    except IOError:
        print("Can't create file")
    return file


# Demande à l'utilisateur de rentrer un proxy sous la forme ip:port
# Si l'utilisateur entre "no", alors le proxy systeme par défaut est utilisé
def query_proxy():
    ip_and_port = str(input("Proxy (ip:port) (Type 'no' for no proxy) :"))
    if ip_and_port == "no":
        proxies = {}
    else:
        proxies = {
            'http': 'http://' + ip_and_port + '/',
            'https': 'https://' + ip_and_port + '/'
        }
    return proxies


# Fusionne ensemble deux dictionnaires d'utilisateurs
def merge():
    # On fabrique une liste de tuple (begin, end), ils representent les fichiers.
    list_file = os.listdir(PATH_DATA)
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


# Compte le nombre d'entrée dans le dictionnaire d'utilisateur
def count():
    with open(PATH_DATA + os.listdir(PATH_DATA)[0], "r") as file:
        dict1 = json.loads(file.read())
        print("# of entry : " + str(len(dict1)))


# Processus principal, qui prend en entrée deux bornes de l'intervalle d'id à scrapper et le proxy par lequel passer.
def main(n_from, n_to, proxies):
    print("Scrapping process started, scrapping from {} to {}.".format(str(n_from), str(n_to)))
    data, last_i = scrap(n_from, n_to, proxies)
    if last_i < n_to:
        n_to = last_i

    json_file = create_file(n_from, n_to)
    if json_file == "notopen":
        print(json.dumps(data))
    else:
        json_file.write(json.dumps(data))

    log("Program ended.")


# Le wrapper rend l'execution du main (processus principal) multi-thread.
def wrapper():
    # On demande à l'utilisateur de rentrer l'intervalle d'id qu'il veut scrapper.
    n_from = int(input("From (id): "))
    n_to = int(input("To (id): "))
    proxies = query_proxy()

    # On vient créer une liste de NUMBER_OF_PROCESS de processus, a qui on donne a chacun une part égale de travail.
    # Chaque processus execute la fonction main.
    p = []
    for i in range(0, NUMBER_OF_PROCESS):
        lower_bound = int(i * ((n_to - n_from) / NUMBER_OF_PROCESS) + n_from + 1)
        upper_bound = int((i + 1) * ((n_to - n_from) / NUMBER_OF_PROCESS) + n_from)
        p.append(Process(target=main, args=(lower_bound, upper_bound, proxies)))

    # On start tous les processus
    for pi in p:
        pi.start()

    # Et on attend leurs fins
    for pi2 in p:
        pi2.join()

    # On merge tous les fichiers créés par chaque processus jusqu'à ce qu'il n'en reste qu'un
    while len(os.listdir(PATH_DATA)) > 1:
        print("Nombre de fichier restant : " + str(len(os.listdir(PATH_DATA))))
        merge()
    count()


if __name__ == "__main__":
    wrapper()

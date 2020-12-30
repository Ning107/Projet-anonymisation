import spacy
from spacy.matcher import Matcher
import os

path = "Corpus"
files = os.listdir(path)

# effacer le fichier ".DS_Store"
for file in files:
    if file.startswith('.') and os.path.isfile(os.path.join(path,file)):
        files.remove(file)

# parcourire tous les textes dans le dossier "Corpus"
for file in files:
    if not os.path.isdir(file):
        f = open(path + "/" + file);
        iter_f = iter(f)
        text = ""
        for line in iter_f:
            text += line # la variable "text" contient le contenu de chaque fichier

# text = "Téléphone : 04-77-30-48-44 ou 06-87-58-12-62 ou 07.70.50.22.22 ou 06 72 34 65 62 ou 0632121854 . Et l' adresse mail de Léa est ningzgre@gmial.com"

        processeur = spacy.load("fr")
        contenu = processeur(text)

        # initialiser Matcher
        matcher = Matcher(processeur.vocab)

        ########## Numero ##########
        # matche les numero de format 04-77-30-48-44 ou 06 72 34 65 62
        patternTel1 = [
                    {"SHAPE":'dd'},
                    {'ORTH': '-', 'OP': '?'},
                    {"SHAPE":'dd'},
                    {'ORTH': '-', 'OP': '?'},
                    {"SHAPE": 'dd'},
                    {'ORTH': '-', 'OP': '?'},
                    {"SHAPE": 'dd'},
                    {'ORTH': '-', 'OP': '?'},
                    {"IS_DIGIT":True}]
        # matche les numero de format 0611223344
        patternTel2 = [{"TEXT":{"REGEX": "[0-9]{10}"}}]
        # matche les numero de format 06.11.22.33.44
        patternTel3 = [{"TEXT":{"REGEX": "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"}}]

        # ajouter le paterne
        matcher.add("TEL_PATTERN",None,patternTel1,patternTel2,patternTel3)

        # trouver tous les matches dans le texte
        matches = matcher(contenu)

        # anonymiser les numeros trouves
        tels = []
        for match_id, start, end in matches:
            span = contenu[start:end]
            tels.append(span.text)

        for tel in tels:
            text = text.replace(tel,'[Tel]')

        ########## Mail ##########
        # match le contenu de email
        patternEmail = [{"TEXT": {"REGEX": "[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+"}}]
        matcher.add("Email", None, patternEmail)
        # trouver tous les matches dans le texte
        matches = matcher(contenu)
        # anonymiser les mails trouves
        mails = []
        for match_id, start, end in matches:
            span = contenu[start:end]
            mails.append(span.text)

        for mail in mails:
            text = text.replace(mail, '[Mail]')


        ########## Adresse ##########

        voies = ["rue", "place", "avenue", "boulevard", "allée"]

        # repérer les adresses ou nom des rues
        patternLieu = [{"IS_DIGIT" : True},    # n° de rue
                        {"LOWER" : {"IN" : voies }},  # type de voie
                        # {"POS" : "DET", "OP" : "*"},  # déterminant(s) (facultatif) -> ça marche pas
                        {"POS" : "PROPN", "OP" : "+"}    # nom de la voie
                        # {"TEXT":{"REGEX": "[0-9]{5}"}}  # code postal
                        ]
        # ici il reconnaît que les adresses de type "NUM + voie + NOM" (12 rue Pasteur)


        matcher.add("Lieu", None, patternLieu)
        matches = matcher(contenu)

        lieux = []
        for match_id, start, end in matches:
            span = contenu[start:end]
            lieux.append(span.text)

        for lieu in lieux :
            text = text.replace(lieu, '[LIEU]')


        ########## entités nommées ##########

        # Reconnaitre les entités nommées
        Enti = []
        for ent in contenu.ents:
            Enti.append((ent.text,ent.label_))

        # anaonymiser les entités nommées par leurs étiquettes
        for elt in Enti:
            # print(elt)
            text = text.replace(elt[0],"["+elt[1]+"]")


        print(text)

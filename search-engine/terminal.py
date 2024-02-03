from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append('crawler/')

import nltk
from nltk.corpus import stopwords
import os
from dotenv import load_dotenv



# Recherche utilisateur
search_text = input('Veuillez entrer votre recherche : ').lower()



# Langue dispo
languages = nltk.corpus.stopwords.fileids()
print("\nLangues supportées par NLTK : ")
for lang in languages:
    print(lang)

lang = input('\nVeuillez entrer la langue de votre recherche (english si non langue non supportée) : ').lower()

try:
    stop_words = set(stopwords.words(lang))
except:
    stop_words = set(stopwords.words('english'))



# Traitement du texte de la recherche
    
# Garder uniquement les caratères alphanumériques et les espaces
text_brut = ''.join(c if c.isalpha() or c.isspace() else ' ' for c in search_text)
text_brut = ' '.join(text_brut.split()).lower()

# Supprimer les mots du text brut qui sont dans la ban list
text_brut_mots_techniques = ' '.join(word for word in text_brut.split() if word not in stop_words)

search_words = text_brut_mots_techniques.split()

# Créer une chaîne de la forme "('interbev', 'cniel', 'anicap')"
if len(search_words) == 1:
    search_words_string = f"('{search_words[0]}')"
else:
    search_words_string = str(tuple(search_words))



# Connexion BD
load_dotenv()

DB_SERVER = os.getenv('DB_SERVER')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')
DB_BASE = os.getenv('DB_BASE')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PWD}@{DB_SERVER}:{DB_PORT}/{DB_BASE}')
Session = sessionmaker(bind=engine)
session = Session()



# Monter la requete
query = text("""
    SELECT
        w2.link,
        w2.title,  
        SUM(
            COALESCE(ww.nb_occurrences_title, 0) * (1 + LOG(1 + w2.title_nb_words)) +
            COALESCE(ww.nb_occurrences_description, 0) * (1 + LOG(1 + w2.description_nb_words)) +
            COALESCE(ww.nb_occurrences_title1, 0) * (1 + LOG(1 + w2.title1_nb_words)) +
            COALESCE(ww.nb_occurrences_title2, 0) * (1 + LOG(1 + w2.title2_nb_words)) +
            COALESCE(ww.nb_occurrences_title3, 0) * (1 + LOG(1 + w2.title3_nb_words)) +
            COALESCE(ww.nb_occurrences_title4, 0) * (1 + LOG(1 + w2.title4_nb_words)) +
            COALESCE(ww.nb_occurrences_title5, 0) * (1 + LOG(1 + w2.title5_nb_words)) +
            COALESCE(ww.nb_occurrences_title6, 0) * (1 + LOG(1 + w2.title6_nb_words)) +
            COALESCE(ww.nb_occurrences_text, 0) * (1 + LOG(1 + w2.text_nb_words)) +
            COALESCE(ww.nb_occurences_img_alt, 0) * (1 + LOG(1 + w2.img_alt_nb_words))
        ) AS tot_correspondance
    FROM
        word w
    LEFT JOIN
        website_word ww ON w.id_word = ww.id_word
    LEFT JOIN
        website w2 ON ww.id_website = w2.id_website
    WHERE
        w.lib_word IN """ + search_words_string  + """
    GROUP BY
        w2.id_website
    ORDER BY
        tot_correspondance DESC
""")



# Exécuter la requête
with engine.connect() as connection:
    result = connection.execute(query)

    # Afficher les résultats
    for row in result:
        print('\nLien : ', row[0], '\nTitre : ', row[1], '\nScore : ', row[2])

    download = input('\nVoulez-vous télécharger les résultats ? (Y/n) : ')
    if download.lower() == 'y' or download == '':
        # Réexécuter la requête ou stocker les résultats dans une liste
        result = connection.execute(query)

        # Créer le nom du fichier en fonction des mots de recherche
        filename = f"resultats_{'_'.join(search_words)}.txt"

        specific_folder = "recherches_resultats"
        folder_path = os.path.join(os.getcwd(), specific_folder)

        filepath = os.path.join(folder_path, filename)

        os.makedirs(folder_path, exist_ok=True)

        # Écrire les résultats dans le fichier 
        with open(filepath, 'w', encoding='utf-8') as file:
            for row in result:
                file.write(f'Lien : {row[0]}\nTitre : {row[1]}\nScore : {row[2]}\n\n')


        print(f"\nLes résultats ont été téléchargés dans : {filepath}")


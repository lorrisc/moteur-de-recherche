import sys
sys.path.append('bd/')

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound

from bs4 import BeautifulSoup

import nltk
from nltk.corpus import stopwords

from dotenv import load_dotenv
import os
import time
from datetime import datetime
import random
import requests
from urllib.parse import urljoin, urlparse, urlunparse
import logging

from database import Base, Website, PendingSite, Word, WebsiteLink, WebsiteWord
from nltk_functions import lang_to_nltk_lang

def extract_text_from_tags(soup, tag):
    return ' '.join(html_text.text.strip() for html_text in soup.find_all(tag))


def get_words(ban_list, text):
    if text is None:
        return []
    
    # Garder uniquement les caracètres alphanumériques et les espaces et les nombres
    text_brut = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
    text_brut = ' '.join(text_brut.split()).lower()



    # Supprimer les mots du text brut qui sont dans la ban list
    text_brut_mots_techniques = ' '.join(word for word in text_brut.split() if word not in ban_list)

    return text_brut_mots_techniques.split()

def is_valid_url(url):
    lower_url = url.lower()

    if lower_url.endswith(tuple(IGNORED_EXTENSIONS)):
        return False

    if any(lower_url.startswith(prefix) for prefix in IGNORED_START):
        return False

    return True

def crawl_page(url):
    try:
        # Ne pas survisiter un domaine
        domain = urlparse(url).netloc
        now = time.time()
        if domain in last_visit_times and now - last_visit_times[domain] < 5:  # 5 secondes
            print("Auto time out : " + domain)
            return
        last_visit_times[domain] = now

        if is_valid_url(url) is False:
            return
        
        response = requests.get(url, timeout=10)

        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' in content_type or response.content.startswith(b'%PDF'):
            print('Document : ' + url)
            return

        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

        # Langue
        lang = soup.html.get('lang') if soup.html and 'lang' in "lang" in soup.html.attrs else None

        lang_nltk = lang_to_nltk_lang(lang)
        stop_words = set(stopwords.words(lang_nltk))

        # Titre
        title = soup.title.string if soup.title else None
        title_brut = get_words(stop_words, title)

        # Description
        description = soup.find('meta', {'property': 'og:description'})['content'] if soup.find('meta', {'property': 'og:description'}) else None
        description_brut = get_words(stop_words, description)

        # Titre 1 à 6
        titles1 = get_words(stop_words, extract_text_from_tags(soup, 'h1'))
        titles2 = get_words(stop_words, extract_text_from_tags(soup, 'h2'))
        titles3 = get_words(stop_words, extract_text_from_tags(soup, 'h3'))
        titles4 = get_words(stop_words, extract_text_from_tags(soup, 'h4'))
        titles5 = get_words(stop_words, extract_text_from_tags(soup, 'h5'))
        titles6 = get_words(stop_words, extract_text_from_tags(soup, 'h6'))

        # Tous les textes
        text = get_words(stop_words, ' '.join(soup.stripped_strings))

        # Alt des images
        img_alt = [img.get('alt') for img in soup.find_all('img') if img.get('alt') is not None and img.get('alt').strip()]
        img_alt = get_words(stop_words, ' '.join(img_alt))

        # Liens
        links = [link.get('href') for link in soup.find_all('a') if link.get('href') is not None and link.get('href').strip()]


        # Insérer website
        website = Website(
            domain=domain,
            title=title,
            title_nb_words=len(title_brut),
            link=url,
            lang=lang,
            description=description,
            description_nb_words=len(description_brut),
            title1_nb_words=len(titles1),
            title2_nb_words=len(titles2),
            title3_nb_words=len(titles3),
            title4_nb_words=len(titles4),
            title5_nb_words=len(titles5),
            title6_nb_words=len(titles6),
            text_nb_words=len(text),
            img_alt_nb_words=len(img_alt),
        )

        existing_website = session.query(Website).filter_by(link=url).first()

        if existing_website:
            # Le site existe déjà, mettre à jour
            website.id_website = existing_website.id_website
            website = session.merge(website)

            # Supprimer les mots et liens existants
            session.query(WebsiteWord).filter_by(id_website=website.id_website).delete()
            session.query(WebsiteLink).filter_by(id_website_from=website.id_website).delete()
        else:
            session.add(website)
        
        session.commit()


        # Insérer mots
        words = set(title_brut + description_brut + titles1 + titles2 + titles3 + titles4 + titles5 + titles6 + text + img_alt)
        for word in words:

            # Insérer le mot si il n'existe pas
            word_instance = session.query(Word).filter_by(lib_word=word).first()
            if not word_instance:
                word_instance = Word(lib_word=word)
                session.add(word_instance)
                session.flush()

            # Insérer le lien entre le mot et le site
            website_word_instance = WebsiteWord(
                id_website=website.id_website,
                id_word=word_instance.id_word,
                nb_occurrences_title=title_brut.count(word),
                nb_occurrences_description=description_brut.count(word),
                nb_occurrences_title1=titles1.count(word),
                nb_occurrences_title2=titles2.count(word),
                nb_occurrences_title3=titles3.count(word),
                nb_occurrences_title4=titles4.count(word),
                nb_occurrences_title5=titles5.count(word),
                nb_occurrences_title6=titles6.count(word),
                nb_occurrences_text=text.count(word),
                nb_occurences_img_alt=img_alt.count(word)
            )
            session.add(website_word_instance)


        # Insérer liens
        pending_sites_to_add = []
        for link in links:
            if link.startswith('http'):
                absolute_link = link
            else:
                # Lien relatif
                absolute_link = urljoin(url, link)

                # Supprimer le fragment (ancre) de l'URL
                parsed_url = urlparse(absolute_link)
                absolute_link = urlunparse(parsed_url._replace(fragment=''))

            if absolute_link != url:
                # Vérifier si le lien existe déjà dans PendingSite
                existing_pending_site = session.query(PendingSite).filter_by(link=absolute_link).first()

                # Vérifier si le lien existe déjà dans Website
                existing_website = session.query(Website).filter_by(link=absolute_link).first()

                # Insérer le site web
                if not existing_website:
                    website_instance = Website(link=absolute_link)
                    session.add(website_instance)
                    session.flush()
                    link_id = website_instance.id_website
                else:
                    link_id = existing_website.id_website

                # Insérer le lien entre les deux sites
                website_link = WebsiteLink(
                    id_website_from=website.id_website,
                    id_website_to=link_id
                )
                session.merge(website_link)

                # Ajouter le lien à la liste d'attente si le site n'existe pas déjà
                if not existing_pending_site and absolute_link not in pending_sites_to_add:
                    pending_sites_to_add.append(absolute_link)


        # Insérer les liens dans PendingSite
        if pending_sites_to_add:
            session.bulk_save_objects([PendingSite(link=link) for link in pending_sites_to_add])

        # Supprimer l'URL de la liste d'attente
        pending_site = session.query(PendingSite).filter(PendingSite.link == url).first()
        if pending_site:
            session.delete(pending_site)

        session.commit()

        print(f"Site inséré (+{len(pending_sites_to_add)}): {url}")


    except Exception as e:
        session.rollback()
        logging.error(f"{url} - Erreur: {e}")
        print(e)

        # Supprimer l'URL de la liste d'attente
        pending_site = session.query(PendingSite).filter(PendingSite.link == url).first()
        if pending_site:
            session.delete(pending_site)

        session.commit()


if __name__ == '__main__':

    load_dotenv()

    # Connexion BD
    DB_SERVER = os.getenv('DB_SERVER')
    DB_PORT = os.getenv('DB_PORT')
    DB_USER = os.getenv('DB_USER')
    DB_PWD = os.getenv('DB_PWD')
    DB_BASE = os.getenv('DB_BASE')

    engine = create_engine(f'postgresql://{DB_USER}:{DB_PWD}@{DB_SERVER}:{DB_PORT}/{DB_BASE}')

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    logging.basicConfig(filename='erreurs.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    # Début et fin des liens à ignorer
    IGNORED_EXTENSIONS = {'.zip', '.pdf', '.xlsx', '.png', '.jpg', '.jpeg'}
    IGNORED_START = {'mailto:', 'tel:', 'javascript:'}

    last_visit_times = {} # Dernier site visité

    while True:
        print("\nSuppression site récents (10s)")
        now = time.time()
        last_visit_times = {domain: last_visit_time for domain, last_visit_time in last_visit_times.items() if now - last_visit_time < 10}
        print(f"Nombre de sites récents: {len(last_visit_times)}\n")

        pending_links = set(pending.link for pending in session.query(PendingSite).order_by(func.random()).limit(50)) # 50 sites aléatoires dans la base
        pending_links_final = (link for link in pending_links if urlparse(link).netloc not in last_visit_times) # Ne pas survisiter un domaine

        if not any(pending_links_final):
            starting_urls = ["https://sql.sh/cours/jointures/left-join", "https://www.onf.fr/", "https://moselle.chambre-agriculture.fr/"]
            for url in starting_urls:
                crawl_page(url)
        else:
            for url in pending_links_final:
                crawl_page(url)
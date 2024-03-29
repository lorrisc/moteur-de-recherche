from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey , create_engine, Index
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Website(Base):
    __tablename__ = 'website'
    id_website = Column(Integer, primary_key=True)
    domain = Column(String, index=True)
    title = Column(String)
    title_nb_words = Column(Integer)
    link = Column(String, unique=True, nullable=False)
    lang = Column(String)
    description = Column(Text)
    description_nb_words = Column(Integer)
    title1_nb_words = Column(Integer)
    title2_nb_words = Column(Integer)
    title3_nb_words = Column(Integer)
    title4_nb_words = Column(Integer)
    title5_nb_words = Column(Integer)
    title6_nb_words = Column(Integer)
    text_nb_words = Column(Integer)
    img_alt_nb_words = Column(Integer)
    updated_date = Column(DateTime, default=datetime.utcnow)
    website_words = relationship('WebsiteWord', back_populates='website')
    website_links_from = relationship('WebsiteLink', back_populates='website_from', foreign_keys='WebsiteLink.id_website_from')
    website_links_to = relationship('WebsiteLink', back_populates='website_to', foreign_keys='WebsiteLink.id_website_to')

class PendingSite(Base):
    __tablename__ = 'pending_site'
    id_pending_site = Column(Integer, primary_key=True)
    link = Column(String, nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

class Word(Base):
    __tablename__ = 'word'
    id_word = Column(Integer, primary_key=True)
    lib_word = Column(String, unique=True, nullable=False)
    website_words = relationship('WebsiteWord', back_populates='word')

class WebsiteLink(Base):
    __tablename__ = 'website_link'
    id_website_from = Column(Integer, ForeignKey('website.id_website'), primary_key=True)
    id_website_to = Column(Integer, ForeignKey('website.id_website'), primary_key=True)
    website_from = relationship('Website', foreign_keys=[id_website_from], back_populates='website_links_from')
    website_to = relationship('Website', foreign_keys=[id_website_to], back_populates='website_links_to')

class WebsiteWord(Base):
    __tablename__ = 'website_word'
    id_website = Column(Integer, ForeignKey('website.id_website'), primary_key=True)
    id_word = Column(Integer, ForeignKey('word.id_word'), primary_key=True)
    nb_occurrences_title = Column(Integer)
    nb_occurrences_description = Column(Integer)
    nb_occurrences_title1 = Column(Integer)
    nb_occurrences_title2 = Column(Integer)
    nb_occurrences_title3 = Column(Integer)
    nb_occurrences_title4 = Column(Integer)
    nb_occurrences_title5 = Column(Integer)
    nb_occurrences_title6 = Column(Integer)
    nb_occurrences_text = Column(Integer)
    nb_occurences_img_alt = Column(Integer)
    website = relationship('Website', back_populates='website_words')
    word = relationship('Word', back_populates='website_words')

-- Liste non exhaustive de requetes utiles pour le projet


select * from pending_site ps;

select * from website w; 

select * from website_link wl;

select * from website_word ww;

select * from word w;



DROP TABLE public.pending_site CASCADE;

DROP TABLE public.website CASCADE;

DROP TABLE public.website_link CASCADE;

DROP TABLE public.website_word CASCADE;

DROP TABLE public.word CASCADE;



-- voir le nombre de sites web visités
SELECT COUNT(*) AS total,
       COUNT(CASE WHEN w.domain IS NOT NULL THEN 1 END) AS total_site_visite
FROM website w;



-- Site web les plus populaires
-- (le plus de liens vers eux)
select id_website_to, count(*), title, link
from website_link wl
left join website w on wl.id_website_to = w.id_website 
group by id_website_to, title, link
order by count(*) desc;



-- Test de recherche de mots en appliquant un poids
select 
	w2.id_website, 
	w2.link ,
	sum(
		coalesce(ww.nb_occurrences_title, 0) * (1 + log(1 + w2.title_nb_words)) +
		coalesce(ww.nb_occurrences_description, 0) * (1 + log(1 + w2.description_nb_words)) +
		coalesce(ww.nb_occurrences_title1, 0) * (1 + log(1 + w2.title1_nb_words)) +
		coalesce(ww.nb_occurrences_title2, 0) * (1 + log(1 + w2.title2_nb_words)) +
		coalesce(ww.nb_occurrences_title3, 0) * (1 + log(1 + w2.title3_nb_words)) +
		coalesce(ww.nb_occurrences_title4, 0) * (1 + log(1 + w2.title4_nb_words)) +
		coalesce(ww.nb_occurrences_title5, 0) * (1 + log(1 + w2.title5_nb_words)) +
		coalesce(ww.nb_occurrences_title6, 0) * (1 + log(1 + w2.title6_nb_words)) +
		coalesce(ww.nb_occurrences_text, 0) * (1 + log(1 + w2.text_nb_words)) +
		coalesce(ww.nb_occurences_img_alt, 0) * (1 + log(1 + w2.img_alt_nb_words))
	) as tot_correspondance
from word w 
left join website_word ww on w.id_word = ww.id_word 
left join website w2 on ww.id_website = w2.id_website 
where w.lib_word in ('sql', 'left', 'join')
group by w2.id_website
order by tot_correspondance desc
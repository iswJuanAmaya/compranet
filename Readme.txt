@ABOUT
Robot que raspa la página de compranet, ingresa algunos filtros, itera pagina por pagina y anuncio por anuncio,
extrae información básica del anuncio, economicos y precios, la almacena en concluidos.csv, economicos.csv, y 
precios.csv respectivamente.

@Requirements:
python 3.11
chrome
instalar requirements.txt -> pip install -r requirements.txt

scraper_concluidos.py -> script principal que debe ejecutarse para recuperar la información

layout_csv.py -> script que crea las bdd(CUIDADO, no debe ejecutarse o se borraran datos preexistentes)
requirements.txt -> lista de dependencias del proyecto
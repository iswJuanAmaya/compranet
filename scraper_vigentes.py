from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import date, datetime
from colorama import Fore
import time
import os
import time
import shutil
import random
import pandas as pd
import re

def timing_val(func):
    """Decorador para medir el tiempo que tarda una función en ejecturse."""
    def wrapper(*arg, **kw):
        t1 = time.time()
        func(*arg, **kw)
        t2 = time.time()
        segs = int(t2 - t1)
        if segs > 60:
            minutes = str(segs/60)
            print(f"tardó {minutes[0:5]} minutos...")
        else:
            print(f"tardó {segs} segs...")
        return segs
    return wrapper


def normalizar(text: str) -> str:
    """retorna la cadena del parametro sin acentos, en minuscula 
       y quita espacios al principio o fin de la cadena """
       
    a,b = 'áéíóúüÁÉÍÓÚÜ','aeiouuAEIOUU'
    trans = str.maketrans(a,b)
    try:
        text_normalized = text.translate(trans).lower().strip()
    except:
        print(f"error normalizando: {text}")
        text_normalized = "Error"
    return text_normalized


def duerme(a:int, b:int=0):
    "Sleeps for @a seconds, if b is given it'll sleep for a random between @a, @b"
    time_to_sleep = random.uniform(a, b) if b else a
    time.sleep(time_to_sleep)


def interceptor(request):
    global actual_page
    if "expedientes?rows" in request.url:
        request.querystring = f'rows=100&page={actual_page}'


def set_driver():
    """Initialize a webdriver to simulate chrome browser"""
    global driver
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument("--headless")
    #options.add_argument("--incognito")
    options.add_argument("--window-size=1920, 1080")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    
    #Se metio un error debido a la deshabilitación de cookies de 3ros en chrome.
    executable_path = ChromeDriverManager().install()
    executable_path = executable_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe")

    #Dispara chrome
    driver = webdriver.Chrome(options=options,
                service=Service(executable_path=executable_path),
            )
    driver.request_interceptor = interceptor
    print("driver correctamente inicializado.")


def load_csv(file_name:str) -> pd.DataFrame:
    #lee la tabla de la pagina
    return pd.read_csv(file_name, encoding='utf-8')


def espera_carga_componenete(a:int=5, b:int=180):
    "Espera que aparezca y desaparezca el loading... de la página."
    global driver
    try:
        xp = '//div[@class="spinner"]'
        WebDriverWait(driver, a).until(EC.visibility_of_element_located((By.XPATH, xp)))
    except TimeoutException:
        print("OJO, no apareció la leyenda de carga")
    try:
        WebDriverWait(driver, b).until(EC.invisibility_of_element_located((By.XPATH, xp)))
    except TimeoutException:
        print("Error: No desaparece leyenda cargando")
    
    time.sleep(1)


def click(xp:str, dormir:bool=True):
    "Hace scroll a un elemento, se mueve a el  y le da click "
    global driver

    element = driver.find_element(By.XPATH, xp)
    ActionChains(driver).scroll_to_element(element)\
        .move_to_element(element).pause(1).perform()
    element.click()

    if dormir:
        duerme(2, 5)


def fill(xp:str, txt:str):
    """Encuentra un input por xpath, lo rellena
    letra por letra con el txt recibido, esto para 
    asemejar un comortamiento más humano"""
    global driver
    element = driver.find_element(By.XPATH, xp)
    for letter in txt:
        element.send_keys(letter)
        duerme(.1, 1)


def persist_click():
    "este click fallaba porque tardaba en cargar la lista de opciones"
    tries = 0
    while tries < 5:
        print(f"Falló click de adquisiciones, parece que el submenú desplegable de opciones no ha cargado,\
               reintento {tries+1}...")
        try:
            click('//*[text()="ADQUISICIONES"]')
            return
        except:
            duerme(4.2, 8.7)
            tries += 1


def set_filters():
    """Setea los filtros del landing page"""
    global claves
    print("-> proceso: PROCEDIMIENTO DE CONTRATACIÓN")
    click('//*[@name="proceso"]')
    click('//*[text()="PROCEDIMIENTO DE CONTRATACIÓN"]')
    #click('//*[text()="PROYECTO DE CONVOCATORIA"]')

    # print("más filtros")
    # click('//*[@label="Filtros"]/button')

    # print(f"-> claves: {claves}")
    # click('//*[@name="claves"]')
    # for clave in claves:
    #     xp = '//p-multiselect[@name="claves"]//input[contains(@class,"filter")]'
    #     fill(xp=xp, txt=clave)
    #     duerme(1, 2)

    #     click(f'//*[contains(text(),"{clave}")]', dormir=False)
    #     duerme(.5, 1.5)

    #     driver.find_element(By.XPATH, xp).clear()
    #     duerme(.5,2)

    print("buscar")
    click(xp='//span[text()="Buscar"]', dormir=False)
    espera_carga_componenete()


def get_text_by_xpath(xp:str, required:bool=False, join:bool=False):
    """Dado un xpath extrae el texto y lo retorna
    en caso de fallar se retorna un string vacio, 
    a menos que sea un campo requerido,en cuyo caso retorna false
    
    si join es enviado todo el texto encontrado en el xpath
    se concatena separado por una coma. """
    try:
        if not join:
            txt = driver.find_element(By.XPATH, xp).text
        else:
            finds = driver.find_elements(By.XPATH, xp)
            txt = ",".join([i.text for i in finds])

        return txt
    
    except:
        if required:
            return False
        else:
            return ""


def get_page_info() -> dict:
    """Extrae la información general del anuncio y lo guarda en concluidos"""
    global driver, anuncio, today

    #oportunnity url
    uri = driver.current_url
    print(f"  {uri}")

    #Código del expediente
    cod_exp = get_text_by_xpath(xp='//label[text()="Código del expediente:"]/following-sibling::label', required=True)
    #Número de procedimiento de contratación
    num_proc = get_text_by_xpath(xp='//label[text()="Número de procedimiento de contratación:"]/following-sibling::label')
    if not num_proc:
        num_proc = get_text_by_xpath(xp='//label[text()="Código del proyecto de convocatoria:"]/following-sibling::label')
    #Dependencia (SOLO TEXTO DESPUÉS DEL GUIÓN “-”)
    dependencia = get_text_by_xpath(xp='//label[text()="Dependencia o Entidad:"]/following-sibling::label')
    #Unidad Compradora (SOLO CÓDIGO IDENTIDICADOR)
    unidad_comp = get_text_by_xpath(xp='//label[text()="Unidad compradora"]/following-sibling::label')
    #Correo electrónico Unidad compradora
    correo = get_text_by_xpath(xp='//label[text()="Correo electrónico unidad compradora:"]/following-sibling::label')
    # Nombre del procedimiento de contratación
    nombre_procedimiento = get_text_by_xpath(xp='//label[text()="Nombre del procedimiento de contratación:"]/following-sibling::label')
    # Tipo de procedimiento
    tipo_proc = get_text_by_xpath(xp='//label[text()="Tipo de procedimiento de contratación:"]/following-sibling::label')
    # Entidad Federativa
    entidad_fed = get_text_by_xpath(xp='//label[text()="Entidad Federativa donde se llevará a cabo la contratación:"]/following-sibling::label')
    # Año del ejercicio presupuestal
    anio_ej = get_text_by_xpath(xp='//label[text()="Año del ejercicio presupuestal:"]/following-sibling::label')
    # Procedimiento exclusivo para MiPymes
    proc_exc = get_text_by_xpath(xp='//label[text()="Procedimiento exclusivo para MIPYMES:"]/following-sibling::label')
    # Lista de Claves
    claves_list = get_text_by_xpath(xp='//th[text()="Clave"]/ancestor::thead/following-sibling::tbody/tr/td[1]', join=True)
    # Participación de Testigo Social
    part_testigo = get_text_by_xpath(xp='//label[text()="Participación de Testigo Social:"]/following-sibling::label')
    # Abastecimiento simultaneo
    abastecimiento_sim = get_text_by_xpath(xp='//label[text()="Abastecimiento simultáneo:"]/following-sibling::label')
    # Plurianual
    plurianual = get_text_by_xpath(xp='//label[text()="Es plurianual:"]/following-sibling::label')
    # Tipo de contratación
    tipo_cont = get_text_by_xpath(xp='//label[text()="Tipo de contratación:"]/following-sibling::label')
    # Anticipo
    anticipo = get_text_by_xpath(xp='//label[text()="Anticipo:"]/following-sibling::label')
    # Forma de Pago
    forma_pago = get_text_by_xpath(xp='//label[text()="Forma de pago:"]/following-sibling::label')
    # Plazo para entrega de garantía
    plazo_garant = get_text_by_xpath(xp='//label[text()="Plazo en días para entregar la garantía:"]/following-sibling::label')
    # Número de meses para la garantía
    meses_garant = get_text_by_xpath(xp='//label[text()="Número de meses que debe cumplir la garantía:"]/following-sibling::label')
    #Garantía de cumplimiento
    garant_cump = get_text_by_xpath(xp='//label[text()="Garantía de cumplimiento:"]/following-sibling::label')
    # Carácter
    caracter = get_text_by_xpath(xp='//label[text()="Carácter:"]/following-sibling::label')
    # Caso fortuito o fuerza mayor
    caso_fort  = get_text_by_xpath(xp='//label[text()="Caso fortuito o fuerza mayor:"]/following-sibling::label')
    # Tipo de contrato abierto
    tipo_cont_abierto = get_text_by_xpath(xp='//label[text()="Tipo de contrato abierto:"]/following-sibling::label')

    # Fecha y hora de publicación:
    fecha_pub = get_text_by_xpath(xp='//label[text()="Fecha y hora de publicación:"]/following-sibling::label')
    if fecha_pub:
        try:
            fecha_pub = datetime.strptime(fecha_pub, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M")
        except:
            print(f"Error formateando la fecha {fecha_pub} de la op:\n{uri}")
            fecha_pub = today

    # anuncio = {'cod_exp':cod_exp, 'num_proc':num_proc}
    # extraer_anexos()

    return {'cod_exp':cod_exp, 'num_proc':num_proc, 'dependencia':dependencia, 'unidad_comp':unidad_comp, 
            'correo':correo, 'nombre_procedimiento':nombre_procedimiento, 'tipo_proc':tipo_proc, 
            'entidad_fed':entidad_fed, 'anio_ej':anio_ej, 'proc_exc':proc_exc, 'fecha_pub':fecha_pub, 
            'claves_list':claves_list, 'part_testigo':part_testigo, 'abastecimiento_sim':abastecimiento_sim, 
            'plurianual':plurianual, 'tipo_cont':tipo_cont, 'anticipo':anticipo, 'forma_pago':forma_pago, 
            'plazo_garant':plazo_garant, 'meses_garant':meses_garant,'garant_cump':garant_cump, 'caracter':caracter, 'caso_fort ':caso_fort , 
            'tipo_cont_abierto':tipo_cont_abierto, 'uri':uri, 'scrapped_day':today
        }


def get_text_from_column(columns, indice:int, required:bool=False):
    """De prueba no se ejecutó"""
    try:
        txt = columns[indice].text.strip()
        return txt
    
    except:
        if required:
            return False
        else:
            return "falló"


def print_e(msg):
    print(Fore.RED+ msg +Fore.RESET)


def print_w(msg):
    print(Fore.YELLOW+ msg +Fore.RESET)


def get_page_prices():
    """Extrae información de economicos y precios"""
    global driver, today, keywords, claves

    #Esto debido a que a veces economicos no cargaba, y aveces trae un layout distinto
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    xp_1 = '//th[text()="Descripción CUCoP+"]/ancestor::div[contains(@class,"header")]/following-sibling::div/table//tr'
    xp_2 = '//th[text()="Descripción CUCoP+"]/ancestor::thead/following-sibling::tbody/tr'
    xp_economicos = xp_1
    economicos = driver.find_elements(By.XPATH, xp_1)
    iterations = 0
    if len(economicos)<1:
        print('  No cargaron economicos, se esperará')
        while True:
            economicos = driver.find_elements(By.XPATH, xp_2)
            if len(economicos)>0:
                xp_economicos = xp_2
                print(f"   economicos tipo 2")
                break

            duerme(6)

            economicos = driver.find_elements(By.XPATH, xp_1)
            if len(economicos)>0:
                xp_economicos = xp_1
                break
            
            iterations += 1
            if iterations>30:
                print('   Se esperó 3 minutos y no cargaron.')
                break

    duerme(.7, 1.5)
    #oportunnity url
    uri = driver.current_url
    #Código del expediente
    cod_exp = get_text_by_xpath(xp='//label[text()="Código del expediente:"]/following-sibling::label', required=True)
    #Número de procedimiento de contratación
    num_proc = get_text_by_xpath(xp='//label[text()="Número de procedimiento de contratación:"]/following-sibling::label')
    if not num_proc:
        num_proc = get_text_by_xpath(xp='//label[text()="Código del proyecto de convocatoria:"]/following-sibling::label')
    #Dependencia (SOLO TEXTO DESPUÉS DEL GUIÓN “-”)
    dependencia = get_text_by_xpath(xp='//label[text()="Dependencia o Entidad:"]/following-sibling::label')
    # Año del ejercicio presupuestal
    anio_ej = get_text_by_xpath(xp='//label[text()="Año del ejercicio presupuestal:"]/following-sibling::label')
    # Lista de Claves
    claves_list = get_text_by_xpath(xp='//th[text()="Clave"]/ancestor::thead/following-sibling::tbody/tr/td[1]', join=True)
    #claves_alert = [c for c in claves_list.split(",") if c in claves]
    #is_alert_for_claves = claves_alert if claves_alert else False
    #Unidad Compradora (SOLO CÓDIGO IDENTIDICADOR)
    unidad_comp = get_text_by_xpath(xp='//label[text()="Unidad compradora"]/following-sibling::label')
    #Descripción detallada del procedimiento de contratación
    desc_det_anuncio = get_text_by_xpath(xp='//label[text()="Descripción detallada del procedimiento de contratación:"]/following-sibling::label')
    if not desc_det_anuncio: 
        desc_det_anuncio = get_text_by_xpath(xp='//label[text()="Descripción detallada del proyecto de convocatoria:"]/following-sibling::label')
    try:
        num_uc = unidad_comp.split(" ", 1)[0]
        nom_uc = unidad_comp.split(" ", 1)[1]
    except:
        num_uc = ""
        nom_uc = unidad_comp

    #Fecha y hora límite para envío de aclaraciones a través de CompraNet: #JC https://upcp-compranet.hacienda.gob.mx/sitiopublico/#/sitiopublico/detalle/2635437a35a6460c916295a9458d5ed1/proyecto
    fecha_presentacion = get_text_by_xpath(xp='//label[text()="Fecha y hora de presentación y apertura de proposiciones:"]/following-sibling::label')
    if not fecha_presentacion:
        fecha_presentacion = get_text_by_xpath(xp='//label[text()="Fecha y hora límite para recepción de comentarios:"]/following-sibling::label')
    
    # Fecha y hora de publicación:
    fecha_pub = get_text_by_xpath(xp='//label[text()="Fecha y hora de publicación:"]/following-sibling::label')
    if fecha_pub:
        try:
            fecha_pub = datetime.strptime(fecha_pub, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M")
        except:
            print(f"Error formateando la fecha {fecha_pub} de la op:\n{uri}")
            fecha_pub = today
    else:
        # Fecha y hora de publicación del proyecto de convocatoria:
        fecha_pub = get_text_by_xpath(xp='//label[text()="Fecha y hora de publicación del proyecto de convocatoria:"]/following-sibling::label')
        try:
            fecha_pub = datetime.strptime(fecha_pub, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M")
        except:
            print(f"Error formateando la fecha {fecha_pub} de la op:\n{uri}")
            fecha_pub = today
        
    # --ECONOMICOS--
    economicos_list = []
    economic_ids = []
    #Itera páginas
    for i in range(1, 26):
        print(f"  Obteniendo economicos pag: {i}")
        economicos = driver.find_elements(By.XPATH, xp_economicos)
        numero = economicos[0].text.split(" ",1)[0]
        #Itera filas de economicos
        for row_economic in economicos:
            col = row_economic.find_elements(By.XPATH,"./td")
            _id = col[0].text
            if _id in economic_ids:
                print_e(f"  economico {_id} está repetido por alguna extraña razón")
            partida_esp = col[1].text
            clave_cucop = col[2].text
            desc_cucop = col[3].text
            desc_det = col[4].text
            #Esta columna algunas pocas veces no viene
            unidades_medida = col[5].text if len(col)>5 else ""
            cantidad_solicitada = col[6].text if len(col)>6 else ""
            #Busca un patron de 3 o 4 digitos, punto, 3 o 4 digitos, punto,3 o 4 digitos, y desues otros 2 digitos opcionales
            claves_compendio = re.findall(r"\d{3,4}.{1}\d{3,4}.{1}\d{3,4}.?\d{0,2}", desc_cucop)#CUCOP
            clave_compendio = claves_compendio[0].strip().replace(" ",".") if len(claves_compendio)>0 else ""
            
            # ALERTS PART !!!
            desc = normalizar(desc_det)
            keywords_finded = [w for w in keywords if w in desc]
            if keywords_finded:
                is_alert_for_keywords = ",".join(keywords_finded)
                print_w(is_alert_for_keywords)
            else:
                is_alert_for_keywords = False

            economicos_list.append({
                "Clave compendio":clave_compendio, "Codigo del expediente":cod_exp, "Número del procedimiento o contratación":num_proc,
                "Partida específica":partida_esp, "Clave CUCoP+":clave_cucop, "Descripción CUCoP+": desc_cucop, 
                "Descripción detallada":desc_det, "Unidad de medida":unidades_medida, "Cantidad solicitada":cantidad_solicitada,
                "Clave partidas":claves_list, "Dependencia":dependencia, "desc_det_anuncio":desc_det_anuncio,
                "uc":nom_uc, "fecha_presentacion":fecha_presentacion, "fecha_pub":fecha_pub, "is_alert_for_keywords":is_alert_for_keywords, 
                "uri":uri, "scrapped_day":today
            })
        economic_ids.append(_id)

        next_page_btn = driver.find_element(By.XPATH,'//span[text()="ECONÓMICOS"]/ancestor::p-tabview//button[contains(@class,"p-paginator-next")]')
        if "p-disabled" in next_page_btn.get_attribute("class"):
            print("  no hay más páginas disponibles")
            break

        for i in range(0, 10):
            #Revisa si hay más paginas disponibles
            next_page_btn = driver.find_element(By.XPATH,'//span[text()="ECONÓMICOS"]/ancestor::p-tabview//button[contains(@class,"p-paginator-next")]')
            if "p-disabled" in next_page_btn.get_attribute("class"):
                print("  no hay más páginas disponibles")
                break

            #Da click en next page
            ActionChains(driver).scroll_to_element(next_page_btn)\
                .pause(1).click(next_page_btn).perform()
            
            time.sleep(5)

            #Espera nuevos economicos por un máximo de 60 segundos 
            t_end = time.time() + 120
            numero_nuevo = driver.find_elements(By.XPATH, xp_economicos)[0].text.split(" ",1)[0]
            while time.time() < t_end and numero == numero_nuevo:
                try:
                    numero_nuevo = driver.find_elements(By.XPATH, xp_economicos)[0].text.split(" ",1)[0]
                except:
                    pass
            
            #Sí aparecieron nuevos economicos los recolecta...
            if int(numero_nuevo) > int(numero):
                break
            else:# sí no aparecieron nuevos economicos en un minuto busca la siguiente página.
                print("  no aparecieron nuevos economicos en un minuto")

    return economicos_list


def scrape_page(page_numb):
    """Itera todos los renglones del landing page,
    uno por uno da click en el para extraer su informacion
    y guardarla en la bdd"""
    global driver,  gobernanza, vig_file_name, procedimientos_guardados,\
        economicos_file_name,  num_proc_added, rows_aded

    # Obtiene las filas del landing page
    rows = driver.find_elements(By.XPATH, '//td[@class="p-link2"]')
    ops_found = len(rows)
    print(f"se encontraron {ops_found} oportunidades en está página")
    for i in range(0, ops_found):
        """ Itera fila por fila del LP,
        busca el numero de procedimiento en la bdd, si ya existe lo omite
        si no le da click para ir a la página de detalle, 
        ahí extrae la información de cada oportunidad, cuando termina
        vuelve al LP, y repite fila por fila.
        """
        rows = driver.find_elements(By.XPATH, '//td[@class="p-link2"]')
        n_proc = rows[i].text

        if procedimientos_guardados['num_proc'].str.contains(n_proc).any() or n_proc in num_proc_added:
            print(f"\nprocedimiento:{i+1} - {n_proc} ya está en la bdd")
            continue

        # Entra a la página de detalle
        rows[i].click()
        espera_carga_componenete()
        
        print(f"\nExtrayendo información del anuncio {i+1} - {n_proc}")

        #Extrae informacion de Economicos.csv
        try:
            economic_list = get_page_prices()
        except Exception as e:
            print_e(f"  fallo obtención de conomicos, error: {e}")
            economic_list = False
            driver.save_screenshot(f"./{str(page_numb)}_{i}_error.png")
        
        # Extrae información de concluidos.csv
        try:
            new_row = get_page_info()
        except Exception as e:
            print_e(f"  error: {e}")
            new_row['dependencia'] = "Error:::"
            driver.save_screenshot(f"./{str(page_numb)}_{i}_error.png")

        if not new_row['cod_exp'] or not new_row['num_proc']:
            print(f"Error recuperando informacón básica del anuncio: {new_row['uri']}") 
            print(f"codigo de expediente: {new_row['cod_exp']}")
            print(f"numero de exp: {new_row['num_proc']}")
            driver.save_screenshot(f"./{str(page_numb)}_{i}_error.png")
        else:
            df = pd.DataFrame([new_row])
            df.to_csv(vig_file_name, index=False, header=False, encoding='utf-8', mode='a')

            if economic_list:
                df = pd.DataFrame(economic_list)
                df.to_csv(economicos_file_name, index=False, header=False, encoding='utf-8', mode='a')
                print("  SE EXTRAJO Y GUARDÓ INFORMACIÓN DE ECONOMICOS.")
            else:
                print_e("  ", economic_list)
            
            #agrega el numero de procedimiento para evitar repetirlo.s
            num_proc_added.append(new_row['num_proc'])
            rows_aded += 1

        driver.back()
        espera_carga_componenete()

        if rows_aded > gobernanza:
            raise Exception("Se alcanzo el númeor máximo de oportunidades por ejecución.")
        
        duerme(.5, 2)


def paginate():
    """Itera las páginas disponibles una por una"""
    global driver, main_url, gobernanza, actual_page

    print(f"Entrando a la pagina principal: {main_url}")
    driver.get(main_url)
    espera_carga_componenete()

    print("\nSeteando filtros")
    set_filters()
    
    #PAGINACIÓN
    actual_page = 1
    for i in range(1, 100):
        """Itera las páginas de anuncios, por cada página de detalle
        obtiene la información y la guarda en la bdd.
        sigue iterando páginas mientras el botón de "siguiente página
        siga disponible.
        """
        print(f"\nObteniendo información pag {i}")
        scrape_page(i)

        next_page_btn = driver.find_element(By.XPATH,'//button[contains(@class,"p-paginator-next")]')
        if "p-disabled" in next_page_btn.get_attribute("class"):
            print("Se acabaron las páginas disponibles")
            break
        else:
            print(f"Cambiando a página: {i+1}")
            actual_page += 1
            ActionChains(driver).scroll_to_element(next_page_btn)\
                .pause(1).click(next_page_btn).perform()
            espera_carga_componenete()
            duerme(2, 6)


@timing_val
def main():
    """ Declara variables globales que se usan en diferentes funciones
    carga identificadores unicos de la bdd para evitar raspar anuncios ya 
    agregados, inicializa el driver(chrome) e inicia el proceso de páginacion
    """
    global main_url, today, driver, keywords, anuncio, gobernanza, claves, vig_file_name,\
           rows_aded, procedimientos_guardados, economicos_file_name, \
           anexos_full_dir, num_proc_added, actual_page
    
    actual_page = 1
    num_proc_added = [] #guarda número de procedimiento de los anuncios agregados a la base de datos para evitar repeticiones
    anuncio = {} #Sirve para anexos
    anexos_full_dir = r""
    rows_aded = 0 #cantidad de anuncios agregados a la bdd
    gobernanza = 100 #número máximo de anuncios a agregar por ejecución(la idea es evitar bloqueos permitiendo que el robot corra indefinidamente)
    today = date.today().strftime("%d/%m/%Y") #fecha de ejecución 
    
    #nombre de las bases de datos
    vig_file_name = './vigentes.csv'
    economicos_file_name = './vigentes_economicos.csv'
    
    main_url = 'https://upcp-compranet.hacienda.gob.mx/sitiopublico/#/'
    
    claves = ['15901', '26101', '26102', '26103', '15401', '21101', '37501', '37502', '37503', 
              '37504', '37601', '37602', '37701', '37801', '37802', '37901', '38101', '38102', 
              '38103', '38201', '38301', '38401', '38501', '44101', '44102', '44103', '44104', 
              '34101']

    keywords = ['vales','despensa','gasolina','combustible','tarjeta','monedero','vestimenta','viatico','regalo','restaurante',
                'ropa','viaje','mantenimiento','vehiculo','mtto','preventivo','correctivo','premium','magna','fin de año',
                'abarrote','aguinaldo','alimentacion','alimenta','alimentic','alimento','arillo','bono','canjeable','cena',
                'comedor','comida','cupon','desayun','diesel','dispersion','enser','fin año','juguete','lubrica','medio',
                'pago','premio','prevision','recompensa','restaurant','subsistencia','chip','electronic','inteligente',
                'magnetic','uniforme','utiles escolar','vale','vestido','vestir','vestuari','viveres','apoyo','asistencia',
                'ayuda','gasto','prestacion','programa','laboral','social','trabajo','incentivo','aditivo','apoyos economicos',
                'apoyo monetarios','fintech','viaticos','control de gastos','caja chica','atm','retiro en efectivo',
                'cajero automatico','tarjetas','sello de caja']
    
    #Carga los numeros de procedimiento para evitar repeticiones
    print("\nCargando el dataset de oportunidades guardadas...")
    procedimientos_guardados = pd.read_csv(vig_file_name, usecols = ['num_proc'])

    print("\nInicializando driver <----")
    set_driver()

    print("\nInicia proceso de scrapping - paginacion <----")
    paginate()

    print(f"\nSe agregaron {rows_aded} oportunidades nuevas a la bdd", "-----------El Robot Terminó con exito-----------")


if __name__ == "__main__":
    #FLAG para probar y mejorar detección de errores 
    prueba = False

    if prueba:
        main()
        driver.close()

    else:
        try:
            main()
            driver.close()
        except Exception as e:
            print(f"error: {e}")
            if driver:
                driver.save_screenshot("./vg_MAIN_error.png")
                driver.close()

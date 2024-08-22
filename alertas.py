import os
from datetime import date, timedelta
import time
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


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


def send_email(subject, body, sender, recipients, password):
    """Envía un correo electrónico con el cuerpo y el asunto especificados. """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = 'iswjuanamaya@gmail.com'
    msg['Cco'] = ',gustavo.gilramos@gmail.com'

    # añade @body como el cuerpo del correo, con el html renderizado.
    part2 = MIMEText(body, 'html')  
    msg.attach(part2)

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()


def generate_body(alerts_df:pd.DataFrame, msg:str)->str:
    """ recibe un dataframe filtrado con las alertas correspondientes,
    las itera y construlle un html con las alertas que servirá 
    como cuerpo del correo. eg:

    <html>
    <head></head>
        <body>
            <h1>Se encontraron nuevas oportunidades!</h1><br><br>
                <h2>UNGM</h2>
                1. <a href="{detail_url}">{title}</a><br>
                Deadline: {date}<br>
                Fecha de publicacion: {date}<br><br>

                2. <a href="{detail_url}">{title}</a><br>
                Deadline: {date}<br>
                Fecha de publicacion: {date}<br><br>

                <h2>UNOPS</h2>
                1. <a href="{detail_url}">{title}</a><br>
                Deadline: {date}<br>
                Fecha de publicacion: {date}<br><br>

                2. <a href="{detail_url}">consulting expert to luxemburg</a><br>
                Deadline: 2018-01-01<br>
                Fecha de publicacion: 2018-01-01<br><br>
        </body>
    </html>
    """

    html = f"""
    <html>
    <head></head>
    <body>
        <h2>{msg}</h2>
    """
    
    i=1
    for group_name, df_group in alerts_df.groupby('Número del procedimiento o contratación'):
        dependencia = df_group['Dependencia'].iloc[0]
        desc_det_an = df_group['desc_det_anuncio'].iloc[0]
        desc_det_an = desc_det_an[0:105] + "..." if len(desc_det_an)>105 else desc_det_an
        unidad_comp = df_group['uc'].iloc[0]
        fec_pres = df_group['fecha_presentacion'].iloc[0]
        fec_pub = df_group['fecha_pub'].iloc[0]
        detail_url = df_group['uri'].iloc[0]
        ecos_cant = len(df_group)
        
        html += f"{i}. <a href='{detail_url}'>{desc_det_an}</a><br>"
        html += f"<strong>Dependencia:</strong> {dependencia}<br>" if dependencia else ""
        html += f"<strong>Unidad compradora:</strong> {unidad_comp}<br>" if unidad_comp else ""
        html += f"<strong>Fecha y hora límite para envío de aclaraciones:</strong> {fec_pres}<br>" if fec_pres else ""
        html += f"<strong>Fecha de publicacion:</strong> {fec_pub}<br>" if fec_pub else ""
        
        keyword_desc = []
        for group_name, df_group in df_group.groupby('is_alert_for_keywords'):
            break_for_group =  False if len(df_group)<5 else True

            for row_index, row in df_group.iterrows():
                keywords_alert = row['is_alert_for_keywords']
                keywords_finded = keywords_alert.split(",")

                desc_detallada = row['Descripción detallada']
                desc_n = normalizar(desc_detallada)
                
                for keyword in keywords_finded:
                    match = re.search(keyword, desc_n)
                    indice_start = match.start()-40
                    indice_start = indice_start if indice_start>=0 else 0
                    keyword_desc.append(keyword+": "+
                        desc_detallada[indice_start:match.start()+55].strip().replace("\n","")
                        )
                    
                if break_for_group:
                    break

        kw_added = []
        desc_not_added = []
        descriptions = []
        for e in keyword_desc:
            kw = e.split(":")[0]
            if kw not in kw_added:
                kw_added.append(kw)
                descriptions.append(e)
            else:
                desc_not_added.append(e)
        
        cant_descs = len(descriptions)
        if cant_descs<10 and desc_not_added:
            for dna in desc_not_added:
                descriptions.append(dna)
                if len(descriptions)>9:
                    break
        
        html += f"<strong>Se encontraron {ecos_cant} economicos con los siguientes keywords:</strong> {", ".join(kw_added)}<br>"
        for enunciado in descriptions:
            html += f"<strong>-></strong>{enunciado.lower()}<br>"

        html += "<br>"
        i += 1

    html += """
        </body>
        </html>
        """
    
    return html


def generate_df_to_fill_body(df:pd.DataFrame, tipo:str) -> pd.DataFrame:
    """
    Receive a dataframe with all the opportunities scrapped and 
    return a dataframe with the opportunities with alert depending on the type 
    of alert 
    daily: opportunities scrapped today; tuesday, wednesday, thursday, friday
    weekly: it will be sent on thursday
    monday: it will be contain opportunities scrapped on monday, sunday and saturday
    """
    global today_datetime, today
    print("generando html para enviar las alertas por correo")

    if tipo == "diario":
        #selecciona las oportunidades escrapeadas hoy y que tengan alerta
        nuevas_alertas = df\
                            [
                                (df['scrapped_day'] == today) & (df['is_alert_for_keywords'] != "False") 
                            ]
        
        #selecciona las oportunidades escrapeadas hoy
        nuevas_oportunidades = df\
                                [
                                    (df['scrapped_day'] == today)
                                ]
        
        msg = f"{len(nuevas_alertas)} economicos con alerta por keyword encontrados dentro de {len(nuevas_oportunidades)} economicos raspados"
            
        print(msg)
        return nuevas_alertas, msg
    
    elif tipo == "semanal":

        #['22/03/2023','21/03/2023','20/03/2023','19/03/2023','18/03/2023','17/03/2023','16/03/2023']
        fechas_semanales = [
                today_datetime.strftime("%d/%m/%Y"),
                (today_datetime - timedelta(1)).strftime("%d/%m/%Y"), 
                (today_datetime - timedelta(2)).strftime("%d/%m/%Y"),
                (today_datetime - timedelta(3)).strftime("%d/%m/%Y"),
                (today_datetime - timedelta(4)).strftime("%d/%m/%Y"),
                (today_datetime - timedelta(5)).strftime("%d/%m/%Y"),
                (today_datetime - timedelta(6)).strftime("%d/%m/%Y")
            ]
        
        #selecciona las oportunidades escrapeadas sabado, domingo y lunes y que tengan alerta
        nuevas_alertas = df[['url_detail_id','title','source','location','opening_date','closing_date']]\
            [
                (df['scrapped_day'].isin(fechas_semanales)) & (df['is_alert'] == True)
            ]
        
        #selecciona las oportunidades escrapeadas sabado, domingo y lunes 
        nuevas_oportunidades = df[['url_detail_id','title']]\
                                [
                                    (df['scrapped_day'].isin(fechas_semanales)) 
                                ]
        
        msg = f""" {len(nuevas_alertas)} \
            alertas detectadas en {len(nuevas_oportunidades)} oportunidades minadas"""
            
        print(msg)
        
        return nuevas_alertas, msg
    
    elif tipo == "lunes":

        #['20/03/2023', '19/03/2023', '18/03/2023']
        sab_dom_lun = [
                today_datetime.strftime("%d/%m/%Y"),
                (today_datetime - timedelta(1)).strftime("%d/%m/%Y"), 
                (today_datetime - timedelta(2)).strftime("%d/%m/%Y") 
            ]
        
        #selecciona las oportunidades escrapeadas sabado, domingo y lunes y que tengan alerta
        nuevas_alertas = df[['url_detail_id','title','source','location','opening_date','closing_date']]\
            [
                (df['scrapped_day'].isin(sab_dom_lun)) & (df['is_alert'] == True)
            ]
        
        #selecciona las oportunidades escrapeadas sabado, domingo y lunes 
        nuevas_oportunidades = df[['url_detail_id','title']]\
                                [
                                    (df['scrapped_day'].isin(sab_dom_lun)) 
                                ]
        
        msg = f""" {len(nuevas_alertas)} \
            alertas detectadas en {len(nuevas_oportunidades)} oportunidades minadas"""
            
        print(msg)
        
        return nuevas_alertas, msg


def main():
    """
    Script orquestador de la ejecución de los scripts de extracción, transformación y carga de datos.

    1) Itera sobre el diccionario folders, toma la llave como la carpeta, se mueve a ella, 
    ejecuta el script y vuelve a la carpeta raiz

    2) Lee el archivo de alertas y lo convierte en un dataframe con las alertas correspondientes, 
    al final envia el correo y si hay alertas
    
    """
    global sender, recipients, password, today, today_datetime
    sender = "alquimiadigital23@gmail.com"
    recipients = ["iswjuanamaya@gmail.com", "gustavo.gilramos@gmail.com"]#, "dss.tisalud@gmail.com"
    password = "vaillidatntojvsc" 
    today_datetime = date.today()
    today = date.today().strftime("%d/%m/%Y")

    #--// Empieza el algoritmo de generacion de alertas y envió de correos //--#
    # 2) corre el script de generacion y envio de alertas
    print("--------->>>>>>>>>>> Algoritmo de generacion de alertas......")

    #lee las oportunidades guardadas
    print("leyendo oportunidades guardadas")
    df = pd.read_csv('vigentes_economicos.csv', encoding='utf-8')

    #martes, miercoles, jueves y viernes
    if today_datetime.weekday() in [1,2,3,4]:

        print("Generando dataFrame con las alertas diarias")
        nuevas_alertas, msg = generate_df_to_fill_body(df, "diario")

        cant_alertas = len(nuevas_alertas)
        if cant_alertas > 0:
            print(f"enviando {cant_alertas} alertas")
            body_html = generate_body(nuevas_alertas, msg)
            subject = f"Nuevas oportunidades"
            send_email(subject, body_html, sender, recipients, password)

        else:
            print("no hay alertas el día de hoy")

        #Jueves
        # if today_datetime.weekday() == 3:
        #     print("----Jueves----")
        #     print("Generando dataFrame con las alertas de esta semana")
        #     nuevas_alertas, msg = generate_df_to_fill_body(df, "semanal")

        #     cant_alertas = len(nuevas_alertas)
        #     if cant_alertas > 0:
        #         print(f"enviando {cant_alertas} alertas")
        #         body_html_sem = generate_body(nuevas_alertas, msg)
        #         subject = "Resumen de oportunidades semanal"
        #         send_email(subject, body_html_sem, sender, recipients, password)

        #     else:
        #         print("no hay alertas el día de hoy")

    #lunes
    elif today_datetime.weekday() == 0:
        print("Generando dataFrame con las alertas del sabado, domingo y lunes")
        nuevas_alertas, msg = generate_df_to_fill_body(df, "lunes")
        
        cant_alertas = len(nuevas_alertas)
        if cant_alertas > 0:
            print(f"enviando {cant_alertas} alertas")
            body_html = generate_body(nuevas_alertas, msg)
            subject = f"{cant_alertas} nuevas oportunidades"
            send_email(subject, body_html, sender, recipients, password)

        else:
            print("no hay alertas")

    # fin de semana no se envian alertas
    elif today_datetime.weekday() in [5,6]:
        print("--> Hoy es fin de semana, no se envian alertas")


if __name__ == "__main__":
    main()

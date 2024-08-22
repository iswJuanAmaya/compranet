import pandas as pd

#CUIDADO ESTO ES PARA REFERENCIA, EJECUTAR ESTE SCRIPT PUEDE BORRAR ARCHIVOS YA CON INFORMACIÓN.
df = pd.DataFrame(columns=["Clave compendio", "Codigo del expediente","Número del procedimiento o contratación",
                           "Partida específica","Clave CUCoP+","Descripción CUCoP+","Descripción detallada",
                           "Unidad de medida","Cantidad solicitada","Clave partidas","Dependencia","desc_det_anuncio",
                           "uc", "fecha_presentacion","fecha_pub", "is_alert_for_keywords", "uri","scrapped_day"])
df.to_csv('vigentes_economicos.csv', index=False, encoding='utf-8', header=True)
del df


#crea el layout del csv de oportunidades
df = pd.DataFrame(columns=['cod_exp','num_proc','dependencia','unidad_comp','correo','nombre_procedimiento',
                        'tipo_proc','entidad_fed','anio_ej','proc_exc','fecha_pub','claves_list','part_testigo',
                        'abastecimiento_sim','plurianual','tipo_cont','anticipo','forma_pago','plazo_garant',
                        'meses_garant','garant_cump','caracter','caso_fort ','tipo_cont_abierto','uri','scrapped_day'])
df.to_csv('vigentes.csv', index=False, encoding='utf-8', header=True)
del df

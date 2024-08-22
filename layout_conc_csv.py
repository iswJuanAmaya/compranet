import pandas as pd

#CUIDADO ESTO ES PARA REFERENCIA, EJECUTAR ESTE SCRIPT PUEDE BORRAR ARCHIVOS YA CON INFORMACIÓN.
df = pd.DataFrame(columns=["Clave compendio","Clave Cucop","Descripción detallada","Codigo del expediente",
                           "Número del procedimiento o contratación","Dependencia","Número Unidad Compradora",
                           "Nombre Unidad Compradora","Fecha y hora de la publicación","Año del ejercicio presupuestal",
                           "Clave partidas","Proveedor","Número de contrato","Fecha de inicio","Fecha de fin",
                           "Importe Unitario sin Impuestos","Total Sin IVA","Total con IVA","uri","scrapped_day"])
df.to_csv('precios.csv', index=False, encoding='utf-8', header=True)
del df

df = pd.DataFrame(columns=["Clave compendio", "Codigo del expediente","Número del procedimiento o contratación",
                           "Partida específica","Clave CUCoP+","Descripción CUCoP+","Descripción detallada",
                           "Unidad de medida","Cantidad solicitada","uri","scrapped_day"])
df.to_csv('economicos.csv', index=False, encoding='utf-8', header=True)
del df


#crea el layout del csv de oportunidades
df = pd.DataFrame(columns=['cod_exp','num_proc','dependencia','unidad_comp','correo','nombre_procedimiento',
                        'tipo_proc','entidad_fed','anio_ej','proc_exc','fecha_pub','claves_list','part_testigo',
                        'abastecimiento_sim','plurianual','tipo_cont','anticipo','forma_pago','plazo_garant',
                        'meses_garant','garant_cump','caracter','caso_fort ','tipo_cont_abierto','uri','scrapped_day'])
df.to_csv('concluidos.csv', index=False, encoding='utf-8', header=True)
del df

#crea el csv con el layout final de ANEXOS
# df = pd.DataFrame(columns=['cod_exp','num_proc','anexo','scrapped_day'])
# df.to_csv('anexos.csv', index=False, encoding='utf-8', header=True)


"""
'cod_exp','num_proc','dependencia','unidad_comp','correo','nombre_procedimiento',
'tipo_proc','entidad_fed','anio_ej','proc_exc','fecha_pub','claves_list','part_testigo',
'abastecimiento_sim','plurianual','tipo_cont','anticipo','forma_pago','plazo_garant',
'meses_garant','caracter','caso_fort ','tipo_cont_abierto','uri'

-Código del expediente
-Número de procedimiento de contratación
-Dependencia (SOLO TEXTO DESPUÉS DEL GUIÓN “-”)
-Unidad Compradora (SOLO CÓDIGO IDENTIDICADOR)
-Correo electrónico Unidad compradora
-Nombre del procedimiento de contratación
-Tipo de procedimiento
-Entidad Federativa
-Año del ejercicio presupuestal
-Procedimiento exclusivo para MiPymes
-Fecha de Publicación
-Lista de Claves
-Participación de Testigo Social
-Abastecimiento simultaneo
-Plurianual
-Tipo de contratación
-Anticipo
-Forma de Pago
-Plazo para entrega de garantía
-Número de meses para la garantía
-Carácter
-Caso fortuito o fuerza mayor
-Tipo de contrato abierto
-Garantía de cumplimiento
"""


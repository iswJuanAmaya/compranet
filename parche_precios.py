import pandas as pd


"""
Elimina los registros con erro por layout de la bdd
y agrega la nueva columa para "total cantidad minima" 
"""

#Lee los dataFrames
df =  pd.read_csv('precios.csv')
df_c = pd.read_csv('concluidos.csv')

#Encuentra las oportunidades de precios con error
procedimientos_with_error = df['Número del procedimiento o contratación'][df['Dependencia'].str.startswith("Error")].unique()

new_df = df[~df['Número del procedimiento o contratación'].isin(procedimientos_with_error)].copy()
new_df_c = df_c[~df_c['num_proc'].isin(procedimientos_with_error)]

#Se declara nueva columna para nuevo layout
new_df['total cantidad minima'] = ''


#Se guardan los cambios
new_df.to_csv('precios.csv', index=False,  encoding='utf-8')
new_df_c.to_csv('concluidos.csv', index=False,  encoding='utf-8')


cant_eliminada = len(df) - len(new_df)
cant_eliminada_conc = len(df_c) - len(new_df_c)
print(f"Se eliminaron {cant_eliminada} registros de precios y {cant_eliminada_conc} de concluidos")
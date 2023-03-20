import time
import numpy as np
import pandas as pd
import plotly.express as px
import warnings
from fonctions_utiles import (
    generation_moyenne,
    ajout_demande,
    ajout_offre,
    calcul_equilibre,
    generation_moyenne_autocorr,
)

pd.options.mode.chained_assignment = None  # default='warn'
warnings.simplefilter(action="ignore", category=FutureWarning)

# Reading data
prod_conso_fatale_day = pd.read_csv("datasets/prod_conso_fatale_day.csv")
prod_conso_fatale_H = pd.read_csv("datasets/prod_conso_fatale_H.csv")
prod_pilotable = pd.read_csv("datasets/prod_pilotable.csv", sep=";")
prix_commo = pd.read_csv("datasets/prix_commodites.csv")

# Example of 2023-2024
date_range = pd.date_range(start="2023-10-01", end="2024-10-01")
print(date_range)
result = pd.DataFrame(columns=('Date', 'Heure', 'Prix', 'Consommation', 'Production'))
result_production = pd.DataFrame(columns=('Date', 'techno', 'Volume', 'Prix'))

# On génère les prix des commodités sur l'années

prix_commo = generation_moyenne(prix_commo)

# On génère les variables fatales aléatoires autocorrélées

prod_conso_fatale_day = generation_moyenne_autocorr(prod_conso_fatale_day)

# print(time.thread_time())

#### La simulation commence ici

# On boucle sur l'année
for date in date_range:

    print(date)
    # On définit le numéro de la semaine et du jour en question
    day = date.weekday() + 1
    week = date.isocalendar()[1]

    # On selectionne les grandeurs fatales de la journée en question
    prod_conso_fatale = prod_conso_fatale_day[
        (prod_conso_fatale_day['week'] == week) & (prod_conso_fatale_day['day'] == day)]

    # on calcule le prix des commodités

    mois = date.month

    prix_charbon = \
        prix_commo[(prix_commo['month'] == mois) & (prix_commo['commodite'] == 'Prix_Charbon')].value_d.values[0]
    prix_gaz = prix_commo[(prix_commo['month'] == mois) & (prix_commo['commodite'] == 'Prix_Gaz')].value_d.values[0]
    prix_CO2 = prix_commo[(prix_commo['month'] == mois) & (prix_commo['commodite'] == 'Prix_CO2')].value_d.values[0]
    prix_brent = prix_commo[(prix_commo['month'] == mois) & (prix_commo['commodite'] == 'Prix_Brent')].value_d.values[0]

    # On boucle sur les heures de la journée

    for h in range(24):
        # On sélectionne le coefficient de l'heure
        prod_conso_fatale_h = prod_conso_fatale.copy()
        coefficient_h = prod_conso_fatale_H[
            (prod_conso_fatale_H['week'] == week) & (prod_conso_fatale_H['day'] == day) & (
                    prod_conso_fatale_H['hour'] == h)]

        # on joint les deux tables, puis on réalise le calcul
        prod_conso_fatale_h = prod_conso_fatale_h.merge(coefficient_h, left_on='techno', right_on='techno')
        prod_conso_fatale_h['value_h'] = prod_conso_fatale_h['value'] * prod_conso_fatale_h['value_d']

        # On crée un data frame pour recenser les demandes et offres
        equilibre = pd.DataFrame(columns=('Sens', 'Volume_Start', 'Volume_End', 'Prix_Start', 'Prix_End'))

        # On crée un data Frame pour calculer l'énergie par techno

        production = pd.DataFrame(columns=('techno', 'Volume', 'Prix'))

        # On suppose que la consommation est demandée au prix plafond (4000 €/MWh)

        equilibre = ajout_demande(4000,
                                  prod_conso_fatale_h[prod_conso_fatale_h['techno'] == 'consommation'].value_h.values[
                                      0], equilibre)

        # On ajoute la production ENR à 0 €/MWh, sauf le lac qui est proposé au prix du gaz et le nucléaire.

        [equilibre, production] = ajout_offre(0, prod_conso_fatale_h[
            prod_conso_fatale_h['techno'] == 'eolien'].value_h.values[0], equilibre, production, 'eolien')

        [equilibre, production] = ajout_offre(0, prod_conso_fatale_h[
            prod_conso_fatale_h['techno'] == 'solaire'].value_h.values[0], equilibre, production, 'solaire')
        [equilibre, production] = ajout_offre(0, prod_conso_fatale_h[
            prod_conso_fatale_h['techno'] == 'fil_eau'].value_h.values[0], equilibre, production, 'fil_eau')
        [equilibre, production] = ajout_offre(0, prod_conso_fatale_h[
            prod_conso_fatale_h['techno'] == 'cogeneration'].value_h.values[0], equilibre, production, 'cogeneration')

        [equilibre, production] = ajout_offre(8, prod_conso_fatale_h[
            prod_conso_fatale_h['techno'] == 'nucleaire'].value_h.values[0], equilibre, production, 'nucleaire')

        # On ajoute la production pilotable
        # On calcule le prix par technologie fossile

        prod_pilotable['cout'] = prod_pilotable['CO2'] * prix_CO2 + prod_pilotable['Gaz'] * prix_gaz + prod_pilotable[
            'Charbon'] * prix_charbon + prod_pilotable['Brent'] * prix_brent

        [equilibre, production] = ajout_offre(prod_pilotable[prod_pilotable['techno'] == 'ccgt'].cout.values[0],
                                              prod_pilotable[prod_pilotable['techno'] == 'ccgt'].puissance.values[0],
                                              equilibre, production, 'ccgt')
        [equilibre, production] = ajout_offre(prod_pilotable[prod_pilotable['techno'] == 'tac gaz'].cout.values[0],
                                              prod_pilotable[prod_pilotable['techno'] == 'tac gaz'].puissance.values[0],
                                              equilibre, production, 'tac gaz')
        [equilibre, production] = ajout_offre(prod_pilotable[prod_pilotable['techno'] == 'tac fioul'].cout.values[0],
                                              prod_pilotable[prod_pilotable['techno'] == 'tac fioul'].puissance.values[
                                                  0], equilibre, production, 'tac fioul')
        [equilibre, production] = ajout_offre(prod_pilotable[prod_pilotable['techno'] == 'charbon'].cout.values[0],
                                              prod_pilotable[prod_pilotable['techno'] == 'charbon'].puissance.values[0],
                                              equilibre, production, 'charbon')
        [equilibre, production] = ajout_offre(prod_pilotable[prod_pilotable['techno'] == 'ccgt'].cout.values[0],
                                              prod_conso_fatale_h[
                                                  prod_conso_fatale_h['techno'] == 'lac'].value_h.values[0], equilibre,
                                              production, 'lac')

        # On ajoute les interconnexions à la demande et à l'offre

        [equilibre, production] = ajout_offre(
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_1'].cout.values[0],
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_1'].puissance.values[0], equilibre, production,
            'interconnexion_1')
        [equilibre, production] = ajout_offre(
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_2'].cout.values[0],
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_2'].puissance.values[0], equilibre, production,
            'interconnexion_2')
        [equilibre, production] = ajout_offre(
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_3'].cout.values[0],
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_3'].puissance.values[0], equilibre, production,
            'interconnexion_3')
        [equilibre, production] = ajout_offre(
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_4'].cout.values[0],
            prod_pilotable[prod_pilotable['techno'] == 'interconnexion_4'].puissance.values[0], equilibre, production,
            'interconnexion_4')

        equilibre = ajout_demande(prod_pilotable[prod_pilotable['techno'] == 'interconnexion_1'].cout.values[0] - 1,
                                  prod_pilotable[prod_pilotable['techno'] == 'interconnexion_1'].puissance.values[0],
                                  equilibre)
        equilibre = ajout_demande(prod_pilotable[prod_pilotable['techno'] == 'interconnexion_2'].cout.values[0] - 1,
                                  prod_pilotable[prod_pilotable['techno'] == 'interconnexion_2'].puissance.values[0],
                                  equilibre)
        equilibre = ajout_demande(prod_pilotable[prod_pilotable['techno'] == 'interconnexion_3'].cout.values[0] - 1,
                                  prod_pilotable[prod_pilotable['techno'] == 'interconnexion_3'].puissance.values[0],
                                  equilibre)
        equilibre = ajout_demande(prod_pilotable[prod_pilotable['techno'] == 'interconnexion_4'].cout.values[0] - 1,
                                  prod_pilotable[prod_pilotable['techno'] == 'interconnexion_4'].puissance.values[0],
                                  equilibre)

        # Calcul du prix et volume d'équilibre

        [prix, volume] = calcul_equilibre(equilibre)

        # On détermine la production par technologie en classant les technologies par prix et en comparant à la production totale
        production = production.sort_values(by=['Prix'])

        # On réalise la somme cumulative des puissances disponibles

        production['VolumeCumul'] = production.Volume.cumsum()

        # On compare à la production totale de la journée
        production['VolumeCumul'] = production['VolumeCumul'] - volume

        # Les technologies qui fonctionnent sont celles dans le merit order
        production['VolumeCumul'][production['VolumeCumul'] < 0] = 0
        production['Volume'] = production['Volume'] - production['VolumeCumul']
        production['Volume'][production['Volume'] < 0] = 0

        production = production.drop(columns=['VolumeCumul'])
        production['Date'] = date + pd.DateOffset(hours=h)

        result = result.append({
            'Date': date + pd.DateOffset(hours=h),
            'Heure': h,
            'Prix': prix,
            'Consommation': prod_conso_fatale_h.loc[prod_conso_fatale_h['techno'] == 'consommation', 'value_h'].values[0],
            'Production': production,
            'Export': volume - prod_conso_fatale_h.loc[prod_conso_fatale_h['techno'] == 'consommation', 'value_h'].values[0]
        }, ignore_index=True)

        result_production = result_production.append(production)

fig = px.line(result, x="Date", y="Consommation", title='Consommation')
fig.show()
fig_1 = px.line(result_production[result_production['techno'] == 'eolien'], x="Date", y="Volume", title='Eolien')
fig_1.show()
fig_2 = px.line(result_production[result_production['techno'] == 'solaire'], x="Date", y="Volume", title='Solaire')
fig_2.show()
fig_3 = px.line(result_production[result_production['techno'] == 'nucleaire'], x="Date", y="Volume", title='Nucleaire')
fig_3.show()
fig_4 = px.line(result, x="Date", y="Prix", title='Prix')
fig_4.show()

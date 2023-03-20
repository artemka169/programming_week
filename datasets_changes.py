import pandas as pd
import numpy as np


def prix_com_changes():
    # Load the dataset
    data = pd.read_csv("datasets/prix_commodites.csv")

    # Define the price increase factors for different energy sources
    gas_price_increase = 1.5
    coal_price_increase = 1.4
    oil_price_increase = 1.3

    # Define the time horizon for the analysis (1 year)
    time_horizon = 12

    # Modify the dataset
    for i in range(time_horizon):
        month_data = data[data['month'] == i + 1]

        # Gradually increase the prices of gas, coal, and oil over the time horizon
        month_data.loc[month_data['commodite'] == 'Prix_Gaz', 'moyenne'] *= (1 + (i / time_horizon) * (gas_price_increase - 1))
        month_data.loc[month_data['commodite'] == 'Prix_Charbon', 'moyenne'] *= (1 + (i / time_horizon) * (coal_price_increase - 1))
        month_data.loc[month_data['commodite'] == 'Prix_Brent', 'moyenne'] *= (1 + (i / time_horizon) * (oil_price_increase - 1))

        data.update(month_data)

    # Save the modified dataset
    data.to_csv("datasets/prix_commodites_modified.csv", index=False)


def prod_conso_fatale_day_changes():
    data_day = pd.read_csv("datasets/prod_conso_fatale_day.csv")

    # Define the increase factors for different energy sources
    gas_price_increase = 1.5
    coal_price_increase = 1.4
    oil_price_increase = 1.3

    # Define the percentage increase in renewables and other energy sources
    renewable_increase = 0.1
    nuclear_increase = 0.05

    # Additional percentage increases for 'fil_eau', 'lac', 'cogeneration', and 'consommation'
    fil_eau_increase = 0.02
    lac_increase = 0.03
    cogeneration_increase = 0.04
    consommation_increase = 0.03

    # Define the time horizon for the analysis (1 year)
    time_horizon_weeks = 52

    # Modify the dataset
    for i in range(time_horizon_weeks):
        for index, row in data_day.iterrows():
            if row['week'] == i + 1:
                tech = row['techno']
                if tech in ['gas', 'coal', 'oil']:
                    increase = {'gas': gas_price_increase, 'coal': coal_price_increase, 'oil': oil_price_increase}[tech]
                elif tech in ['solaire', 'eolien', 'nucleaire']:
                    increase = renewable_increase if tech in ['solaire', 'eolien'] else nuclear_increase
                elif tech == 'fil_eau':
                    increase = fil_eau_increase
                elif tech == 'lac':
                    increase = lac_increase
                elif tech == 'cogeneration':
                    increase = cogeneration_increase
                elif tech == 'consommation':
                    increase = consommation_increase
                else:
                    continue

                data_day.at[index, 'moyenne'] *= (1 + (i / time_horizon_weeks) * increase)

    data_day.to_csv("datasets/prod_conso_fatale_day_modified.csv", index=False)


def prod_conso_fatale_hour_changes():
    # Read the original dataset
    data_hour = pd.read_csv('datasets/prod_conso_fatale_H.csv')

    # Define the increase factors for each technology
    solaire_increase = 0.1
    eolien_increase = 0.15
    nucleaire_increase = 0.05
    fil_eau_increase = 0.02
    lac_increase = 0.03
    cogeneration_increase = 0.04
    consommation_increase = 0.01
    time_horizon_weeks = 52

    # Apply the increase factors
    for i in range(1, time_horizon_weeks + 1):
        week_data = data_hour[data_hour['week'] == i]

        for tech, increase in [("solaire", solaire_increase), ("eolien", eolien_increase), ("nucleaire", nucleaire_increase),
                              ("fil_eau", fil_eau_increase), ("lac", lac_increase), ("cogeneration", cogeneration_increase),
                              ("consommation", consommation_increase)]:
            data_hour.loc[(data_hour['week'] == i) & (data_hour['techno'] == tech), 'value'] *= (1 + (i / time_horizon_weeks) * increase)

    # Save the updated dataset
    data_hour.to_csv('datasets/prod_conso_fatale_H_updated.csv', index=False)


def update_prod_pilotable():

    increase_factors = {
    'ccgt': -0.02,
    'tac gaz': -0.03,
    'tac fioul': -0.04,
    'charbon': -0.05,
    'interconnexion_1': -0.05,
    'interconnexion_2': -0.05,
    'interconnexion_3': -0.05,
    'interconnexion_4': -0.05,
}
    pilotable_data = pd.read_csv('datasets/prod_pilotable.csv', delimiter=';', index_col='techno')

    for tech, increase in increase_factors.items():
        if tech in pilotable_data.index:
            pilotable_data.loc[tech, 'puissance'] *= (1 + increase)

    pilotable_data.to_csv('datasets/prod_pilotable_updated.csv', sep=';', index_label='techno')


prix_com_changes()
prod_conso_fatale_day_changes()
prod_conso_fatale_hour_changes()
update_prod_pilotable()

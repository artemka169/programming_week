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



import pandas as pd

def prod_conso_fatale_day_changes():
    data_day = pd.read_csv("datasets/prod_conso_fatale_day.csv")

    # Define the increase factors for different energy sources
    gas_price_increase = 1.5
    coal_price_increase = 1.4
    oil_price_increase = 1.3

    # Define the percentage increase in renewables and other energy sources
    renewable_increase = 0.1
    nuclear_increase = 0.05

    # Define the time horizon for the analysis (1 year)
    time_horizon_weeks = 52

    # Get the unique technologies in the dataset
    technologies = data_day['techno'].unique()

    # Modify the dataset
    for i in range(time_horizon_weeks):
        week_data = data_day[data_day['week'] == i + 1]

        # Gradually increase the prices of gas, coal, and oil over the time horizon
        if 'gas' in technologies:
            week_data.loc[week_data['techno'] == 'gas', 'moyenne'] *= (1 + (i / time_horizon_weeks) * (gas_price_increase - 1))
        if 'coal' in technologies:
            week_data.loc[week_data['techno'] == 'coal', 'moyenne'] *= (1 + (i / time_horizon_weeks) * (coal_price_increase - 1))
        if 'oil' in technologies:
            week_data.loc[week_data['techno'] == 'oil', 'moyenne'] *= (1 + (i / time_horizon_weeks) * (oil_price_increase - 1))

        # Gradually increase the consumption of renewables and nuclear energy
        if 'solaire' in technologies:
            week_data.loc[week_data['techno'] == 'solaire', 'moyenne'] *= (1 + (i / time_horizon_weeks) * renewable_increase)
        if 'eolien' in technologies:
            week_data.loc[week_data['techno'] == 'eolien', 'moyenne'] *= (1 + (i / time_horizon_weeks) * renewable_increase)
        if 'nucleaire' in technologies:
            week_data.loc[week_data['techno'] == 'nucleaire', 'moyenne'] *= (1 + (i / time_horizon_weeks) * nuclear_increase)

        data_day.update(week_data)

    data_day.to_csv("datasets/prod_conso_fatale_day_modified.csv", index=False)




def prod_conso_fatale_H_changes():
    data_hourly = pd.read_csv("datasets/prod_conso_fatale_H.csv")

    # Define the increase factors for different energy sources
    gas_price_increase = 1.5
    coal_price_increase = 1.4
    oil_price_increase = 1.3

    # Define the percentage increase in renewables and other energy sources
    renewable_increase = 0.1
    nuclear_increase = 0.05

    # Define the time horizon for the analysis (1 year)
    time_horizon_weeks = 52

    # Get the unique technologies in the dataset
    technologies = data_hourly['techno'].unique()

    # Modify the dataset
    for i in range(time_horizon_weeks):
        for j in range(7):
            for k in range(24):
                hourly_data = data_hourly[(data_hourly['week'] == i + 1) & (data_hourly['day'] == j + 1) & (data_hourly['hour'] == k)]

                # Gradually increase the prices of gas, coal, and oil over the time horizon
                if 'gas' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'gas', 'value'] *= (1 + (i / time_horizon_weeks) * (gas_price_increase - 1))
                if 'coal' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'coal', 'value'] *= (1 + (i / time_horizon_weeks) * (coal_price_increase - 1))
                if 'oil' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'oil', 'value'] *= (1 + (i / time_horizon_weeks) * (oil_price_increase - 1))

                # Gradually increase the consumption of renewables and nuclear energy
                if 'solaire' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'solaire', 'value'] *= (1 + (i / time_horizon_weeks) * renewable_increase)
                if 'eolien' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'eolien', 'value'] *= (1 + (i / time_horizon_weeks) * renewable_increase)
                if 'nucleaire' in technologies:
                    hourly_data.loc[hourly_data['techno'] == 'nucleaire', 'value'] *= (1 + (i / time_horizon_weeks) * nuclear_increase)

                # Update the main dataset
                data_hourly.update(hourly_data)

    # Save the modified dataset
    data_hourly.to_csv("datasets/prod_conso_fatale_H_modified.csv", index=False)


def modify_prod_pilotable():
    data_pilotable = pd.read_csv("datasets/prod_pilotable.csv", delimiter=';')

    # Define the increase factors for different energy sources
    gas_price_increase = 1.5
    coal_price_increase = 1.4
    oil_price_increase = 1.3

    # Define the percentage increase in renewables and other energy sources
    renewable_increase = 0.1
    nuclear_increase = 0.05

    # Define the time horizon for the analysis (1 year)
    time_horizon_weeks = 52

    # Modify the dataset
    for i in range(time_horizon_weeks):
        # Gradually increase the prices of gas, coal, and oil over the time horizon
        data_pilotable.loc[data_pilotable['techno'] == 'ccgt', 'Gaz'] *= (1 + (i / time_horizon_weeks) * (gas_price_increase - 1))
        data_pilotable.loc[data_pilotable['techno'] == 'tac gaz', 'Gaz'] *= (1 + (i / time_horizon_weeks) * (gas_price_increase - 1))
        data_pilotable.loc[data_pilotable['techno'] == 'tac fioul', 'Brent'] *= (1 + (i / time_horizon_weeks) * (oil_price_increase - 1))
        data_pilotable.loc[data_pilotable['techno'] == 'charbon', 'Charbon'] *= (1 + (i / time_horizon_weeks) * (coal_price_increase - 1))

        # Gradually increase the consumption of renewables and nuclear energy
        # The example dataset doesn't include renewable energy sources or nuclear energy, so there's no need to modify them here

    # Save the modified dataset
    data_pilotable.to_csv("datasets/prod_pilotable_modified.csv", index=False, sep=';')


prix_com_changes()
prod_conso_fatale_day_changes()
# prod_conso_fatale_H_changes()
# modify_prod_pilotable()

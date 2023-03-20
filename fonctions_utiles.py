import numpy as np
import pandas as pd
from typing import List, Tuple

# Fonction pour ajouter une variable aléatoire gaussienne à un data frame
def generation_moyenne(Data):
    Data['value_d'] = Data.apply(lambda row: np.random.normal(row['moyenne'], row['ecart_type']), axis=1)
    Data = Data.drop(columns=['moyenne', 'ecart_type'])
    return Data


def generation_moyenne_autocorr(Data, corr=0.8):
    def generate_values(techno_data):
        std_vec = techno_data['ecart_type'].to_numpy()
        mean_vec = techno_data['moyenne'].to_numpy()
        n = len(std_vec)

        cov_matrix = np.zeros((n, n))
        cov_matrix[np.eye(n, dtype=bool)] = std_vec ** 2
        cov_matrix[np.eye(n, k=1, dtype=bool)] = std_vec[:-1] * std_vec[1:] * corr
        cov_matrix[np.eye(n, k=-1, dtype=bool)] = cov_matrix[np.eye(n, k=1, dtype=bool)]

        res = np.random.multivariate_normal(mean_vec, cov_matrix, 1).T
        return res

    Data['value_d'] = None

    for techno in Data['techno'].unique():
        techno_data = Data[Data['techno'] == techno]
        values = generate_values(techno_data)
        Data.loc[Data['techno'] == techno, 'value_d'] = values

    Data = Data.drop(columns=['moyenne', 'ecart_type'])
    return Data





# Ajout de la demande dans le dataFrame equilibre
# Il faut éviter les fonctions palier pour s'assurer de limiter des problèmes de discontinuités lors du calcul de l'équilibre
# Comme sur la véritable enchère, on fait des pas de 0,1 €/MWh et on suppose que la fonction volume=f(prix) est linéaire par morceaux
def ajout_demande(prix, volume, equilibre):
    new_rows = [
        {'Sens': 'D', 'Volume_Start': volume, 'Volume_End': volume, 'Prix_Start': 0, 'Prix_End': prix},
    ]

    if prix < 4000:
        new_rows.extend([
            {'Sens': 'D', 'Volume_Start': volume, 'Volume_End': 0, 'Prix_Start': prix, 'Prix_End': prix + 0.1},
            {'Sens': 'D', 'Volume_Start': 0, 'Volume_End': 0, 'Prix_Start': prix + 0.1, 'Prix_End': prix + 4000},
        ])

    return equilibre.append(new_rows, ignore_index=True)



# Ajout de l'offre dans le dataFrame equilibre

def ajout_offre(prix: float, volume: float, equilibre: pd.DataFrame, 
                production: pd.DataFrame, techno: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Ensure volume is non-negative
    volume = max(volume, 0)

    new_rows = [
        {'Sens': 'O', 'Volume_Start': volume, 'Volume_End': volume, 'Prix_Start': prix, 'Prix_End': 4000},
    ]

    if prix > 0:
        new_rows.extend([
            {'Sens': 'O', 'Volume_Start': 0, 'Volume_End': volume, 'Prix_Start': prix - 0.1, 'Prix_End': prix},
            {'Sens': 'O', 'Volume_Start': 0, 'Volume_End': 0, 'Prix_Start': 0, 'Prix_End': prix - 0.1},
        ])

    equilibre = equilibre.append(new_rows, ignore_index=True)
    production = production.append({'techno': techno, 'Volume': volume, 'Prix': prix}, ignore_index=True)

    return equilibre, production



# Function calculating the supply/demand balance


def calcul_equilibre(equilibre: pd.DataFrame) -> List[float]:
    unique_prices = np.unique(pd.concat([equilibre.Prix_Start, equilibre.Prix_End]))
    price_intervals = pd.DataFrame({'Prix_Start_El': unique_prices[:-1], 'Prix_End_El': unique_prices[1:]})

    equilibre = equilibre.reset_index().merge(price_intervals, how='cross')

    equilibre = equilibre[
        (equilibre['Prix_Start_El'] >= equilibre['Prix_Start']) & (equilibre['Prix_End_El'] <= equilibre['Prix_End'])]

    equilibre = equilibre.groupby(['Prix_Start_El', 'Prix_End_El', 'Sens']).sum().reset_index()

    equilibre = equilibre.pivot(index=['Prix_Start_El', 'Prix_End_El'], columns='Sens',
                                values=['Volume_Start', 'Volume_End'])

    if equilibre.iloc[1].Volume_Start.D < equilibre.iloc[1].Volume_Start.O:
        return [0, equilibre.iloc[1].Volume_Start.D]

    offer_max = max(equilibre.Volume_End.O)

    equilibre = equilibre[
        (equilibre.Volume_Start.D > equilibre.Volume_Start.O) & (equilibre.Volume_End.D < equilibre.Volume_End.O)]

    if not equilibre.empty:
        equilibre = equilibre.reset_index()
        clearing_ratio = (equilibre.Volume_Start.O - equilibre.Volume_Start.D) / (
                equilibre.Volume_End.D - equilibre.Volume_Start.D + equilibre.Volume_Start.O - equilibre.Volume_End.O)
        clearing_prix = clearing_ratio.values[0] * (equilibre.Prix_End_El.values[0] - equilibre.Prix_Start_El.values[0]) + \
                        equilibre.Prix_Start_El.values[0]
        clearing_volume = clearing_ratio.values[0] * (equilibre.Volume_End.D.values[0] - equilibre.Volume_Start.D.values[0]) + \
                          equilibre.Volume_Start.D.values[0]
    else:
        clearing_prix = 4000
        clearing_volume = offer_max

    return [clearing_prix, clearing_volume]

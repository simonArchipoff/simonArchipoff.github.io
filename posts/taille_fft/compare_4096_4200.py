import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
from scipy import stats

d4096 = pd.read_csv("./fft4096",names=["size","duration_ns"],sep=';',header=1)
d4200 = pd.read_csv("./fft4200",names=["size","duration_ns"],sep=';',header=1)

#plt.hist(d4096['duration_ns'].to_numpy(), bins=30, alpha=0.5, label='4096')
#plt.hist(d4200['duration_ns'].to_numpy(), bins=30, alpha=0.5, label='4200')

donnees4096 = d4096['duration_ns'].to_numpy()
donnees4200 = d4200['duration_ns'].to_numpy()

plt.plot(donnees4096,label="4096")
plt.plot(donnees4200,label="4200")
plt.legend()
plt.show()

# Calculer la moyenne
moyenne1, moyenne2 = np.mean(donnees4096), np.mean(donnees4200)

# Calculer la médiane
median1, median2 = np.median(donnees4096), np.median(donnees4200)

# Calculer l'écart-type
std_dev1, std_dev2 = np.std(donnees4096), np.std(donnees4200)

# Calculer la variance
variance1, variance2 = np.var(donnees4096), np.var(donnees4200)

# Effectuer un test de Wilcoxon-Mann-Whitney
statistique, p_value = stats.mannwhitneyu(donnees4096, donnees4200)

# Afficher les résultats
print(f"Moyenne 4096: {moyenne1}, Moyenne 4200: {moyenne2}")
print(f"Médiane 1: {median1}, Médiane 2: {median2}")
print(f"Écart-type 1: {std_dev1}, Écart-type 2: {std_dev2}")
print(f"Variance 1: {variance1}, Variance 2: {variance2}")
print(f"Statistique de Wilcoxon-Mann-Whitney : {statistique}, p-value : {p_value}")

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob


fichiers_csv = glob.glob("./result_2p*.csv")

# Initialisez une liste pour stocker les DataFrames de chaque fichier CSV
dfs = []
# Parcourez chaque fichier CSV et lisez-le en tant que DataFrame, puis ajoutez-le à la liste
for fichier_csv in fichiers_csv:
    df = pd.read_csv(fichier_csv,names=["size","duration_ns"],sep=';',header=1)
    dfs.append(df)

df= pd.concat(dfs).sort_values(by='size')

fichiers_csv = glob.glob("./result_all_2p*.csv")

dfs = []
for fichier_csv in fichiers_csv:
    d = pd.read_csv(fichier_csv,names=["size","duration_ns"],sep=';',header=1)
    dfs.append(d)


df_all = pd.concat(dfs).sort_values(by='size').dropna()

def factoriser_nombre(n):
    factors = []
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def power_of_2(n):
    return set(factoriser_nombre(n)) == set({2})

# Appliquer la fonction de factorisation à la colonne 'size' et créer une nouvelle colonne 'factors'
df['factors'] = df['size'].apply(factoriser_nombre)
df_all['factors'] = df_all['size'].apply(factoriser_nombre)


df = df.iloc[::-1]
df['min_time_for_later_sizes'] = df['duration_ns'].cummin()
df = df.iloc[::-1]


#df_all = df_all.iloc[::-1]
df_all['max_time_for_later_sizes'] = df_all['duration_ns'].cummax()
#df_all = df_all.iloc[::-1]

df = df.iloc[::-1]
mins = df[df['min_time_for_later_sizes'].diff() != 0]
df = df.iloc[::-1]

#df_all = df_all.iloc[::-1]
maxs = df_all[df_all['max_time_for_later_sizes'].diff() != 0]
#df_all = df_all.iloc[::-1]

df = df.iloc[::-1]
pow_of_2 = df[df['size'].apply(power_of_2)]
df = df.iloc[::-1]
#almost_mins = df[df['duration_ns'] < 1.1 * df['min_time_for_later_sizes']]

df = df.reset_index(drop=True)
plt.step(mins['size'], mins['duration_ns'],where='post', marker='o', color='b',label="minimum time size")
#plt.plot(df['size'], df['max_time_for_later_sizes'],color='r')
plt.step(pow_of_2['size'],pow_of_2['duration_ns'],where='post',marker='o',color='g',label="power of two")
plt.step(maxs['size'], maxs['duration_ns'], where='post',marker='o', color='r')
plt.plot(df_all['size'],df_all['duration_ns'].rolling(window=50).mean(),color="pink",label="moyenne glissante (50)")

plt.xlabel('Taille')
plt.ylabel('Temps (ns)')
plt.legend()
#plt.xticks([2**i for i in range(int(np.log2(df['size'].max())) + 1)])
plt.xscale('log', base=2)
plt.yscale('log',base=10)
plt.title('Min Time for Later Sizes vs. Taille')
plt.grid(True)
plt.show()

# Affichez le DataFrame final
print(df)


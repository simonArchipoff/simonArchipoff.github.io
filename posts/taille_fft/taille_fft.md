# Quelle taille pour une FFT ?

## Introduction
Dans le cadre de mon projet [ATSAHSNA](https://github.com/simonArchipoff/ATSAHSNA), j'ai été conduit à m'interesser aux [transformée en ondelette continues(CWT)](https://fr.wikipedia.org/wiki/Ondelette).


## Contexte

Bien que le résultat soit très proche de ce qu'on obtient avec une [transformée de fourier à court terme(STFT)](https://fr.wikipedia.org/wiki/Transform%C3%A9e_de_Fourier_%C3%A0_court_terme), l'algorithme est très différent.

![comparaison STFT et CWT](stft_cwt.png)

Comme nous pouvons le voir, le temps de calcul pour la transformée en ondelette est plus de 10 fois plus longue que la STFT avec [scipy.signal.cwt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.cwt.html). Je me suis assuré qu'il utilisait bien la transformée de fourier pour la convolution.
D'un point de vue expérience utilisateur, si 0.06 seconde est perceptible, 0.8s est très long.

Pour une carte temps/fréquence de $t$ unités sur $n$ fréquences :
* La transformée de fourier à court terme nécessite $t$ transformée de fourier de taille $n$
* La transformée en ondelette continue nécessite $3\times{}n$ transformée de fourier d'une taille $t$

Dans mes cas d'usage typique pour la STFT, les données de chaque transformée de fourier tienent dans le cache L1 d'un processeur moderne, le temps de calcul est principalement dépendant de la longueur de l'entrée.
Par exemple pour un enregistrement audio à 48000 échantillons par seconde, avec $n = 2048$ on couvre le spectre audible.
Bref, on peut considérer $n$ comme constant et le temps de calcul d'une STFT linéaire avec $t$.

À l'inverse, pour la CWT c'est la taille des transformées de fourier qui dépendent de $t$. Hors le temps d'execution d'une transformée de fourier ne croit pas linéairement avec la taille de son entrée,
celui ci est très dépendant de la décomposition en facteur premier de la taille de l'entrée. Ce petit exemple illustré est biaisé en faveur du STFT, j'ai choisi les paramètres pour qu'il produise  une sortie de la même taille que la transformée en ondelette. Dans un cas réel, sa taille serait bien inférieure. Pour les paramètres, c'est un signal à 8kHz de la STFT : fenetres de hann de taille 1024 par incrément de 1 seulement. Pour la cwt les fréquences sont héritées de la stft, la longueur est imposée par l'entrée, et l'ondelette et celle de morlet avec le paramètre de nombre de cycle de $40$, ce qui est assez élevé. Ce parametre permet l'arbitrage sur la résolution entre la fréquence et la position. Plus l'ondelette est longue, plus elle selectionne sa propre fréquence, moins elle la localise précisement, et réciproquement. J'ai choisi ce parametre pour faire converger le résultat avec la STFT, qui a une très bonne résolution fréquentielle, et une très mauvaise résolution temporelle.

Paradoxalement augmenter la taille de l'entrée est un moyen d'accelerer ce calcul.

## Optimiser la taille

Une très bonne heuristique est « prendre la puissance de deux suivante »,
cela conduit parfois à littéralement doubler la taille de l'entrée, donc multiplier par plus de deux le temps de calcul,
mais cela met à l'abri de faire exploser ce temps de calcul (multiplié par 10).

Nous avons un arbitrage à faire entre limiter la taille des données et préserver une « belle » factorisation de cette taille.

Mon but est très pragmatique, avoir une méthode rapide et simple pour améliorer cette heuristique.
Je me propose de mesurer des temps d'executions de transformées de fourier, de regarder les valeurs qui se comportent bien et d'en déduire une meilleure heuristique que la puissance de 2 suivante.

J'ai réalisé ce benchmark avec fftw3 3.3.10 avec g++ -O3 en version 13.2.1 sur un AMD Ryzen 5 5600G.

![comparaison size](compare_taille_fft.png)

En abscisse la taille de l'entrée, en ordonnée le temps de calcul pour une FFT.

* La courbe verte représente le temps pour une entrée donnée avec la stratégie "prendre la puissance de 2 supérieure.
* La courbe bleu représente le temps si l'on prend une taille suppérieure qui minimise le temps de calcul.
* La courbe rouge est donnée à titre indicatif, c'est en quelque sorte la duale de la courbe bleu, elle représente les pire choix en matière se tailles.
* La courbe rose est également donnée à titre indicatif, il s'agit de la moyenne glissante sur toute les tailles. On peut voir que les cas les pires sont suffisament graves pour affecter significativement la moyenne.

Comme nous pouvons le voir, la stratégie verte est pas mal, mais sous optimale. Si nous observons les factorisation des points de la courbe bleu, nous remarquons que l'on trouve des facteurs jusqu'à 7, en petit nombre, ainsi que des facteurs 5 et 3, même si les facteurs 2 sont toujours majoritaires.

[données factorisation valeur minimale](min_factor.md)



## Étrangeté

J'ai été surpris de ne pas voir systématiquement les puissances de deux dans les minimums. C'est à dire qu'il arrive que les points verts soient strictement au dessus de la courbe bleu. Dans un premier temps j'ai mis ça sur le compte de bruit de mesure, après avoir fait en sorte d'absorber ce bruit dans des mesures multiples je retrouve les mêmes différences.

| taille puissance de 2 |  durée en $\mu\text{s}$ ||   taille optimal |   durée $\mu\text{s}$ | factorisation |
|-------:|--------------:|-|-------------:|---------------------------:|:-------------------------------------|
| 131072 |        440.636 ||       134400 |                     419.057 | [2, 2, 2, 2, 2, 2, 2, 2, 3, 5, 5, 7] |
|  65536 |        194.448 ||        67200 |                     176.851 | [2, 2, 2, 2, 2, 2, 2, 3, 5, 5, 7]    |
|  32768 |        104.760 ||        33600 |                      82.358 | [2, 2, 2, 2, 2, 2, 3, 5, 5, 7]       |
|  16384 |         39.552 ||        16800 |                      38.739 | [2, 2, 2, 2, 2, 3, 5, 5, 7]          |
|   4096 |          8.602 ||         4480 |                       7.548 | [2, 2, 2, 2, 2, 2, 2, 5, 7]          |

Il semble que parfois les facteurs 5 et 7 soient encore meilleurs que les facteurs 2. Je connais mal les algo FFT, cela mériterait d'être investigué davantage.

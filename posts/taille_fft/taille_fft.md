# Quelle taille pour une FFT ?

## Introduction
Dans le cadre de mon projet [ATSAHSNA](https://github.com/simonArchipoff/ATSAHSNA), j'ai été conduit à m'interesser aux [transformée en ondelette continues(CWT)](https://fr.wikipedia.org/wiki/Ondelette).


## Contexte

Bien que le résultat soit très proche de ce qu'on obtient avec une [transformée de fourier à court terme(STFT)](https://fr.wikipedia.org/wiki/Transform%C3%A9e_de_Fourier_%C3%A0_court_terme), l'algorithme est très différent.
Pour une carte temps/fréquence de $t$ unités sur $n$ fréquences :
* La transformée de fourier à court terme nécessite $t$ transformée de fourier de taille $n$
* La transformée en ondelette continue nécessite $3\times{}n$ transformée de fourier d'une taille $t$

Dans mes cas d'usage typique pour la STFT, les données de chaque transformée de fourier tienent dans le cache L1 d'un processeur moderne, le temps de calcul est principalement dépendant de la longueur de l'entrée.
Par exemple pour un enregistrement audio à 48000 échantillons par seconde, avec $n = 2048$ on couvre le spectre audible.
Bref, on peut considérer $n$ comme constant et le temps de calcul d'une STFT linéaire avec $t$.


À l'inverse, pour la CWT c'est la taille des transformées de fourier qui dépendent de $t$. Hors le temps d'execution d'une transformée de fourier ne croit pas linéairement avec la taille de son entrée,
celui ci est très dépendant de la décomposition en facteur premier de la taille de l'entrée.

Une très bonne heuristique est « prendre la puissance de deux suivante »,
cela conduit parfois à littéralement doubler la taille de l'entrée, donc multiplier par plus de deux le temps de calcul,
mais cela met à l'abri de faire exploser ce temps de calcul (multiplié par 10).

Nous avons un arbitrage à faire entre limiter la taille des données et préserver une « belle » factorisation de cette taille.

Mon but est très pragmatique, avoir une méthode rapide et simple pour améliorer cette euristique.
Je me propose de mesurer des temps d'executions de transformées de fourier, de regarder les valeurs qui se comportent bien et d'en déduire une meilleure heuristique que la puissance de 2 suivante.





## Étrangeté

J'ai été surpris de ne pas voir systématiquement les puissances de deux dans les minimums, dans un premier temps j'ai mis ça sur le compte de bruit de mesure, puis j'ai investigué davantage. Finalement, il s'avère que le temps de calcul d'une fft de taille  $4096 = 2^{12}$ est plus important que celui d'une fft de taille $4200 = 2^3 \times{} 3 \times{} 5^2 \times{} 7$, lors que cette première valeur est à la fois inférieure et jouit d'une meilleure factorisation.

| | Taille 4096       | Taille 4200       |
| ------------------ | ----------------- | ----------------- |
| Moyenne            | $8.862\mu\text{s}$           | $8.065\mu\text{s}$             |
| Médiane            | $8.677\mu\text{s}$             | $7.995\mu\text{s}$             |


<details>
  <summary>Je ne sais pas lire ça, mais dans un soucis d'exhaustivité, voici les algos utilisées pour 4096 et 4200, respectivement.</summary>
(dft-ct-dit/8
  (dftw-direct-8/28 "t1fv_8_avx")
  (dft-ct-dit/8
    (dftw-direct-8/56-x8 "t2fv_8_avx")
    (dft-vrank>=1-x8/1
      (dft-direct-64-x8 "n2fv_64_avx"))))

(dft-ct-dit/20
  (dftw-direct-20/76 "t1fv_20_avx")
  (dft-ct-dit/15
    (dftw-direct-15/56-x20 "t1fv_15_avx")
    (dft-vrank>=1-x15/1
      (dft-direct-14-x20 "n2fv_14_avx"))))
</details>




<!--





## Section 2 : Objectifs
[Définition des objectifs ou des questions que l'article va aborder.]

## Section 3 : Méthodologie
[Explication des méthodes ou des approches utilisées.]

## Section 4 : Résultats
[Présentation des résultats obtenus.]

## Section 5 : Discussion
[Analyse des résultats et discussion des implications.]

## Conclusion
[Résumé des points clés et éventuelles recommandations.]

## Ressources Additionnelles
[Liste de références, liens, ou ressources supplémentaires.]

---

**À propos de l'auteur**
[Bref paragraphe sur l'auteur et ses domaines d'expertise.]

**Contact**
[Coordonnées de l'auteur ou liens vers les profils sociaux.]
-->

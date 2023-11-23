# Quelle taille pour une FFT ?

## Introduction
Dans le cadre de mon projet [ATSAHSNA](https://github.com/simonArchipoff/ATSAHSNA), j'ai été conduit à m'interesser aux [transformée en ondelette continues(CWT)](https://fr.wikipedia.org/wiki/Ondelette).


## Section 1 : Contexte

Bien que le résultat soit très proche de ce qu'on obtient avec une [transformée de fourier à court terme(STFT)](https://fr.wikipedia.org/wiki/Transform%C3%A9e_de_Fourier_%C3%A0_court_terme), l'algorithme est très différent.
Pour une carte temps/fréquence de $t$ unités sur $n$ fréquences :
* La transformée de fourier à court terme nécessite $t$ transformée de fourier de taille $n$
* La transformée en ondelette continue nécessite $3*n$ transformée de fourier d'une taille $t$

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

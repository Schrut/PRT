# Projet de Réalisation Technique (PRT)
> _M1 IS, Spécialité Imagerie Numérique, Année 2017-2018_.

## Sujet n°8 : Stabilisation, géolocalisation précise et re-échantillonage spatial et temporel d'images de satellites météo géostationnaires.

Binôme :  
__Thibault HECKEL__   
__Florian GIMENEZ__

## Dépendances :
- [Python](https://docs.python.org/3/)
- [PyQt5](https://pypi.python.org/pypi/PyQt5)
- [numpy](https://pypi.python.org/pypi/numpy/1.14.0)
- [opencv-python](https://pypi.python.org/pypi/opencv-python)
- [osmapi](https://pypi.python.org/pypi/osmapi)
- [matplotlib]

https://pypi.python.org/pypi/tifffile
https://pypi.python.org/pypi/qimage2ndarray/1.6

## Lancer le programme :
```bash
cd /src && python3 main.py
```
---
### Erreurs à la compilation :
- > import _tkinter # If this fails your Python may not be configured for Tk   

Installer le paquêt tk manquant ([archWiki](https://www.archlinux.org/packages/extra/x86_64/tk/))

- > ValueError: Only know how to handle extensions: ['png']; with Pillow installed matplotlib can handle more images

Installer le paquêt manquant pillow
```bash
# pip install pillow
```
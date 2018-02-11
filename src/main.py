"""
Main module

Tout ce qui est dans ces guillemets s'appelle une docstring.

Pour VisualStudioCode:
installer `pylint`:
    # pip install pylint
    (le # ici c'est pour sudo (( enfin à faire en admin )), une convention, et oui une de plus, sinon ce serait $)
"""
#!/usr/bin/python3

#
# Un très bon tuto qui permet de prendre
# en main très facilement la lib pyQt5
# http://zetcode.com/gui/pyqt5/firstprograms/
#


import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
)

# Ici la classe NewWindow hérite de QWidget
# C'est-à-dire qu'elle pourra utiliser toutes
# les fonctions de la classe QWidget
# Par exemple, `.show()`
class NewWindow(QWidget):
    """
    A New Window class
    """

    # Un commentaire python
    # 
    # __init__ ici représente le constructeur de la classe
    # `NewWindow`
    # Il sera appelé automatiquement quand on appelera la fonction
    # `NewWindow()` qui créera donc une nouvelle instance
    # de NewWindow.
    #
    # le mot clé self, fait bien évidement référence
    # à l'instance de la classe elle même.
    # On cherche à construire ici un objet.
    #
    # On remarque d'ailleurs que le constructeur ne prend pas d'arguments
    def __init__(self):
        super().__init__()
        self.build()

    def build(self):
        """
        init UI of NewWindow
        """
        # Création d'un bouton qui permet de quitter l'application
        btn = QPushButton("Button", self)
        # On "connect" notre boutton à une action lorsqu'il est dans l'état "clicked"
        btn.clicked.connect(QApplication.instance().quit)
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Main test")
        self.show()


def main():
    """
    Main function
    """
    app = QApplication(sys.argv)
    win = NewWindow()
    sys.exit(app.exec_())
    #ici on utilse exec_ avec un "underscore" car "exec" est déjà un mot clé du langage Python

if __name__ == "__main__":
    main()
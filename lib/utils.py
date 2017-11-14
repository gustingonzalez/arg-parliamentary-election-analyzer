# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Nombre: utils.py
- Descripción: Contiene funciones de utilidad:
    - cfg (function), ver docstring.
    - clearscreen (function), ver docstring.
    - makedirs (function), ver docstring.
- Autor: Agustín González.
- Modificado: 05/11/17.
"""

import os
from configparser import ConfigParser


def cfg():
    """Retorna configparser del script."""
    cparser = ConfigParser()
    cparser.read("settings.ini")
    return cparser


def clearscreen():
    """Limpia pantalla de forma estándar."""
    os.system('cls' if os.name == 'nt' else 'clear')


def makedirs(dir):
    """Crea el conjunto de directorios especificado, sólo si es necesario."""
    if not os.path.exists(dir):
        os.makedirs(dir)

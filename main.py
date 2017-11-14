#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Nombre: main.py
- Descripción: ejecuta el analizador de mesas de votación. Nota: es requisito
previo que exista la caché de response (WebCache). Para ello, antes de ejecutar
este archivo, se necesita haber ejecutado el script "requester.py".
- Autor: Agustín González.
- Modificado: 26/10/17
"""

import os
import sys
import traceback

from lib import utils
from lib.analyzer import VotingStation, VotingStationCollection


def main(args):
    """Punto de entrada."""

    utils.clearscreen()

    # Lectura de configuración
    cfg = utils.cfg()
    webcachedir = cfg["Dirs"]["WebCache"]

    # Rangos excluidos.
    cavoided_ranges = cfg["Statistics"]["AvoidedRanges"].split(",")
    avoided_ranges = []
    for srange in cavoided_ranges:
        splitted = srange.split("-")
        avoided_range = range(int(splitted[0]), int(splitted[1]))
        avoided_ranges.append(avoided_range)

    # Filenames.
    filenames = next(os.walk(webcachedir))[2]

    # Mesas de votación.
    voting_tables = []

    print("Analizando archivos...\n")

    # Si no existe directorio...
    if not os.path.exists(webcachedir):
        msg = "No se ha encontrado el directorio caché, por favor ejecute el "
        msg += "script 'request.py'."
        print(msg)
        exit(1)

    # Examinación de archivos.
    for filename in filenames:
        try:
            # Número de mesa de votación.
            vtnumber = int(filename.split("_")[1].replace(".htm", ""))

            # Análisis de exclusión de análisis.
            avoid = False
            for avoided_range in avoided_ranges:
                if vtnumber in avoided_range:
                    # Se continúa examinando el siguiente elemento.
                    continue

            # Si la mesa se debe excluir del análisis.
            if avoid:
                continue

            # Apertura de archivo.
            path = webcachedir + "/" + filename
            file = open(path)
            html = file.read()
            file.close()

            # Parsing y append.
            vtable = VotingStation(html)
            voting_tables.append(vtable)
        except:
            traceback.print_exc()

            msg = "Error al analiar el archivo {0}. Verifíquelo manualmente."
            print(msg.format(filename))
            input()

    # Analizador de mesas de votación.
    collection = VotingStationCollection(voting_tables)
    collection.print_analysis()
    collection.save_analysis()


# Entrada de aplicación.
if __name__ == "__main__":
    sys.exit(main(sys.argv))

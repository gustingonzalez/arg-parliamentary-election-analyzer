# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Nombre: requester.py
- Descripción: obtiene el conjunto de documentos html, según los parámetros de
la sección "Connection", para luego almacenarlos en el directorio (WebCache)
especificado en el archivo de configuración.
- Autor: Agustín González.
- Modificado: 05/11/17
"""

import os
import sys
import time
import http.client
from lib import utils



class VotingStationRange(object):
    """Rango de mesas de circuito."""

    def __init__(self, circuit, init, end):
        self.circuit = circuit
        self.init = init
        self.end = end


def parse_ranges(scircuits, sranges):
    """Realiza parseo de str de config de rangos a lista."""

    lcircuits = [x.strip() for x in scircuits.split(",")]
    lranges = [x.strip() for x in sranges.split(",")]

    if(len(lcircuits) != len(lranges)):
        exit("La cantidad de circuitos y de rangos no coincide.")

    # Lista de objetos.
    ranges = []

    # Recorrida de circuitos.
    for circuit in lcircuits:
        # Pop de ranges y split para obtención de subrangos.
        subranges = lranges.pop(0).split(" ")

        # Exploración de subrangos
        for subrange in subranges:
            splitted = subrange.split("-")
            init = int(splitted[0])
            end = int(splitted[1])

            # Creación de vtrange.
            vtrange = VotingStationRange(circuit, init, end)

            # Append a list.
            ranges.append(vtrange)

    return ranges


def build_url(url_path_format, province, district, circuit, vtnumber):
    """Realiza build de url en base a parámetros."""

    # Fill de circuit con "_" (len debe ser 5).
    tofillcircuit = 5 - len(circuit)
    filledcircuit = circuit + "_" * tofillcircuit

    # Armado de URL.
    url = url_path_format.format(province, district, circuit,
                                 vtnumber.zfill(5), filledcircuit)

    return url


def save(html, path):
    """Almacena html en path indicado."""
    fhtml = open(path, "w")
    fhtml.write(html)
    fhtml.close()


def main(args):
    utils.clearscreen()

    # Lectura de configuración
    cfg = utils.cfg()

    section = "Connection"
    # Host.
    host = cfg[section]["Host"]

    # URL.
    url_path_format = cfg[section]["URLPathFormat"]

    # Prov. number
    province = cfg[section]["Province"]

    # Distrito.
    district = cfg[section]["District"]

    # Rangos de mesa por circuito.
    vtranges = parse_ranges(cfg[section]["Circuits"],
                            cfg[section]["Ranges"])

    # Directorio.
    dir = cfg["Dirs"]["WebCache"]

    # Creación de directorio (si no existe no lo vuelve a crear.)
    utils.makedirs(dir)

    # Recorrida de rangos de mesa.
    for vtrange in vtranges:
        # Recorrida de mesas.
        for vtnumber in range(vtrange.init, vtrange.end+1):

            # 1. Verificación de existencia de path.
            print("Mesa {0} - ".format(vtnumber), end="")
            circuit = vtrange.circuit
            path = dir + "/" + str(circuit) + "_" + str(vtnumber) + ".htm"
            os.path.exists(dir)

            # Si existe el path.
            if os.path.exists(path):
                print("Ya existe en caché.")
                # No se realiza conexión.
                continue

            # 2. Request a host.
            connection = http.client.HTTPConnection(host, 80)
            connection.connect()

            url = build_url(url_path_format, province, district,
                            circuit, str(vtnumber))
            connection.request("GET", url)

            # 3. Get de response.
            print("Obteniendo: " + url)
            response = connection.getresponse()

            # 4. Verificación de status.
            if(response.status == 404):
                msg = "No existe response a partir de la mesa {0}."
                print(msg.format(vtnumber))
                input("Presione ENTER para continuar...")
                break

            # 5. HTML (se utiliza decode, ya que read retorna bytes).
            html = response.read().decode("utf-8")

            # 6. Save de html en path circuit_vtnumber
            save(html, path)

            # 7. Sleep para evitar posible baneo de IP.
            time.sleep(0.1)


# Entrada de aplicación.
if __name__ == "__main__":
    sys.exit(main(sys.argv))

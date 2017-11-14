#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Nombre: analyzer.py
- Descripción: contiene las clases necesarias para analizar las mesas de vota-
ción (nota: el término "mesa electoral" se ha traducido como "voting station",
de ahí el nombre de ciertas variables y clases):
    - StatisticsAnalyzer (class), ver docstring.
    - VotingStationStatus (class), ver docstring.
    - VotingCategories (class), ver docstring.
    - VotingStationInformation (class), ver docstring.
    - VotingStation (class), ver docstring.
    - VotingStationCollection (class), ver docstring.
- Autor: Agustín González.
- Modificado: 05/11/17.
"""

from bs4 import BeautifulSoup
from lib import utils


class StatisticsAnalyzer:
    """Permite los siguientes análisis estadísticos en base a una muestra (lista):
    - Medidas de tendencia central:
        - Media: promedio de lista.
        - Mediana: elemento central de lista.
    - Limites para análisis de valores atípicos:
        - Límite inferior: valores de la lista por debajo de este deberán con-
        siderarse atípicos.
        - Límite superior: valores de la lista por encima de este deberán con-
        siderarse atípicos.

    Respecto a los límites inferior y superior:
    - El límite inferior se calcula como: q1 - iqrpond * qrange.
    - El límite superior se calcula como: q3 + iqrpond * qrange
    q1 y q3 refieren el primer y tercer cuartil de la lista, respectivamente.
    qrange es el rango intercuartil (es decir, q3-q1).
    iqrpond es la ponderación dada a qrange. Los valores recomendados, para
    hallar los límites son:
    - 1.5, para lím. interiores, lo que permite detectar val. atípicos leves.
    - 3, para lím. exteriores, lo que permite detectar val. atípicos extremos.
    Para este caso en particular, recomiendo (luego de algunas pruebas) un
    valor de 1.0, pues valores iguales o superiores a 1.5 no detectan anomalías
    que resultan interesantes a los efectos del análisis de las mesas de vota-
    ción. El uso del valor 1.0 intenta reducir los límites, para "suavizar" la
    búsqueda de valores anómalos."""

    def __init__(self, lst, iqr_ponderation=1.00):
        """Inicializa clase.

        Args:
            lst (list): lista a analizar.
            iqr_ponderation (float): suavizador de IQR (rango intercuartilíco).
            Establecido, por omisión, en 1.0."""
        lst.sort()
        self.__lst = lst

        # Ponderación de rango intercuartil.
        self.__iqr_ponderation = iqr_ponderation

        # Cálculo de cuartiles.
        self.__calculate_quartiles()

    def average(self):
        """Retorna la media de los valores de la lista.

        Returns:
            average (int/float): de valores de la lista.
        """

        total = 0
        for item in self.__lst:
            total += item
        return total/len(self.__lst)

    def median(self, lst=[]):
        """Retorna la mediana de una lista pasada por parámetro.

        Args:
            lst (list): Lista de la que se requiere calcular la mediana. Por
            omisión, el parámetro se establecerá en la lista con la que fue
            instanciada la clase.

        Returns:
            median (int/float): mediana de los valores de lista."""
        if not lst:
            lst = self.__lst
        lst.sort()

        # Si la lista es vacía.
        if not lst:
            return 0
        # Si la lista tiene un sólo valor.
        elif len(lst) == 1:
            return lst[0]
        # Si la lista tiene sólo dos valores.
        elif len(lst) == 2:
            return lst[0]/lst[1]

        # En cualquier otro caso:
        # Se utiliza redondeo hacia arriba, para casos con listas con cantidad
        # impar de elementos. Ej: dada una lista de 3 elementos, 3/2 es 1.5.
        # Luego, redondeando, se obtiene 2, la mediana de la lista.
        middle = round((len(lst)/2))-1

        # Si la lista tiene una cantidad par de valores...
        if len(lst) % 2 == 0:
            # Mediana = (dos valores centrales)/2
            return (lst[middle] + lst[(middle)+1])/2

        # Si la lista tiene una cantidad impar de valores.
        return lst[middle]

    def __calculate_quartiles(self):
        """Realiza cálculo de cuartiles."""
        # Cálculo de segundo cuartil.
        self.__q2 = self.median(self.__lst)

        # Sublistas según q2.
        lstq1 = [x for x in self.__lst if x < self.__q2]
        lstq2 = [x for x in self.__lst if x > self.__q2]

        # Cáculo de primer cuartil.
        self.__q1 = self.median(lstq1)

        # Cálculo de tercer cuartil.
        self.__q3 = self.median(lstq2)

        # Rango intercuartil.
        self.__qrange = self.__q3 - self.__q1

    def lower_limit(self):
        """Retorna límite inferior.

        Returns:
            lower_limit: elementos de la lista por debajo de este valor deberán
            considerarse atípicos.
        ."""
        # En realidad se multiplica por 1.5
        return self.__q1 - self.__iqr_ponderation * self.__qrange

    def upper_limit(self):
        """Retorna límite superior.

        Returns:
            upper_limit: elementos de la lista por encima de este valor deberán
            considerarse atípicos.
        """
        return self.__q3 + self.__iqr_ponderation * self.__qrange


class VotingStationStatus(object):
    """Estados (anomalías) posibles en las mesas de votación."""

    NotComputed = "Acta no computada. Estado: {0}"
    ImpugnedVotes = "Más de {0} votos impugnados. Cantidad: {1}"
    UpperOfAvg = "{0} para {1} por encima de la media. Valor de referencia:" \
                 " {2}, valor de la mesa: {3}"
    LowerOfAvg = "{0} para {1} por debajo de la media. Valor de referencia:"  \
                 " {2}, valor de la mesa: {3}"


class VotingCategories(object):
    """Votos por categoría."""

    def __init__(self):
        # Votos a senador nacional.
        self.national_senator = 0

        # Votos a diputado nacional.
        self.national_deputy = 0

        # Votos a diputado provincial.
        self.provintial_deputy = 0

        # Votos a concejal y consejeros escolares.
        self.councilor = 0


class VotingStationInformation(object):
    """Información de mesa."""

    def __init__(self):
        # Circuito de votación
        self.circuit = ""

        # Número de mesa
        self.station_number = ""

        # Estado de mesa.
        self.status = ""

        # Observaciones (seteada durante análisis en VotingStationCollection).
        self.remarks = []


class VotingStation(object):
    """Mesa de votación."""

    # String que indica estado de mesa 'grabada' en sistema.
    status_ok = "grabada"

    def __init__(self, html):
        """Inicializa mesa de votación con los datos del html.

        Args:
            html (string): página html de mesa de votación con el formato de
            las de resultados.gob.ar"""

        # Archivo de configuración a mem. (evita posteriores lect. de disco).
        self.__cfg = utils.cfg()

        # Diccionario de votos (tipos de voto y partidos políticos).
        self.votes = {}

        # Parser html.
        html_parser = BeautifulSoup(html, "lxml")

        # Tablas parseadas de html (son 4).
        self.__tables = html_parser.findAll("table")

        # Parseo de información general.
        self.__parse_information()

        # Si la mesa fue grabada...
        if self.information.status.lower() == VotingStation.status_ok:
            # Parseo de otros votos.
            self.__parse_other_votes()

            # Parseo de votos impugnados.
            self.__parse_impugned_votes()

            # Parseo de votos a partidos.
            self.__parse_political_parties_votes()

    def __parseHTMLtable(self, html_table):
        """Parsea tabla HTML a tabla leíble en python.

        Args:
            html_table (string), tabla de votación html.

        Returns:
            table (list[list]), tabla parseada."""

        table = []
        i = 0
        for row in html_table.findAll("tr"):
            columns = row.findAll("td")
            table.append([])
            for column in columns:
                table[i].append(column.getText().rstrip())
            i += 1

        return table

    def __parse_vote_type(self, table_index, vtype_index):
        """Parsea tipo de voto (a partido político, nulo, en blanco, etc) de
        una tabla y lo asigna a la categoría adecuada (senador, diputado, etc).

        Args:
            table_index (int): índice de tabla a parsear.
            vtype_index (int): índice de tipo de voto a parsear.

        Return:
            categories (VotingCategories): cantidad de votos por categoría.
        """

        categories = VotingCategories()

        parsed = self.__parseHTMLtable(self.__tables[table_index])

        ns = parsed[vtype_index][0]
        categories.national_senator = int(ns) if ns != "" else None

        nd = parsed[vtype_index][1]
        categories.national_deputy = int(nd) if nd != "" else None

        ps = parsed[vtype_index][2]
        categories.provintial_deputy = int(ps) if ps != "" else None

        co = parsed[vtype_index][3]
        categories.councilor = int(co) if co != "" else None

        return categories

    def __parse_information(self):
        """Parsea información general de la mesa (tabla 1 de html)."""

        parsed = self.__parseHTMLtable(self.__tables[0])

        info = VotingStationInformation()
        info.section = parsed[1][0].strip()
        info.circuit = parsed[2][0].strip()
        info.station_number = parsed[3][0].strip()
        info.status = parsed[4][0].strip().lower()

        self.information = info

    def __parse_other_votes(self):
        """Parsea votos nulos, en blanco y recurridos (tabla 2 de html)."""

        self.votes["null"] = self.__parse_vote_type(1, 1)
        self.votes["blank"] = self.__parse_vote_type(1, 2)
        self.votes["appealed"] = self.__parse_vote_type(1, 3)

    def __parse_impugned_votes(self):
        """Parsea votos impugnados (tabla 3 de html)."""

        parsed = self.__tables[2].findAll("td")[0]
        self.impugned_votes = int(parsed.getText())

    def __parse_political_parties_votes(self):
        """Parsea votos de partidos políticos (tabla 4 de html). El orden de los
        partidos políticos se establece según orden de aparición en la opción
        Keys, sección "PoliticalParties" del archivo de configuración."""

        # Lectura de configuración
        cfg = self.__cfg
        political_parties = cfg["PoliticalParties"]["Keys"].split(",")

        # Index en tabla de partido político
        index = 1

        # Asignación de votos de la sección a partido político.
        for pp in political_parties:
            self.votes[pp.strip()] = self.__parse_vote_type(3, index)
            # Incremento de identificador.
            index += 1


class VotingStationCollection:
    """Colección que agrupa varias mesas de votación (VotingStation) con el
    fin de realizar los análisis pertinentes."""

    def __init__(self, vstations):
        """Inicializa colección.

        Args:
            vstations (list): listado de mesas de votación.
        """

        # Mesas de votación
        self.__vstations = vstations

        # Mesas observadas.
        self.__remarked_vstations = []

        # Diccionario de categorías (equivalente con enum VotingCategories).
        self.__categories = {"national_senator": "Senador nacional",
                             "national_deputy": "Diputado nacional",
                             "provintial_deputy": "Dipuado provincial",
                             "councilor": "Concejal"}
        # Tipos de voto.
        self.__vote_types = {"blank": "Votos en blanco",
                             "null": "Votos nulos"}

        # Actualización de tipos de voto (append de partidos políticos).
        self.__update_vote_types()

        # Circuitos de votación
        self.__load_circuits()

        # Carga de configuración a memoria.
        self.__load_cfg()

        # Análisis.
        self.__analize()

    def __update_vote_types(self):
        """Actualiza los tipos de voto, agregando los partidos políticos
        especificados en el archivo de configuración."""
        cfg = utils.cfg()

        sPoliticalParties = "PoliticalParties"

        keys = cfg[sPoliticalParties]["Keys"].split(",")
        values = cfg[sPoliticalParties]["Values"].split(",")

        if len(keys) != len(values):
            msg = "La cantidad de keys y values de los partidos políticos \
            especificados en el archivo de configuración no es la misma."
            print(msg)
            exit(1)

        for i in range(0, len(keys)):
            # Saneamiento de keys y values
            keys[i] = keys[i].strip()
            values[i] = values[i].strip()

            # Agregación de key, value de partidos políticos a tipos de voto.
            self.__vote_types[keys[i]] = "Votos de " + values[i]

    def __load_circuits(self):
        """Carga los circuitos de votación especificados en la config."""
        lst = []
        for vs in self.__vstations:
            if vs.information.circuit not in lst:
                lst.append(vs.information.circuit)

        self.__circuits = lst

    def __load_cfg(self):
        """Carga configuración de tipos de votos de los que se deberá realizar
        análisis de cota inferior y superior, y aquellas categorías que se
        deberán exluir del análisis. También carga la ponderancia del multipli-
        cador para cada tipo de voto."""
        cfg = utils.cfg()

        # Load de tipos de votos a analizar (cota inferior y superior) y de
        # categorías a excluir de análisis.
        section = "Statistics"

        optionupper = cfg[section]["VoteTypesUpperCheck"]
        optionlower = cfg[section]["VoteTypesLowerCheck"]
        optionavoid = cfg[section]["AvoidedCategories"]

        self.__st_upper_check = [x.strip() for x in optionupper.split(",")]
        self.__st_lower_check = [x.strip() for x in optionlower.split(",")]
        self.__st_avoid_check = [x.strip() for x in optionavoid.split(",")]
        self.__st_max_impugned = int(cfg[section]["ImpugnedVotesAdmitted"])

        # Ponderación de rango intercuartil a la hora de analizar valores
        # atípicos.
        self.__iqr_ponderation = float(cfg[section]["IqrPonderation"])

    def __get_by_circuit(self, circuit, vstations=[]):
        """Obtiene, de la lista de mesas especificada, aquellas del circuito indicado.

        Args:
            circuit (string): circuito a recuperar.
            vstations (list): lista de mesas en las que realizar la búsqueda.
            En caso de no especificarse, se utiliza la de la colección.

        Returns:
            lst (list): mesas de votación del circuito indicado."""

        if len(vstations) == 0:
            vstations = self.__vstations

        lst = []

        for vs in vstations:
            if vs.information.circuit == circuit:
                lst.append(vs)

        return lst

    def __get_circuit_statistics(self, circuit, vtype, vcategory):
        """Obtiene estadísticas del circuito indicado, para el tipo de voto y
        categoría especificados.

        Args:
            circuit (string): circuito a analizar.
            vtype (string): tipo de voto (blanco, nulo, etc).
            vcategory (string): categoría (senador, diputado, etc)

        Returns:
            statistics (StatisticsAnalyzer): estadísticas del circuito."""

        vstations = self.__get_by_circuit(circuit)
        lst = []

        for vs in vstations:
            if(vs.information.status.lower() == "grabada"):
                categories = vs.votes[vtype]

                # Obtención de atributo según categoría.
                count = getattr(categories, vcategory)

                # Si hay votos.
                if(count is not None):
                    lst.append(count)

        return StatisticsAnalyzer(lst, self.__iqr_ponderation)

    def __verify_status(self, vstation):
        """Verifica el estado de una mesa de votación.
        Args:
            vstation (VotingStation): mesa de votación a analizar.

        Returns:
            remark (string): observación en caso de que la mesa no haya sido
            cargada. Si no hay observaciones se retorna vacío.
        """
        remark = ""
        # Si acta no fue grabada...
        if vstation.information.status.lower() != VotingStation.status_ok:
            status = vstation.information.status
            remark = VotingStationStatus.NotComputed.format(status)

        return remark

    def __verify_impugned(self, vstation):
        """Verifica los votos impugnados de una mesa de votación.
        Args:
            vstation (VotingStation): mesa de votación a analizar.

        Returns:
            remark (string): observación en caso de que la mesa no haya sido
            cargada. Si no hay observaciones, se retorna vacío."""
        remark = ""

        # Si se supera la cantidad máxima de votos impugnados admitidos.
        count = vstation.impugned_votes
        max = self.__st_max_impugned
        if count > max:
            remark = VotingStationStatus.ImpugnedVotes.format(max, count)
        return remark

    def __verify_deviation(self, circuit, vcount, vtype, vcategory):
        """Verifica si los votos de la mesa pasada por parámetro son menores/
        superiores a los límites inferior/superior. Nota: la verificación
        sólo se realiza si el tipo de voto o partido político se ha especifica-
        do en las opciones "VoteTypesUpperCheck" o "VoteTypesLowerCheck"
        (sección Statistics) del archivo de configuración.

        Args:
            circuit (string): circuito al que corresponde el conteo.
            vcount (int): cantidad de votos para el tipo de voto y categoría.
            vtype (string): tipo de voto.
            vcategory (string): tipo de categoría.

        Returns:
            remarks (list): listado de observaciones."""

        # Valores estadísticos del circuito.
        statistics = self.__get_circuit_statistics(circuit, vtype, vcategory)

        # Tipos de votos a chequear.
        tocheck = []

        # Comentarios.
        remarks = []

        # Verificación en límites inferior (i=0) y superior (i=1)
        for i in range(0, 2):
            # Indica si los val. de la mesa se encuentran en los límites.
            in_bound = True

            # Observación.
            remark = ""

            if i == 0:
                # lower limit check.
                # Obtención de elementos a chequear.
                tocheck = self.__st_lower_check

                # Si la cantidad de votos es menor a la esperada.
                if vcount < statistics.lower_limit():
                    in_bound = False

                    # Observación establecida en lower.
                    remark = VotingStationStatus.LowerOfAvg

            else:
                # upper limit check.
                # Obtención de elementos a chequear.
                tocheck = self.__st_upper_check

                # Si la cantidad de votos supera la esperada.
                if vcount > statistics.upper_limit():
                    in_bound = False
                    # Observación. establecido en upper.
                    remark = VotingStationStatus.UpperOfAvg

            # Si está en los límites...
            if in_bound:
                # Continuación con el siguiente item.
                continue

            # Si no está en los límites y se debe chequear...
            elif vtype in tocheck:
                # Formateo de comentario.
                remark = remark.format(self.__vote_types[vtype],
                                       self.__categories[vcategory],
                                       round(statistics.average()), vcount)
                remarks.append(remark)

        return remarks

    def __verify_statistics(self, circuit, vstation):
        """Verifica estadísticas de la mesa de votación pasada por parámetro.

        Args:
            circuit (string): circuito de la mesa de votación.
            vstation (VotingStation): mesa de votación.

        Returns:
            remarks (list): listado de observaciones."""

        remarks = []

        for vtype in self.__vote_types.keys():
            for vcategory in self.__categories.keys():

                # Si la mesa se debe evitar del análisis.
                if vcategory in self.__st_avoid_check:
                    continue

                # Obtención de categorías de tipo de voto.
                category_votes = vstation.votes[vtype]

                # Obtención de conteo de la categoría específica.
                vcount = getattr(category_votes, vcategory)

                # Si el conteo es nulo.
                if vcount is None:
                    continue

                # Add de comentarios de categoría analizada.
                cat_remarks = self.__verify_deviation(circuit, vcount,
                                                      vtype, vcategory)

                if len(cat_remarks) > 0:
                    remarks.extend(cat_remarks)

        return remarks

    def __analize(self):
        """Realiza análisis de la colección de mesas de votación."""

        # Análisis por circuito.
        for circuit in self.__circuits:
            # Obtención de votos de circuito.
            vstations = self.__get_by_circuit(circuit)

            # Análisis de mesas de votación.
            for vstation in vstations:
                print("Analizando", vstation.information.station_number)

                # Análisis de estado de la mesa.
                remark = self.__verify_status(vstation)

                if remark:
                    vstation.information.remarks.append(remark)

                # Si no hay observaciones (estado ok)...
                if not remark:
                    # Análisis de votos impugnados.
                    remark = self.__verify_impugned(vstation)

                    if(remark):
                        vstation.information.remarks.append(remark)

                    # Análisis estadístico de circuito.
                    remarks = self.__verify_statistics(circuit, vstation)

                    if len(remarks) > 0:
                        vstation.information.remarks.extend(remarks)

                # Si hay observaciones...
                if len(vstation.information.remarks) > 0:
                    self.__remarked_vstations.append(vstation)

    def save_analysis(self):
        """Almacena, en el directorio especificado en el archivo de configuraci-
        ón, el análisis resultante."""

        # Obtención de configuración.
        cfg = utils.cfg()
        dir = cfg["Dirs"]["Statistics"]
        utils.makedirs(dir)

        # Print en directorio.
        self.print_analysis(dir)

    def print_analysis(self, dir=""):
        """Imprime en pantalla (o en un directorio) el análisis resultante.

        Args:
            dir (string): directorio de salida (opcional). Si es vacío, la im-
            presión se realiza en pantalla."""

        # Archivo de salida (outputfile).
        ofile = None

        # Evaluación por circuitos.
        for circuit in self.__circuits:

            # Establecimiento de un output file por circuito.
            if dir != "":
                ofile = open(dir + "/" + circuit + ".txt", "w")

            # Filtro por circuito.
            filtered = self.__get_by_circuit(circuit,
                                             self.__remarked_vstations)

            # Sorted.
            ordered = sorted(filtered, key=lambda x:
                             int(x.information.station_number))

            # Impresión de mesas de votación con observaciones.
            for vs in ordered:
                print("Datos de mesa:", file=ofile)
                print("- Circuito:", vs.information.circuit, file=ofile)
                print("- Sección:", vs.information.section, file=ofile)
                print("- Mesa:", vs.information.station_number, file=ofile)
                print("- Observaciones:", file=ofile)

                for remark in vs.information.remarks:
                    print("  - " + remark, file=ofile)

                # Pretty print ;)
                print("", file=ofile)

            # Impresión de resumen del circuito.
            msg = "Mesas con observaciones (circuito {0}): {1}\n"
            print(msg.format(circuit, len(filtered)), file=ofile)

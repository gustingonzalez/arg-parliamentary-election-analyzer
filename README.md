# Analizador de elecciones legislativas (Argentinian parliamentary election analyzer)
El repositorio arg-parliamentary-election-analyzer, permite el análisis de los resultados de las elecciones legislativas de Argentina (2017).

# Motivación
Luego de las **elecciones legislativas** del 22 de octubre del 2017, junto a unos compañeros, decidimos buscar anomalías en los telegramas de la ciudad de José C. Paz, desde la web [resultados.gob.ar](http://resultados.gob.ar). A decir verdad, personalmente, no esperaba encontrar muchas irregularidades. Sin embargo, a medida que los revisábamos, nos encontrábamos con números cada vez más extraños. A pesar de esta curiosidad, el hecho de revisar una por una las mesas, se volvía un tanto tedioso y aburrido conforme pasaban los minutos por lo que, al final, decidí hacer algo mucho más divertido e interesante: un *pequeño aplicativo* que lo hiciera por nosotros y que, además, otorgue un análisis mucho más objetivo.

# Funcionamiento
De forma breve, el aplicativo funciona de la siguiente manera:
- Un **requester** (solicitante) descarga los telegramas especificados desde la web [resultados.gob.ar](http://resultados.gob.ar).
- Un **analizador**, analiza los datos cacheados por el requester y remarca (observa) aquellas mesas que presentan anomalías.

## Método de análisis
Por cada mesa:
1. En primera instancia se verifica si, según la web, la mesa ha **sido computada**. En caso afirmativo, se continúa con el paso 2, de otro modo, se observa la mesa, y se verifica la siguiente.
2. Si la mesa fue computada, se realiza la verificación de **votos impugnados** por encima del valor especificado en la configuración.
3. Finalmente, se buscan anomalías en los valores de los **votos en blanco**, **nulos** y a **partidos políticos** por cada categoría (senador, diputado nacional, diputado provincial y concejal) de la mesa, mediante [análisis de cuartiles](https://es.wikipedia.org/wiki/Cuartil). Los límites inferior y superior se calculan por circuito y categoría. Por ejemplo, por defecto, en el caso de los votos en blanco, se verifica si estos pasan el límite superior (aunque también es posible verificar si son menores al límite inferior). Para los partidos políticos se sigue la misma metodología.

### Análisis de cuartiles
Dada una muestra (lista de votos para una categoría de un circuito determinado), el límite inferior y superior se calculan de la siguiente manera:
- **Límite inferior**: ![q1-iqrpond*qrange](https://latex.codecogs.com/gif.latex?Q_%7B1%7D%20-%20iqrpond%20*%20qrange)
- **Límite superior**: ![q3+iqrpond*qrange](https://latex.codecogs.com/gif.latex?Q_%7B3%7D%20&plus;%20iqrpond%20*%20qrange)

#### Explicación
- ![q1](https://latex.codecogs.com/gif.latex?Q_%7B1%7D) y ![q3](https://latex.codecogs.com/gif.latex?Q_%7B3%7D) refieren, respectivamente, al **primer** y **tercer cuartil** de una muestra dada. Siendo ![m](https://latex.codecogs.com/gif.latex?m) la **mediana** (elemento central) de la muestra, la variable ![q1](https://latex.codecogs.com/gif.latex?Q_%7B1%7D) queda definida como la mediana de la lista conformada por los valores ubicados a la izquierda de ![m](https://latex.codecogs.com/gif.latex?m) y ![q3](https://latex.codecogs.com/gif.latex?Q_%7B3%7D) por la mediana de la lista definida por los valores ubicados a la derecha de ![m](https://latex.codecogs.com/gif.latex?m).
- ![qrange](https://latex.codecogs.com/gif.latex?qrange), el **rango intercuartil**, se define como: ![q3-q1](https://latex.codecogs.com/gif.latex?Q_%7B3%7D%20-%20Q_%7B1%7D).
- ![iqrpond](https://latex.codecogs.com/gif.latex?iqrpond) es la **ponderación** dada a ![qrange](https://latex.codecogs.com/gif.latex?qrange). Los valores recomendados (estadísticamente), para hallar los límites son:
    - 1.5, para **límites interiores**, lo que permite detectar **valores atípicos leves**.
    - 3, para **límites exteriores**, lo que permite detectar **valores atípicos extremos**.

> A pesar de la recomendación “estadística” para ![qrange](https://latex.codecogs.com/gif.latex?qrange), en este caso en concreto, recomiendo (luego de algunas pruebas) un valor de 1.0 ya que, valores iguales o superiores a 1.5, no detectan anomalías interesantes a los efectos del análisis de las mesas de votación. El uso del valor 1.0 "suaviza" la búsqueda de valores anómalos (de todas formas, esto es configurable).

#### Ejemplo
Suponiendo que, en un circuito dado, para la categoría de concejales de un partido político determinado, se tiene la lista de votos ![P](https://latex.codecogs.com/gif.latex?P) = [40, 41, 70, 41, 20], donde cada ![xEP](https://latex.codecogs.com/gif.latex?x%5Cepsilon%20P) corresponde a la cantidad de votos de cada mesa del circuito, en primera instancia, se ordena la lista por lo que, entonces ![P](https://latex.codecogs.com/gif.latex?P) = [10, 39, 40, 41, 41, 45, 70]. Luego, ![q2](https://latex.codecogs.com/gif.latex?Q_%7B2%7D) (la mediana de ![P](https://latex.codecogs.com/gif.latex?P)) está dada por el elemento “central”, en este caso 41. Tomando como base esta variable, es posible dividir ![P](https://latex.codecogs.com/gif.latex?P) en 2:
- ![P1](https://latex.codecogs.com/gif.latex?P_%7B1%7D) = [10, 39, 40], los elementos ubicados a la izquierda de ![q2](https://latex.codecogs.com/gif.latex?Q_%7B2%7D).
- ![P3](https://latex.codecogs.com/gif.latex?P_%7B3%7D) = [41, 45, 70], los elementos ubicados a la derecha de ![q2](https://latex.codecogs.com/gif.latex?Q_%7B2%7D).

Luego, ![q1](https://latex.codecogs.com/gif.latex?Q_%7B1%7D) queda definida como la mediana de ![P1](https://latex.codecogs.com/gif.latex?P_%7B1%7D), y ![q3](https://latex.codecogs.com/gif.latex?Q_%7B3%7D) como la mediana de ![P3](https://latex.codecogs.com/gif.latex?P_%7B3%7D), para el caso:
- ![q1](https://latex.codecogs.com/gif.latex?Q_%7B1%7D) = 39
- ![q3](https://latex.codecogs.com/gif.latex?Q_%7B3%7D) = 45

Por su parte, la variable ![qrange](https://latex.codecogs.com/gif.latex?qrange) queda definida por 45-39 (![q3-q1](https://latex.codecogs.com/gif.latex?Q_%7B3%7D-Q_%7B1%7D)), es decir, ![qrange](https://latex.codecogs.com/gif.latex?qrange)=6. Luego, teniendo en cuenta que:
- El límite inferior se calcula como: ![q1-iqrpond*qrange](https://latex.codecogs.com/gif.latex?Q_%7B1%7D%20-%20iqrpond%20*%20qrange)
- El límite superior se calcula como: ![q3+iqrpond*qrange](https://latex.codecogs.com/gif.latex?Q_%7B3%7D%20&plus;%20iqrpond%20*%20qrange)

Se realiza el reemplazo en las fórmulas de límite inferior y superior y, suponiendo a ![iqrpond](https://latex.codecogs.com/gif.latex?iqrpond)=1.0, se tiene que:
- **Límite inferior** = 39-1*6 = 33
- **Límite superior** = 45+1*6 = 51

Finalmente, computados los límites inferior y superior, se puede decir que, de la lista ![P](https://latex.codecogs.com/gif.latex?P), el valor 10 (que es menor al límite inferior) y el valor 70 (que es mayor al límite superior), son valores atípicos para ese circuito dado, por tanto las correspondientes mesas serán observadas.

# Requerimientos previos
[Python3](https://www.python.org/downloads/): Python versión 3
```
sudo apt-get install python3
```
[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): BeautifulSoup versión 4
```
pip3 install beautifulsoup4
```

# Configuración previa (settings.ini)
En el archivo **settings.ini** se define la configuración del aplicativo. Tanto para la especificación del archivo de configuración, como para su lectura, se utiliza la metodología acorde para la librería [ConfigParser](https://docs.python.org/2/library/configparser.html).

## Sección Connection
La sección **Connection** refiere a los datos que utilizará el requester, y consta de las siguientes opciones:
- **Host**, por defecto “resultados.gob.ar”, indica el servidor al que se harán los requests (*se recomienda no alterar su valor*).

- **URLPathFormat**, por defecto “/99/resu/content/telegramas/{0}/{1}/{2}/{0}{1}{4}{3}.htm”, indica el formato de url (*al igual que con Host, se recomienda no alterar su valor*). Por otra parte, el valor {0} dentro del string corresponde a la provincia (ver item *Province*), el valor {1} al distrito (ver item *District*), el valor {2} al circuito (ver item *Circuit*), el valor {3} al número de mesa de votación de la que se requiere conocer los datos y el valor {4}, también al circuito, pero con un fill necesario para la url (de 5). Por ejemplo, si se analiza la provincia 2, distrito 129, circuito 0398, mesa 1, la URL queda definida como: [/99/resu/content/telegramas/02/129/0398/021290398_00001.htm](http://resultados.gob.ar/99/resu/content/telegramas/02/129/0398/021290398_00001.htm) (lo que, en tiempo de ejecución, se concatena al host).

- **Province**, establecido por defecto en "02" (Buenos Aires), indica la provincia a la que corresponde el análisis. Este dato debe extraerse (habiendo ingresado previamente a la [web de consulta de telegramas](http://resultados.gob.ar/99/resu/content/telegramas/Itelegramas.htm)), del número ubicado a la izquierda del nombre de la provincia (nota: el número debe transcribirse "tal cual", inclusive con los ceros delanteros):

   ![provinces](https://user-images.githubusercontent.com/21322277/32806466-6e8d374a-c96b-11e7-9d90-5944cb2591ab.png)

- **District**, establecido en "129" (José C. Paz), indica el distrito. Este dato se debe obtener desde la siguiente tabla (con los ceros a la izquierda correspondientes, si así fuera), luego de haber seleccionado la provincia:

   ![districts](https://user-images.githubusercontent.com/21322277/32806465-6e40db34-c96b-11e7-8684-7f64ca0f66c3.png)

- **Circuits**: indica los circuitos a analizar, separados por coma. Para el distrito del ejemplo (129), los circuitos se deberían denotar de la forma: "0398, 0398A, 0398B" (nota: los ceros ubicados a la izquierda también deben incluirse):

   ![circuits](https://user-images.githubusercontent.com/21322277/32806464-6df54ef8-c96b-11e7-9cb2-35faba6957c0.png)

- **Ranges**: indica los rangos a analizar para cada circuito, separados por coma. La configuración deberá establecerse según los números de mesa disponibles para el circuito. Cada conjunto de rangos (separados por un espacio, en caso de corresponder a un mismo circuito) se deberá corresponder con el orden en el que se han indicado los circuitos (ver sección *Circuits*). Por ejemplo, teniendo en cuenta que los rangos 1-211 y 9001-9026 se corresponden con el circuito 0398, el 212-428 con el 0398A y el 429-603 con el 0398B, la configuración *Ranges* quedaría establecida de la forma: "1-211 9001-9026, 212-428, 429-603".

   ![ranges](https://user-images.githubusercontent.com/21322277/32806470-7037ebee-c96b-11e7-81be-9a5f617fa786.png)


## Sección Dirs
La sección **Dirs**, contiene las opciones correspondientes a los directorios de salida:
- **WebCache**, establecido por defecto en “output/response”, indica el directorio de salida de la caché web.
- **Statistics**, establecido por defecto en “output/statistics”, indica el directorio de salida del análisis.

## Sección PoliticalParties
La sección **PoliticalParties** contiene las opciones correspondientes a los partidos políticos analizados en el distrito. Por ejemplo, dada la url [resultados.gob.ar/99/resu/content/telegramas/02/129/0398/021290398_00001.htm](http://resultados.gob.ar/99/resu/content/telegramas/02/129/0398/021290398_00001.htm), se obtiene la siguiente tabla:

![table](https://user-images.githubusercontent.com/21322277/32806467-6ed49f7c-c96b-11e7-95bb-8d13459ce4b9.png)

Luego, los partidos políticos se deberían especificar teniendo en cuenta el mismo orden en el que aparecen en la tabla (cabe aclarar que el orden es igual para todo el distrito por lo que, con evaluar una única mesa, alcanza). Por ejemplo, para el caso, el orden sería: “*1PAIS*”, “*UNIDAD CIUDADANA*”, “*CAMBIEMOS BUENOS AIRES*”, “*FRENTE JUSTICIALISTA*” y “*FRENTE DE IZQUIERDA Y LOS TRABAJADORES*”. Respecto a las opciones de la sección:
- En el apartado **Keys**, se debe especificar el “identificador” de cada uno de los partidos políticos presentes en la tabla (los cuales pueden ser arbitrarios, siempre y cuando se tenga en cuenta el orden de aparición de cada uno, y se separen con coma). Estos identificadores son útiles en la sección *Statistics*, donde es posible especificar los partidos políticos de los que se requiere analizar votos por debajo/encima del límite inferior/superior. Para el caso dado, la configuración podría quedar definida como: "1pais, uc, cambiemos, fj, fit".
- En el apartado **Values**, se debe especificar el nombre de cada uno de los partidos políticos, también respetando el orden de la tabla (como en el caso anterior, la especificación puede ser arbitraria). Para este caso, los valores podrían establecerse en “1Pais, Unidad Ciudadana, Cambiemos, Frente Justicialista, FIT” por lo que, finalmente, la clave "1pais" se correspondería con el valor "1Pais", "uc" con "Unidad Ciudadana", "cambiemos" con "Cambiemos", "fj" con "Frente Justicialista" y "fit" con "FIT". Como dato obvio, la cantidad de keys y values debe coincidir. 

## Sección Statistics
La sección **Statistics**, permite especificar las opciones referentes al analizador:
- **IqrPonderation**, por defecto en "1.0", indica la ponderación del [IQR](https://es.wikipedia.org/wiki/Rango_intercuart%C3%ADlico) dada a la fórmula que permite calcular los límites inferior y superior (ver sección de *Funcionamiento*).
- **ImpugnedVotesAdmitted**, indica el máximo admitido de votos impugnados (por defecto en "2").
- **VoteTypesUpperCheck**, indica qué tipos de votos (separados por coma) se deberán tener en cuenta para el análisis de las cantidades que son mayores al límite superior. Los posibles valores son: blank, null y también los identificadores especificados en la opción **Keys** (sección **PoliticalParties**), para el caso, "1pais", "uc", "cambiemos", "fj" y "fit". Por defecto, se encuentra establecido en "blank, null, fit, 1pais, uc, cambiemos".
- **VoteTypesLowerCheck**, por defecto en “fit, cambiemos”, cumple la misma función que *VoteTypesUpperCheck*, pero para el caso del límite inferior.
- **AvoidedCategories**, por defecto en “national_senator, national_deputy, provintial_senator”, indica las categorías excluidas del análisis (separadas por coma). Los posibles valores son:
  - **national_senator**: senador nacional.
  - **national_deputy**: diputado nacional.
  - **provintial_deputy**: diputado provincial.
  - **councilor**: concejal y consejeros escolares.
- **AvoidedRanges**, indica los rangos de mesa excluidos del análisis (los cuales deben especificarse separados por coma). Para el caso dado, se ha especificado el valor "9001-9026".


# Ejecución

Una vez instalado Python, y habiendo especificado los circuitos y mesas a analizar (entre otras opciones, en el archivo de configuración), se deberá ejecutar (estando en el directorio donde se encuentran los scripts), el **requester**:
```
python3 requester.py
```
El requester descargará los archivos de cada mesa en el directorio “WebCache” especificado. Posterior a su ejecución, se deberá invocar el script **principal**:
```
python3 main.py
```
Con este comando, se analizarán los archivos (telegramas) cacheados. El **análisis** (un archivo de texto por cada circuito), se volcará en el directorio especificado en la opción “Statistics” del archivo de configuración.


# Descripción de scripts
**[/requester.py](/requester.py)**: obtiene el conjunto de documentos html, según los parámetros de la sección *Connection*, para luego almacenarlos en el directorio (WebCache) especificado en el archivo de configuración.

**[/main.py](/main.py)**: ejecuta el analizador de mesas de votación. Nota: es requisito previo que exista la caché de response (*WebCache*). Para ello, antes de ejecutar este script, se necesita haber ejecutado [/requester.py](/requester.py).

# Descripción de dependencias internas
**[/lib/analyzer.py](/lib/analyzer.py)**: contiene las clases necesarias para analizar las mesas de votación (nota: el término **mesa electoral** se ha traducido como **voting station**, de ahí el nombre de ciertas variables y clases):
- **StatisticsAnalyzer** (*class*), permite los siguientes análisis estadísticos en base a una muestra (lista):
    - *Medidas de tendencia central*:
        - *Media*: promedio de lista.
        - *Mediana*: elemento central de lista.
    - *Limites para análisis de valores atípicos*:
        - *Límite inferior*: valores de la lista por debajo de este deberán considerarse atípicos.
        - *Límite superior*: valores de la lista por encima de este deberán considerarse atípicos.
- **VotingStationStatus** (*class*), estados (anomalías) posibles en las mesas de votación.
- **VotingCategories** (*class*), votos por categoría (senador, diputado nacional, dipuado provincial, concejal).
- **VotingStationInformation** (*class*), información de mesa (circuito, número, estado y comentarios).
- **VotingStation** (*class*), mesa de votación: permite el parseo del html.
- **VotingStationCollection** (*class*), colección que agrupa varias mesas de votación (VotingStation) con el fin de realizar los análisis pertinentes.

**[/lib/utils.py](/lib/utils.py)**: contiene funciones de utilidad:
- **cfg** (*function*), retorna configparser del script.
- **clearscreen** (*function*), limpia pantalla de forma estándar.
- **makedirs** (*function*), crea el conjunto de directorios especificado, sólo si es necesario.

# Resultados
Teniendo en cuenta la configuración pre-establecida del archivo [/settings.ini](/settings.ini), el resultado luego de ejecutado el **requester**, se puede encontrar [aquí](https://www.dropbox.com/s/lxvmu6ocxbfhcnh/response.zip?dl=0), mientras que el del **analizador** [aquí](https://www.dropbox.com/s/j8n4u4yt1bi6na7/statistics.zip?dl=0).

# Autor
Agustín González

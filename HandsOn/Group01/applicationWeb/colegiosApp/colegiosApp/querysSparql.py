# Querys Sparql
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, XML
from rdflib.plugins.sparql import prepareQuery
import json

class Colegios:
    def __init__(self):
        self.tipoCentro = {'Todos': 1, 'Otros': 2, 'Educación Infantil': 'INFANTIL', 'Educación Primaria': 'PRIMARIA',
                           'Educación Secundaria': 'SECUNDARIA'}
        self.titCentro = {'Todos': 1, 'Privado': 'PRIVADO', 'Privado Concertado': 'PRIVADO CONCERTADO',
                          'Público': 'PÚBLICO', 'Público-Titularidad Privada': 'PÚBLICO-TITULARIDAD PRIVADA'}

    def nombreColegio(self, nombre):
        global auxDic
        g = rdflib.Graph()

        g.parse("../../rdf/output-with-links.nt")

        q = f"""
        PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX  cap: <http://www.colegiosapp.org/ontology#>
        PREFIX  dbo: <http://dbpedia.org/ontology#>
        PREFIX  owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?name ?tipoVia ?nomCalle ?numCalle ?x ?y ?wikidata ?municipio
            WHERE{{
            ?centro cap:hasAddress ?calle.
            ?calle cap:hasNameAddress ?nomCalle.
            ?calle cap:hasType ?tipoVia.
            ?calle cap:hasNumber ?numCalle.
            ?centro cap:xCoordinate ?x.
            ?centro cap:yCoordinate ?y.
            ?centro cap:nameSchool ?name.
            ?centro cap:ownMunicipality ?muni.
            ?muni owl:sameAs ?wikidata.
            ?centro cap:idSchool ?id.
            ?muni cap:hasNameMunicipality ?municipio.
               FILTER regex(?name , "{nombre}").
        }}  GROUP BY ?id ORDER BY ?name
        """
        gres = g.query(q)

        resultado = []
        for row in gres:
            auxDic = {'name': row[0],
                      'calle': row[1] + " " + row[2] + ", " + row[3],
                      'xCoord': float(row[4].toPython()),
                      'yCoord': float(row[5].toPython()),
                      'municipio': row[7]
                      }
            aux = row[6].replace("https://wikidata.org/entity/", "")
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

            sparql.setQuery(f"""
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            
            SELECT ?flag
                WHERE {{
                    wd:{aux} wdt:P41 ?flag
                }}
            """)
            try:
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                svg = results['results']['bindings'][0]['flag']['value']
                auxDic['svg'] = svg
                resultado.append(auxDic)
            except:
                print(Exception)
        return resultado

    def nombreColAvanzada(self, tipo, titularidad, municipio, codigoPostal, limite):
        tipoAux = self.tipoCentro.get(tipo)
        titAux = self.titCentro.get(titularidad)
        print(tipoAux, titAux, municipio, codigoPostal)

        g = rdflib.Graph()
        g.parse("../../rdf/output-with-links.nt")
        qtit = ""
        qtipo = ""
        qmuni = ""
        qpost = ""
        if tipoAux != 1 and tipoAux != 2:
            qtipo = f"""?centro cap:hasTypeSchool ?tipo
                        FILTER regex(?tipo , "{tipoAux}").
                        """
        elif tipoAux == 2:
            qtipo = f"""?centro cap:hasTypeSchool ?tipo
                        FILTER (!regex(?tipo , "INFANTIL")).
                        ?centro cap:hasTypeSchool ?tipo
                        FILTER (!regex(?tipo , "PRIMARIA")).
                        ?centro cap:hasTypeSchool ?tipo
                        FILTER (!regex(?tipo , "SECUNDARIA")).
                        """
        if titAux != 1:
            qtit = f"""?centro cap:ownership ?tit
                        FILTER (?tit = "{titAux}").
                        """
        if municipio != "":
            qmuni = f"""?muni cap:hasNameMunicipality ?nomMuni
                       FILTER regex(?nomMuni , "{municipio}").
                        """
        if codigoPostal != "":
            qpost = f"""?calle cap:hasPostalCode ?postal
                        FILTER (?postal = "{codigoPostal}").
                        """
        qfinal = f"""
                PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX  cap: <http://www.colegiosapp.org/ontology#>
                PREFIX  dbo: <http://dbpedia.org/ontology#>
                PREFIX  owl: <http://www.w3.org/2002/07/owl#>

                SELECT ?name ?tipoVia ?nomCalle ?numCalle ?x ?y
                    WHERE{{
                    ?centro cap:idSchool ?id.
                    ?centro cap:hasAddress ?calle.
                    ?calle cap:hasNameAddress ?nomCalle.
                    ?calle cap:hasType ?tipoVia.
                    ?calle cap:hasNumber ?numCalle.
                    ?centro cap:xCoordinate ?x.
                    ?centro cap:yCoordinate ?y.
                    ?centro cap:nameSchool ?name.
                    ?centro cap:ownMunicipality ?muni.
                    """ + qmuni + qpost + qtipo + qtit + f"""}}
                GROUP BY ?id ORDER BY ?name LIMIT {limite}
                """
        gres = g.query(qfinal)
        resultado = []
        for row in gres:
            auxDic = {'name': row[0],
                      'calle': row[1] + " " + row[2] + ", " + row[3],
                      'xCoord': float(row[4].toPython()),
                      'yCoord': float(row[5].toPython())
                      }
            resultado.append(auxDic)
        return resultado

    def numeroPoblacion(self, municipio, sexo, edMin, edMax):
        numPobl = 0
        nomMuni = ''
        result = self.buscarIntAux(edMin, edMax)
        arrMin = result[0]
        arrMax = result[1]
        qsexo = ""
        if sexo != "Ambos":
            qsexo = f"""?group cap:hasGender ?sexo
                        FILTER (?sexo = "{sexo}").
                        """
        for min, max in zip(arrMin, arrMax):
            g = rdflib.Graph()
            g.parse("../../rdf/output-with-links.nt")
            qfinal = f"""
                    PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
                    PREFIX  cap: <http://www.colegiosapp.org/ontology#>
                    PREFIX  dbo: <http://dbpedia.org/ontology#>
                    PREFIX  owl: <http://www.w3.org/2002/07/owl#>
                    
                    SELECT ?pobl ?nameMuni
                        WHERE{{
                            ?group cap:liveIn ?muni.
                            ?muni cap:hasNameMunicipality ?nameMuni
                                FILTER (?nameMuni = "{municipio}").
                            ?group cap:minAge ?min
                                FILTER (?min = "{min}"^^xsd:int).
                            ?group cap:maxAge ?max
                                FILTER (?max = "{max}"^^xsd:int).
                            ?group cap:numPeople ?pobl.
                            """ + qsexo + f"""}}
                    """
            gres = g.query(qfinal)
            for row in gres:
                nomMuni = row[1]
                numPobl = numPobl + int(row[0])
        resultado = {'numPobl': numPobl, 'nomMuni': nomMuni}
        return resultado

    def buscarIntAux(self, min, max):
        min = int(min)
        max = int(max)
        x = min
        y = max
        arrMin = []
        arrMax = []
        while x < max:
            arrMin.append(x)
            x = x + 5
        while y > min:
            arrMax.insert(0, y)
            y = y - 5
        return [arrMin, arrMax]


# aux = Colegios()
# aux.nombreColAvanzada('Educación Infantil', 'Privado', 'Madrid', '28027', 50)
# print(aux.nombreColAvanzada('Otros', 'Todos', 'Madrid', '', 50))
#
# aux = Colegios()
# aux.numeroPoblacion('Ajalvir', 'Hombre', 5, 29)
aux = Colegios()
print(aux.nombreColegio("SAN BLAS"))
# Querys Sparql
import rdflib
from rdflib.plugins.sparql import prepareQuery


class Colegios:
    def __init__(self):
        self.tipoCentro = {'Todos': 1, 'Otros': 2, 'Educación Infantil': 3, 'Educación Primaria': 4, 'Educación '
                                                                                                     'Secundaria': 5}
        self.titCentro = {'Todos': 1, 'Privado': 2, 'Privado Concertado': 3, 'Público': 4,
                          'Público-Titularidad Privada': 5}

    def numColegios(self):
        g = rdflib.Graph()

        g.parse("../../rdf/output-with-links.nt")

        q = """
                PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX  cap: <http://www.colegiosapp.org/ontology#>
                PREFIX  dbo: <http://dbpedia.org/ontology#>
                PREFIX  owl: <http://www.w3.org/2002/07/owl#>

                SELECT (count(?centro) as ?c)
                    WHERE{
                    ?centro cap:idSchool ?name.      
                }
                """
        gres = g.query(q)
        for row in gres:
            return row[0]

    def nombreColegio(self, nombre):
        g = rdflib.Graph()

        g.parse("../../rdf/output-with-links.nt")

        q = f"""
        PREFIX  xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX  cap: <http://www.colegiosapp.org/ontology#>
        PREFIX  dbo: <http://dbpedia.org/ontology#>
        PREFIX  owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?name ?tipoVia ?nomCalle ?numCalle
            WHERE{{
            ?centro cap:hasAddress ?calle.
            ?calle cap:hasNameAddress ?nomCalle.
            ?calle cap:hasType ?tipoVia.
            ?calle cap:hasNumber ?numCalle.
            ?centro cap:nameSchool ?name
               FILTER regex(?name , "{nombre}").
        }} LIMIT 50
        """
        gres = g.query(q)
        resultado = []

        for row in gres:
            auxDic = {'colegio': row[0]}
            auxCalle = row[1] + " " + row[2] + ", " + row[3]
            auxDic['calle'] = auxCalle
            resultado.append(auxDic)
        return resultado

    def nombreColAvanzada(self, tipo, titularidad, municipio, codigoPostal):
        tipoAux = self.tipoCentro.get(tipo)
        titAux = self.titCentro.get(titularidad)
        print(tipoAux, titAux, municipio, codigoPostal)
#
# aux = Colegios()
#
# aux.nombreColAvanzada('Educación Primaria','Privado', 'Madrid', '28027')
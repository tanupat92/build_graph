import json
import pickle
from Graph import Graph
from utils import combine_haplotype

if __name__ == '__main__':
    with open("config.json", "r") as jsonfile:
        config = json.load(jsonfile)
        print("Read successful")
    all_success = pickle.load(open(config["ALL_RESPONSE"], "rb"))
    drug_dict = pickle.load(open(config["DRUG_DICT"], "rb"))
    adverse_event = pickle.load(open(config["ADVERSE"], "rb"))
    illness = pickle.load(open(config["ILLNESS"], "rb"))
    g = Graph(config["IP"], config["PORT"])
    g.connect_janusgraph()
    # g.add_vertex("Drug", {'name': 'test3'})

    for drug_name in all_success.keys():

        # add Drug vertex
        drug_prop = {'name': drug_name, 'id': drug_dict[drug_name]}
        drug_query = g.g.V().has('Drug', 'name', drug_name)
        if not drug_query.hasNext():   # hasnext
            g.add_vertex("Drug", drug_prop)  # add vertex
        drug_vertex = g.g.V().has('Drug', 'name', drug_name).next()  # query
        print(f"Query drug_vertex: {drug_vertex}")

        d = all_success[drug_name]['data']
        for page in d:
            print("********************************************************************")
            print('................VERTEX ADDING.............')
            # add Disease vertex
            diseases = [(disease['name'], disease['id']) for disease in page['relatedDiseases']]
            ill = []
            adv = []
            for dis in diseases:
                dis_query = g.g.V().has('Disease', 'name', dis[0])
                if not dis_query.hasNext():  # hasnext
                    g.add_vertex("Disease", {'name': dis[0], 'id': dis[1]})  # add vertex

                disease_vertex = g.g.V().has('Disease', 'name', dis[0]).next()
                print(f"Query disease_vertex: {disease_vertex}")
                if (drug_name, dis[0], dis[1]) in illness:
                    ill.append(disease_vertex)
                    print(f"    This disease {disease_vertex} is an illness")
                else:
                    adv.append(disease_vertex)
                    print(f"    This disease {disease_vertex} is an adverse event")

            # add Gene vertex
            genes = page['location']['genes']
            alleles = page['location']['haplotypes']
            allele = combine_haplotype(alleles)
            gene_vertices = []
            for gene in genes:
                gene_query = g.g.V().\
                    has('Gene', 'symbol', gene['symbol']).\
                    has('Gene', 'allele', allele)
                if not gene_query.hasNext():
                    g.add_vertex("Gene", {
                        'name': gene['name'],
                        'symbol': gene['symbol'],
                        'id': gene['id'],
                        'allele': allele,
                        'phenotype': page['allelePhenotypes'][0]['phenotype'],
                        'evidence': page['levelOfEvidence']['term']
                    })
                gene_vertex = g.g.V().\
                    has('Gene', 'symbol', gene['symbol']).\
                    has('Gene', 'allele', allele).next()
                print(f"Query gene_vertex: {gene_vertex}")
                gene_vertices.append(gene_vertex)
            print("********************************************************************")
            print('................EDGE ADDING.............')
            # add edge
            for ill_vertex in ill:
                e = g.g.addE('treat')
                e.from_(drug_vertex)
                e.to(ill_vertex)
                print('drug treat illness')
                e.next()

            for adv_vertex in adv:
                for gene_vertex in gene_vertices:
                    e = g.g.addE('cause')
                    e.from_(gene_vertex)
                    e.to(adv_vertex)
                    print('gene cause adverse')
                    e.next()
            for gene_vertex in gene_vertices:
                e = g.g.addE('associate')
                e.from_(drug_vertex)
                e.to(gene_vertex)
                print('drug associate gene')
                e.next()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

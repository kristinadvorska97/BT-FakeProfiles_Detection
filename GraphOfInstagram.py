import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


class GraphOfInstagram:
    def __init__(self):
        self.edges = set()
        self.nodes = set()
        self.G = nx.Graph()
        self.graph_name = None

        self.karate_graph = nx.karate_club_graph()
        self.les_miserables = nx.les_miserables_graph()

    def prepare_main_graph_data(self):
        with open("data/truthseeker1119.json", "r") as graph_data:
            raw_data = json.load(graph_data)
            self.graph_name = graph_data.name[5:].replace(".json","")

        for k, v in raw_data.items():
            if k not in self.nodes:
                self.nodes.add(k)
            for item in v:
                if item not in self.nodes:
                    self.nodes.add(item)
                self.edges.add((k, item))
                self.edges.add((item, k))

    def create_main_graph(self):
        self.G.add_nodes_from(self.nodes)
        self.G.add_edges_from(self.edges)

    def draw_main_graph(self):
        pos = nx.spring_layout(self.G)
        plt.rcParams['figure.figsize'] = [33, 20]
        
        nx.draw_networkx(self.G, pos=pos, with_labels=True, font_size=18, font_family="monospace",
                         node_size=1400, width=1.5, node_color='#eb4034', edge_color='#c6c9bf')

        save_file = "SavedNetworks/" + self.graph_name + ".png"
        plt.savefig(save_file)
        plt.clf()

    def draw_complex_networks(self, graph, filename):
        pos = nx.spring_layout(graph)
        plt.rcParams['figure.figsize'] = [30, 20]

        nx.draw_networkx(graph, pos=pos, with_labels=True, font_size=20, font_family="monospace",
                         node_size=2000, width=1, node_color='#5eb4b5', edge_color='#c6c9bf')

        save_file = "SavedNetworks/" + filename + ".png"
        plt.savefig(save_file)
        plt.clf()


    def graph_clustering(self,graph):
        return nx.average_clustering(graph)

    def graph_transitivity(self,graph):
        return nx.transitivity(graph)

    def graph_short_path(self,graph):
        return nx.average_shortest_path_length(graph)

    def graph_smallworld_effect(self,graph):
        smallworld_omega = nx.omega(graph)
        smallworld_sigma = nx.sigma(graph)

        if (-1 < smallworld_omega < 1) and smallworld_sigma > 1:
            return True
        else:
            return False

    def plot_degree_dist(self,G,name):
        degrees = [G.degree(n) for n in G.nodes()]
        plt.hist(degrees, color = "#5ba663")
        plt.ylabel("Frequency")
        plt.xlabel("Degree")
        plt.title("Degree distribution of " + name + "´s network")
        plt.savefig("final_analysis/" + name + "_deg-distribution.png")

    def graph_hubs(self,graph):
        degrees = nx.degree(graph)
        sum_degrees = sum([pair[1] for pair in degrees])
        average = sum_degrees/len(graph.nodes)

        number_of_hubs = 0
        for node in degrees:
            if node[1] > average + 5:
                number_of_hubs += 1

        return number_of_hubs

    def full_analysis(self):
        data = {
            self.graph_name: [len(self.G.nodes),len(self.G.edges),self.graph_clustering(self.G),
                              self.graph_transitivity(self.G), self.graph_smallworld_effect(self.G),
                              nx.average_shortest_path_length(self.G),self.graph_hubs(self.G)],

            "Zachary´s Karate Club": [len(self.karate_graph.nodes),len(self.karate_graph.edges),
                             self.graph_clustering(self.karate_graph), self.graph_transitivity(self.karate_graph),
                             self.graph_smallworld_effect(self.karate_graph),
                             nx.average_shortest_path_length(self.karate_graph),self.graph_hubs(self.karate_graph)],

            "Les Miserables": [len(self.les_miserables.nodes),len(self.les_miserables.edges),
                               self.graph_clustering(self.les_miserables), self.graph_transitivity(self.les_miserables),
                               self.graph_smallworld_effect(self.les_miserables),
                               nx.average_shortest_path_length(self.les_miserables),self.graph_hubs(self.les_miserables)
                               ]
        }

        df = pd.DataFrame(data, index=["Nodes","Edges","Clustering","Transitivity","Small-world Effect",
                                       "Average Short-path","Hubs"])
        print(df)
        
        analysis_name = "final_analysis/" + self.graph_name + "_analysis.csv"
        df.to_csv(analysis_name)

    def read_dataframe(self):
        df = pd.read_csv("final_analysis/truthseeker1119_analysis.csv")
        print(df)


if __name__ == '__main__':
    graph = GraphOfInstagram()
    graph.prepare_main_graph_data()
    graph.create_main_graph()


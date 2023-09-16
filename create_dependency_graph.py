import ast
import networkx as nx
import matplotlib.pyplot as plt
import argparse
from typing import Dict


def analyze_code(code: str) -> Dict[str, nx.DiGraph]:
    tree = ast.parse(code)
    graphs = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            graph = nx.DiGraph()
            graphs[class_name] = graph

            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.FunctionDef):
                    function_name = f"{class_name}.{sub_node.name}"
                    graph.add_node(function_name)

                    for attr_node in ast.walk(sub_node):
                        if isinstance(attr_node, ast.Attribute):
                            attribute_name = attr_node.attr
                            graph.add_node(attribute_name)
                            graph.add_edge(function_name, attribute_name)

    return graphs


def draw_graphs(graphs: Dict[str, nx.DiGraph]):
    for class_name, graph in graphs.items():
        plt.figure()
        plt.title(f"Class: {class_name}")
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', font_weight='bold')
        plt.show()


def read_code_from_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and generate a graph of function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    code = read_code_from_file(file_path)
    graphs = analyze_code(code)
    draw_graphs(graphs)

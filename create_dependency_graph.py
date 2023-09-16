import ast
import networkx as nx
import matplotlib.pyplot as plt
import argparse


def read_code_from_file(file_path: str) -> str:
    """指定されたファイルパスからPythonコードを読み込む。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_class_node(class_node: ast.ClassDef) -> nx.DiGraph:
    """クラスのASTノードを解析して、関数とメンバー変数の関係を表すグラフを生成する。"""
    graph = nx.DiGraph()
    class_name = class_node.name

    for sub_node in ast.walk(class_node):
        if isinstance(sub_node, ast.FunctionDef):
            function_name = f"{class_name}.{sub_node.name}"
            graph.add_node(function_name)

            for attr_node in ast.walk(sub_node):
                if isinstance(attr_node, ast.Attribute):
                    attribute_name = attr_node.attr
                    graph.add_node(attribute_name)
                    graph.add_edge(function_name, attribute_name)

    return graph


def analyze_code(code: str) -> dict[str, nx.DiGraph]:
    """Pythonコードを解析して、各クラスの関数とメンバー変数の関係を表すグラフを生成する。"""
    tree = ast.parse(code)
    graphs = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            graphs[node.name] = analyze_class_node(node)

    return graphs


def draw_graphs(graphs: dict[str, nx.DiGraph]) -> None:
    """生成されたグラフを描画する。"""
    for class_name, graph in graphs.items():
        plt.figure()
        plt.title(f"Class: {class_name}")
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', font_weight='bold')
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and generate a graph of function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    code = read_code_from_file(file_path)
    graphs = analyze_code(code)
    draw_graphs(graphs)

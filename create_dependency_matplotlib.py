"""Python コードを読みこみ、メソッドとフィールドとの関係を matplotlib で描画するツール."""

import argparse

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

import create_dependency


_COLOR_CLASS = '#FF4040'
_COLOR_FUNCTION = '#0080FF'
_COLOR_FIELD = '#80FF00'


class GraphBuilder:
    """グラフのノードとエッジを追加するクラス"""

    def __init__(self) -> None:
        """コンストラクタ"""
        self.graph = nx.DiGraph()

    def add_nodes_and_edges(self, class_to_func_data: create_dependency.ClassToFuncType) -> None:
        """ノードとエッジを追加するメソッド"""
        for class_name, func_to_attr in class_to_func_data.items():
            self.graph.add_node(class_name, color=_COLOR_CLASS)

            for func_name, attrs in func_to_attr.items():
                full_func_name = f"{func_name}"
                self.graph.add_node(full_func_name, color=_COLOR_FUNCTION)
                self.graph.add_edge(class_name, full_func_name)

                for attr in attrs:
                    full_attr_name = f"{attr}"
                    self.graph.add_node(full_attr_name, color=_COLOR_FIELD)
                    self.graph.add_edge(full_func_name, full_attr_name)


class GraphStyler:
    """グラフにスタイルを適用するクラス"""

    def __init__(self, graph: nx.DiGraph) -> None:
        """コンストラクタ"""
        self.graph = graph

    def apply_style(self) -> dict:
        """スタイルを適用するメソッド"""
        return {node: data['color'] for node, data in self.graph.nodes(data=True)}


class GraphRenderer:
    """グラフを描画するクラス"""

    def __init__(self, graph: nx.DiGraph) -> None:
        """コンストラクタ"""
        self.graph = graph

    def render(self, colors: dict[str, str], class_names: list[str]) -> None:
        """複数のグラフを描画するメソッド"""
        for idx, class_name in enumerate(class_names):
            subG = self._create_subgraph_for_class(class_name)
            self._draw_single_graph(subG, colors, idx)
            plt.title(f"Class: {class_name}")

        plt.show()  # すべてのウィンドウを一度に表示

    def _create_subgraph_for_class(self, class_name: str) -> nx.DiGraph:
        sub_nodes = [class_name]

        # 直接的な子孫ノード（メソッド、フィールド）を取得
        descendants = list(self.graph.successors(class_name))
        sub_nodes.extend(descendants)

        # 子孫ノードから更に繋がる子孫（基本的にフィールド）を取得
        for desc in descendants:
            sub_descendants = list(self.graph.successors(desc))
            sub_nodes.extend(sub_descendants)

        return self.graph.subgraph(sub_nodes)

    def _draw_single_graph(self, subG: nx.DiGraph, colors: dict[str, str], figure_idx: int) -> None:
        """単一のグラフを描画する"""
        plt.figure(figure_idx)

        pos = nx.spring_layout(subG)
        nx.draw(subG, pos, with_labels=True, node_color=[colors[n] for n in subG.nodes()])

        self._add_legend()

    def _add_legend(self) -> None:
        """凡例を追加する."""
        red_patch = mpatches.Patch(color=_COLOR_CLASS, label='Class')
        blue_patch = mpatches.Patch(color=_COLOR_FUNCTION, label='Function')
        green_patch = mpatches.Patch(color=_COLOR_FIELD, label='Field')
        plt.legend(handles=[red_patch, blue_patch, green_patch])


def draw_class_to_func_graph(class_to_func_data: create_dependency.ClassToFuncType) -> None:
    """主要な処理を行う関数"""
    builder = GraphBuilder()
    builder.add_nodes_and_edges(class_to_func_data)

    styler = GraphStyler(builder.graph)
    colors = styler.apply_style()

    renderer = GraphRenderer(builder.graph)
    class_names = list(class_to_func_data.keys())
    renderer.render(colors, class_names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and draw graph for function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    class_relations = create_dependency.CodeAnalyzer.analyze_code(file_path)
    draw_class_to_func_graph(class_relations)

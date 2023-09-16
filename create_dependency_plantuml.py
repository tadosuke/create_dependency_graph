import ast
import argparse
from typing import Dict, List


class CodeReader:
    """Pythonコードをファイルから読み込むクラス。"""

    @staticmethod
    def read_from_file(file_path: str) -> str:
        """指定されたファイルパスからPythonコードを読み込む。"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class CodeAnalyzer:
    """Pythonコードを解析するクラス。"""

    @staticmethod
    def analyze_class_node(class_node: ast.ClassDef) -> Dict[str, List[str]]:
        """クラスのASTノードを解析して、関数とメンバー変数の関係を表す辞書を生成する。"""
        relations = {}

        for sub_node in ast.walk(class_node):
            if isinstance(sub_node, ast.FunctionDef):
                function_name = sub_node.name
                relations[function_name] = []

                for attr_node in ast.walk(sub_node):
                    if isinstance(attr_node, ast.Attribute):
                        attribute_name = attr_node.attr
                        relations[function_name].append(attribute_name)

        return relations

    @staticmethod
    def analyze_code(code: str) -> Dict[str, Dict[str, List[str]]]:
        """Pythonコードを解析して、各クラスの関数とメンバー変数の関係を表す辞書を生成する。"""
        tree = ast.parse(code)
        class_relations = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_relations[node.name] = CodeAnalyzer.analyze_class_node(node)

        return class_relations


class PlantUMLGenerator:
    """PlantUML形式のコードを生成するクラス。"""

    @staticmethod
    def generate(class_relations: Dict[str, Dict[str, List[str]]]) -> str:
        """関数とメンバー変数の関係を表す辞書からPlantUML形式のコードを生成する。"""
        plantuml_code = "@startuml\n"

        for class_name, relations in class_relations.items():
            plantuml_code += f"class {class_name} {{\n"

            attributes = set()
            for function_name, attribute_list in relations.items():
                plantuml_code += f"entity func_{function_name}\n"
                attributes.update(attribute_list)

            for attribute in attributes:
                plantuml_code += f"() {attribute}\n"

            for function_name, attribute_list in relations.items():
                for attribute in attribute_list:
                    plantuml_code += f"func_{function_name} --> {attribute}\n"

            plantuml_code += "}\n"

        plantuml_code += "@enduml\n"
        return plantuml_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and generate PlantUML code for function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    code = CodeReader.read_from_file(file_path)
    class_relations = CodeAnalyzer.analyze_code(code)
    plantuml_code = PlantUMLGenerator.generate(class_relations)

    print(plantuml_code)

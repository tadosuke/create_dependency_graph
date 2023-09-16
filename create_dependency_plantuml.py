"""Python コードを読みこみ、メソッドとフィールドとの関係を PlantUML 形式で出力するツール."""

from __future__ import annotations

import ast
import argparse


# 型エイリアス
FuncToAttrType = dict[str, list[str]]
ClassToFuncType = dict[str, FuncToAttrType]


class CodeReader:
    """Pythonコードをファイルから読み込むクラス。"""

    @staticmethod
    def read_from_file(file_path: str) -> str:
        """指定されたファイルパスからPythonコードを読み込む。"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class CodeAnalyzer:
    """Pythonコードを解析するクラス。"""

    @classmethod
    def analyze_code(cls, code: str) -> ClassToFuncType:
        """Pythonコードを解析して、各クラスの関数とメンバー変数の関係を表す辞書を生成する。"""
        tree = ast.parse(code)
        class_relations = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_relations[node.name] = cls._analyze_class_node(node)

        return class_relations

    @classmethod
    def _analyze_class_node(cls, class_node: ast.ClassDef) -> FuncToAttrType:
        """クラスのASTノードを解析して、関数とメンバー変数の関係を表す辞書を生成する。"""
        relations = {}

        # プロパティ一覧を取得
        properties = CodeAnalyzer._get_properties(class_node)

        # 関数と属性の関係を解析
        for sub_node in ast.walk(class_node):
            if not isinstance(sub_node, ast.FunctionDef):
                continue

            function_name = sub_node.name
            relations[function_name] = []

            for attr_node in ast.walk(sub_node):
                if not isinstance(attr_node, ast.Attribute):
                    continue

                attribute_name = attr_node.attr
                if attribute_name in properties:
                    continue

                relations[function_name].append(attribute_name)

        return relations

    @classmethod
    def _get_properties(cls, class_node: ast.ClassDef) -> set[str]:
        """プロパティ名の一覧を取得する."""
        properties = set()
        for sub_node in ast.walk(class_node):
            if isinstance(sub_node, ast.FunctionDef):
                for decorator in sub_node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "property":
                        properties.add(sub_node.name)
        return properties


class PlantUMLGenerator:
    """PlantUML形式のコードを生成するクラス。"""

    @classmethod
    def generate(cls, class_relations: ClassToFuncType) -> str:
        """関数とメンバー変数の関係を表す辞書からPlantUML形式のコードを生成する。"""
        plantuml_code = "@startuml\n"

        for class_name, relations in class_relations.items():
            plantuml_code += f"class {class_name} {{\n"

            attributes = set()
            for _, attribute_list in relations.items():
                attributes.update(attribute_list)

            plantuml_code += cls._generate_attribute_section(attributes)
            plantuml_code += cls._generate_function_section(relations)
            plantuml_code += cls._generate_relations_section(relations)

            plantuml_code += "}\n"

        plantuml_code += "@enduml\n"
        return plantuml_code

    @classmethod
    def _generate_attribute_section(cls, attributes: set[str]) -> str:
        """属性のPlantUMLセクションを生成する"""
        attribute_section = ""
        for attribute in attributes:
            attribute_section += f"() {attribute}\n"  # circle として表現
        return attribute_section

    @classmethod
    def _generate_function_section(cls, relations: dict[str, list[str]]) -> str:
        """関数のPlantUMLセクションを生成する"""
        function_section = ""
        for function_name, _ in relations.items():
            function_section += f"entity f_{function_name}\n"
        return function_section

    @classmethod
    def _generate_relations_section(cls, relations: dict[str, list[str]]) -> str:
        """関数と属性の関係のPlantUMLセクションを生成する"""
        relations_section = ""
        for function_name, attribute_list in relations.items():
            for attribute in attribute_list:
                relations_section += f"f_{function_name} --> {attribute}\n"
        return relations_section


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

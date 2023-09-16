"""Python コードを読みこみ、メソッドとフィールドとの関係を PlantUML 形式で出力するツール."""

from __future__ import annotations

import argparse

import create_dependency


class PlantUMLGenerator:
    """PlantUML形式のコードを生成するクラス。"""

    @classmethod
    def generate(cls, class_relations: create_dependency.ClassToFuncType) -> str:
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

    class_relations = create_dependency.CodeAnalyzer.analyze_code(file_path)

    plantuml_code = PlantUMLGenerator.generate(class_relations)

    print(plantuml_code)

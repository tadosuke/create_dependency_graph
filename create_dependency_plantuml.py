"""Python コードを読みこみ、メソッドとフィールドとの関係を PlantUML 形式で出力するツール."""

from __future__ import annotations

import argparse

import create_dependency


class PlantUMLGenerator:
    """PlantUML形式のコードを生成するクラス。"""

    @classmethod
    def generate(cls, class_relations: create_dependency.ClassToFuncType) -> str:
        plantuml_code = "@startuml\n"

        for class_name, (relations, unused_vars) in class_relations.items():
            plantuml_code += f"rectangle {class_name} {{\n"

            attributes = set()
            for _, attribute_list in relations.items():
                attributes.update(attribute_list)

            # 未使用の変数も含める
            attributes.update(unused_vars)

            plantuml_code += cls._generate_attribute_section(attributes)
            plantuml_code += cls._generate_function_section(relations)
            plantuml_code += cls._generate_relations_section(relations)
            plantuml_code += cls._generate_unused_vars_section(unused_vars)

            plantuml_code += "}\n"

        plantuml_code += "@enduml\n"
        return plantuml_code

    @classmethod
    def _generate_attribute_section(cls, attributes: set[str]) -> str:
        attribute_section = ""
        for attribute in attributes:
            attribute_section += f"() {attribute}\n"
        return attribute_section

    @classmethod
    def _generate_function_section(cls, relations: dict[str, list[str]]) -> str:
        function_section = ""
        for function_name, _ in relations.items():
            function_section += f"() f_{function_name}\n"
        return function_section

    @classmethod
    def _generate_relations_section(cls, relations: dict[str, list[str]]) -> str:
        relations_section = ""
        for function_name, attribute_list in relations.items():
            for attribute in attribute_list:
                relations_section += f"f_{function_name} --> {attribute}\n"
        return relations_section

    @classmethod
    def _generate_unused_vars_section(cls, unused_vars: set[str]) -> str:
        """未使用変数のPlantUMLセクションを生成する"""
        unused_vars_section = ""
        for unused_var in unused_vars:
            unused_vars_section += f"() {unused_var} <<unused>>\n"  # <<unused>> ステレオタイプを付与
        return unused_vars_section


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze Python code and generate PlantUML code for function and member variable relationships.')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')

    args = parser.parse_args()
    file_path = args.file_path

    class_relations = create_dependency.CodeAnalyzer.analyze_code(file_path)

    plantuml_code = PlantUMLGenerator.generate(class_relations)

    print(plantuml_code)

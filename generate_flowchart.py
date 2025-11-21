#!/usr/bin/env python3
"""
Generates a flowchart from a Python script by analyzing its function calls.
The output is in Graphviz DOT format.
"""

import ast
import argparse
import sys
from pathlib import Path
import subprocess
from datetime import datetime
import json

class FunctionCallVisitor(ast.NodeVisitor):
    """
    An AST visitor to trace function calls and build a call graph.
    """
    def __init__(self):
        self.graph = {}
        self.current_function = None
        self.function_stack = []

    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        self.function_stack.append(node.name)
        self.current_function = node.name
        if self.current_function not in self.graph:
            self.graph[self.current_function] = []
        
        self.generic_visit(node)
        
        self.function_stack.pop()
        if self.function_stack:
            self.current_function = self.function_stack[-1]
        else:
            self.current_function = None

    def visit_Call(self, node):
        """Visit a function call."""
        if self.current_function:
            callee_name = self.get_callee_name(node.func)
            if callee_name:
                self.graph[self.current_function].append(callee_name)
                
                if callee_name.endswith('add_node') and len(node.args) > 1:
                    node_arg = node.args[1]
                    if isinstance(node_arg, ast.Name):
                        self.graph[self.current_function].append(node_arg.id)
                    elif isinstance(node_arg, ast.Lambda) and isinstance(node_arg.body, ast.Call):
                        lambda_callee = self.get_callee_name(node_arg.body.func)
                        if lambda_callee:
                            self.graph[self.current_function].append(lambda_callee)
                
                if callee_name.endswith('add_conditional_edges') and len(node.args) > 1:
                    cond_arg = node.args[1]
                    if isinstance(cond_arg, ast.Name):
                        self.graph[self.current_function].append(cond_arg.id)

        self.generic_visit(node)

    def get_callee_name(self, func_node):
        """Recursively get the name of a callee."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None

def analyze_code(file_path):
    """
    Reads and analyzes Python code to build a function call graph and get defined functions.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    tree = ast.parse(code)

    defined_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    
    return visitor.graph, defined_functions

def filter_graph(graph, defined_functions):
    """Filters a call graph to only include functions defined in the source file."""
    filtered_graph = {func: [] for func in defined_functions}

    for caller, callees in graph.items():
        if caller in defined_functions:
            filtered_callees = [callee for callee in callees if callee in defined_functions]
            if filtered_callees:
                filtered_graph[caller].extend(filtered_callees)
    return filtered_graph

def generate_dot_graph(graph, script_name):
    """
    Generates a Graphviz DOT representation of the call graph.
    """
    dot_lines = ["digraph G {"]
    dot_lines.append(f'  label="{script_name}";')
    dot_lines.append("  labelloc=t;")
    dot_lines.append("  rankdir=LR;")
    dot_lines.append("  node [shape=box, style=rounded, fontname=\"Helvetica\"];")
    dot_lines.append("  edge [fontname=\"Helvetica\"];")

    all_nodes = set(graph.keys())
    for callees in graph.values():
        all_nodes.update(callees)

    for node in sorted(list(all_nodes)):
         dot_lines.append(f'  "{node}";')

    for caller, callees in graph.items():
        if callees:
            for callee in sorted(list(set(callees))):
                dot_lines.append(f'  "{caller}" -> "{callee}";')
    
    dot_lines.append("}")
    return "\n".join(dot_lines)

def main():
    """
    Main function to parse arguments and run the analysis.
    """
    parser = argparse.ArgumentParser(
        description="Generate a flowchart JSON, PNG, and SVG from a Python script.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("python_file", help="Path to the Python script to analyze.")
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Do not generate PNG and SVG images (requires Graphviz)."
    )
    parser.add_argument(
        "--print-dot",
        action="store_true",
        help="Print the DOT representation to stdout after generating files."
    )
    args = parser.parse_args()

    script_path = Path(args.python_file)

    try:
        full_graph, defined_functions = analyze_code(script_path)
        graph = filter_graph(full_graph, defined_functions)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base_filename = f"{script_path.stem}_flowchart_{timestamp}"
        
        json_output_path = script_path.parent / f"{base_filename}.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        print(f"Call graph data saved to: {json_output_path}")

        dot_representation = generate_dot_graph(graph, script_path.name)

        if args.print_dot:
            print("\n--- DOT Representation ---")
            print(dot_representation)

        if args.no_images:
            return

        # --- Image Generation ---
        png_output_path = script_path.parent / f"{base_filename}.png"
        svg_output_path = script_path.parent / f"{base_filename}.svg"

        try:
            # Generate PNG
            subprocess.run(
                ['dot', '-Tpng', '-o', str(png_output_path)],
                input=dot_representation, encoding='utf-8', check=True, capture_output=True
            )
            print(f"Flowchart image saved to: {png_output_path}")

            # Generate SVG
            subprocess.run(
                ['dot', '-Tsvg', '-o', str(svg_output_path)],
                input=dot_representation, encoding='utf-8', check=True, capture_output=True
            )
            print(f"Flowchart image saved to: {svg_output_path}")

        except FileNotFoundError:
            print("\nWarning: 'dot' command not found (Graphviz). Images were not generated.", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print("\nError executing 'dot' command:", file=sys.stderr)
            print(e.stderr, file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: Input file not found at {script_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
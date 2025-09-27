#!/usr/bin/env python3
"""
Convert Markdown files to PDF with PlantUML diagram support.

This script converts .md files to PDF using markdown-pdf or pandoc,
with automatic PlantUML diagram rendering.

Requirements:
    - Python 3.6+
    - pandoc or markdown-pdf (npm install -g markdown-pdf)
    - PlantUML (java -jar plantuml.jar)
    - Java Runtime for PlantUML
    - wkhtmltopdf (for better HTML to PDF conversion)
    
Optional:
    - typora (for GUI-based conversion)
"""

import os
import sys
import subprocess
import tempfile
import shutil
import re
import argparse
from pathlib import Path
from typing import List, Optional, Tuple


class MarkdownToPdfConverter:
    """Converter for Markdown files to PDF with PlantUML support."""
    
    def __init__(self, use_pandoc: bool = True, plantuml_jar: Optional[str] = None):
        """
        Initialize converter.
        
        Args:
            use_pandoc: Use pandoc (True) or markdown-pdf (False)
            plantuml_jar: Path to plantuml.jar file
        """
        self.use_pandoc = use_pandoc
        self.plantuml_jar = plantuml_jar or self._find_plantuml()
        self.temp_dir = None
        
    def _find_plantuml(self) -> Optional[str]:
        """Find PlantUML jar file in common locations."""
        common_paths = [
            "/usr/share/plantuml/plantuml.jar",
            "/usr/local/share/plantuml/plantuml.jar",
            "~/plantuml.jar",
            "./plantuml.jar",
            "../plantuml.jar",
            "C:/tools/plantuml/plantuml.jar",
            "C:/Program Files/PlantUML/plantuml.jar",
        ]
        
        for path in common_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
                
        # Try to find with which command
        try:
            result = subprocess.run(["which", "plantuml"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        return None
        
    def _check_dependencies(self) -> List[str]:
        """Check for required dependencies."""
        missing = []
        
        # Check for pandoc or markdown-pdf
        if self.use_pandoc:
            if not shutil.which("pandoc"):
                missing.append("pandoc")
            # Check for pdflatex or wkhtmltopdf
            if not shutil.which("pdflatex") and not shutil.which("wkhtmltopdf"):
                missing.append("pdflatex or wkhtmltopdf")
        else:
            if not shutil.which("markdown-pdf"):
                missing.append("markdown-pdf (install with: npm install -g markdown-pdf)")
                
        # Check for Java (needed for PlantUML)
        if not shutil.which("java"):
            missing.append("java")
            
        # Check for PlantUML
        if not self.plantuml_jar:
            missing.append("plantuml.jar")
            
        return missing
        
    def _extract_and_render_plantuml(self, markdown_content: str, temp_dir: str) -> str:
        """
        Extract PlantUML diagrams and render them to images.
        
        Args:
            markdown_content: Original markdown content
            temp_dir: Temporary directory for image files
            
        Returns:
            Modified markdown content with image links
        """
        # Pattern to match PlantUML blocks
        patterns = [
            (r'```puml\n(.*?)\n```', 'puml'),
            (r'```plantuml\n(.*?)\n```', 'plantuml'),
            (r'```\{\.puml\}\n(.*?)\n```', 'puml'),
            (r'```\{\.plantuml\}\n(.*?)\n```', 'plantuml'),
        ]
        
        modified_content = markdown_content
        diagram_count = 0
        
        for pattern, lang in patterns:
            matches = re.finditer(pattern, markdown_content, re.DOTALL)
            
            for match in matches:
                diagram_count += 1
                plantuml_code = match.group(1)
                
                # Save PlantUML code to temp file
                puml_file = os.path.join(temp_dir, f"diagram_{diagram_count}.puml")
                with open(puml_file, 'w', encoding='utf-8') as f:
                    f.write(plantuml_code)
                    
                # Render to PNG
                png_file = os.path.join(temp_dir, f"diagram_{diagram_count}.png")
                self._render_plantuml(puml_file, png_file)
                
                # Replace in markdown with image link
                if os.path.exists(png_file):
                    img_tag = f"![Diagram {diagram_count}]({png_file})"
                    modified_content = modified_content.replace(match.group(0), img_tag)
                    
        return modified_content
        
    def _render_plantuml(self, puml_file: str, output_file: str) -> bool:
        """
        Render PlantUML file to image.
        
        Args:
            puml_file: Path to .puml file
            output_file: Path to output image file
            
        Returns:
            True if successful
        """
        try:
            if self.plantuml_jar:
                # Use jar file
                if self.plantuml_jar.endswith('.jar'):
                    cmd = ["java", "-jar", self.plantuml_jar, 
                           "-tpng", "-o", os.path.dirname(output_file), puml_file]
                else:
                    # Assume it's a script
                    cmd = [self.plantuml_jar, "-tpng", 
                           "-o", os.path.dirname(output_file), puml_file]
                    
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # PlantUML creates file with specific naming
                expected_output = puml_file.replace('.puml', '.png')
                if os.path.exists(expected_output) and expected_output != output_file:
                    shutil.move(expected_output, output_file)
                    
                return result.returncode == 0
        except Exception as e:
            print(f"Error rendering PlantUML: {e}", file=sys.stderr)
            
        return False
        
    def convert_with_pandoc(self, input_file: str, output_file: str, 
                           temp_content: str) -> bool:
        """
        Convert using pandoc.
        
        Args:
            input_file: Original markdown file path
            output_file: Output PDF file path  
            temp_content: Modified markdown content
            
        Returns:
            True if successful
        """
        try:
            # Save modified content to temp file
            temp_md = os.path.join(self.temp_dir, "temp_converted.md")
            with open(temp_md, 'w', encoding='utf-8') as f:
                f.write(temp_content)
                
            # Pandoc command with options for better formatting
            cmd = [
                "pandoc",
                temp_md,
                "-o", output_file,
                "--pdf-engine=pdflatex",  # or wkhtmltopdf, xelatex
                "--highlight-style=tango",
                "--toc",  # Table of contents
                "--toc-depth=3",
                "-V", "geometry:margin=1in",
                "-V", "fontsize=11pt",
                "-V", "linkcolor=blue",
                "--metadata", f"title={Path(input_file).stem}",
            ]
            
            # Try with pdflatex first, fallback to HTML
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Try with HTML engine
                cmd[3] = "--pdf-engine=wkhtmltopdf"
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            if result.returncode != 0:
                print(f"Pandoc error: {result.stderr}", file=sys.stderr)
                return False
                
            return True
            
        except Exception as e:
            print(f"Error in pandoc conversion: {e}", file=sys.stderr)
            return False
            
    def convert_with_markdown_pdf(self, input_file: str, output_file: str,
                                 temp_content: str) -> bool:
        """
        Convert using markdown-pdf.
        
        Args:
            input_file: Original markdown file path
            output_file: Output PDF file path
            temp_content: Modified markdown content
            
        Returns:
            True if successful
        """
        try:
            # Save modified content to temp file
            temp_md = os.path.join(self.temp_dir, "temp_converted.md")
            with open(temp_md, 'w', encoding='utf-8') as f:
                f.write(temp_content)
                
            # markdown-pdf command
            cmd = ["markdown-pdf", temp_md, "-o", output_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"markdown-pdf error: {result.stderr}", file=sys.stderr)
                return False
                
            return True
            
        except Exception as e:
            print(f"Error in markdown-pdf conversion: {e}", file=sys.stderr)
            return False
            
    def convert_file(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """
        Convert a markdown file to PDF.
        
        Args:
            input_file: Path to input .md file
            output_file: Path to output .pdf file (optional)
            
        Returns:
            True if successful
        """
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            return False
            
        # Generate output filename if not provided
        if not output_file:
            output_file = Path(input_file).with_suffix('.pdf')
            
        print(f"Converting: {input_file} -> {output_file}")
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="md2pdf_")
        
        try:
            # Read markdown content
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract and render PlantUML diagrams
            if self.plantuml_jar:
                print("Processing PlantUML diagrams...")
                content = self._extract_and_render_plantuml(content, self.temp_dir)
                
            # Convert to PDF
            if self.use_pandoc:
                success = self.convert_with_pandoc(input_file, str(output_file), content)
            else:
                success = self.convert_with_markdown_pdf(input_file, str(output_file), content)
                
            if success:
                print(f"Successfully converted to: {output_file}")
            else:
                print(f"Failed to convert: {input_file}", file=sys.stderr)
                
            return success
            
        finally:
            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                
    def convert_directory(self, directory: str, recursive: bool = False) -> Tuple[int, int]:
        """
        Convert all markdown files in a directory.
        
        Args:
            directory: Directory path
            recursive: Process subdirectories
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        success_count = 0
        fail_count = 0
        
        pattern = "**/*.md" if recursive else "*.md"
        md_files = list(Path(directory).glob(pattern))
        
        if not md_files:
            print(f"No markdown files found in '{directory}'")
            return (0, 0)
            
        print(f"Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            if self.convert_file(str(md_file)):
                success_count += 1
            else:
                fail_count += 1
                
        return (success_count, fail_count)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF with PlantUML support"
    )
    parser.add_argument(
        "input",
        help="Input markdown file or directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output PDF file (for single file conversion)"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    parser.add_argument(
        "--engine",
        choices=["pandoc", "markdown-pdf"],
        default="pandoc",
        help="Conversion engine to use (default: pandoc)"
    )
    parser.add_argument(
        "--plantuml-jar",
        help="Path to plantuml.jar file"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = MarkdownToPdfConverter(
        use_pandoc=(args.engine == "pandoc"),
        plantuml_jar=args.plantuml_jar
    )
    
    # Check dependencies
    if args.check_deps:
        missing = converter._check_dependencies()
        if missing:
            print("Missing dependencies:")
            for dep in missing:
                print(f"  - {dep}")
            sys.exit(1)
        else:
            print("All dependencies are installed.")
            if converter.plantuml_jar:
                print(f"PlantUML found at: {converter.plantuml_jar}")
            sys.exit(0)
            
    # Check dependencies before conversion
    missing = converter._check_dependencies()
    if missing:
        print("Error: Missing dependencies:", file=sys.stderr)
        for dep in missing:
            print(f"  - {dep}", file=sys.stderr)
        print("\nInstallation hints:", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt-get install pandoc texlive-latex-base", file=sys.stderr)
        print("  With PlantUML: sudo apt-get install plantuml", file=sys.stderr)
        print("  Or download: https://plantuml.com/download", file=sys.stderr)
        sys.exit(1)
        
    # Process input
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Single file conversion
        if not input_path.suffix == '.md':
            print(f"Error: Input file must be a .md file", file=sys.stderr)
            sys.exit(1)
            
        success = converter.convert_file(str(input_path), args.output)
        sys.exit(0 if success else 1)
        
    elif input_path.is_dir():
        # Directory conversion
        if args.output:
            print("Warning: --output is ignored for directory conversion")
            
        success, fail = converter.convert_directory(str(input_path), args.recursive)
        print(f"\nConversion complete: {success} successful, {fail} failed")
        sys.exit(0 if fail == 0 else 1)
        
    else:
        print(f"Error: '{args.input}' is not a file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
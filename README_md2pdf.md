# Markdown to PDF Conversion Tools

This directory contains scripts to convert Markdown files to PDF with PlantUML diagram support.

## Available Scripts

### 1. Python Script: `convert_md_to_pdf.py`
Full-featured Python script with PlantUML rendering support.

### 2. Bash Script: `convert_md_to_pdf.sh`
Simple shell script wrapper for quick conversions.

## Quick Start

### Convert RFID documentation to PDF:

```bash
# Single file conversion
./convert_md_to_pdf.py rfid_modbus_tunnel_led_control.md

# Convert all documentation
./convert_md_to_pdf.py ../documentation/Modbus/ -r

# Using bash script
./convert_md_to_pdf.sh rfid_modbus_sequence_write_block.md
```

## Installation

### Ubuntu/Debian:
```bash
# Basic requirements
sudo apt-get update
sudo apt-get install -y pandoc texlive-latex-base texlive-xetex

# For PlantUML support
sudo apt-get install -y plantuml default-jre

# Alternative: wkhtmltopdf for HTML-based conversion
sudo apt-get install -y wkhtmltopdf
```

### Windows (WSL):
```bash
# Same as Ubuntu/Debian above
# Or use Windows-native tools:
# - Install MiKTeX for LaTeX: https://miktex.org/
# - Install Pandoc: https://pandoc.org/installing.html
# - Install PlantUML: https://plantuml.com/download
```

### macOS:
```bash
# Using Homebrew
brew install pandoc
brew install --cask mactex  # For LaTeX support
brew install plantuml

# Or for lighter installation
brew install pandoc
brew install --cask wkhtmltopdf
```

### Using Docker (no local installation needed):
```bash
# Pull the pandoc Docker image
docker pull pandoc/latex:latest

# Use the -d flag with the bash script
./convert_md_to_pdf.sh -d document.md
```

## Python Script Usage

```bash
# Check dependencies
python3 convert_md_to_pdf.py --check-deps

# Convert single file
python3 convert_md_to_pdf.py input.md -o output.pdf

# Convert directory (all .md files)
python3 convert_md_to_pdf.py /path/to/docs/

# Recursive conversion
python3 convert_md_to_pdf.py /path/to/docs/ -r

# Specify PlantUML jar location
python3 convert_md_to_pdf.py input.md --plantuml-jar /path/to/plantuml.jar

# Use different engine
python3 convert_md_to_pdf.py input.md --engine markdown-pdf
```

## Bash Script Usage

```bash
# Convert single file
./convert_md_to_pdf.sh document.md
./convert_md_to_pdf.sh -o custom_output.pdf document.md

# Convert all .md files in directory
./convert_md_to_pdf.sh /path/to/docs
./convert_md_to_pdf.sh -r /path/to/docs  # Recursive

# Use Docker (no pandoc installation needed)
./convert_md_to_pdf.sh -d document.md

# Show help
./convert_md_to_pdf.sh -h
```

## Features

### PlantUML Support
Both scripts automatically detect and render PlantUML diagrams in markdown files:
- Supports `puml` and `plantuml` code blocks
- Renders diagrams to PNG images
- Embeds images in the final PDF

### Supported PlantUML Syntax:
````markdown
```puml
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi!
@enduml
```
````

### Multiple Conversion Engines
- **Pandoc** (default): Best quality, requires LaTeX
- **wkhtmltopdf**: HTML-based, good for web content
- **markdown-pdf**: Node.js based, simple installation

## Troubleshooting

### Missing Dependencies
Run the dependency check:
```bash
python3 convert_md_to_pdf.py --check-deps
```

### PlantUML Not Found
1. Install PlantUML:
   ```bash
   sudo apt-get install plantuml
   ```
2. Or download jar manually:
   ```bash
   wget https://github.com/plantuml/plantuml/releases/download/v1.2024.0/plantuml.jar
   python3 convert_md_to_pdf.py input.md --plantuml-jar ./plantuml.jar
   ```

### LaTeX Errors
If you get LaTeX errors, try:
1. Using wkhtmltopdf engine instead
2. Installing full LaTeX distribution:
   ```bash
   sudo apt-get install texlive-full
   ```

### Windows-Specific Issues
- Use WSL2 for best compatibility
- Or use native Windows tools with adjusted paths
- Docker option works well on Windows

## Examples for RFID Documentation

Convert all RFID documentation:
```bash
# Convert specific RFID docs
./convert_md_to_pdf.py rfid_modbus_tunnel_led_control.md
./convert_md_to_pdf.py rfid_modbus_sequence_write_block.md

# Convert all Modbus documentation
./convert_md_to_pdf.py ../documentation/Modbus/ -r

# Batch convert with bash script
for file in *.md; do
    ./convert_md_to_pdf.sh "$file"
done
```

## Output

PDFs are created in the same directory as the source files with `.pdf` extension:
- `document.md` → `document.pdf`
- PlantUML diagrams are automatically rendered and embedded
- Table of contents is generated automatically
- Syntax highlighting for code blocks
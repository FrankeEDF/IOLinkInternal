#!/bin/bash
# Simple shell script wrapper for markdown to PDF conversion
# Supports both single files and batch conversion

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PLANTUML_JAR="/usr/share/plantuml/plantuml.jar"
USE_DOCKER=false
DOCKER_IMAGE="pandoc/latex:latest"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to render PlantUML diagrams
render_plantuml() {
    local md_file="$1"
    local temp_dir="$2"
    
    if [ ! -f "$PLANTUML_JAR" ] && ! command_exists plantuml; then
        print_warning "PlantUML not found, skipping diagram rendering"
        return 1
    fi
    
    # Extract PlantUML blocks and render them
    local diagram_count=0
    
    # Create a temporary file for processing
    local temp_md="${temp_dir}/processed.md"
    cp "$md_file" "$temp_md"
    
    # Find and process PlantUML blocks
    while IFS= read -r line; do
        if [[ "$line" =~ ^\`\`\`(puml|plantuml) ]]; then
            ((diagram_count++))
            local puml_file="${temp_dir}/diagram_${diagram_count}.puml"
            local png_file="${temp_dir}/diagram_${diagram_count}.png"
            
            # Extract diagram content
            sed -n '/^```\(puml\|plantuml\)/,/^```/p' "$md_file" | \
                sed '1d;$d' > "$puml_file"
            
            # Render with PlantUML
            if [ -f "$PLANTUML_JAR" ]; then
                java -jar "$PLANTUML_JAR" -tpng "$puml_file" -o "$temp_dir" 2>/dev/null
            else
                plantuml -tpng "$puml_file" -o "$temp_dir" 2>/dev/null
            fi
            
            if [ -f "$png_file" ]; then
                print_info "Rendered PlantUML diagram ${diagram_count}"
            fi
        fi
    done < "$md_file"
    
    echo "$temp_md"
}

# Function to convert with pandoc
convert_with_pandoc() {
    local input_file="$1"
    local output_file="$2"
    local use_docker="$3"
    
    local basename=$(basename "$input_file" .md)
    
    if [ "$use_docker" = true ]; then
        # Use Docker container for pandoc
        docker run --rm \
            -v "$(pwd):/data" \
            -v "$(dirname "$input_file"):/source" \
            "$DOCKER_IMAGE" \
            "/source/$(basename "$input_file")" \
            -o "/data/$output_file" \
            --pdf-engine=xelatex \
            --highlight-style=tango \
            --toc \
            -V geometry:margin=1in \
            -V fontsize=11pt \
            -V linkcolor=blue \
            --metadata title="$basename"
    else
        # Use local pandoc installation
        pandoc "$input_file" \
            -o "$output_file" \
            --pdf-engine=xelatex \
            --highlight-style=tango \
            --toc \
            -V geometry:margin=1in \
            -V fontsize=11pt \
            -V linkcolor=blue \
            --metadata title="$basename" 2>/dev/null || \
        pandoc "$input_file" \
            -o "$output_file" \
            --pdf-engine=pdflatex \
            --highlight-style=tango \
            --toc \
            -V geometry:margin=1in \
            -V fontsize=11pt \
            -V linkcolor=blue \
            --metadata title="$basename" 2>/dev/null || \
        pandoc "$input_file" \
            -o "$output_file" \
            --pdf-engine=wkhtmltopdf 2>/dev/null
    fi
}

# Function to convert single file
convert_file() {
    local input_file="$1"
    local output_file="${2:-${input_file%.md}.pdf}"
    
    if [ ! -f "$input_file" ]; then
        print_error "File not found: $input_file"
        return 1
    fi
    
    print_info "Converting: $input_file -> $output_file"
    
    # Create temp directory
    local temp_dir=$(mktemp -d)
    
    # Process PlantUML if needed
    local processed_file="$input_file"
    if grep -q '```\(puml\|plantuml\)' "$input_file"; then
        print_info "Processing PlantUML diagrams..."
        processed_file=$(render_plantuml "$input_file" "$temp_dir")
    fi
    
    # Convert to PDF
    if convert_with_pandoc "$processed_file" "$output_file" "$USE_DOCKER"; then
        print_info "Successfully converted: $output_file"
        rm -rf "$temp_dir"
        return 0
    else
        print_error "Conversion failed for: $input_file"
        rm -rf "$temp_dir"
        return 1
    fi
}

# Function to convert all files in directory
convert_directory() {
    local directory="$1"
    local recursive="${2:-false}"
    
    if [ ! -d "$directory" ]; then
        print_error "Directory not found: $directory"
        return 1
    fi
    
    local count=0
    local success=0
    local failed=0
    
    # Find markdown files
    if [ "$recursive" = true ]; then
        local files=$(find "$directory" -name "*.md" -type f)
    else
        local files=$(find "$directory" -maxdepth 1 -name "*.md" -type f)
    fi
    
    # Convert each file
    for file in $files; do
        ((count++))
        if convert_file "$file"; then
            ((success++))
        else
            ((failed++))
        fi
    done
    
    print_info "Conversion complete: $success successful, $failed failed (total: $count)"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] <input>

Convert Markdown files to PDF with PlantUML support.

Arguments:
    input           Markdown file or directory to convert

Options:
    -o, --output    Output PDF file (for single file only)
    -r, --recursive Process directories recursively
    -d, --docker    Use Docker container for pandoc
    -h, --help      Show this help message

Examples:
    # Convert single file
    $0 document.md
    $0 -o output.pdf document.md
    
    # Convert all .md files in directory
    $0 /path/to/docs
    $0 -r /path/to/docs  # Recursive
    
    # Use Docker for conversion (no local pandoc needed)
    $0 -d document.md

Dependencies:
    - pandoc (or Docker)
    - pdflatex, xelatex, or wkhtmltopdf
    - plantuml (optional, for diagram rendering)
    - java (for PlantUML)

Installation (Ubuntu/Debian):
    sudo apt-get install pandoc texlive-latex-base texlive-xetex
    sudo apt-get install plantuml default-jre
    
    Or use Docker:
    docker pull pandoc/latex:latest
EOF
}

# Main script
main() {
    local input=""
    local output=""
    local recursive=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -o|--output)
                output="$2"
                shift 2
                ;;
            -r|--recursive)
                recursive=true
                shift
                ;;
            -d|--docker)
                USE_DOCKER=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                input="$1"
                shift
                ;;
        esac
    done
    
    # Check if input is provided
    if [ -z "$input" ]; then
        print_error "No input file or directory specified"
        show_usage
        exit 1
    fi
    
    # Check dependencies
    if [ "$USE_DOCKER" = false ]; then
        if ! command_exists pandoc; then
            print_error "pandoc is not installed"
            print_info "Install with: sudo apt-get install pandoc"
            print_info "Or use Docker: $0 -d $input"
            exit 1
        fi
    else
        if ! command_exists docker; then
            print_error "Docker is not installed"
            exit 1
        fi
    fi
    
    # Process input
    if [ -f "$input" ]; then
        # Single file
        convert_file "$input" "$output"
    elif [ -d "$input" ]; then
        # Directory
        if [ -n "$output" ]; then
            print_warning "Output option ignored for directory conversion"
        fi
        convert_directory "$input" "$recursive"
    else
        print_error "Input is neither a file nor a directory: $input"
        exit 1
    fi
}

# Run main function
main "$@"
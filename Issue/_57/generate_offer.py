from __future__ import annotations

import copy
import re
from datetime import date, timedelta
from pathlib import Path
from typing import List, Tuple

from odf.opendocument import load
from odf import text, table, style, teletype
from odf.element import Element

TODAY = date(2026, 3, 26)


def extract_text(el: Element) -> str:
    parts: List[str] = []
    for node in el.childNodes:
        if hasattr(node, 'data'):
            parts.append(node.data)
        else:
            parts.append(extract_text(node))
    return ''.join(parts)


def set_paragraph_text(p: Element, value: str) -> None:
    # remove old children
    for child in list(p.childNodes):
        p.removeChild(child)
    teletype.addTextToElement(p, value)


def replace_text_in_template(doc, old: str, new: str) -> bool:
    for p in doc.getElementsByType(text.P):
        current = extract_text(p)
        if current == old:
            set_paragraph_text(p, new)
            return True
    return False


def add_styles(doc):
    styles = doc.automaticstyles

    bold = style.Style(name='InlineBold', family='text')
    bold.addElement(style.TextProperties(fontweight='bold', fontweightasian='bold', fontweightcomplex='bold'))
    styles.addElement(bold)

    table_style = style.Style(name='MdTable', family='table')
    table_style.addElement(style.TableProperties(width='16cm', align='margins'))
    styles.addElement(table_style)

    col_style = style.Style(name='MdTableCol', family='table-column')
    col_style.addElement(style.TableColumnProperties(columnwidth='4cm'))
    styles.addElement(col_style)

    cell_style = style.Style(name='MdCell', family='table-cell')
    cell_style.addElement(style.TableCellProperties(border='0.06pt solid #000000', padding='0.08cm'))
    styles.addElement(cell_style)

    head_cell_style = style.Style(name='MdHeadCell', family='table-cell')
    head_cell_style.addElement(
        style.TableCellProperties(border='0.06pt solid #000000', padding='0.08cm', backgroundcolor='#DDDDDD'))
    styles.addElement(head_cell_style)

    return {
        'bold': bold,
        'table': table_style,
        'col': col_style,
        'cell': cell_style,
        'head_cell': head_cell_style,
    }


def add_inline_markdown(paragraph: Element, text_value: str, bold_style_name: str) -> None:
    pattern = re.compile(r'(\*\*[^*]+\*\*)')
    parts = pattern.split(text_value)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            span = text.Span(stylename=bold_style_name)
            teletype.addTextToElement(span, part[2:-2])
            paragraph.addElement(span)
        else:
            teletype.addTextToElement(paragraph, part)


class Block:
    pass


class Heading(Block):
    def __init__(self, level: int, content: str):
        self.level = level
        self.content = content


class Paragraph(Block):
    def __init__(self, content: str):
        self.content = content


class BulletList(Block):
    def __init__(self, items: List[str]):
        self.items = items


class MdTable(Block):
    def __init__(self, headers: List[str], rows: List[List[str]]):
        self.headers = headers
        self.rows = rows


class HorizontalRule(Block):
    pass


TABLE_SEP_RE = re.compile(r'^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$')


def is_table_row(line: str) -> bool:
    return line.count('|') >= 2 and line.strip().startswith('|') and line.strip().endswith('|')


def parse_markdown(md: str) -> List[Block]:
    lines = md.splitlines()
    blocks: List[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == '---':
            blocks.append(HorizontalRule())
            i += 1
            continue

        m = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if m:
            blocks.append(Heading(len(m.group(1)), m.group(2).strip()))
            i += 1
            continue

        if is_table_row(stripped) and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and is_table_row(lines[i].strip()):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            blocks.append(MdTable(headers, rows))
            continue

        if re.match(r'^[-*]\s+', stripped):
            items = []
            while i < len(lines):
                cur = lines[i].rstrip()
                cur_stripped = cur.strip()
                if not cur_stripped:
                    i += 1
                    break
                m2 = re.match(r'^[-*]\s+(.*)$', cur_stripped)
                if not m2:
                    break
                item = m2.group(1).strip()
                i += 1
                # continuation lines indented by 2+ spaces
                while i < len(lines):
                    nxt = lines[i].rstrip()
                    if not nxt.strip():
                        i += 1
                        break
                    if re.match(r'^\s{2,}\S', nxt) and not re.match(r'^\s*[-*]\s+', nxt):
                        item += ' ' + nxt.strip()
                        i += 1
                    else:
                        break
                items.append(item)
            blocks.append(BulletList(items))
            continue

        para_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            nxts = nxt.strip()
            if not nxts:
                i += 1
                break
            if nxts == '---' or re.match(r'^(#{1,6})\s+', nxts) or re.match(r'^[-*]\s+', nxts):
                break
            if is_table_row(nxts) and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1].strip()):
                break
            para_lines.append(nxts)
            i += 1
        blocks.append(Paragraph(' '.join(para_lines)))
    return blocks


def build_elements(doc, blocks: List[Block], styles_map) -> List[Element]:
    result: List[Element] = []
    for block in blocks:
        if isinstance(block, Heading):
            h = text.H(outlinelevel=min(block.level, 6))
            add_inline_markdown(h, block.content, styles_map['bold'].getAttribute('name'))
            result.append(h)
        elif isinstance(block, Paragraph):
            p = text.P()
            add_inline_markdown(p, block.content, styles_map['bold'].getAttribute('name'))
            result.append(p)
        elif isinstance(block, BulletList):
            lst = text.List()
            for item_text in block.items:
                li = text.ListItem()
                p = text.P()
                add_inline_markdown(p, item_text, styles_map['bold'].getAttribute('name'))
                li.addElement(p)
                lst.addElement(li)
            result.append(lst)
        elif isinstance(block, MdTable):
            t = table.Table(stylename=styles_map['table'])
            col_count = max(len(block.headers), max((len(r) for r in block.rows), default=0))
            for _ in range(col_count):
                t.addElement(table.TableColumn(stylename=styles_map['col']))
            # header
            tr = table.TableRow()
            for head in block.headers:
                cell = table.TableCell(valuetype='string', stylename=styles_map['head_cell'])
                p = text.P()
                add_inline_markdown(p, head, styles_map['bold'].getAttribute('name'))
                cell.addElement(p)
                tr.addElement(cell)
            t.addElement(tr)
            # rows
            for row in block.rows:
                tr = table.TableRow()
                padded = row + [''] * (col_count - len(row))
                for cell_text in padded:
                    cell = table.TableCell(valuetype='string', stylename=styles_map['cell'])
                    p = text.P()
                    add_inline_markdown(p, cell_text, styles_map['bold'].getAttribute('name'))
                    cell.addElement(p)
                    tr.addElement(cell)
                t.addElement(tr)
            result.append(t)
        elif isinstance(block, HorizontalRule):
            p = text.P()
            teletype.addTextToElement(p, '—' * 60)
            result.append(p)
    return result


def main():
    base = Path(R"C:\git\Schlegel\IOLink\Issue\_57")
    template = base / 'Angebot_Blank_2.odt'
    md_file = base / 'ANGEBOTSTEXT.md'
    output = base / 'Angebot_Aus_MD2.odt'

    doc = load(str(template))
    styles_map = add_styles(doc)

    # update template date in the header if present
    replace_text_in_template(doc, '24.10.24', TODAY.strftime('%d.%m.%Y'))

    md_text = md_file.read_text(encoding='utf-8')
    md_text = md_text.replace('[Heute]', TODAY.strftime('%d.%m.%Y'))
    md_text = md_text.replace('[Datum + 14 Tage]', (TODAY + timedelta(days=14)).strftime('%d.%m.%Y'))
    md_text = md_text.replace('[Ihr Name]', 'Daniel Franke')

    blocks = parse_markdown(md_text)
    elements = build_elements(doc, blocks, styles_map)

    # Insert after the existing content table; keep final empty paragraph.
    body = doc.text
    insert_at = len(body.childNodes)
    if insert_at > 0 and body.childNodes[-1].qname[1] == 'p':
        insert_at -= 1

    # add spacer before content
    spacer = text.P()
    teletype.addTextToElement(spacer, '')
    body.insertBefore(spacer, body.childNodes[insert_at] if insert_at < len(body.childNodes) else None)

    for element in elements:
        body.insertBefore(element, body.childNodes[insert_at + 1] if insert_at + 1 < len(body.childNodes) else None)
        insert_at += 1

    doc.save(str(output))
    print(f'Created {output}')


if __name__ == '__main__':
    main()

"""
Gera um PDF a partir de um markdown usando markdown + reportlab.

Estratégia: usa o markdown para gerar tokens "block-level" (heading, paragraph,
list, code, table, blockquote, hr) e renderiza cada um como um flowable do
reportlab. Inline (negrito, itálico, código) é tratado com regex.
"""
import re
import sys
from pathlib import Path

import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=20, leading=24,
                             spaceBefore=18, spaceAfter=10, textColor=colors.HexColor("#1a365d")),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=15, leading=19,
                             spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#2c5282")),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontSize=12.5, leading=16,
                             spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#2b6cb0")),
        "h4": ParagraphStyle("h4", parent=base["Heading4"], fontSize=11.5, leading=15,
                             spaceBefore=8, spaceAfter=3, textColor=colors.HexColor("#3182ce")),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=10, leading=14,
                               spaceAfter=6, alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=10, leading=14,
                                 leftIndent=14, bulletIndent=2, spaceAfter=2),
        "code": ParagraphStyle("code", parent=base["Code"], fontName="Courier", fontSize=8.5,
                               leading=11, leftIndent=8, rightIndent=8,
                               spaceBefore=4, spaceAfter=8, backColor=colors.HexColor("#f5f5f5"),
                               borderColor=colors.HexColor("#dddddd"), borderWidth=0.5,
                               borderPadding=6, textColor=colors.HexColor("#1a202c")),
        "quote": ParagraphStyle("quote", parent=base["BodyText"], fontSize=10, leading=14,
                                leftIndent=14, textColor=colors.HexColor("#4a5568"), spaceAfter=6),
        "table_cell": ParagraphStyle("table_cell", parent=base["BodyText"], fontSize=9, leading=12),
        "table_header": ParagraphStyle("table_header", parent=base["BodyText"], fontSize=9, leading=12,
                                       textColor=colors.whitesmoke, fontName="Helvetica-Bold"),
    }


def render_inline(text: str) -> str:
    """Renderiza marcações inline do markdown para tags de reportlab."""
    # Escapa primeiro
    out = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Código inline
    out = re.sub(r"`([^`]+)`", r'<font face="Courier" color="#c7254e">\1</font>', out)
    # Negrito
    out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
    # Itálico (sem confundir com negrito)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", out)
    # Links
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<font color="#3182ce"><u>\1</u></font>', out)
    return out


# ── Parser simples em blocos ──────────────────────────────────────────────────
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE   = re.compile(r"^```(\w*)\s*$")
HR_RE      = re.compile(r"^(\*\s*\*\s*\*|-\s*-\s*-|_{3,})\s*$")
UL_RE      = re.compile(r"^(\s*)[-*+]\s+(.*)$")
OL_RE      = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
BQ_RE      = re.compile(r"^>\s?(.*)$")
TABLE_SEP  = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


def parse_blocks(md_text: str) -> list:
    """Quebra o markdown em uma lista de blocos (dict com 'type' e 'content')."""
    lines = md_text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    def blank():
        return i < n and lines[i].strip() == ""

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Linha em branco
        if stripped == "":
            i += 1
            continue

        # Fenced code
        m = FENCE_RE.match(line)
        if m:
            lang = m.group(1) or ""
            i += 1
            buf = []
            while i < n and not FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1  # pula linha de fechamento
            blocks.append({"type": "code", "lang": lang, "content": "\n".join(buf)})
            continue

        # Heading
        m = HEADING_RE.match(line)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue

        # HR
        if HR_RE.match(line):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Tabela: começa com |, segunda linha deve ser separadora
        if stripped.startswith("|") and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2  # pula header + sep
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue

        # Blockquote
        if BQ_RE.match(line):
            buf = []
            while i < n and BQ_RE.match(lines[i]):
                buf.append(BQ_RE.match(lines[i]).group(1))
                i += 1
            blocks.append({"type": "blockquote", "text": "\n".join(buf)})
            continue

        # Lista
        if UL_RE.match(line) or OL_RE.match(line):
            ordered = bool(OL_RE.match(line))
            items = []
            while i < n:
                m_u = UL_RE.match(lines[i])
                m_o = OL_RE.match(lines[i])
                if ordered and m_o:
                    items.append(m_o.group(3))
                    i += 1
                elif (not ordered) and m_u:
                    items.append(m_u.group(2))
                    i += 1
                else:
                    break
            blocks.append({"type": "list", "ordered": ordered, "items": items})
            continue

        # Parágrafo: junta linhas consecutivas até blank
        buf = [line]
        i += 1
        while i < n and lines[i].strip() != "" and not HEADING_RE.match(lines[i]) \
                and not FENCE_RE.match(lines[i]) and not UL_RE.match(lines[i]) \
                and not OL_RE.match(lines[i]) and not BQ_RE.match(lines[i]) \
                and not HR_RE.match(lines[i]):
            buf.append(lines[i])
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(s.strip() for s in buf)})

    return blocks


def blocks_to_flowables(blocks: list, styles: dict) -> list:
    flowables = []
    for b in blocks:
        t = b["type"]
        if t == "heading":
            style = styles[f"h{min(b['level'], 4)}"]
            flowables.append(Paragraph(render_inline(b["text"]), style))
        elif t == "paragraph":
            flowables.append(Paragraph(render_inline(b["text"]), styles["body"]))
        elif t == "code":
            code = b["content"].rstrip()
            flowables.append(Preformatted(code, styles["code"]))
        elif t == "hr":
            flowables.append(Spacer(1, 6))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
            flowables.append(Spacer(1, 6))
        elif t == "blockquote":
            flowables.append(Paragraph(render_inline(b["text"]), styles["quote"]))
        elif t == "list":
            for n, item in enumerate(b["items"], start=1):
                bullet = f"{n}." if b["ordered"] else "•"
                flowables.append(Paragraph(f"{bullet} {render_inline(item)}", styles["bullet"]))
        elif t == "table":
            data = [[Paragraph(render_inline(h), styles["table_header"]) for h in b["header"]]]
            for row in b["rows"]:
                # garante que a linha tenha o mesmo nº de colunas
                while len(row) < len(b["header"]):
                    row.append("")
                data.append([Paragraph(render_inline(c), styles["table_cell"]) for c in row])
            tbl = Table(data, hAlign="LEFT", repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ]))
            flowables.append(tbl)
            flowables.append(Spacer(1, 6))
    return flowables


def main():
    if len(sys.argv) < 3:
        print("Uso: md_to_pdf.py entrada.md saida.pdf")
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    md_text = src.read_text(encoding="utf-8")
    # força processamento do markdown (apenas para validar que o texto é ok)
    _ = markdown.markdown(md_text, extensions=["fenced_code", "tables", "sane_lists"])

    blocks = parse_blocks(md_text)
    styles = build_styles()
    flowables = blocks_to_flowables(blocks, styles)

    doc = SimpleDocTemplate(
        str(dst), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Randongeon — Guia de Estudo (Backend / POO)",
        author="Grupo Randongeon",
    )
    doc.build(flowables)
    print(f"OK: {dst}  ({dst.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

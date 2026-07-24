#!/usr/bin/env python3
"""Generate DOI-identified editorial revisions of Axion papers and reports."""
from __future__ import annotations

import base64
import hashlib
import io
import re
import zlib
from pathlib import Path

import markdown
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[2]
PAPERS = ROOT / "lotofacil_axion" / "docs" / "papers"
REPORTS = ROOT / "lotofacil_axion" / "docs" / "reports"
DOI = "10.5281/zenodo.21522330"
DOI_URL = f"https://doi.org/{DOI}"

ARTICLE_TARGETS = {
    "article_01_source": "artigo_01_resultados_intermediarios_v1.0.1.pdf",
    "article_02_source": "artigo_02_otimizacao_combinatoria_exata_v2.0.1.pdf",
}

REPORT_TARGETS = {
    "relatorio_tecnico_01_robustez_mineracao_parametros.pdf": "relatorio_tecnico_01_robustez_mineracao_parametros_v1.0.1.pdf",
    "relatorio_tecnico_02_otimizacao_multiobjetivo_carteiras.pdf": "relatorio_tecnico_02_otimizacao_multiobjetivo_carteiras_v1.0.1.pdf",
    "relatorio_tecnico_03_limites_exatos_11_12_13.pdf": "relatorio_tecnico_03_limites_exatos_11_12_13_v1.0.1.pdf",
    "relatorio_tecnico_04_fronteira_orcamento_eficiencia_marginal.pdf": "relatorio_tecnico_04_fronteira_orcamento_eficiencia_marginal_v1.0.1.pdf",
}


def decode_sources() -> None:
    payload_dir = PAPERS / "source_payloads"
    for stem in ARTICLE_TARGETS:
        encoded = (payload_dir / f"{stem}.zlib.b64").read_text(encoding="utf-8").strip()
        text = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
        (PAPERS / f"{stem}.md").write_text(text, encoding="utf-8")


def article_css() -> str:
    return """
    @page { size: A4; margin: 22mm 20mm 20mm 22mm;
      @bottom-center { content: "Modelo Axion Lotofácil - documentação técnica DOI 10.5281/zenodo.21522330";
        font-size: 8pt; color: #555; } }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 10.2pt;
      line-height: 1.38; color: #202124; text-align: justify; }
    h1 { color: #164b7a; font-size: 15pt; margin-top: 18pt; page-break-after: avoid; }
    h2 { color: #164b7a; font-size: 12.5pt; margin-top: 14pt; page-break-after: avoid; }
    h3 { color: #164b7a; font-size: 11pt; page-break-after: avoid; }
    p { margin: 0 0 7pt 0; }
    table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt 0; font-size: 8.4pt; }
    th, td { border: 0.6pt solid #8aa0b5; padding: 4pt; vertical-align: top; }
    th { background: #dce8f2; font-weight: bold; }
    blockquote { margin: 8pt 18pt; color: #333; }
    a { color: #164b7a; text-decoration: none; }
    ul, ol { margin-top: 3pt; margin-bottom: 8pt; }
    code { font-family: monospace; font-size: 9pt; }
    """


def render_articles() -> None:
    for stem, filename in ARTICLE_TARGETS.items():
        md_path = PAPERS / f"{stem}.md"
        text = md_path.read_text(encoding="utf-8")
        body = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "sane_lists", "smarty"],
            output_format="html5",
        )
        html = f"<!doctype html><html><head><meta charset='utf-8'><style>{article_css()}</style></head><body>{body}</body></html>"
        HTML(string=html, base_url=str(PAPERS)).write_pdf(PAPERS / filename)


def cover_page(title: str) -> bytes:
    buff = io.BytesIO()
    doc = SimpleDocTemplate(
        buff,
        pagesize=A4,
        rightMargin=24 * mm,
        leftMargin=24 * mm,
        topMargin=26 * mm,
        bottomMargin=24 * mm,
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="AxionTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=HexColor("#164b7a"), spaceAfter=16))
    styles.add(ParagraphStyle(name="AxionBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=11, leading=16, alignment=4, spaceAfter=11))
    story = [
        Paragraph("MODELO AXION LOTOFÁCIL", styles["AxionTitle"]),
        Paragraph(title, styles["Heading1"]),
        Spacer(1, 18),
        Paragraph("Revisão editorial 1.0.1", styles["AxionBody"]),
        Paragraph("Esta revisão acrescenta a identificação do DOI e formaliza os endereços permanentes. Os métodos, resultados, tabelas e conclusões da versão arquivada 1.0 permanecem inalterados.", styles["AxionBody"]),
        Spacer(1, 18),
        Paragraph(f"DOI da versão arquivada 1.0: <link href='{DOI_URL}'>{DOI}</link>", styles["AxionBody"]),
        Paragraph("Referência: NASCIMENTO, Jacson Cruz do. Modelo Axion Lotofácil: série de relatórios técnicos nº 1–4. Versão 1.0. Brasília, 2026. Zenodo.", styles["AxionBody"]),
        Spacer(1, 24),
        Paragraph("Documento técnico não submetido à revisão por pares. Não constitui recomendação financeira nem garantia de premiação.", styles["AxionBody"]),
    ]
    doc.build(story)
    return buff.getvalue()


def footer_overlay(width: float, height: float) -> bytes:
    buff = io.BytesIO()
    c = canvas.Canvas(buff, pagesize=(width, height))
    c.setFillColor(HexColor("#555555"))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(width / 2, 10 * mm, f"Revisão editorial 1.0.1 | DOI da versão arquivada: {DOI}")
    c.save()
    return buff.getvalue()


def title_from_filename(filename: str) -> str:
    stem = filename.removesuffix(".pdf")
    stem = re.sub(r"^relatorio_tecnico_\d+_", "", stem)
    return stem.replace("_", " ").capitalize()


def revise_report(source: Path, target: Path) -> None:
    source_reader = PdfReader(source)
    writer = PdfWriter()
    cover = PdfReader(io.BytesIO(cover_page(title_from_filename(source.name))))
    writer.add_page(cover.pages[0])
    for page in source_reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay = PdfReader(io.BytesIO(footer_overlay(width, height))).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)
    writer.add_metadata({
        "/Title": f"{title_from_filename(source.name)} - revisão 1.0.1",
        "/Author": "Jacson Cruz do Nascimento",
        "/Subject": f"Modelo Axion Lotofácil - DOI {DOI}",
        "/Keywords": "Lotofácil; combinatória; otimização; DOI; Zenodo",
    })
    with target.open("wb") as handle:
        writer.write(handle)


def render_reports() -> None:
    for source_name, target_name in REPORT_TARGETS.items():
        revise_report(REPORTS / source_name, REPORTS / target_name)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums() -> None:
    report_lines = []
    for target in REPORT_TARGETS.values():
        path = REPORTS / target
        report_lines.append(f"{sha256(path)}  {path.name}")
    (REPORTS / "CHECKSUMS_v1.0.1.sha256").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    paper_lines = []
    for target in ARTICLE_TARGETS.values():
        path = PAPERS / target
        paper_lines.append(f"{sha256(path)}  {path.name}")
    (PAPERS / "CHECKSUMS_DOI_REVISIONS.sha256").write_text("\n".join(paper_lines) + "\n", encoding="utf-8")


def main() -> None:
    PAPERS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    decode_sources()
    render_articles()
    render_reports()
    write_checksums()
    print("DOI revisions generated successfully.")


if __name__ == "__main__":
    main()

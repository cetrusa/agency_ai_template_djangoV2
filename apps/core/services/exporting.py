from __future__ import annotations

import csv
import importlib
from io import BytesIO
from typing import Iterable
from datetime import datetime

from django.http import FileResponse, StreamingHttpResponse
from django.utils import timezone


class _Echo:
    """File-like adapter for csv.writer streaming."""

    def write(self, value: str) -> str:  # pragma: no cover
        return value


def _default_filename(base: str, ext: str) -> str:
    ts = timezone.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in base.strip())
    safe = safe or "export"
    return f"{safe}_{ts}.{ext}"


def _convert_datetime(value):
    """Convierte datetimes con timezone a naive para Excel."""
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def stream_csv(
    *,
    queryset,
    fields: list[str],
    headers: list[str],
    filename_base: str = "export",
) -> StreamingHttpResponse:
    """Stream CSV without loading all rows in memory."""

    if len(fields) != len(headers):
        raise ValueError("fields y headers deben tener el mismo tamaño")

    pseudo_buffer = _Echo()
    writer = csv.writer(pseudo_buffer)

    def row_iter() -> Iterable[bytes]:
        # UTF-8 BOM ayuda a Excel a detectar UTF-8 correctamente.
        yield b"\xef\xbb\xbf"
        yield writer.writerow(headers).encode("utf-8")
        for row in queryset.values_list(*fields).iterator(chunk_size=2000):
            yield writer.writerow(["" if v is None else v for v in row]).encode("utf-8")

    resp = StreamingHttpResponse(row_iter(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{_default_filename(filename_base, "csv")}"'
    return resp


def build_xlsx(
    *,
    queryset,
    fields: list[str],
    headers: list[str],
    filename_base: str = "export",
    sheet_name: str = "Export",
) -> FileResponse:
    """Generate XLSX (Excel). Uses write_only mode to reduce memory, but returns a bytes response."""

    if len(fields) != len(headers):
        raise ValueError("fields y headers deben tener el mismo tamaño")

    try:
        openpyxl = importlib.import_module("openpyxl")
        Workbook = getattr(openpyxl, "Workbook")
    except Exception as e:
        raise RuntimeError("Dependencia faltante: openpyxl") from e

    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title=sheet_name[:31])

    ws.append(headers)
    for row in queryset.values_list(*fields).iterator(chunk_size=2000):
        # Convertir datetimes con timezone a naive para Excel
        converted_row = [_convert_datetime(v) for v in row]
        ws.append(list(converted_row))

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = _default_filename(filename_base, "xlsx")
    return FileResponse(
        bio,
        as_attachment=True,
        filename=filename,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def build_pdf_table(
    *,
    queryset,
    fields: list[str],
    headers: list[str],
    title: str = "Export",
    filename_base: str = "export",
) -> FileResponse:
    """Generate a simple professional PDF table (landscape) with header title + date."""

    if len(fields) != len(headers):
        raise ValueError("fields y headers deben tener el mismo tamaño")

    try:
        colors = importlib.import_module("reportlab.lib.colors")
        pagesizes = importlib.import_module("reportlab.lib.pagesizes")
        styles_mod = importlib.import_module("reportlab.lib.styles")
        platypus = importlib.import_module("reportlab.platypus")
        tables_mod = importlib.import_module("reportlab.platypus.tables")
        A4 = getattr(pagesizes, "A4")
        landscape = getattr(pagesizes, "landscape")
        getSampleStyleSheet = getattr(styles_mod, "getSampleStyleSheet")
        LongTable = getattr(platypus, "LongTable")
        Paragraph = getattr(platypus, "Paragraph")
        SimpleDocTemplate = getattr(platypus, "SimpleDocTemplate")
        Spacer = getattr(platypus, "Spacer")
        TableStyle = getattr(tables_mod, "TableStyle")
    except Exception as e:
        raise RuntimeError("Dependencia faltante: reportlab") from e

    now = timezone.localtime(timezone.now())
    subtitle = now.strftime("%Y-%m-%d %H:%M")

    # Construimos data (header + rows). Para PDFs muy grandes, esto puede crecer.
    data: list[list[str]] = [headers]
    for row in queryset.values_list(*fields).iterator(chunk_size=2000):
        data.append(["" if v is None else str(v) for v in row])

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
        title=title,
    )

    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Paragraph(subtitle, styles["Normal"]),
        Spacer(1, 12),
    ]

    table = LongTable(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D5DD")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)
    doc.build(story)

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=_default_filename(filename_base, "pdf"),
        content_type="application/pdf",
    )

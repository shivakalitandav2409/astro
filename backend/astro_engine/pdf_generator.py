"""PDF generator for Platinum Kundali reports and Store/Portal invoices."""

from __future__ import annotations

from typing import Any
from fpdf import FPDF


def _safe_ascii(val: Any) -> str:
    return str(val).encode("latin-1", "replace").decode("latin-1")


def generate_kundli_pdf(bundle: dict[str, Any]) -> bytes:
    member = bundle["member"]
    chart = bundle["chart"]
    dashas = bundle["dashas"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(pdf.epw, 10, _safe_ascii(f"Vashist Jyotish Kundali Report - {member['name']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        pdf.epw,
        7,
        _safe_ascii(
            f"DOB: {member['dob']} | Time: {member['birth_time']} | Place: {member['place_name']} "
            f"({member['latitude']}, {member['longitude']}) | Plan: {member['plan_name']}"
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        pdf.epw,
        7,
        _safe_ascii(f"Ascendant (Lagna): {chart['ascendant']['rashi']} {chart['ascendant']['dms']} | Lahiri Ayanamsa: {chart['ayanamsa']}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(pdf.epw, 8, "Planetary Positions (Sidereal Lahiri)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for p in chart["planets"]:
        retro = " (R)" if p["retrograde"] else ""
        line = (
            f"{p['planet']:8s} | H{p['house']:<2d} | {p['rashi']:<22s} | {p['dms']:<10s} | "
            f"{p['nakshatra']} (P{p['pada']}) | {p['dignity']}{retro}"
        )
        pdf.cell(pdf.epw, 6, _safe_ascii(line), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(pdf.epw, 8, "Vimshottari Mahadasha Periods", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for md in dashas["mahadashas"]:
        mark = " [CURRENT]" if md["is_current"] else ""
        pdf.cell(
            pdf.epw,
            6,
            _safe_ascii(f"{md['planet']:8s} | {md['start_date']} to {md['end_date']} ({md['duration_years']} yrs){mark}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(pdf.epw, 8, "12-Ghar Summary & Remedies", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    for gp in bundle["ghar_predictions"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(
            pdf.epw,
            4.8,
            _safe_ascii(f"House {gp['house']} ({gp['theme']}): {gp['prediction']} Remedy: {gp['upay']}"),
        )
        pdf.ln(1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(pdf.epw, 5, _safe_ascii("ASTRO · Explore the Cosmos & Destiny | Developed by Shivang Saxena"), new_x="LMARGIN", new_y="NEXT", align="C")

    return bytes(pdf.output())


def generate_order_invoice_pdf(order: dict[str, Any], items: list[dict[str, Any]], account: dict[str, Any]) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(pdf.epw, 10, "GDV Panel & AstroScience Unified - Tax Invoice", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(pdf.epw, 6, _safe_ascii(f"Order #: {order['order_number']} | Date: {order['created_at'][:10]}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 6, _safe_ascii(f"Customer: {account['name']} ({account.get('email') or account.get('phone')})"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 6, _safe_ascii(f"Payment Ref: {order['razorpay_payment_id'] or order['razorpay_order_id']} | Status: {order['payment_status']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(pdf.epw, 7, "Line Items", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for it in items:
        pdf.cell(pdf.epw, 6, _safe_ascii(f"- {it['title']} x{it['quantity']}  =  INR {it['unit_price'] * it['quantity']}"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(pdf.epw, 7, _safe_ascii(f"Subtotal: INR {order['subtotal']} | Discount: INR {order['discount']} | Credits: INR {order['credits_used']} | GST: INR {order['gst']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 8, _safe_ascii(f"Total Paid: INR {order['total_amount']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(pdf.epw, 5, _safe_ascii("ASTRO · Explore the Cosmos & Destiny | Developed by Shivang Saxena"), new_x="LMARGIN", new_y="NEXT", align="C")

    return bytes(pdf.output())

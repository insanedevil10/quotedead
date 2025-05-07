
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def export_quote_to_pdf(filepath, project, rooms, quote_calculator):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    x_margin = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_margin, y, "Interior Design Execution Quote")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(x_margin, y, f"Client: {project.get('client_name', '')}")
    y -= 15
    c.drawString(x_margin, y, f"Location: {project.get('location', '')}")
    y -= 15
    c.drawString(x_margin, y, f"Project Type: {project.get('project_type', '')}")
    y -= 25

    for room in rooms:
        summary = quote_calculator.generate_room_summary(room)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, y, f"Room: {summary['room_name']}")
        y -= 18
        c.setFont("Helvetica", 10)
        for item in summary["items"]:
            line = f"- {item['name']} ({item['category']}): {item['quantity']} {item['uom']} @ ₹{item['unit_cost']} = ₹{item['total_cost']}"
            if y < 80:
                c.showPage()
                y = height - 50
            c.drawString(x_margin + 10, y, line)
            y -= 14
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(x_margin + 10, y, f"Room Total: ₹{summary['total']}")
        y -= 20
        if y < 80:
            c.showPage()
            y = height - 50

    grand_total = quote_calculator.calculate_project_total(rooms)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, f"Grand Total: ₹{grand_total}")
    c.showPage()
    c.save()

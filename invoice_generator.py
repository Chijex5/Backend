from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO

def generate_invoice(customer_name, address, date, method, purchases, output_filename, invoice_number, logo_path=None, stylish_ub_path=None):
    # Create the PDF document
    pdf = SimpleDocTemplate(output_filename, pagesize=A4)
    elements = []
    
    # Sample style for text
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = TA_CENTER
    title_style.fontSize = 24  # Make title font bigger
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Optional Logo: Stylish UB next to UNIBOOKS title
    if stylish_ub_path:
        ub_logo = Image(stylish_ub_path, 0.8 * inch, 0.8 * inch)
        ub_logo.hAlign = 'CENTER'
        elements.append(ub_logo)
    
    # Add Title (Unibooks Header)
    elements.append(Spacer(1, 0.2 * inch))  # Space before title
    elements.append(Paragraph(f"UNIBOOKS", title_style))
    
    # Invoice number and date on the right side
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Invoice #: {invoice_number}", normal_style))
    elements.append(Paragraph(f"Date: {date}", normal_style))
    
    # Customer information on the left side
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Invoice to: {customer_name}", normal_style))
    elements.append(Paragraph(f"{address}", normal_style))
    
    # Space before the table
    elements.append(Spacer(1, 0.3 * inch))
    
    # Create Table Data
    table_data = [["Book Code", "Quantity", "Unit Price", "Total"]]
    total_amount = 0
    
    for purchase in purchases:
        book_code = purchase['book_code']
        quantity = purchase['quantity']
        unit_price = purchase['unit_price']
        total_price = purchase['total_price']
        total_amount += total_price
        
        table_data.append([book_code, quantity, f"N{unit_price:.2f}", f"N{total_price:.2f}"])
    
    # Subtotal, Tax, and Total rows
    # Subtotal, Tax, and Total rows
    # Subtotal, Tax, and Total rows
    table_data.append(["", "", "Subtotal", f"N{total_amount:.2f}"])
    table_data.append(["", "", "Our Fees (10%)", f"N{method['tax']:.2f}"])
    table_data.append(["", "", "Total", f"N{total_amount + method['tax']:.2f}"])


    # Create Table
    table = Table(table_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])

    # Styling the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4caf50")),  # Green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.black),  # Borders for the book data only
        ('BACKGROUND', (0, 1), (-1, -4), colors.whitesmoke),  # Data rows
        ('TEXTCOLOR', (0, 1), (-1, -4), colors.black),
        ('BACKGROUND', (-2, -3), (-1, -1), colors.whitesmoke),  # Highlight for Subtotal, Tax, Total
        ('TEXTCOLOR', (-2, -3), (-1, -1), colors.black),
        ('FONTNAME', (-2, -3), (-1, -1), 'Helvetica-Bold'),  # Bold font for Subtotal, Tax, Total
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (-2, -3), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for the header row
        ('LINEBELOW', (0, 0), (-1, -4), 0.5, colors.black),  # Borders up to book data
        ('LINEABOVE', (-2, -3), (-1, -1), 0, colors.white),  # Remove borders for Subtotal, Tax, Total
    ])

    table.setStyle(table_style)

    
    elements.append(table)
    
    # Footer Section: Payment Information and Signature
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Payment Method: {method['type']}", normal_style))
    elements.append(Paragraph(f"Account Name: {method['account_name']}", normal_style))
    elements.append(Paragraph(f"Account No.: {method['account_number']}", normal_style))
    elements.append(Paragraph(f"Checked Out On: {method['pay_by']}", normal_style))
    
    
    # Signature and Thank You Message
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Authorized Signed", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Thank you for choosing Unibooks!", normal_style))
    
    # Build PDF
    pdf.build(elements)

# Example usage with logo
purchases = [
    {'book_code': 'STA211', 'quantity': 1, 'unit_price': 200, 'total_price': 200},
    {'book_code': 'STA231', 'quantity': 2, 'unit_price': 150, 'total_price': 300},
    {'book_code': 'COS201', 'quantity': 1, 'unit_price': 250, 'total_price': 250},
]

method = {
    "type" : "Bank Transfer",
    "account_name" : "John Doe",
    "account_number" : "0123 4567 8901",
    "pay_by" : "23 June 2023",
    "tax": 75
    }

generate_invoice(
    customer_name="John Doe",
    address="123 Anywhere St., Any City, ST 12345",
    date="2024-09-19",
    purchases=purchases,
    method=method,
    output_filename="custom_unibooks_invoice.pdf",
    invoice_number="52131",
    logo_path=None,  # Set your logo path here if available
    stylish_ub_path=r"uni2.png"  # Replace with UB logo path
)

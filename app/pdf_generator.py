from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import HRFlowable
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class RestaurantPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create elegant menu-style typography."""

        # Restaurant name - elegant serif font
        self.styles.add(ParagraphStyle(
            name='RestaurantName',
            parent=self.styles['Title'],
            fontSize=24,  # Smaller than before
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=28
        ))

        # Tagline - elegant italic
        self.styles.add(ParagraphStyle(
            name='Tagline',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Times-Italic',
            leading=14
        ))

        # Section headers - sophisticated style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#8B4513'),  # Saddle brown
            spaceAfter=8,
            spaceBefore=12,
            fontName='Times-Bold',
            alignment=TA_CENTER,
            leading=16
        ))

        # Menu category - understated elegance
        self.styles.add(ParagraphStyle(
            name='MenuCategory',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c2c2c'),
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            leading=14
        ))

        # Menu item name
        self.styles.add(ParagraphStyle(
            name='MenuItem',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold',
            leading=12
        ))

        # Menu item description
        self.styles.add(ParagraphStyle(
            name='MenuDescription',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#555555'),
            fontName='Helvetica',
            leading=10
        ))

        # Price style
        self.styles.add(ParagraphStyle(
            name='Price',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#8B4513'),
            fontName='Helvetica',
            alignment=TA_RIGHT
        ))

        # Compact body text
        self.styles.add(ParagraphStyle(
            name='CompactBody',
            parent=self.styles['BodyText'],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#333333')
        ))

    def _draw_decorative_line(self, canvas, doc):
        """Draw decorative elements on each page."""
        canvas.saveState()
        # Subtle border
        canvas.setStrokeColor(colors.HexColor('#d4af37'))  # Gold color
        canvas.setLineWidth(0.5)
        # Top and bottom decorative lines
        canvas.line(72, letter[1] - 50, letter[0] - 72, letter[1] - 50)
        canvas.line(72, 50, letter[0] - 72, 50)
        canvas.restoreState()

    def generate_pdf(self, restaurant_data):
        """Generate an elegant menu-style PDF."""
        buffer = io.BytesIO()

        # Smaller margins for menu feel
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=60,
            bottomMargin=40,
        )

        # Set up decorative page template
        doc.build_flowables = self._build_with_decoration

        elements = []

        concept = restaurant_data['concept']
        menu = restaurant_data['menu']
        metadata = restaurant_data['metadata']

        # Decorative divider
        def add_divider():
            elements.append(Spacer(1, 8))
            elements.append(HRFlowable(
                width="50%",
                thickness=0.5,
                color=colors.HexColor('#d4af37'),
                hAlign='CENTER'
            ))
            elements.append(Spacer(1, 8))

        # Header Section with elegant styling
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(concept['name'].upper(), self.styles['RestaurantName']))
        elements.append(Paragraph(f"~ {concept['tagline']} ~", self.styles['Tagline']))

        add_divider()

        # Compact info section
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )

        info_text = f"{metadata['cuisine']} • {metadata['style']} • {metadata['price_range']}"
        elements.append(Paragraph(info_text, info_style))

        elements.append(Spacer(1, 15))

        # Concept in a box
        concept_table = Table([[Paragraph(concept['concept'], self.styles['CompactBody'])]],
                              colWidths=[6.5 * inch])
        concept_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d4af37')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(concept_table)

        elements.append(Spacer(1, 15))

        # Signature Dish - Highlighted
        sig_dish_data = [[
            Paragraph("⭐ SIGNATURE DISH", ParagraphStyle(
                'SigTitle',
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#8B4513')
            )),
            Paragraph(concept['signature_dish'], ParagraphStyle(
                'SigDesc',
                fontSize=9,
                fontName='Helvetica-Oblique',
                textColor=colors.HexColor('#333333')
            ))
        ]]

        sig_table = Table(sig_dish_data, colWidths=[1.5 * inch, 5 * inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('RIGHTPADDING', (0, 0), (0, 0), 10),
        ]))
        elements.append(sig_table)

        add_divider()

        # Menu Header
        elements.append(Paragraph("MENU", ParagraphStyle(
            'MenuHeader',
            fontSize=16,
            fontName='Times-Bold',
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=15
        )))

        # Menu Sections with two-column layout for mains
        menu_sections = [
            ('appetizers', 'Starters'),
            ('mains', 'Main Courses'),
            ('desserts', 'Sweet Endings'),
            ('beverages', 'Drinks')
        ]

        for section_key, section_title in menu_sections:
            if section_key in menu and menu[section_key]:
                # Section header with decorative elements
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(
                    f"~ {section_title.upper()} ~",
                    self.styles['MenuCategory']
                ))
                elements.append(Spacer(1, 8))

                # Create menu items
                menu_data = []
                for item in menu[section_key]:
                    # Format dietary info
                    dietary_text = ""
                    if item.get('dietary'):
                        dietary_text = f" <font size='7' color='#7cb342'>({', '.join(item['dietary'])})</font>"

                    # Item name and description in one cell
                    item_content = f"<b>{item['name']}</b>{dietary_text}<br/>"
                    item_content += f"<font size='8' color='#666666'>{item['description']}</font>"

                    # Price with dots leading to it
                    price_text = f"<font color='#8B4513'>{item['price']}</font>"

                    menu_data.append([
                        Paragraph(item_content, self.styles['Normal']),
                        Paragraph(price_text, self.styles['Price'])
                    ])

                # Create table with elegant styling
                if section_key == 'mains':
                    # Mains get more space
                    col_widths = [5.5 * inch, 0.8 * inch]
                else:
                    col_widths = [5.3 * inch, 0.8 * inch]

                menu_table = Table(menu_data, colWidths=col_widths)
                menu_table.setStyle(TableStyle([
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    # Add subtle dots between items and prices
                    ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.HexColor('#e0e0e0')),
                ]))
                elements.append(menu_table)

        # Footer
        elements.append(Spacer(1, 30))
        add_divider()

        # USPs in elegant footer
        elements.append(Paragraph("Why Choose Us", ParagraphStyle(
            'FooterTitle',
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.HexColor('#8B4513')
        )))
        elements.append(Spacer(1, 5))

        usp_text = " • ".join(concept['unique_selling_points'])
        elements.append(Paragraph(
            usp_text,
            ParagraphStyle(
                'USP',
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#666666'),
                leftIndent=20,
                rightIndent=20
            )
        ))

        elements.append(Spacer(1, 15))

        # Generated by footer
        footer_text = f"ConceptKitchen • {datetime.now().strftime('%B %Y')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )))

        # Build PDF
        doc.build(elements, onFirstPage=self._draw_decorative_line,
                onLaterPages=self._draw_decorative_line)
        buffer.seek(0)
        return buffer

    def _build_with_decoration(self, flowables):
        """Custom build method to add page decorations."""
        self.build(flowables, onFirstPage=self._draw_decorative_line,
                   onLaterPages=self._draw_decorative_line)
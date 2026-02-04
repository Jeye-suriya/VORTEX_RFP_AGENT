

import os
from fpdf import FPDF
from datetime import datetime

def get_noto_serif_font():
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_path = os.path.join(font_dir, 'NotoSerif-Regular.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(
            f"NotoSerif-Regular.ttf not found in {font_dir}. Please download it from https://fonts.google.com/specimen/Noto+Serif and place it in the 'fonts' folder."
        )
    return font_path








class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('NotoSerif', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.set_text_color(0, 0, 0)

def create_proposal_pdf(proposal: dict, filename: str):
    font_path = get_noto_serif_font()
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font('NotoSerif', '', font_path, uni=True)
    pdf.add_font('NotoSerif', 'B', font_path, uni=True)
    pdf.add_font('NotoSerif', 'I', font_path, uni=True)

    # Title page with logo placeholder
    pdf.add_page()
    logo_path = os.path.join(os.path.dirname(__file__), 'fonts', 'logo.png')
    # Center and enlarge logo
    if os.path.exists(logo_path):
        # Calculate center x for large logo
        logo_width = 120
        page_width = pdf.w - pdf.l_margin - pdf.r_margin
        x_center = (page_width - logo_width) / 2 + pdf.l_margin
        pdf.image(logo_path, x=x_center, y=20, w=logo_width)
    # Add large 'Proposal' note in the middle
    pdf.set_y(100)
    pdf.set_font("NotoSerif", 'B', 38)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 30, "PROPOSAL", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    # Add file name (if available) with extra spacing below 'PROPOSAL'
    if filename:
        pdf.ln(10)
        pdf.set_font("NotoSerif", '', 18)
        pdf.cell(0, 16, os.path.basename(filename), ln=True, align='C')
    # Add date at the bottom center of the title page only
    pdf.set_y(pdf.h - 30)
    pdf.set_font("NotoSerif", '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(10)
    # Executive summary will be on its own section page, not title page

    # Table of Contents (table format)
    sections = proposal.get('sections', [])
    section_start_pages = []
    # Reserve TOC page, will fill later
    pdf.add_page()
    toc_page = pdf.page_no()
    pdf.set_font("NotoSerif", 'B', 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Table of Contents", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)
    pdf.set_font("NotoSerif", 'B', 13)
    # Table header
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(15, 10, "S.No", border=1, fill=True, align='C')
    pdf.cell(120, 10, "Title", border=1, fill=True, align='C')
    pdf.cell(0, 10, "Pg.No", border=1, ln=True, fill=True, align='C')
    pdf.set_font("NotoSerif", '', 13)
    toc_y_start = pdf.get_y()
    toc_row_height = 10
    toc_rows = len(sections)
    for _ in range(toc_rows):
        pdf.cell(15, toc_row_height, "", border=1)
        pdf.cell(120, toc_row_height, "", border=1)
        pdf.cell(0, toc_row_height, "", border=1, ln=True)
    pdf.ln(4)

    # Render sections and track their start pages
    for sec in sections:
        pdf.add_page()
        section_start_pages.append(pdf.page_no())
        pdf.set_font("NotoSerif", 'B', 14)
        pdf.cell(0, 8, sec.get('title'), ln=True)
        pdf.ln(2)
        pdf.set_font("NotoSerif", '', 11)
        content = sec.get('content', '')
        def expand_content(text):
            return text
        if 'pricing' in sec['title'].lower():
            pricing = proposal.get('pricing', {})
            line_items = pricing.get('line_items', [])
            scenarios = pricing.get('scenarios', {})
            if line_items:
                pdf.set_font("NotoSerif", 'B', 12)
                pdf.cell(0, 8, "Pricing Breakdown", ln=True)
                pdf.set_font("NotoSerif", '', 11)
                col_widths = [40, 25, 35, 80]
                pdf.set_fill_color(220, 220, 220)
                pdf.cell(col_widths[0], 8, "Requirement", border=1, fill=True)
                pdf.cell(col_widths[1], 8, "Hours", border=1, fill=True)
                pdf.cell(col_widths[2], 8, "Cost", border=1, fill=True)
                pdf.cell(col_widths[3], 8, "Notes", border=1, ln=True, fill=True)
                for item in line_items:
                    y_before = pdf.get_y()
                    x_left = pdf.get_x()
                    req = str(item.get('requirement_id', ''))
                    hrs = str(item.get('hours', ''))
                    cost = f"${item.get('cost', 0):,.2f}"
                    notes = str(item.get('notes', ''))
                    notes_lines = pdf.multi_cell(col_widths[3], 8, notes, border=0, align='L', split_only=True)
                    n_lines = len(notes_lines)
                    row_height = max(8, 8 * n_lines)
                    pdf.set_xy(x_left, y_before)
                    pdf.cell(col_widths[0], row_height, req, border=1)
                    pdf.cell(col_widths[1], row_height, hrs, border=1)
                    pdf.cell(col_widths[2], row_height, cost, border=1)
                    x_notes = pdf.get_x()
                    y_notes = pdf.get_y()
                    pdf.multi_cell(col_widths[3], 8, notes, border=1, align='L')
                    pdf.set_xy(x_left, y_before + row_height)
                pdf.ln(4)
                pdf.set_font("NotoSerif", 'B', 12)
                pdf.cell(0, 8, "Pricing Scenarios", ln=True)
                pdf.set_font("NotoSerif", '', 11)
                pdf.cell(50, 8, "Scenario", border=1, fill=True)
                pdf.cell(0, 8, "Total Cost", border=1, ln=True, fill=True)
                for label, value in scenarios.items():
                    pdf.cell(50, 8, label.capitalize(), border=1)
                    pdf.cell(0, 8, f"${value:,.2f}", border=1, ln=True)
                pdf.ln(4)
            if content:
                pdf.multi_cell(0, 6, expand_content(content))
        else:
            if content:
                pdf.multi_cell(0, 6, expand_content(content))
            if 'solution' in sec['title'].lower():
                chart_path = os.path.join(os.path.dirname(__file__), 'solution_chart.png')
                if os.path.exists(chart_path):
                    pdf.ln(4)
                    pdf.image(chart_path, x=30, w=150)
        pdf.ln(2)

    # Fill in the TOC table with section info and page numbers
    pdf.page = toc_page
    pdf.set_y(toc_y_start)
    pdf.set_font("NotoSerif", '', 13)
    for idx, sec in enumerate(sections, start=1):
        pdf.cell(15, toc_row_height, str(idx), border=1, align='C')
        pdf.cell(120, toc_row_height, sec.get('title', ''), border=1)
        pdf.cell(0, toc_row_height, str(section_start_pages[idx-1]), border=1, ln=True, align='C')

    # Footer and save
    pdf.output(filename)







    font_path = get_noto_serif_font()
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font('NotoSerif', '', font_path, uni=True)
    pdf.add_font('NotoSerif', 'B', font_path, uni=True)
    pdf.add_font('NotoSerif', 'I', font_path, uni=True)

    # Title page
    pdf.add_page()
    pdf.set_font("NotoSerif", 'B', 20)
    pdf.cell(0, 12, f"Proposal: {proposal.get('client', 'Client')}", ln=True, align='C')
    pdf.ln(8)
    pdf.set_font("NotoSerif", '', 12)
    pdf.cell(0, 8, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}", ln=True, align='C')

    # Table of Contents (simple list)
    pdf.add_page()
    pdf.set_font("NotoSerif", 'B', 14)
    pdf.cell(0, 8, "Table of Contents", ln=True)
    pdf.ln(4)
    pdf.set_font("NotoSerif", '', 12)
    sections = proposal.get('sections', [])
    for idx, sec in enumerate(sections, start=1):
        pdf.cell(0, 6, f"{idx}. {sec.get('title')}", ln=True)
    pdf.ln(6)

    # Render sections with headings and richer content
    for sec in sections:
        pdf.add_page()
        pdf.set_font("NotoSerif", 'B', 18)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 12, sec.get('title'), ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)
        pdf.set_font("NotoSerif", '', 13)
        content = sec.get('content', '')
        # If this is the pricing section, render as table
        if 'pricing' in sec['title'].lower():
            pricing = proposal.get('pricing', {})
            line_items = pricing.get('line_items', [])
            scenarios = pricing.get('scenarios', {})
            if line_items:
                pdf.set_font("NotoSerif", 'B', 14)
                pdf.set_fill_color(220, 235, 255)
                pdf.cell(0, 10, "Pricing Breakdown", ln=True, fill=True)
                pdf.set_font("NotoSerif", '', 12)
                # Table header
                pdf.set_fill_color(220, 220, 220)
                pdf.cell(40, 10, "Requirement", border=1, fill=True)
                pdf.cell(25, 10, "Hours", border=1, fill=True)
                pdf.cell(35, 10, "Cost", border=1, fill=True)
                pdf.cell(0, 10, "Notes", border=1, ln=True, fill=True)
                # Table rows
                for item in line_items:
                    pdf.cell(40, 10, str(item.get('requirement_id', '')), border=1)
                    pdf.cell(25, 10, str(item.get('hours', '')), border=1)
                    pdf.cell(35, 10, f"${item.get('cost', 0):,.2f}", border=1)
                    # Wrap notes text in the cell
                    notes = str(item.get('notes', ''))
                    x = pdf.get_x()
                    y = pdf.get_y()
                    w = pdf.w - pdf.l_margin - pdf.r_margin - 100  # Remaining width for notes
                    h = pdf.font_size * (notes.count('\n') + 1) + 4
                    pdf.multi_cell(0, 10, notes, border=1)
                    pdf.set_xy(x + 100, y)  # Move to next row
                    pdf.ln(h - 10)
                pdf.ln(6)
                # Pricing scenarios
                pdf.set_font("NotoSerif", 'B', 14)
                pdf.set_fill_color(220, 235, 255)
                pdf.cell(0, 10, "Pricing Scenarios", ln=True, fill=True)
                pdf.set_font("NotoSerif", '', 12)
                pdf.cell(50, 10, "Scenario", border=1, fill=True)
                pdf.cell(0, 10, "Total Cost", border=1, ln=True, fill=True)
                for label, value in scenarios.items():
                    pdf.cell(50, 10, label.capitalize(), border=1)
                    pdf.cell(0, 10, f"${value:,.2f}", border=1, ln=True)
                pdf.ln(6)
            # Add the rest of the content
            if content:
                pdf.multi_cell(0, 8, content)
        else:
            # For other sections, only use actual content
            if content:
                pdf.multi_cell(0, 8, content)
            # Add a placeholder for visuals (e.g., chart)
            if 'solution' in sec['title'].lower():
                chart_path = os.path.join(os.path.dirname(__file__), 'solution_chart.png')
                if os.path.exists(chart_path):
                    pdf.ln(4)
                    pdf.image(chart_path, x=30, w=150)
        pdf.ln(4)


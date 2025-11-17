"""
PDF Generator
Generate professional branded PDF reports using ReportLab
"""
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate professional PDF reports"""

    def __init__(self):
        """Initialize PDF generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Get company info from config
        self.company_name = Config.get('COMPANY_NAME', 'Your Company')
        self.report_author = Config.get('REPORT_AUTHOR', 'Brandea GbR')
        self.author_email = Config.get('REPORT_AUTHOR_EMAIL', 'info@brandea.de')
        self.author_website = Config.get('REPORT_AUTHOR_WEBSITE', 'www.brandea.de')

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#FF4B4B'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0068C9'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#262730'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#262730'),
            spaceAfter=10,
            fontName='Helvetica'
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        ))

    def generate_weekly_report(
        self,
        analysis: Dict,
        campaign_df: pd.DataFrame,
        ad_df: pd.DataFrame,
        charts_data: Optional[Dict] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate weekly performance report PDF

        Args:
            analysis: AI analysis results
            campaign_df: Campaign performance data
            ad_df: Ad performance data
            charts_data: Optional chart images
            output_path: Output file path

        Returns:
            Path to generated PDF
        """
        # Create output path
        if output_path is None:
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(reports_dir, f'weekly_report_{timestamp}.pdf')

        # Create PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=2*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )

        # Build content
        story = []

        # Cover page
        story.extend(self._create_cover_page(
            title='Weekly Performance Report',
            subtitle=f'{self.company_name}',
            date_range=analysis.get('date_range', 'N/A')
        ))

        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph('Executive Summary', self.styles['CustomHeading']))
        story.append(Spacer(1, 0.3*cm))

        # Parse and add analysis text
        full_analysis = analysis.get('full_analysis', 'Keine Analyse verfügbar')
        self._add_markdown_text(story, full_analysis)

        story.append(Spacer(1, 0.5*cm))

        # Campaign Performance Table
        if not campaign_df.empty:
            story.append(PageBreak())
            story.append(Paragraph('Kampagnen Performance', self.styles['CustomHeading']))
            story.append(Spacer(1, 0.3*cm))

            campaign_table = self._create_dataframe_table(
                campaign_df,
                columns=['campaign_name', 'spend', 'leads', 'cpl', 'frequency']
            )
            story.append(campaign_table)
            story.append(Spacer(1, 0.5*cm))

        # Ad Performance Table
        if not ad_df.empty:
            story.append(PageBreak())
            story.append(Paragraph('Ad Performance', self.styles['CustomHeading']))
            story.append(Spacer(1, 0.3*cm))

            # Show top 10 ads
            ad_table = self._create_dataframe_table(
                ad_df.head(10),
                columns=['ad_name', 'spend', 'leads', 'cpl', 'hook_rate', 'hold_rate']
            )
            story.append(ad_table)

        # Footer
        story.append(PageBreak())
        story.extend(self._create_footer_page())

        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)

        logger.info(f"PDF report generated: {output_path}")
        return output_path

    def _create_cover_page(self, title: str, subtitle: str, date_range: str) -> List:
        """Create cover page elements"""
        elements = []

        # Add logo if exists
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'brandea_logo.png')
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=5*cm, height=5*cm)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 1*cm))
            except Exception as e:
                logger.warning(f"Could not load logo: {str(e)}")

        # Title
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Subtitle
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#262730'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 1*cm))

        # Date range
        date_style = ParagraphStyle(
            name='DateRange',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f'Zeitraum: {date_range}', date_style))
        elements.append(Spacer(1, 0.5*cm))

        # Generation date
        gen_date = datetime.now().strftime('%d.%m.%Y')
        elements.append(Paragraph(f'Erstellt am: {gen_date}', date_style))

        return elements

    def _create_footer_page(self) -> List:
        """Create footer page with branding"""
        elements = []

        elements.append(Paragraph('Über diesen Report', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.3*cm))

        footer_text = f"""
        Dieser Report wurde automatisch generiert von <b>{self.report_author}</b>.<br/>
        <br/>
        Kontakt: {self.author_email}<br/>
        Website: {self.author_website}<br/>
        <br/>
        Powered by AI-gestützte Meta Ads Analyse.
        """

        elements.append(Paragraph(footer_text, self.styles['CustomBody']))

        return elements

    def _create_dataframe_table(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Table:
        """
        Create formatted table from DataFrame

        Args:
            df: DataFrame to display
            columns: Columns to include

        Returns:
            ReportLab Table object
        """
        if columns:
            df = df[columns].copy()

        # Format numeric columns
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                if 'cpl' in col.lower() or 'spend' in col.lower():
                    df[col] = df[col].apply(lambda x: f'€{x:,.2f}')
                elif 'rate' in col.lower():
                    df[col] = df[col].apply(lambda x: f'{x:.1f}%')
                elif 'frequency' in col.lower():
                    df[col] = df[col].apply(lambda x: f'{x:.2f}')
                else:
                    df[col] = df[col].apply(lambda x: f'{x:,}')

        # Create table data
        data = [df.columns.tolist()] + df.values.tolist()

        # Create table
        table = Table(data, repeatRows=1)

        # Style table
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0068C9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F2F6')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        return table

    def _add_markdown_text(self, story: List, text: str):
        """
        Add markdown-formatted text to story

        Args:
            story: Story list to append to
            text: Markdown text
        """
        # Simple markdown parsing
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                story.append(Spacer(1, 0.2*cm))
                continue

            # Headers
            if line.startswith('# '):
                story.append(Paragraph(line[2:], self.styles['CustomHeading']))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], self.styles['CustomSubheading']))
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                story.append(Paragraph('• ' + line[2:], self.styles['CustomBody']))
            elif line.startswith('🔴') or line.startswith('🟡') or line.startswith('🟢'):
                story.append(Paragraph(line, self.styles['CustomBody']))
            # Regular text
            else:
                story.append(Paragraph(line, self.styles['CustomBody']))

    def _add_page_number(self, canvas, doc):
        """
        Add page number and footer to page

        Args:
            canvas: ReportLab canvas
            doc: Document template
        """
        page_num = canvas.getPageNumber()
        text = f"{self.report_author} | {self.author_website} | Seite {page_num}"

        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawCentredString(A4[0] / 2, 1.5*cm, text)
        canvas.restoreState()

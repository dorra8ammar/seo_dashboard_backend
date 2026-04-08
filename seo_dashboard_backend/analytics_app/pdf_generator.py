"""
Générateur de rapports PDF pour SEOmind
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime


def generate_seo_report(website_name, website_url, ga_data, search_console_data, recommendations):
    """
    Génère un rapport PDF complet avec les données SEO
    """
    buffer = BytesIO()
    
    # Créer le document PDF (format paysage)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        alignment=1,
        spaceAfter=20
    )
    
    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#111827'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # ========== EN-TÊTE ==========
    story.append(Paragraph("SEO<span color='#6366f1'>mind</span>", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Informations du rapport
    story.append(Paragraph("<b>Rapport SEO</b>", subtitle_style))
    story.append(Paragraph(f"Date de génération : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # ========== INFORMATIONS SITE ==========
    story.append(Paragraph("<b>Informations du site</b>", subtitle_style))
    story.append(Paragraph(f"Nom : {website_name}", normal_style))
    story.append(Paragraph(f"URL : {website_url}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # ========== DONNÉES GOOGLE ANALYTICS ==========
    if ga_data:
        story.append(Paragraph("<b>📊 Google Analytics</b>", subtitle_style))
        
        total_users = sum(row.get('users', 0) for row in ga_data)
        total_sessions = sum(row.get('sessions', 0) for row in ga_data)
        total_views = sum(row.get('views', 0) for row in ga_data)
        
        kpi_data = [
            ['Indicateur', 'Total sur la période'],
            ['Utilisateurs', str(total_users)],
            ['Sessions', str(total_sessions)],
            ['Pages vues', str(total_views)],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[5*cm, 5*cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Évolution
        story.append(Paragraph("<b>Évolution sur 30 jours</b>", normal_style))
        
        chart_data = [['Date', 'Users', 'Sessions', 'Views']]
        for row in ga_data[-10:]:
            chart_data.append([
                row.get('date', ''),
                str(row.get('users', 0)),
                str(row.get('sessions', 0)),
                str(row.get('views', 0))
            ])
        
        chart_table = Table(chart_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        chart_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        story.append(chart_table)
        story.append(Spacer(1, 0.5*cm))
    
    # ========== DONNÉES SEARCH CONSOLE ==========
    if search_console_data:
        story.append(Paragraph("<b>🔍 Google Search Console</b>", subtitle_style))
        
        keywords_data = [['Mot-clé', 'Clics', 'Impressions', 'CTR', 'Position']]
        for row in search_console_data[:15]:
            keywords_data.append([
                row.get('keyword', '')[:30],
                str(row.get('clicks', 0)),
                str(row.get('impressions', 0)),
                f"{row.get('ctr', 0)*100:.1f}%",
                f"{row.get('position', 0):.1f}"
            ])
        
        keywords_table = Table(keywords_data, colWidths=[5*cm, 2*cm, 2.5*cm, 2*cm, 2*cm])
        keywords_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        story.append(keywords_table)
        story.append(Spacer(1, 0.5*cm))
        
        total_clicks = sum(row.get('clicks', 0) for row in search_console_data)
        total_impressions = sum(row.get('impressions', 0) for row in search_console_data)
        avg_position = sum(row.get('position', 0) for row in search_console_data) / len(search_console_data) if search_console_data else 0
        
        stats_data = [
            ['Total clics', str(total_clicks)],
            ['Total impressions', str(total_impressions)],
            ['CTR moyen', f"{(total_clicks/total_impressions*100):.1f}%" if total_impressions > 0 else '0%'],
            ['Position moyenne', f"{avg_position:.1f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[5*cm, 5*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.5*cm))
    
    # ========== RECOMMANDATIONS IA ==========
    if recommendations:
        story.append(Paragraph("<b>🤖 Recommandations SEO IA</b>", subtitle_style))
        
        for i, rec in enumerate(recommendations, 1):
            if rec.get('priority') == 1:
                color = '#dc2626'
                priority_text = "HAUTE PRIORITÉ"
            elif rec.get('priority') == 2:
                color = '#d97706'
                priority_text = "PRIORITÉ MOYENNE"
            else:
                color = '#059669'
                priority_text = "PRIORITÉ BASSE"
            
            rec_text = f"""
            <b>{i}. {rec.get('title', '')}</b><br/>
            <font color='{color}'>[{priority_text}]</font><br/>
            {rec.get('description', '')}<br/>
            <i>Action : {rec.get('action', 'Non spécifiée')}</i>
            """
            story.append(Paragraph(rec_text, normal_style))
            story.append(Spacer(1, 0.3*cm))
    
    # ========== PIED DE PAGE ==========
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"<i>Rapport généré automatiquement par SEOmind - {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
        normal_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer

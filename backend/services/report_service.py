import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

from ..models.calibration import CalibrationRun

class ReportService:
    @staticmethod
    def generate_calibration_report(calibration: CalibrationRun) -> bytes:
        """
        Generate a PDF report for a calibration run.
        Returns the PDF content as bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Custom Styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#a275c2')  # Primary Color
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#4a4a4a')
        )

        # Header
        story.append(Paragraph("Reporte de Calibración Hand-Eye", title_style))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Summary Section
        story.append(Paragraph("Resumen de Ejecución", heading_style))
        
        summary_data = [
            ["ID Calibración:", str(calibration.id)],
            ["Nombre:", calibration.name],
            ["Estado:", calibration.status.upper()],
            ["Método:", calibration.method or "N/A"],
            ["Fecha Creación:", calibration.created_at.strftime('%Y-%m-%d %H:%M')],
            ["Usuario:", calibration.user.username if calibration.user else "N/A"]
        ]
        
        t_summary = Table(summary_data, colWidths=[2*inch, 4*inch])
        t_summary.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#555555')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 12))

        # Metrics Section
        if calibration.status == "completed":
            story.append(Paragraph("Métricas de Calidad", heading_style))
            
            # Helper to format metrics
            def format_metric(value, unit):
                return f"{value:.4f} {unit}" if value is not None else "N/A"

            metrics_data = [
                ["Métrica", "Valor", "Estado"],
                ["Error de Reproyección", format_metric(calibration.reprojection_error, "mm"), "PASS" if (calibration.reprojection_error or 0) < 1.0 else "WARN"],
                ["Error de Rotación", format_metric(calibration.rotation_error_deg, "deg"), "PASS" if (calibration.rotation_error_deg or 0) < 0.5 else "WARN"],
                ["Error de Traslación", format_metric(calibration.translation_error_mm, "mm"), "PASS" if (calibration.translation_error_mm or 0) < 5.0 else "WARN"],
                ["Poses Procesadas", f"{calibration.poses_valid or 0} / {calibration.poses_processed or 0}", "INFO"]
            ]
            
            t_metrics = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            
            # Style for metrics table
            metric_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ])
            
            # Color coding for PASS/WARN
            for i, row in enumerate(metrics_data[1:], start=1):
                status = row[2]
                if status == "PASS":
                    metric_style.add('TEXTCOLOR', (2,i), (2,i), colors.green)
                elif status == "WARN":
                    metric_style.add('TEXTCOLOR', (2,i), (2,i), colors.orange)
                elif status == "FAIL":
                    metric_style.add('TEXTCOLOR', (2,i), (2,i), colors.red)
            
            t_metrics.setStyle(metric_style)
            story.append(t_metrics)
            story.append(Spacer(1, 20))

            # Transformation Matrix Section
            story.append(Paragraph("Matriz de Transformación Resultante", heading_style))
            
            if calibration.transformation_matrix:
                try:
                    matrix = calibration.transformation_matrix
                    # If it's a string (e.g. from legacy data), parse it
                    if isinstance(matrix, str):
                        import json
                        matrix = json.loads(matrix)
                    
                    # Format matrix for display
                    matrix_data = [[f"{val:.6f}" for val in row] for row in matrix]
                    
                    t_matrix = Table(matrix_data, colWidths=[1.5*inch]*4)
                    t_matrix.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,-1), 'Courier'),
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#a275c2')),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fafafa')),
                        ('PADDING', (0,0), (-1,-1), 10),
                    ]))
                    story.append(t_matrix)
                except:
                    story.append(Paragraph("Error al formatear la matriz.", styles['Normal']))
            else:
                story.append(Paragraph("No hay matriz disponible.", styles['Normal']))

        else:
            story.append(Paragraph("La calibración no se completó exitosamente.", styles['Normal']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

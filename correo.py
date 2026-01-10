"""
Módulo de envío de correos para App Soporte
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import obtener_config, formatear_duracion

def enviar_correo(destinatario, asunto, cuerpo_html):
    """Envía un correo electrónico"""
    try:
        # Obtener configuración SMTP
        smtp_host = obtener_config('smtp_host', '')
        smtp_port = int(obtener_config('smtp_port', '587'))
        smtp_user = obtener_config('smtp_user', '')
        smtp_pass = obtener_config('smtp_pass', '')
        smtp_from = obtener_config('smtp_from', smtp_user)
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            return False, "Configuración de correo incompleta"
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = smtp_from
        msg['To'] = destinatario
        
        # Adjuntar HTML
        parte_html = MIMEText(cuerpo_html, 'html', 'utf-8')
        msg.attach(parte_html)
        
        # Enviar
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return True, "Correo enviado exitosamente"
    
    except Exception as e:
        return False, f"Error al enviar: {str(e)}"

def generar_html_boleta(visita):
    """Genera HTML de una boleta de visita"""
    pendiente_html = ""
    if visita['tiene_pendiente']:
        estado = "✅ Resuelto" if visita.get('pendiente_resuelto') else "⚠️ Pendiente"
        pendiente_html = f"""
        <tr>
            <td style="padding: 10px; background: #fff3cd; border-bottom: 1px solid #ddd;">
                <strong>Pendiente:</strong> {estado}<br>
                {visita.get('descripcion_pendiente', '')}
            </td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .boleta {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #2196f3; color: white; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 15px; border-bottom: 1px solid #eee; }}
            .label {{ color: #666; font-size: 12px; text-transform: uppercase; }}
            .value {{ font-size: 16px; color: #333; margin-top: 5px; }}
            .trabajo {{ background: #f9f9f9; }}
            .footer {{ text-align: center; padding: 15px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="boleta">
            <div class="header">
                <h1>📋 Boleta de Visita</h1>
            </div>
            <div class="content">
                <table>
                    <tr>
                        <td style="width: 50%;">
                            <div class="label">Cliente</div>
                            <div class="value">{visita['cliente_nombre']}</div>
                        </td>
                        <td>
                            <div class="label">Fecha</div>
                            <div class="value">{visita['fecha']}</div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <div class="label">Técnico</div>
                            <div class="value">{visita['soportista_nombre']}</div>
                        </td>
                        <td>
                            <div class="label">Hora / Duración</div>
                            <div class="value">{visita['hora_inicio']} - {formatear_duracion(visita['duracion_minutos'])}</div>
                        </td>
                    </tr>
                    {f'''<tr>
                        <td colspan="2">
                            <div class="label">Persona Atendida</div>
                            <div class="value">{visita['persona_atendida']}</div>
                        </td>
                    </tr>''' if visita.get('persona_atendida') else ''}
                    <tr class="trabajo">
                        <td colspan="2">
                            <div class="label">Trabajo Realizado</div>
                            <div class="value">{visita['trabajo_realizado']}</div>
                        </td>
                    </tr>
                    {pendiente_html}
                </table>
            </div>
            <div class="footer">
                Boleta generada automáticamente - App Soporte
            </div>
        </div>
    </body>
    </html>
    """

def generar_html_reporte(cliente, visitas, fecha_desde, fecha_hasta, tiempo_total):
    """Genera HTML de reporte de visitas"""
    filas_html = ""
    for v in visitas:
        pendiente = "⚠️" if v['tiene_pendiente'] and not v.get('pendiente_resuelto') else ""
        filas_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{v['fecha']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{v['hora_inicio']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{formatear_duracion(v['duracion_minutos'])}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{v['soportista_nombre']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{v['trabajo_realizado'][:50]}... {pendiente}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .reporte {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: #2196f3; color: white; padding: 20px; }}
            .header h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
            .header p {{ margin: 0; opacity: 0.9; }}
            .summary {{ background: #e3f2fd; padding: 15px 20px; display: flex; justify-content: space-between; }}
            .summary-item {{ text-align: center; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
            .summary-label {{ font-size: 12px; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f5f5f5; padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #666; }}
            .footer {{ text-align: center; padding: 15px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="reporte">
            <div class="header">
                <h1>📊 Reporte de Visitas</h1>
                <p><strong>{cliente['nombre']}</strong></p>
                <p>Período: {fecha_desde} al {fecha_hasta}</p>
            </div>
            <div class="summary">
                <div class="summary-item">
                    <div class="summary-value">{len(visitas)}</div>
                    <div class="summary-label">Visitas</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{formatear_duracion(tiempo_total)}</div>
                    <div class="summary-label">Tiempo Total</div>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Hora</th>
                        <th>Duración</th>
                        <th>Técnico</th>
                        <th>Trabajo</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
            <div class="footer">
                Reporte generado automáticamente - App Soporte
            </div>
        </div>
    </body>
    </html>
    """

def generar_html_reporte_imprimible(cliente, visitas, fecha_desde, fecha_hasta, tiempo_total):
    """Genera HTML de reporte optimizado para imprimir/PDF"""
    filas_html = ""
    for i, v in enumerate(visitas):
        pendiente_html = ""
        if v['tiene_pendiente'] and not v.get('pendiente_resuelto'):
            pendiente_html = f'<div style="background:#fff3cd;padding:8px 12px;border-radius:5px;margin-top:8px;font-size:12px;border-left:4px solid #ff9800;">⚠️ PENDIENTE: {v.get("descripcion_pendiente", "")}</div>'
        
        persona_atendida = v.get('persona_atendida', '').strip() if v.get('persona_atendida') else ""
        persona_html = f'<span style="margin-right:20px;">👤 Atendido: {persona_atendida}</span>' if persona_atendida else ""
        
        bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        
        filas_html += f"""
        <div style="background:{bg_color};padding:15px;margin-bottom:10px;border-radius:8px;border:1px solid #eee;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div>
                    <span style="background:#2196f3;color:white;padding:4px 10px;border-radius:5px;font-weight:bold;font-size:14px;">Boleta #{v['id']}</span>
                    <span style="font-weight:bold;color:#333;font-size:16px;margin-left:10px;">{v['fecha']}</span>
                </div>
                <span style="color:#666;">🕐 {v['hora_inicio']} | ⏱️ {formatear_duracion(v['duracion_minutos'])}</span>
            </div>
            <div style="color:#666;font-size:13px;margin-bottom:10px;">
                {persona_html}👷 Técnico: {v['soportista_nombre']}
            </div>
            <div style="background:#f5f5f5;padding:12px;border-radius:5px;font-size:14px;line-height:1.5;">{v['trabajo_realizado']}</div>
            {pendiente_html}
        </div>
        """
    
    from datetime import datetime
    fecha_generacion = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reporte - {cliente['nombre']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; padding: 20px; background: white; }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
        .header {{ background: linear-gradient(135deg, #2196f3, #1976d2); color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .summary {{ display: flex; justify-content: space-around; background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .summary-item {{ text-align: center; }}
        .summary-value {{ font-size: 32px; font-weight: bold; color: #1976d2; }}
        .summary-label {{ font-size: 14px; color: #666; }}
        .visitas {{ margin-bottom: 20px; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; padding: 15px; border-top: 1px solid #eee; }}
        .btn-print {{ background: #4caf50; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px; }}
        .btn-print:hover {{ background: #43a047; }}
        .actions {{ text-align: center; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="actions no-print">
        <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
        <button class="btn-print" style="background:#2196f3;" onclick="window.close()">✖️ Cerrar</button>
    </div>
    
    <div class="header">
        <h1>📋 PcGraf-Soporte</h1>
        <h2>Reporte de Visitas</h2>
        <p><strong>Cliente:</strong> {cliente['nombre']}</p>
        <p><strong>Período:</strong> {fecha_desde} al {fecha_hasta}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <div class="summary-value">{len(visitas)}</div>
            <div class="summary-label">Total Visitas</div>
        </div>
        <div class="summary-item">
            <div class="summary-value">{formatear_duracion(tiempo_total)}</div>
            <div class="summary-label">Tiempo Total</div>
        </div>
    </div>
    
    <div class="visitas">
        {filas_html}
    </div>
    
    <div class="footer">
        Reporte generado el {fecha_generacion} - PcGraf-Soporte
    </div>
</body>
</html>"""


"""
App Soporte - Gestión de Visitas Técnicas
"""
import flet as ft
import os
from datetime import datetime, date
import database as db
import correo

def main(page: ft.Page):
    """Aplicación principal"""
    
    # Configuración de la página
    page.title = "PcGraf-Soporte"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 450
    page.window_height = 750
    
    # ============== COMPONENTES COMUNES ==============
    
    def crear_appbar(titulo, mostrar_atras=True):
        """Crea una barra de aplicación estándar"""
        return ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: ir_inicio(),
                visible=mostrar_atras
            ),
            title=ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor="#2196f3",
            color="white"
        )
    
    def mostrar_mensaje(texto, es_error=False):
        """Muestra un mensaje temporal"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor="#f44336" if es_error else "#4caf50"
        )
        page.snack_bar.open = True
        page.update()
    
    def confirmar_accion(titulo, mensaje, on_confirmar):
        """Muestra diálogo de confirmación"""
        def cerrar(e):
            dlg.open = False
            page.update()
        
        def confirmar(e):
            dlg.open = False
            page.update()
            on_confirmar()
        
        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.TextButton("Confirmar", on_click=confirmar),
            ]
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()
    
    # ============== PANTALLA INICIO ==============
    
    def ir_inicio():
        """Muestra el menú principal"""
        page.clean()
        
        def crear_boton_menu(icono, texto, on_click, color="#2196f3"):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icono, size=40, color=color),
                    ft.Text(texto, size=14, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=140,
                height=120,
                bgcolor="white",
                border_radius=15,
                padding=15,
                on_click=on_click,
                shadow=ft.BoxShadow(blur_radius=10, color="#00000020")
            )
        
        # Contar pendientes
        pendientes = db.obtener_pendientes()
        badge_pendientes = f" ({len(pendientes)})" if pendientes else ""
        
        contenido = ft.Column([
            # Header
            ft.Container(
                content=ft.Column([
                    ft.Text("📋 PcGraf-Soporte", size=28, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("Gestión de Visitas Técnicas", size=14, color="#ffffffcc")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#2196f3",
                padding=30,
                width=float("inf")
            ),
            
            # Menú
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        crear_boton_menu(ft.Icons.ADD_CIRCLE, "Nueva\nVisita", lambda e: ir_nueva_visita(), "#4caf50"),
                        crear_boton_menu(ft.Icons.WARNING, f"Pendientes{badge_pendientes}", lambda e: ir_pendientes(), "#ff9800"),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                    ft.Row([
                        crear_boton_menu(ft.Icons.SEARCH, "Consultar\nBoletas", lambda e: ir_consulta()),
                        crear_boton_menu(ft.Icons.PEOPLE, "Clientes", lambda e: ir_clientes()),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                    ft.Row([
                        crear_boton_menu(ft.Icons.ENGINEERING, "Soportistas", lambda e: ir_soportistas()),
                        crear_boton_menu(ft.Icons.SETTINGS, "Configuración", lambda e: ir_configuracion(), "#757575"),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                expand=True
            )
        ], spacing=0, expand=True)
        
        page.add(contenido)
        page.update()
    
    # ============== PANTALLA CLIENTES ==============
    
    def ir_clientes():
        """Muestra lista de clientes"""
        page.clean()
        
        lista = ft.ListView(spacing=10, padding=15, expand=True)
        
        def cargar_clientes():
            lista.controls.clear()
            clientes = db.obtener_clientes()
            for c in clientes:
                soportista_txt = f"👷 {c.get('soportista_nombre', 'Sin asignar')}" if c.get('soportista_nombre') else ""
                lista.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.BUSINESS, color="#2196f3"),
                            title=ft.Text(c['nombre'], weight=ft.FontWeight.W_500),
                            subtitle=ft.Text(f"📧 {c['correo'] or '-'}  📞 {c['telefono'] or '-'}  {soportista_txt}", size=12),
                            trailing=ft.Row([
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda e, id=c['id']: editar_cliente(id)),
                                ft.IconButton(ft.Icons.DELETE, icon_color="#f44336", 
                                            on_click=lambda e, id=c['id'], nombre=c['nombre']: eliminar_cliente_confirmar(id, nombre)),
                            ], spacing=0, width=80),
                        ),
                        bgcolor="white",
                        border_radius=10,
                        shadow=ft.BoxShadow(blur_radius=5, color="#00000010")
                    )
                )
            if not clientes:
                lista.controls.append(ft.Text("No hay clientes registrados", text_align=ft.TextAlign.CENTER))
            page.update()
        
        def editar_cliente(id):
            ir_form_cliente(id)
        
        def eliminar_cliente_confirmar(id, nombre):
            confirmar_accion(
                "Eliminar Cliente",
                f"¿Eliminar a {nombre}?",
                lambda: eliminar_y_recargar(id)
            )
        
        def eliminar_y_recargar(id):
            db.eliminar_cliente(id)
            mostrar_mensaje("Cliente eliminado")
            cargar_clientes()
        
        page.add(
            crear_appbar("Clientes"),
            lista,
            ft.Row(
                [ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor="#4caf50",
                    on_click=lambda e: ir_form_cliente()
                )],
                alignment=ft.MainAxisAlignment.END,
            )
        )
        cargar_clientes()
    
    def ir_form_cliente(id=None):
        """Formulario de cliente"""
        page.clean()
        
        cliente = db.obtener_cliente(id) if id else {}
        soportistas = db.obtener_soportistas()
        
        txt_nombre = ft.TextField(label="Nombre *", value=cliente.get('nombre', ''), border_radius=10)
        txt_correo = ft.TextField(label="Correo", value=cliente.get('correo', ''), border_radius=10, keyboard_type=ft.KeyboardType.EMAIL)
        txt_telefono = ft.TextField(label="Teléfono", value=cliente.get('telefono', ''), border_radius=10, keyboard_type=ft.KeyboardType.PHONE)
        
        # Dropdown de soportista asignado
        dd_soportista = ft.Dropdown(
            label="Soportista Asignado",
            options=[ft.dropdown.Option(key="", text="-- Sin asignar --")] + 
                    [ft.dropdown.Option(key=str(s['id']), text=s['nombre']) for s in soportistas],
            value=str(cliente.get('soportista_id', '')) if cliente.get('soportista_id') else "",
            border_radius=10
        )
        
        def guardar(e):
            if not txt_nombre.value.strip():
                mostrar_mensaje("El nombre es requerido", True)
                return
            soportista_id = int(dd_soportista.value) if dd_soportista.value else None
            db.guardar_cliente(
                txt_nombre.value.strip(), 
                txt_correo.value.strip(), 
                txt_telefono.value.strip(), 
                soportista_id,
                id
            )
            mostrar_mensaje("Cliente guardado")
            ir_clientes()
        
        page.add(
            crear_appbar("Editar Cliente" if id else "Nuevo Cliente"),
            ft.Container(
                content=ft.Column([
                    txt_nombre,
                    txt_correo,
                    txt_telefono,
                    dd_soportista,
                    ft.ElevatedButton(
                        "Guardar",
                        icon=ft.Icons.SAVE,
                        bgcolor="#4caf50",
                        color="white",
                        width=float("inf"),
                        on_click=guardar
                    )
                ], spacing=15),
                padding=20
            )
        )
        page.update()
    
    # ============== PANTALLA SOPORTISTAS ==============
    
    def ir_soportistas():
        """Muestra lista de soportistas"""
        page.clean()
        
        lista = ft.ListView(spacing=10, padding=15, expand=True)
        
        def cargar():
            lista.controls.clear()
            soportistas = db.obtener_soportistas()
            for s in soportistas:
                lista.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.ENGINEERING, color="#ff9800"),
                            title=ft.Text(s['nombre'], weight=ft.FontWeight.W_500),
                            subtitle=ft.Text(f"📧 {s['correo'] or '-'}", size=12),
                            trailing=ft.Row([
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda e, id=s['id']: ir_form_soportista(id)),
                                ft.IconButton(ft.Icons.DELETE, icon_color="#f44336",
                                            on_click=lambda e, id=s['id'], nombre=s['nombre']: eliminar_soportista_confirmar(id, nombre)),
                            ], spacing=0, width=80),
                        ),
                        bgcolor="white",
                        border_radius=10,
                        shadow=ft.BoxShadow(blur_radius=5, color="#00000010")
                    )
                )
            if not soportistas:
                lista.controls.append(ft.Text("No hay soportistas registrados", text_align=ft.TextAlign.CENTER))
            page.update()
        
        def eliminar_soportista_confirmar(id, nombre):
            confirmar_accion("Eliminar", f"¿Eliminar a {nombre}?", lambda: eliminar_y_recargar(id))
        
        def eliminar_y_recargar(id):
            db.eliminar_soportista(id)
            mostrar_mensaje("Soportista eliminado")
            cargar()
        
        page.add(
            crear_appbar("Soportistas"),
            lista,
            ft.Row(
                [ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor="#4caf50", on_click=lambda e: ir_form_soportista())],
                alignment=ft.MainAxisAlignment.END,
            )
        )
        cargar()
    
    def ir_form_soportista(id=None):
        """Formulario de soportista"""
        page.clean()
        
        soportista = db.obtener_soportista(id) if id else {}
        
        txt_nombre = ft.TextField(label="Nombre *", value=soportista.get('nombre', ''), border_radius=10)
        txt_correo = ft.TextField(label="Correo", value=soportista.get('correo', ''), border_radius=10)
        
        def guardar(e):
            if not txt_nombre.value.strip():
                mostrar_mensaje("El nombre es requerido", True)
                return
            db.guardar_soportista(txt_nombre.value.strip(), txt_correo.value.strip(), id)
            mostrar_mensaje("Soportista guardado")
            ir_soportistas()
        
        page.add(
            crear_appbar("Editar Soportista" if id else "Nuevo Soportista"),
            ft.Container(
                content=ft.Column([txt_nombre, txt_correo,
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, bgcolor="#4caf50", color="white", width=float("inf"), on_click=guardar)
                ], spacing=15),
                padding=20
            )
        )
        page.update()
    
    # ============== PANTALLA NUEVA VISITA ==============
    
    def ir_nueva_visita(id=None):
        """Formulario de nueva visita"""
        page.clean()
        
        visita = db.obtener_visita(id) if id else {}
        
        # Cargar datos para dropdowns
        soportistas = db.obtener_soportistas()
        
        if not soportistas:
            mostrar_mensaje("Primero registre soportistas", True)
            ir_soportistas()
            return
        
        # Variable para almacenar clientes filtrados
        clientes_actuales = []
        
        # Dropdown de clientes (se llenará al seleccionar soportista)
        dd_cliente = ft.Dropdown(
            label="Cliente *",
            options=[],
            value=str(visita.get('cliente_id', '')) if visita.get('cliente_id') else "",
            border_radius=10,
            expand=True
        )
        
        # Checkbox para ver todos los clientes
        chk_ver_todos = ft.Checkbox(label="Ver todos los clientes", value=False)
        
        # Dropdown de soportistas
        dd_soportista = ft.Dropdown(
            label="Técnico *",
            options=[ft.dropdown.Option(key=str(s['id']), text=s['nombre']) for s in soportistas],
            value=str(visita.get('soportista_id', '')) if visita.get('soportista_id') else "",
            border_radius=10
        )
        
        def actualizar_clientes(e=None):
            """Actualiza la lista de clientes según el soportista seleccionado"""
            nonlocal clientes_actuales
            
            if chk_ver_todos.value or not dd_soportista.value:
                # Ver todos los clientes
                clientes_actuales = db.obtener_clientes()
            else:
                # Solo clientes del soportista
                clientes_actuales = db.obtener_clientes(soportista_id=int(dd_soportista.value))
            
            dd_cliente.options = [ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in clientes_actuales]
            
            # Si el cliente actual no está en la lista, limpiar selección
            if dd_cliente.value and not any(str(c['id']) == dd_cliente.value for c in clientes_actuales):
                dd_cliente.value = ""
            
            if not clientes_actuales:
                dd_cliente.options = [ft.dropdown.Option(key="", text="-- No hay clientes asignados --")]
            
            page.update()
        
        dd_soportista.on_change = actualizar_clientes
        chk_ver_todos.on_change = actualizar_clientes
        
        txt_persona = ft.TextField(label="Persona Atendida (opcional)", value=visita.get('persona_atendida', ''), border_radius=10)
        
        # Fecha y hora
        hoy = date.today().strftime('%Y-%m-%d')
        ahora = datetime.now().strftime('%H:%M')
        
        txt_fecha = ft.TextField(label="Fecha *", value=visita.get('fecha', hoy), border_radius=10, hint_text="YYYY-MM-DD")
        txt_hora = ft.TextField(label="Hora Inicio *", value=visita.get('hora_inicio', ahora), border_radius=10, hint_text="HH:MM")
        txt_duracion = ft.TextField(label="Duración (minutos) *", value=str(visita.get('duracion_minutos', '30')), border_radius=10, keyboard_type=ft.KeyboardType.NUMBER)
        
        txt_trabajo = ft.TextField(
            label="Trabajo Realizado *",
            value=visita.get('trabajo_realizado', ''),
            multiline=True,
            min_lines=5,
            max_lines=8,
            border_radius=10
        )
        
        chk_pendiente = ft.Checkbox(label="¿Quedó pendiente?", value=visita.get('tiene_pendiente', False))
        txt_pendiente = ft.TextField(
            label="Descripción del pendiente",
            value=visita.get('descripcion_pendiente', ''),
            multiline=True,
            visible=visita.get('tiene_pendiente', False),
            border_radius=10
        )
        
        # Checkbox para enviar correo
        chk_enviar_correo = ft.Checkbox(label="📧 Enviar boleta por correo al cliente", value=False)
        
        def toggle_pendiente(e):
            txt_pendiente.visible = chk_pendiente.value
            page.update()
        
        chk_pendiente.on_change = toggle_pendiente
        
        def guardar(e):
            # Validaciones
            if not dd_cliente.value:
                mostrar_mensaje("Seleccione un cliente", True)
                return
            if not dd_soportista.value:
                mostrar_mensaje("Seleccione un técnico", True)
                return
            if not txt_trabajo.value.strip():
                mostrar_mensaje("Describa el trabajo realizado", True)
                return
            
            try:
                duracion = int(txt_duracion.value)
            except:
                mostrar_mensaje("Duración debe ser un número", True)
                return
            
            visita_id = db.guardar_visita(
                cliente_id=int(dd_cliente.value),
                soportista_id=int(dd_soportista.value),
                persona_atendida=txt_persona.value.strip(),
                fecha=txt_fecha.value,
                hora_inicio=txt_hora.value,
                duracion_minutos=duracion,
                trabajo_realizado=txt_trabajo.value.strip(),
                tiene_pendiente=chk_pendiente.value,
                descripcion_pendiente=txt_pendiente.value.strip() if chk_pendiente.value else None,
                id=id
            )
            
            mostrar_mensaje("Visita guardada")
            
            # Enviar correo solo si está marcado el checkbox
            if chk_enviar_correo.value:
                visita_guardada = db.obtener_visita(visita_id)
                if visita_guardada.get('cliente_correo'):
                    html = correo.generar_html_boleta(visita_guardada)
                    ok, msg = correo.enviar_correo(
                        visita_guardada['cliente_correo'],
                        f"Boleta de Visita - {visita_guardada['fecha']}",
                        html
                    )
                    mostrar_mensaje(msg, not ok)
                else:
                    mostrar_mensaje("El cliente no tiene correo configurado", True)
            
            ir_inicio()
        
        # Cargar clientes iniciales si hay soportista seleccionado
        if visita.get('soportista_id'):
            actualizar_clientes()
        
        page.add(
            crear_appbar("Editar Visita" if id else "Nueva Visita"),
            ft.Container(
                content=ft.Column([
                    dd_soportista,
                    ft.Row([dd_cliente, chk_ver_todos], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    txt_persona,
                    ft.Row([txt_fecha, txt_hora], spacing=10),
                    txt_duracion,
                    txt_trabajo,
                    chk_pendiente,
                    txt_pendiente,
                    ft.Divider(),
                    chk_enviar_correo,
                    ft.ElevatedButton("Guardar Visita", icon=ft.Icons.SAVE, bgcolor="#4caf50", color="white", width=float("inf"), on_click=guardar)
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    # ============== PANTALLA PENDIENTES ==============
    
    def ir_pendientes():
        """Muestra lista de pendientes"""
        page.clean()
        
        lista = ft.ListView(spacing=10, padding=15, expand=True)
        
        def cargar():
            lista.controls.clear()
            pendientes = db.obtener_pendientes()
            for p in pendientes:
                lista.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING, color="#ff9800", size=20),
                                ft.Text(p['cliente_nombre'], weight=ft.FontWeight.BOLD, expand=True),
                                ft.Text(p['fecha'], size=12, color="#666")
                            ]),
                            ft.Text(p['descripcion_pendiente'] or "Sin descripción", size=13),
                            ft.Text(f"Técnico: {p['soportista_nombre']}", size=11, color="#999"),
                            ft.Row([
                                ft.TextButton("✅ Resolver", on_click=lambda e, id=p['id']: resolver(id)),
                                ft.TextButton("👁️ Ver Boleta", on_click=lambda e, id=p['id']: ver_boleta(id)),
                            ])
                        ], spacing=5),
                        bgcolor="white",
                        border_radius=10,
                        padding=15,
                        shadow=ft.BoxShadow(blur_radius=5, color="#00000010")
                    )
                )
            if not pendientes:
                lista.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=60, color="#4caf50"),
                            ft.Text("¡Sin pendientes!", size=18, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                           alignment=ft.MainAxisAlignment.CENTER),
                        expand=True
                    )
                )
            page.update()
        
        def resolver(id):
            db.resolver_pendiente(id)
            mostrar_mensaje("Pendiente resuelto")
            cargar()
        
        def ver_boleta(id):
            visita = db.obtener_visita(id)
            mostrar_detalle_visita(visita)
        
        page.add(crear_appbar("Pendientes"), lista)
        cargar()
    
    def mostrar_detalle_visita(visita):
        """Muestra detalle de una visita"""
        page.clean()
        
        def enviar(e):
            if visita.get('cliente_correo'):
                html = correo.generar_html_boleta(visita)
                ok, msg = correo.enviar_correo(visita['cliente_correo'], f"Boleta de Visita - {visita['fecha']}", html)
                mostrar_mensaje(msg, not ok)
            else:
                mostrar_mensaje("El cliente no tiene correo", True)
        
        page.add(
            crear_appbar("Detalle de Visita"),
            ft.Container(
                content=ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(visita['cliente_nombre'], size=20, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, size=16), ft.Text(f"{visita['fecha']} - {visita['hora_inicio']}")]),
                                ft.Row([ft.Icon(ft.Icons.TIMER, size=16), ft.Text(db.formatear_duracion(visita['duracion_minutos']))]),
                                ft.Row([ft.Icon(ft.Icons.PERSON, size=16), ft.Text(visita['soportista_nombre'])]),
                                ft.Divider(),
                                ft.Text("Trabajo Realizado:", weight=ft.FontWeight.BOLD),
                                ft.Text(visita['trabajo_realizado']),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("⚠️ Pendiente:", weight=ft.FontWeight.BOLD, color="#ff9800"),
                                        ft.Text(visita.get('descripcion_pendiente', '')),
                                    ]),
                                    visible=visita['tiene_pendiente'] and not visita.get('pendiente_resuelto'),
                                    bgcolor="#fff3cd",
                                    padding=10,
                                    border_radius=5
                                )
                            ], spacing=8),
                            padding=20
                        )
                    ),
                    ft.ElevatedButton("📧 Enviar por Correo", bgcolor="#2196f3", color="white", width=float("inf"), on_click=enviar)
                ], spacing=15),
                padding=20
            )
        )
        page.update()
    
    # ============== PANTALLA CONSULTA ==============
    
    def ir_consulta():
        """Pantalla de consulta de boletas"""
        page.clean()
        
        clientes = db.obtener_clientes()
        
        dd_cliente = ft.Dropdown(
            label="Cliente",
            options=[ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in clientes],
            border_radius=10
        )
        
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1).strftime('%Y-%m-%d')
        
        txt_desde = ft.TextField(label="Desde", value=primer_dia_mes, border_radius=10, hint_text="YYYY-MM-DD")
        txt_hasta = ft.TextField(label="Hasta", value=hoy.strftime('%Y-%m-%d'), border_radius=10, hint_text="YYYY-MM-DD")
        
        lista = ft.ListView(spacing=10, expand=True)
        lbl_resumen = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        
        visitas_resultado = []
        
        def buscar(e):
            nonlocal visitas_resultado
            if not dd_cliente.value:
                mostrar_mensaje("Seleccione un cliente", True)
                return
            
            visitas_resultado = db.obtener_visitas_cliente(
                int(dd_cliente.value),
                txt_desde.value,
                txt_hasta.value
            )
            
            lista.controls.clear()
            
            # Resumen al inicio
            if visitas_resultado:
                tiempo_total = db.calcular_tiempo_total(visitas_resultado)
                lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(str(len(visitas_resultado)), size=28, weight=ft.FontWeight.BOLD, color="#2196f3"),
                                    ft.Text("Visitas", size=12, color="#666")
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                expand=True
                            ),
                            ft.Container(width=1, height=50, bgcolor="#ccc"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(db.formatear_duracion(tiempo_total), size=28, weight=ft.FontWeight.BOLD, color="#4caf50"),
                                    ft.Text("Tiempo Total", size=12, color="#666")
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                expand=True
                            ),
                        ]),
                        bgcolor="#e3f2fd",
                        border_radius=10,
                        padding=15
                    )
                )
            
            # Lista de visitas
            for v in visitas_resultado:
                # Obtener datos con valores por defecto si no existen
                boleta_id = v.get('id', '?')
                fecha = v.get('fecha', 'Sin fecha')
                hora = v.get('hora_inicio', 'N/A')
                duracion = v.get('duracion_minutos', 0)
                soportista = v.get('soportista_nombre', 'Sin asignar')
                trabajo = v.get('trabajo_realizado', '')
                persona_atendida = v.get('persona_atendida', '').strip() if v.get('persona_atendida') else ""
                tiene_pendiente = v.get('tiene_pendiente') and not v.get('pendiente_resuelto')
                
                tecnico_texto = f"👷 Técnico: {soportista}"
                if persona_atendida:
                    tecnico_texto += f"  |  👤 Atendido: {persona_atendida}"
                
                # Construir controles de la tarjeta - cada línea separada
                controles_visita = [
                    # Línea 1: Boleta y Fecha
                    ft.Text(f"📋 Boleta #{boleta_id}  -  {fecha}", size=15, weight=ft.FontWeight.BOLD, color="#2196f3"),
                    # Línea 2: Hora y Tiempo
                    ft.Text(f"🕐 Hora: {hora}   ⏱️ Duración: {db.formatear_duracion(duracion)}", size=13, color="#333"),
                    # Línea 3: Técnico y Persona atendida
                    ft.Text(tecnico_texto, size=12, color="#666"),
                    # Línea 4: Trabajo realizado
                    ft.Container(
                        content=ft.Text(trabajo, size=13),
                        bgcolor="#f5f5f5",
                        border_radius=5,
                        padding=10
                    ),
                ]
                
                # Agregar pendiente si existe
                if tiene_pendiente:
                    controles_visita.append(
                        ft.Container(
                            content=ft.Text(f"⚠️ PENDIENTE: {v.get('descripcion_pendiente', '')}", size=12, color="#ff9800"),
                            bgcolor="#fff3cd",
                            border_radius=5,
                            padding=8
                        )
                    )
                
                lista.controls.append(
                    ft.Container(
                        content=ft.Column(controles_visita, spacing=5),
                        bgcolor="white",
                        border_radius=10,
                        padding=15,
                        margin=ft.margin.only(bottom=10),
                        border=ft.border.all(1, "#e0e0e0"),
                        on_click=lambda e, vis=v: mostrar_detalle_visita(vis)
                    )
                )
            
            if not visitas_resultado:
                lista.controls.append(
                    ft.Text("No se encontraron visitas en el período seleccionado", 
                           text_align=ft.TextAlign.CENTER, color="#666")
                )
            
            lbl_resumen.value = ""
            page.update()
        
        def enviar_reporte(e):
            if not visitas_resultado:
                mostrar_mensaje("Primero busque boletas", True)
                return
            
            cliente = db.obtener_cliente(int(dd_cliente.value))
            if not cliente.get('correo'):
                mostrar_mensaje("El cliente no tiene correo", True)
                return
            
            tiempo_total = db.calcular_tiempo_total(visitas_resultado)
            html = correo.generar_html_reporte(cliente, visitas_resultado, txt_desde.value, txt_hasta.value, tiempo_total)
            ok, msg = correo.enviar_correo(
                cliente['correo'],
                f"Reporte de Visitas {txt_desde.value} al {txt_hasta.value}",
                html
            )
            mostrar_mensaje(msg, not ok)
        
        def exportar_pdf(e):
            if not visitas_resultado:
                mostrar_mensaje("Primero busque boletas", True)
                return
            
            cliente = db.obtener_cliente(int(dd_cliente.value))
            tiempo_total = db.calcular_tiempo_total(visitas_resultado)
            
            # Generar HTML del reporte para imprimir/PDF
            html = correo.generar_html_reporte_imprimible(cliente, visitas_resultado, txt_desde.value, txt_hasta.value, tiempo_total)
            
            # Abrir en nueva ventana
            page.launch_url(f"data:text/html;charset=utf-8,{html.replace('#', '%23').replace(' ', '%20')}")
        
        page.add(
            crear_appbar("Consultar Boletas"),
            ft.Container(
                content=ft.Column([
                    dd_cliente,
                    ft.Row([txt_desde, txt_hasta], spacing=10),
                    ft.ElevatedButton("Buscar", icon=ft.Icons.SEARCH, bgcolor="#2196f3", color="white", width=float("inf"), on_click=buscar),
                    ft.Row([
                        ft.ElevatedButton("📄 Exportar PDF", bgcolor="#ff9800", color="white", expand=True, on_click=exportar_pdf, tooltip="Descargar reporte como PDF"),
                        ft.ElevatedButton("📧 Enviar Correo", bgcolor="#4caf50", color="white", expand=True, on_click=enviar_reporte, tooltip="Enviar reporte por correo"),
                    ], spacing=10),
                    lbl_resumen,
                    lista
                ], spacing=12),
                padding=15,
                expand=True
            )
        )
        page.update()
    
    # ============== PANTALLA CONFIGURACIÓN ==============
    
    def ir_configuracion():
        """Pantalla de configuración"""
        page.clean()
        
        txt_host = ft.TextField(label="Servidor SMTP", value=db.obtener_config('smtp_host', ''), border_radius=10, hint_text="smtp.gmail.com")
        txt_port = ft.TextField(label="Puerto", value=db.obtener_config('smtp_port', '587'), border_radius=10)
        txt_user = ft.TextField(label="Usuario", value=db.obtener_config('smtp_user', ''), border_radius=10)
        txt_pass = ft.TextField(label="Contraseña", value=db.obtener_config('smtp_pass', ''), password=True, can_reveal_password=True, border_radius=10)
        txt_from = ft.TextField(label="Correo remitente", value=db.obtener_config('smtp_from', ''), border_radius=10)
        
        def guardar(e):
            db.guardar_config('smtp_host', txt_host.value)
            db.guardar_config('smtp_port', txt_port.value)
            db.guardar_config('smtp_user', txt_user.value)
            db.guardar_config('smtp_pass', txt_pass.value)
            db.guardar_config('smtp_from', txt_from.value or txt_user.value)
            mostrar_mensaje("Configuración guardada")
        
        def probar(e):
            guardar(e)
            ok, msg = correo.enviar_correo(
                txt_user.value,
                "Prueba App Soporte",
                "<h1>✅ Configuración correcta</h1><p>El correo funciona correctamente.</p>"
            )
            mostrar_mensaje(msg, not ok)
        
        page.add(
            crear_appbar("Configuración"),
            ft.Container(
                content=ft.Column([
                    ft.Text("📧 Configuración de Correo", size=18, weight=ft.FontWeight.BOLD),
                    txt_host,
                    txt_port,
                    txt_user,
                    txt_pass,
                    txt_from,
                    ft.Row([
                        ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, bgcolor="#4caf50", color="white", expand=True, on_click=guardar),
                        ft.ElevatedButton("Probar", icon=ft.Icons.SEND, bgcolor="#2196f3", color="white", expand=True, on_click=probar),
                    ], spacing=10)
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                padding=20
            )
        )
        page.update()
    
    # Iniciar en pantalla principal
    ir_inicio()

# Ejecutar app
ft.app(
    target=main,
    port=int(os.environ.get("PORT", 8080)),
    view=None
)

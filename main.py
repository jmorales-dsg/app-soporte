"""
App Soporte - Gestión de Visitas Técnicas
"""
import flet as ft
import os
from datetime import datetime, date, timedelta
import database as db
import correo

def main(page: ft.Page):
    """Aplicación principal"""
    
    # VERSIÓN - cambiar con cada deploy para verificar
    VERSION = "1.2.8"
    
    # Configuración de la página
    page.title = f"PcGraf-Soporte v{VERSION}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 450
    page.window_height = 750
    
    # Variable de sesión para recordar el soportista seleccionado
    soportista_sesion = {"id": None}
    
    # ============== COMPONENTES COMUNES ==============
    
    def reconectar(e):
        """Recarga la página para reconectar"""
        page.controls.clear()
        page.update()
        ir_inicio()
    
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
            color="white",
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Reconectar",
                    on_click=reconectar
                )
            ]
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
            # Header con botón reconectar
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(expand=True),  # Espaciador izquierdo
                        ft.Column([
                            ft.Text("📋 PcGraf-Soporte", size=28, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text("Gestión de Visitas Técnicas", size=14, color="#ffffffcc"),
                            ft.Text(f"v{VERSION}", size=10, color="#ffffff88")
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                icon_color="white",
                                tooltip="Reconectar",
                                on_click=reconectar
                            ),
                            expand=True,
                            alignment=ft.Alignment(1, -1)  # Derecha arriba
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor="#2196f3",
                padding=20,
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
        
        # Determinar soportista inicial - usar el de sesión si existe
        if visita.get('soportista_id'):
            soportista_inicial = str(visita.get('soportista_id'))
        elif soportista_sesion["id"]:
            soportista_inicial = str(soportista_sesion["id"])
        else:
            soportista_inicial = str(soportistas[0]['id'])
        
        # Cargar clientes ANTES de crear el dropdown
        clientes_actuales = db.obtener_clientes(soportista_id=int(soportista_inicial))
        ver_todos_inicial = False
        if not clientes_actuales:
            clientes_actuales = db.obtener_clientes()
            ver_todos_inicial = True
        
        # Crear opciones de clientes
        opciones_clientes = [ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in clientes_actuales]
        if not opciones_clientes:
            opciones_clientes = [ft.dropdown.Option(key="", text="-- No hay clientes --")]
        
        # Dropdown de clientes - YA con opciones cargadas, con búsqueda
        dd_cliente = ft.Dropdown(
            label="Cliente *",
            options=opciones_clientes,
            value=str(visita.get('cliente_id', '')) if visita.get('cliente_id') else "",
            border_radius=10,
            expand=True,
            enable_filter=True,
            editable=True
        )
        
        # Checkbox para ver todos los clientes
        chk_ver_todos = ft.Checkbox(label="Ver todos los clientes", value=ver_todos_inicial)
        
        # Dropdown de soportistas
        dd_soportista = ft.Dropdown(
            label="Técnico *",
            options=[ft.dropdown.Option(key=str(s['id']), text=s['nombre']) for s in soportistas],
            value=soportista_inicial,
            border_radius=10
        )
        
        def actualizar_clientes(e=None):
            """Actualiza la lista de clientes según el soportista seleccionado"""
            nonlocal clientes_actuales
            
            if chk_ver_todos.value or not dd_soportista.value:
                clientes_actuales = db.obtener_clientes()
            else:
                clientes_actuales = db.obtener_clientes(soportista_id=int(dd_soportista.value))
                if not clientes_actuales:
                    clientes_actuales = db.obtener_clientes()
                    chk_ver_todos.value = True
            
            dd_cliente.options = [ft.dropdown.Option(key=str(c['id']), text=c['nombre']) for c in clientes_actuales]
            
            if dd_cliente.value and not any(str(c['id']) == dd_cliente.value for c in clientes_actuales):
                dd_cliente.value = ""
            
            if not clientes_actuales:
                dd_cliente.options = [ft.dropdown.Option(key="", text="-- No hay clientes --")]
            
            page.update()
        
        dd_soportista.on_change = actualizar_clientes
        chk_ver_todos.on_change = actualizar_clientes
        
        txt_persona = ft.TextField(label="Persona Atendida (opcional)", value=visita.get('persona_atendida', ''), border_radius=10)
        
        # Fecha y hora
        hoy = date.today()
        ahora = datetime.now().strftime('%H:%M')
        
        # Fecha con flechas para cambiar días
        fecha_actual = {"valor": visita.get('fecha', hoy.strftime('%Y-%m-%d'))}
        txt_fecha = ft.TextField(label="Fecha", value=fecha_actual["valor"], border_radius=10, width=120, text_size=13)
        
        def cambiar_fecha(dias):
            try:
                fecha_obj = datetime.strptime(txt_fecha.value, '%Y-%m-%d')
                fecha_obj = fecha_obj + timedelta(days=dias)
                txt_fecha.value = fecha_obj.strftime('%Y-%m-%d')
                page.update()
            except:
                pass
        
        btn_fecha_menos = ft.IconButton(icon=ft.Icons.ARROW_LEFT, icon_size=20, on_click=lambda e: cambiar_fecha(-1), tooltip="Día anterior")
        btn_fecha_mas = ft.IconButton(icon=ft.Icons.ARROW_RIGHT, icon_size=20, on_click=lambda e: cambiar_fecha(1), tooltip="Día siguiente")
        btn_fecha_hoy = ft.TextButton("Hoy", on_click=lambda e: (setattr(txt_fecha, 'value', hoy.strftime('%Y-%m-%d')), page.update()))
        
        txt_hora = ft.TextField(label="Hora", value=visita.get('hora_inicio', ahora), border_radius=10, width=80, text_size=13)
        txt_duracion = ft.TextField(label="Min", value=str(visita.get('duracion_minutos', '30')), border_radius=10, width=60, text_size=13, keyboard_type=ft.KeyboardType.NUMBER)
        
        txt_trabajo = ft.TextField(
            label="Trabajo Realizado *",
            value=visita.get('trabajo_realizado', ''),
            multiline=True,
            min_lines=4,
            max_lines=6,
            border_radius=10,
            text_size=13
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
            
            # Guardar soportista en sesión para próximas visitas
            soportista_sesion["id"] = int(dd_soportista.value)
            
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
        
        page.add(
            crear_appbar("Editar Visita" if id else "Nueva Visita"),
            ft.Container(
                content=ft.Column([
                    dd_soportista,
                    ft.Row([dd_cliente, chk_ver_todos], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    txt_persona,
                    # Fila 1: Fecha con flechas
                    ft.Row([btn_fecha_menos, txt_fecha, btn_fecha_mas, btn_fecha_hoy], 
                           spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    # Fila 2: Hora y Duración
                    ft.Row([txt_hora, ft.Text("Duración:", size=12), txt_duracion, ft.Text("min", size=12)], 
                           spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    txt_trabajo,
                    # Fila 3: Pendiente y Enviar correo juntos
                    ft.Row([chk_pendiente, chk_enviar_correo], spacing=10),
                    txt_pendiente,
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
        clientes_filtrados = clientes.copy()
        cliente_seleccionado = {"id": None, "nombre": ""}
        
        # Campo de búsqueda
        txt_buscar_cliente = ft.TextField(
            label="🔍 Buscar Cliente",
            border_radius=10,
            on_change=lambda e: filtrar_clientes(e.control.value)
        )
        
        # Lista de clientes filtrados
        lista_clientes = ft.ListView(height=150, spacing=2)
        
        def filtrar_clientes(texto):
            nonlocal clientes_filtrados
            texto = (texto or "").lower().strip()
            if texto:
                clientes_filtrados = [c for c in clientes if texto in c['nombre'].lower()]
            else:
                clientes_filtrados = clientes.copy()
            actualizar_lista_clientes()
        
        def seleccionar_cliente(cliente):
            cliente_seleccionado["id"] = cliente['id']
            cliente_seleccionado["nombre"] = cliente['nombre']
            txt_buscar_cliente.value = cliente['nombre']
            txt_buscar_cliente.label = f"✅ Cliente: {cliente['nombre']}"
            lista_clientes.visible = False
            page.update()
        
        def actualizar_lista_clientes():
            lista_clientes.controls.clear()
            for c in clientes_filtrados[:20]:  # Máximo 20 resultados
                lista_clientes.controls.append(
                    ft.Container(
                        content=ft.Text(c['nombre'], size=13),
                        bgcolor="#f5f5f5",
                        border_radius=5,
                        padding=10,
                        on_click=lambda e, cli=c: seleccionar_cliente(cli)
                    )
                )
            lista_clientes.visible = len(clientes_filtrados) > 0
            page.update()
        
        # Inicializar lista
        actualizar_lista_clientes()
        
        # Contenedor de búsqueda de cliente
        contenedor_cliente = ft.Column([
            txt_buscar_cliente,
            lista_clientes
        ], spacing=5)
        
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1).strftime('%Y-%m-%d')
        
        txt_desde = ft.TextField(label="Desde", value=primer_dia_mes, border_radius=10, width=110, text_size=12)
        txt_hasta = ft.TextField(label="Hasta", value=hoy.strftime('%Y-%m-%d'), border_radius=10, width=110, text_size=12)
        
        def abrir_calendario_desde(e):
            date_picker_desde.open = True
            page.update()
        
        def abrir_calendario_hasta(e):
            date_picker_hasta.open = True
            page.update()
        
        def fecha_desde_seleccionada(e):
            txt_desde.value = e.control.value.strftime('%Y-%m-%d')
            page.update()
        
        def fecha_hasta_seleccionada(e):
            txt_hasta.value = e.control.value.strftime('%Y-%m-%d')
            page.update()
        
        date_picker_desde = ft.DatePicker(on_change=fecha_desde_seleccionada)
        date_picker_hasta = ft.DatePicker(on_change=fecha_hasta_seleccionada)
        page.overlay.extend([date_picker_desde, date_picker_hasta])
        
        btn_cal_desde = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_size=20, on_click=abrir_calendario_desde, tooltip="Seleccionar fecha")
        btn_cal_hasta = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_size=20, on_click=abrir_calendario_hasta, tooltip="Seleccionar fecha")
        
        lista = ft.ListView(spacing=10, expand=True)
        lbl_resumen = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        
        visitas_resultado = []
        
        def buscar(e):
            nonlocal visitas_resultado
            if not cliente_seleccionado["id"]:
                mostrar_mensaje("Seleccione un cliente de la lista", True)
                return
            
            visitas_resultado = db.obtener_visitas_cliente(
                int(cliente_seleccionado["id"]),
                txt_desde.value,
                txt_hasta.value
            )
            
            # DEBUG: imprimir datos de la primera visita
            if visitas_resultado:
                print(f"DEBUG v1.0.8 - Primera visita: {visitas_resultado[0]}")
            
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
            
            # Lista de visitas - CON LABELS EXPLÍCITOS
            for v in visitas_resultado:
                boleta_id = v.get('id', '?')
                fecha = v.get('fecha', 'Sin fecha')
                hora = v.get('hora_inicio', '??:??')
                duracion = v.get('duracion_minutos', 0)
                soportista = v.get('soportista_nombre', 'SIN TÉCNICO')
                trabajo = v.get('trabajo_realizado', '(sin detalle)')
                
                # Crear Card con cada campo en línea separada
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"📋 Boleta #{boleta_id} - {fecha}", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
                            ft.Text(f"Hora: {hora}", size=12),
                            ft.Text(f"Duración: {db.formatear_duracion(duracion)}", size=12),
                            ft.Text(f"Técnico: {soportista}", size=12),
                            ft.Divider(height=1),
                            ft.Text(f"Trabajo: {trabajo}", size=13),
                        ], spacing=3),
                        padding=12
                    )
                )
                lista.controls.append(card)
            
            
            
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
            
            cliente = db.obtener_cliente(int(cliente_seleccionado["id"]))
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
            
            # Construir texto del reporte
            lineas = [
                f"═══ REPORTE DE VISITAS ═══",
                f"Cliente: {cliente_seleccionado['nombre']}",
                f"Período: {txt_desde.value} al {txt_hasta.value}",
                f"Total: {len(visitas_resultado)} visitas",
                ""
            ]
            
            for v in visitas_resultado:
                lineas.append(f"▶ Boleta #{v.get('id')} - {v.get('fecha')}")
                lineas.append(f"  Hora: {v.get('hora_inicio', 'N/A')} | Duración: {db.formatear_duracion(v.get('duracion_minutos', 0))}")
                lineas.append(f"  Técnico: {v.get('soportista_nombre', 'N/A')}")
                lineas.append(f"  Trabajo: {v.get('trabajo_realizado', '')}")
                lineas.append("")
            
            texto_reporte = "\n".join(lineas)
            
            # Mostrar diálogo con el reporte
            def cerrar(ev):
                dlg.open = False
                page.update()
            
            btn_copiar_ref = ft.Ref[ft.ElevatedButton]()
            txt_reporte_ref = ft.Ref[ft.TextField]()
            
            async def copiar_reporte(ev):
                try:
                    # Intentar con JavaScript (funciona mejor en iOS)
                    js_code = f'''
                    (async () => {{
                        try {{
                            await navigator.clipboard.writeText(`{texto_reporte.replace('`', "'").replace('\\', '\\\\')}`);
                            return 'ok';
                        }} catch(e) {{
                            return 'error';
                        }}
                    }})()
                    '''
                    result = await page.run_javascript_async(js_code)
                    if result == 'ok':
                        btn_copiar_ref.current.text = "✅ ¡Copiado!"
                        btn_copiar_ref.current.bgcolor = "#4caf50"
                    else:
                        raise Exception("JS clipboard failed")
                except:
                    # Fallback: intentar método de Flet
                    try:
                        page.set_clipboard(texto_reporte)
                        btn_copiar_ref.current.text = "✅ ¡Copiado!"
                        btn_copiar_ref.current.bgcolor = "#4caf50"
                    except:
                        # Si todo falla, dar instrucciones
                        btn_copiar_ref.current.text = "📱 Mantén presionado el texto → Copiar"
                        btn_copiar_ref.current.bgcolor = "#ff9800"
                page.update()
            
            txt_reporte = ft.TextField(value=texto_reporte, multiline=True, read_only=False, min_lines=10, max_lines=12, ref=txt_reporte_ref)
            
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("📄 Reporte para Imprimir"),
                content=ft.Column([
                    ft.Text("Toque 'Copiar' y pegue en Word o WhatsApp:", size=12),
                    txt_reporte,
                    ft.Row([
                        ft.ElevatedButton("📋 Copiar Todo", bgcolor="#2196f3", color="white", on_click=copiar_reporte, ref=btn_copiar_ref),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], tight=True, width=350, spacing=10),
                actions=[ft.TextButton("Cerrar", on_click=cerrar)]
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()
        
        page.add(
            crear_appbar("Consultar Boletas"),
            ft.Container(
                content=ft.Column([
                    contenedor_cliente,
                    ft.Row([txt_desde, btn_cal_desde, txt_hasta, btn_cal_hasta], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
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

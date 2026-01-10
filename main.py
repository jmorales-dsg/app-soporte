import flet as ft
import os

def main(page: ft.Page):
    """App de gestión de pendientes/soporte"""
    
    # Configuración de la página
    page.title = "App Soporte"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 600
    
    # Lista de tareas
    tareas = ft.Column(
        scroll=ft.ScrollMode.AUTO, 
        expand=True,
        spacing=10
    )
    
    # Campo para nueva tarea
    nueva_tarea = ft.TextField(
        hint_text="Escriba una nueva tarea...",
        expand=True,
        border_radius=10,
        on_submit=lambda e: agregar_tarea(e)
    )
    
    def agregar_tarea(e):
        """Agrega una tarea a la lista"""
        if nueva_tarea.value.strip():
            tarea = crear_tarea(nueva_tarea.value.strip())
            tareas.controls.append(tarea)
            nueva_tarea.value = ""
            page.update()
    
    def crear_tarea(texto):
        """Crea un componente de tarea"""
        
        def eliminar_tarea(e):
            tareas.controls.remove(contenedor)
            page.update()
        
        def marcar_completada(e):
            if checkbox.value:
                label.style = ft.TextStyle(
                    decoration=ft.TextDecoration.LINE_THROUGH,
                    color="#9e9e9e"
                )
            else:
                label.style = None
            page.update()
        
        checkbox = ft.Checkbox(
            value=False,
            on_change=marcar_completada
        )
        
        label = ft.Text(texto, expand=True, size=14)
        
        btn_eliminar = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color="#ef5350",
            tooltip="Eliminar",
            on_click=eliminar_tarea
        )
        
        contenedor = ft.Container(
            content=ft.Row([checkbox, label, btn_eliminar]),
            bgcolor="#f5f5f5",
            border_radius=10,
            padding=10
        )
        
        return contenedor
    
    # Encabezado
    encabezado = ft.Container(
        content=ft.Column([
            ft.Text("📋 App Soporte", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Gestiona tus pendientes", size=14, color="#757575")
        ]),
        margin=ft.margin.only(bottom=20)
    )
    
    # Barra de agregar tarea
    barra_agregar = ft.Row([
        nueva_tarea,
        ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE,
            icon_color="#2196f3",
            icon_size=35,
            tooltip="Agregar tarea",
            on_click=agregar_tarea
        )
    ])
    
    # Agregar todo a la página
    page.add(
        encabezado,
        barra_agregar,
        ft.Divider(),
        tareas
    )


# Ejecutar app
# PORT es variable de entorno que Railway asigna automáticamente
ft.app(
    target=main,
    port=int(os.environ.get("PORT", 8080)),
    view=None  # None = modo servidor web
)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import date, datetime
import io

# Configuración de página
st.set_page_config(
    page_title="SGC & Mejora Continua 4.0",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para apariencia moderna y ágil
st.markdown("""
<style>
    .main-header {font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem;}
    .sub-header {font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem;}
    .metric-card {background-color: #F8FAFC; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #2563EB;}
    .alert-danger {background-color: #FEE2E2; color: #991B1B; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #DC2626; font-weight: 600;}
    .alert-success {background-color: #DCFCE7; color: #166534; padding: 0.75rem; border-radius: 0.5rem; border-left: 4px solid #16A34A; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS DE DEMOSTRACIÓN (PLÁSTICOS INDUSTRIALES DEL NORTE) ---
def init_demo_data():
    st.session_state.empresa = "Plásticos Industriales del Norte S.A."
    st.session_state.responsable = "Ing. Alberto Antonio García"
    st.session_state.fecha_reporte = str(date.today())

    # Módulo A: Voz del Cliente
    st.session_state.voc_df = pd.DataFrame([
        {"ID": "VOC-01", "Fecha": "2026-11-02", "Tipo Cliente": "Externo", "Fuente": "Reclamo Formal", "Categoría": "Variabilidad de Peso", "Detalle": "Envases fuera de tolerancia en lote L-402", "Prioridad": "Alta"},
        {"ID": "VOC-02", "Fecha": "2026-11-05", "Tipo Cliente": "Interno", "Fuente": "Operador Línea 2", "Categoría": "Cambio de Molde Lento", "Detalle": "Demora excesiva buscando moldes en almacén", "Prioridad": "Alta"},
        {"ID": "VOC-03", "Fecha": "2026-11-08", "Tipo Cliente": "Externo", "Fuente": "Encuesta Trimestral", "Categoría": "Sellado Deficiente", "Detalle": "Rebaba en cuello de envase alimentario 500ml", "Prioridad": "Media"},
        {"ID": "VOC-04", "Fecha": "2026-11-12", "Tipo Cliente": "Interno", "Fuente": "Supervisor Turno B", "Categoría": "Método No Estandarizado", "Detalle": "Cada turno ajusta parámetros distintos en inyectora", "Prioridad": "Alta"},
        {"ID": "VOC-05", "Fecha": "2026-11-15", "Tipo Cliente": "Externo", "Fuente": "Reclamo Formal", "Categoría": "Variabilidad de Peso", "Detalle": "Diferencia de espesor en paredes de envase 1L", "Prioridad": "Alta"},
    ])

    # Módulo A: Documentos ISO 9001
    st.session_state.iso_df = pd.DataFrame([
        {"Código": "PRO-INY-01", "Procedimiento": "Operación Estándar Máquina Inyectora", "Versión": "v3.2", "Responsable": "Jefe de Producción", "Última Revisión": "2026-10-15", "Estado": "Vigente"},
        {"Código": "PRO-MOL-02", "Procedimiento": "Cambio Rápido y Almacenamiento de Moldes (SMED)", "Versión": "v2.0", "Responsable": "Ing. de Métodos", "Última Revisión": "2026-11-01", "Estado": "Vigente"},
        {"Código": "PRO-CAL-03", "Procedimiento": "Control Estadístico de Peso en Envases", "Versión": "v1.4", "Responsable": "Líder de Calidad", "Última Revisión": "2026-09-20", "Estado": "En Revisión"},
        {"Código": "PRO-AUD-04", "Procedimiento": "Auditoría Interna de Puesto de Trabajo 5S", "Versión": "v1.1", "Responsable": "Coordinador SGC", "Última Revisión": "2026-08-10", "Estado": "Vigente"},
    ])

    # Módulo A: Pareto Defectos
    st.session_state.pareto_df = pd.DataFrame([
        {"Defecto": "Variabilidad de peso (>±2g)", "Frecuencia": 68},
        {"Defecto": "Rebaba en línea de partición", "Frecuencia": 29},
        {"Defecto": "Contaminación / Puntos negros", "Frecuencia": 14},
        {"Defecto": "Incompleto / Falta de llenado", "Frecuencia": 9},
        {"Defecto": "Deformación al desmoldeo", "Frecuencia": 5},
    ])

    # Módulo A: Ishikawa (6M)
    st.session_state.ishikawa_problema = "Variabilidad excesiva en el peso de envases plásticos"
    st.session_state.ishikawa_data = {
        "Mano de Obra": "Operarios de turnos A, B y C aplican criterios distintos; falta de capacitación unificada.",
        "Maquinaria": "Fluctuación térmica en boquilla de inyectora #2; desgaste en válvula check.",
        "Materiales": "Variación en índice de fluidez (MFI) entre lotes de resina de polipropileno.",
        "Método": "Procedimientos documentados desactualizados; ausencia de hoja estándar de parámetros.",
        "Medio Ambiente": "Cambios bruscos de temperatura ambiental entre turno diurno y nocturno.",
        "Medición": "Básculas de piso sin calibración periódica verificada en línea 3."
    }

    # Módulo A: Hoja de Verificación
    st.session_state.checklist_df = pd.DataFrame([
        {"Punto de Control": "Temperatura de zona de alimentación (210°C ± 5°C)", "Lunes": 1, "Martes": 1, "Miércoles": 0, "Jueves": 1, "Viernes": 1},
        {"Punto de Control": "Presión de sostenimiento según ficha estándar", "Lunes": 0, "Martes": 1, "Miércoles": 0, "Jueves": 0, "Viernes": 1},
        {"Punto de Control": "Verificación de tara en báscula digital", "Lunes": 1, "Martes": 1, "Miércoles": 1, "Jueves": 1, "Viernes": 1},
        {"Punto de Control": "Orden de moldes en estantería identificada (5S)", "Lunes": 1, "Martes": 0, "Miércoles": 1, "Jueves": 1, "Viernes": 1},
    ])

    # Módulo A y B: Datos de Proceso (Peso de envases en gramos, Nominal = 50.0g, LIE = 48.5g, LSE = 51.5g)
    np.random.seed(42)
    pesos_iniciales = np.round(np.random.normal(loc=50.15, scale=0.48, size=40), 2)
    st.session_state.proceso_datos = ", ".join(map(str, pesos_iniciales))
    st.session_state.lie = 48.5
    st.session_state.lse = 51.5
    st.session_state.nominal = 50.0

    # Módulo B: Proyectos PHVA (PDCA)
    st.session_state.pdca_df = pd.DataFrame([
        {
            "Proyecto": "Estandarización de Parámetros de Inyección",
            "Planificar (P)": "Reducir dispersión de peso en Línea 1 y 2 un 50% mediante hoja única de parámetros.",
            "Hacer (H - Piloto)": "Prueba piloto de 2 semanas en Turno A con nuevos estándares y capacitación.",
            "Verificar (V)": "Desviación estándar bajó de 0.65g a 0.28g; Cpk subió de 0.78 a 1.38.",
            "Actuar (A)": "Estandarizado en PRO-INY-01 y desplegado a los 3 turnos.",
            "Estado": "Completado"
        },
        {
            "Proyecto": "Optimización SMED Cambio de Moldes",
            "Planificar (P)": "Reducir tiempo de cambio de molde de 45 min a <20 min.",
            "Hacer (H - Piloto)": "Separar preparación externa (precalentamiento) en Línea 3.",
            "Verificar (V)": "Tiempo promedio bajó a 18 min (-60%).",
            "Actuar (A)": "En proceso de actualización de instructivo PRO-MOL-02.",
            "Estado": "En Verificación"
        }
    ])

    # Módulo B: Carta DMAIC
    st.session_state.dmaic = {
        "titulo": "Reducción de Variabilidad de Peso en Envases Alimentarios",
        "objetivo": "Disminuir la desviación estándar del peso en un 50% y lograr Cpk >= 1.33 en 4 meses.",
        "equipo": "Líder: Ing. Métodos | Patrocinador: Gerente General | Miembros: Supervisores A/B/C, Calidad.",
        "cronograma": "Definir (Sem 1-2) -> Medir (Sem 3-5) -> Analizar (Sem 6-9) -> Mejorar (Sem 10-13) -> Controlar (Sem 14-16).",
        "beneficios": "Ahorro de $18,500/año en resina de polipropileno y reducción de 85% en reclamos de clientes.",
        "fase_actual": "Controlar"
    }

    # Módulo B: Buzón Kaizen
    st.session_state.kaizen_df = pd.DataFrame([
        {"ID": "KZN-01", "Proponente": "Carlos Mendoza (Operador)", "Área": "Almacén Moldes", "Propuesta": "Código de colores y etiquetas QR en estantes de moldes", "Impacto": "Alto", "Estado": "Estandarizada"},
        {"ID": "KZN-02", "Proponente": "María Pérez (Calidad)", "Área": "Línea 2", "Propuesta": "Alerta visual luminosa cuando el peso sale de ±1.0g", "Impacto": "Alto", "Estado": "En Prueba Piloto"},
        {"ID": "KZN-03", "Proponente": "Luis Gómez (Mantenimiento)", "Área": "Inyectoras", "Propuesta": "Checklist rápido de 3 minutos antes de arranque de turno", "Impacto": "Medio", "Estado": "Evaluación"},
    ])

    # Módulo B: Lista 5S
    st.session_state.s5_df = pd.DataFrame([
        {"Área": "Almacén de Moldes", "Seiri (Clasificar)": 5, "Seiton (Ordenar)": 5, "Seiso (Limpiar)": 4, "Seiketsu (Estandarizar)": 4, "Shitsuke (Sostener)": 4},
        {"Área": "Línea de Inyección 1", "Seiri (Clasificar)": 4, "Seiton (Ordenar)": 4, "Seiso (Limpiar)": 4, "Seiketsu (Estandarizar)": 3, "Shitsuke (Sostener)": 3},
        {"Área": "Zona de Empaque", "Seiri (Clasificar)": 5, "Seiton (Ordenar)": 4, "Seiso (Limpiar)": 5, "Seiketsu (Estandarizar)": 4, "Shitsuke (Sostener)": 4},
    ])

    # Módulo C: Fases Implementación del Cambio
    st.session_state.cambio_fases_df = pd.DataFrame([
        {"Fase": "1. Diagnóstico", "Tareas Clave": "Estudio de tiempos, Pareto e Ishikawa participativo", "Responsable": "Ing. Métodos", "Fecha Límite": "2026-08-30", "Estado": "Completado", "Avance (%)": 100},
        {"Fase": "2. Diseño", "Tareas Clave": "Nuevo método estándar de inyección y layout 5S", "Responsable": "Equipo Mejora", "Fecha Límite": "2026-09-20", "Estado": "Completado", "Avance (%)": 100},
        {"Fase": "3. Validación", "Tareas Clave": "Prueba piloto en Turno A y ajustes ergonómicos", "Responsable": "Supervisor Turno A", "Fecha Límite": "2026-10-15", "Estado": "Completado", "Avance (%)": 100},
        {"Fase": "4. Implementación", "Tareas Clave": "Capacitación 95 operarios y despliegue en 3 líneas", "Responsable": "RRHH y Producción", "Fecha Límite": "2026-11-15", "Estado": "En Curso", "Avance (%)": 85},
        {"Fase": "5. Seguimiento", "Tareas Clave": "Auditorías semanales y monitoreo de KPIs", "Responsable": "Calidad", "Fecha Límite": "2026-12-20", "Estado": "En Curso", "Avance (%)": 60},
    ])

    # Módulo C: Partes Interesadas (Stakeholders)
    st.session_state.stakeholders_df = pd.DataFrame([
        {"Grupo": "Operarios de Línea (95)", "Nivel Apoyo": "Neutral / Resistencia Leve", "Preocupación Principal": "Miedo a mayor carga de trabajo o sanciones", "Plan de Comunicación": "Talleres prácticos en planta y participación en pruebas piloto"},
        {"Grupo": "Supervisores de Turno", "Nivel Apoyo": "Apoyo Moderado", "Preocupación Principal": "Cumplir cuota de producción durante capacitación", "Plan de Comunicación": "Reuniones semanales de alineación y formación en métodos"},
        {"Grupo": "Mantenimiento", "Nivel Apoyo": "Alto Apoyo", "Preocupación Principal": "Disponibilidad de repuestos para estabilidad térmica", "Plan de Comunicación": "Integración en equipos Kaizen quincenales"},
        {"Grupo": "Calidad y Clientes Internos", "Nivel Apoyo": "Alto Apoyo", "Preocupación Principal": "Reducción de rechazos y reprocesos", "Plan de Comunicación": "Tablero compartido de indicadores en tiempo real"},
    ])

    # Módulo C: Patrocinio Ejecutivo
    st.session_state.patrocinio_df = pd.DataFrame([
        {"Fecha": "2026-09-05", "Nivel": "Alta Dirección (Gerente General)", "Actividad": "Comité Mensual de Revisión", "Decisiones y Recursos": "Aprobación de presupuesto para básculas digitales y estantería 5S"},
        {"Fecha": "2026-10-10", "Nivel": "Liderazgo Intermedio (Supervisores)", "Actividad": "Taller de Ingeniería de Métodos", "Decisiones y Recursos": "Asignación de 30 min quincenales por turno para reuniones Kaizen"},
        {"Fecha": "2026-11-05", "Nivel": "Alta Dirección (Gerente General)", "Actividad": "Recorrido Gemba en Planta", "Decisiones y Recursos": "Reconocimiento público al equipo de Almacén de Moldes por logro SMED"},
    ])

    # Módulo D: Ficha Método Estandarizado
    st.session_state.estandar_df = pd.DataFrame([
        {"Paso": 1, "Actividad": "Verificar temperatura de zonas (210°C) y purgar boquilla", "Tiempo Estándar (s)": 45, "Herramientas": "Pirómetro digital, espátula bronce", "Seguridad / Ergonomía": "Guantes térmicos Nivel 3, careta facial", "Criterio Calidad": "Flujo continuo sin burbujas ni decoloración"},
        {"Paso": 2, "Actividad": "Cargar receta estándar REC-500ML en panel PLC", "Tiempo Estándar (s)": 20, "Herramientas": "Panel táctil PLC", "Seguridad / Ergonomía": "Pantalla a altura visual (1.55m)", "Criterio Calidad": "Presión sostenimiento en 65 bar"},
        {"Paso": 3, "Actividad": "Inspeccionar y pesar muestra de 5 envases consecutivos", "Tiempo Estándar (s)": 35, "Herramientas": "Báscula precisión ±0.01g", "Seguridad / Ergonomía": "Postura neutra, tapete antifatiga", "Criterio Calidad": "Peso entre 48.5g y 51.5g; cero rebaba"},
        {"Paso": 4, "Actividad": "Registrar lectura en gráfico de control y liberar lote", "Tiempo Estándar (s)": 25, "Herramientas": "Tablet / Terminal SGC", "Seguridad / Ergonomía": "Iluminación mínima 500 lux", "Criterio Calidad": "Puntos dentro de límites de control (LCS/LCI)"},
    ])

    # Módulo D: Auditorías de Cumplimiento
    st.session_state.auditorias_df = pd.DataFrame([
        {"ID": "AUD-01", "Fecha": "2026-11-10", "Área": "Línea 1", "Hallazgo": "Operador omitió pesaje de muestra al inicio de turno", "Clasificación": "Desviación de desempeño del trabajador", "Acción Correctiva": "Reentrenamiento en puesto y acompañamiento del supervisor", "Responsable": "Supervisor Turno A", "Estado": "Cerrado"},
        {"ID": "AUD-02", "Fecha": "2026-11-14", "Área": "Línea 2", "Hallazgo": "Tiempo de cambio de molde excede estándar por falta de herramienta accesible", "Clasificación": "Limitación del propio método", "Acción Correctiva": "Enviado al ciclo PDCA/Kaizen para rediseñar carro de herramientas", "Responsable": "Ing. de Métodos", "Estado": "En Ciclo Mejora"},
    ])

    # Módulo D: Tablero KPIs
    st.session_state.kpi_df = pd.DataFrame([
        {"Indicador (KPI)": "Productividad Global (OEE / Unidades/h)", "Línea Base": 100.0, "Meta": 115.0, "Valor Actual": 115.5, "Unidad": "% Índice"},
        {"Indicador (KPI)": "Capacidad del Proceso (Cpk Peso)", "Línea Base": 0.78, "Meta": 1.33, "Valor Actual": 1.38, "Unidad": "Índice"},
        {"Indicador (KPI)": "Tiempo Cambio de Molde (SMED)", "Línea Base": 45.0, "Meta": 20.0, "Valor Actual": 18.0, "Unidad": "Minutos"},
        {"Indicador (KPI)": "Tasa de Desperdicio de Resina", "Línea Base": 4.8, "Meta": 2.0, "Valor Actual": 2.4, "Unidad": "%"},
    ])

if "empresa" not in st.session_state:
    init_demo_data()

# --- FUNCIONES DE CÁLCULO ESTADÍSTICO ---
def parse_datos_proceso(texto):
    try:
        vals = [float(x.strip()) for x in texto.replace("
", ",").split(",") if x.strip() != ""]
        return np.array(vals)
    except Exception:
        return np.array([])

def calcular_capacidad(datos, lie, lse):
    if len(datos) < 2:
        return None
    media = np.mean(datos)
    std = np.std(datos, ddof=1)
    if std == 0:
        return None
    cp = (lse - lie) / (6 * std)
    cpu = (lse - media) / (3 * std)
    cpl = (media - lie) / (3 * std)
    cpk = min(cpu, cpl)
    # Límites de control individuales (I-MR aproximado)
    mr = np.abs(np.diff(datos))
    mr_bar = np.mean(mr)
    d2 = 1.128
    sigma_est = mr_bar / d2
    lcs = media + 3 * sigma_est
    lci = media - 3 * sigma_est
    fuera_control = np.sum((datos > lcs) | (datos < lci))
    return {
        "n": len(datos), "media": media, "std": std,
        "cp": cp, "cpk": cpk, "cpu": cpu, "cpl": cpl,
        "lcs": lcs, "lci": lci, "fuera_control": int(fuera_control)
    }

# --- GENERADOR DE PDFS ---
class ReportePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 58, 138)
        self.cell(0, 8, self.titulo_reporte, ln=True, align="L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        meta = f"Empresa: {st.session_state.empresa} | Fecha: {st.session_state.fecha_reporte} | Responsable: {st.session_state.responsable}"
        self.cell(0, 5, meta.encode("latin-1", "replace").decode("latin-1"), ln=True)
        self.cell(0, 5, f"Fuente de datos: Plataforma Digital SGC & Mejora Continua (Datos cargados en tiempo real)", ln=True)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()} - Documento autogenerado listo para auditoría y decisión gerencial", align="C")

    def seccion(self, texto):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 58, 138)
        self.ln(3)
        self.cell(0, 7, texto.encode("latin-1", "replace").decode("latin-1"), ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 9.5)

    def parrafo(self, texto):
        self.set_font("Helvetica", "", 9.5)
        self.multi_cell(0, 5.5, texto.encode("latin-1", "replace").decode("latin-1"))
        self.ln(2)

def generar_pdf_bytes(tipo):
    pdf = ReportePDF()
    titulos = {
        1: "INFORME 1: DIAGNÓSTICO DE CALIDAD (VOC, PARETO E ISHIKAWA)",
        2: "INFORME 2: PROYECTO DE MEJORA CONTINUA (PDCA / DMAIC)",
        3: "INFORME 3: VARIABILIDAD Y CAPACIDAD DEL PROCESO (CP / CPK)",
        4: "INFORME 4: AUDITORÍA DE CUMPLIMIENTO Y ESTANDARIZACIÓN",
        5: "INFORME 5: IMPLEMENTACIÓN Y GESTIÓN DEL CAMBIO",
        6: "INFORME 6: RESUMEN EJECUTIVO DE INDICADORES (KPI) Y SOSTENIBILIDAD",
        7: "MANUAL DE USUARIO - PLATAFORMA SGC Y MEJORA CONTINUA"
    }
    pdf.titulo_reporte = titulos[tipo]
    pdf.add_page()

    if tipo == 1:
        pdf.seccion("1. Resumen de la Voz del Cliente (VOC)")
        voc = st.session_state.voc_df
        pdf.parrafo(f"Total de registros analizados: {len(voc)} (Externos: {sum(voc['Tipo Cliente']=='Externo')}, Internos: {sum(voc['Tipo Cliente']=='Interno')}).")
        for _, r in voc.iterrows():
            pdf.parrafo(f"- [{r['ID']}] ({r['Tipo Cliente']} - {r['Fuente']}): {r['Categoría']} -> {r['Detalle']} [Prioridad: {r['Prioridad']}]")

        pdf.seccion("2. Priorización de Defectos (Análisis de Pareto 80/20)")
        par = st.session_state.pareto_df.sort_values(by="Frecuencia", ascending=False).copy()
        par["%"] = (par["Frecuencia"] / par["Frecuencia"].sum() * 100).round(1)
        par["% Acum"] = par["%"].cumsum().round(1)
        for _, r in par.iterrows():
            pdf.parrafo(f"- {r['Defecto']}: {r['Frecuencia']} casos ({r['%']}% | Acumulado: {r['% Acum']}%)")

        pdf.seccion(f"3. Análisis de Causa Raíz - Diagrama de Ishikawa (6M)")
        pdf.parrafo(f"Problema principal analizado: {st.session_state.ishikawa_problema}")
        for m, desc in st.session_state.ishikawa_data.items():
            pdf.parrafo(f"* {m}: {desc}")

    elif tipo == 2:
        pdf.seccion("1. Carta de Proyecto Six Sigma (DMAIC)")
        d = st.session_state.dmaic
        pdf.parrafo(f"Proyecto: {d['titulo']}
Objetivo: {d['objetivo']}
Equipo: {d['equipo']}
Cronograma: {d['cronograma']}
Beneficios Esperados: {d['beneficios']}
Fase Actual: {d['fase_actual']}")

        pdf.seccion("2. Estado de Proyectos Ciclo PHVA (PDCA) y Prueba Piloto")
        for _, r in st.session_state.pdca_df.iterrows():
            pdf.parrafo(f"Proyecto: {r['Proyecto']} [Estado: {r['Estado']}]
  - Planificar: {r['Planificar (P)']}
  - Hacer (Piloto): {r['Hacer (H - Piloto)']}
  - Verificar: {r['Verificar (V)']}
  - Actuar: {r['Actuar (A)']}")

    elif tipo == 3:
        datos = parse_datos_proceso(st.session_state.proceso_datos)
        res = calcular_capacidad(datos, st.session_state.lie, st.session_state.lse)
        pdf.seccion("1. Parámetros y Resultados Estadísticos")
        if res:
            pdf.parrafo(f"Tamaño de muestra (n): {res['n']} | Media: {res['media']:.3f} | Desv. Estándar (s): {res['std']:.3f}")
            pdf.parrafo(f"Especificaciones: LIE = {st.session_state.lie} | Nominal = {st.session_state.nominal} | LSE = {st.session_state.lse}")
            pdf.parrafo(f"Índices de Capacidad: Cp = {res['cp']:.2f} | Cpk = {res['cpk']:.2f} (Cpu = {res['cpu']:.2f}, Cpl = {res['cpl']:.2f})")
            pdf.parrafo(f"Control Estadístico: LCS = {res['lcs']:.3f} | LCI = {res['lci']:.3f} | Puntos fuera de control: {res['fuera_control']}")
            pdf.seccion("2. Interpretación Técnica y Decisión")
            interp = "PROCESO CAPAZ (Cpk >= 1.33): El método estandarizado cumple especificaciones con margen seguro." if res['cpk'] >= 1.33 else ("CAPACIDAD MARGINAL (1.00 <= Cpk < 1.33): Requiere monitoreo estricto." if res['cpk'] >= 1.0 else "PROCESO NO CAPAZ (Cpk < 1.00): Alta generación de defectos; requiere intervención inmediata sobre el método.")
            causa = "Se detectaron puntos fuera de control estadístico (Variabilidad de Causa Especial): investigar eventos puntuales." if res['fuera_control'] > 0 else "Proceso estadísticamente estable (solo Variabilidad de Causa Común inherente al método)."
            pdf.parrafo(interp + "
" + causa)
        else:
            pdf.parrafo("Datos insuficientes para calcular capacidad.")

    elif tipo == 4:
        pdf.seccion("1. Hallazgos de Auditoría de Cumplimiento")
        for _, r in st.session_state.auditorias_df.iterrows():
            pdf.parrafo(f"- [{r['ID']}] ({r['Fecha']} - {r['Área']}): {r['Hallazgo']}
  Clasificación: {r['Clasificación']} | Acción: {r['Acción Correctiva']} | Resp: {r['Responsable']} [{r['Estado']}]")
        pdf.seccion("2. Resumen del Método Estandarizado Vigente")
        for _, r in st.session_state.estandar_df.iterrows():
            pdf.parrafo(f"Paso {r['Paso']}: {r['Actividad']} ({r['Tiempo Estándar (s)']}s) - Criterio: {r['Criterio Calidad']}")

    elif tipo == 5:
        pdf.seccion("1. Avance por Fases del Proyecto de Implementación")
        for _, r in st.session_state.cambio_fases_df.iterrows():
            pdf.parrafo(f"- {r['Fase']} [{r['Estado']} - {r['Avance (%)']}%]: {r['Tareas Clave']} (Resp: {r['Responsable']}, Límite: {r['Fecha Límite']})")
        pdf.seccion("2. Mapa de Partes Interesadas y Plan de Comunicación")
        for _, r in st.session_state.stakeholders_df.iterrows():
            pdf.parrafo(f"- {r['Grupo']} ({r['Nivel Apoyo']}): Preocupación: {r['Preocupación Principal']} -> Plan: {r['Plan de Comunicación']}")
        pdf.seccion("3. Registro de Patrocinio Ejecutivo y Liderazgo")
        for _, r in st.session_state.patrocinio_df.iterrows():
            pdf.parrafo(f"- [{r['Fecha']}] {r['Nivel']} ({r['Actividad']}): {r['Decisiones y Recursos']}")

    elif tipo == 6:
        pdf.seccion("1. Tablero de Indicadores Clave (KPI) y Estado de Sostenibilidad")
        for _, r in st.session_state.kpi_df.iterrows():
            # Lógica de cumplimiento (en tiempos o desperdicio menor es mejor)
            menor_mejor = "Tiempo" in r["Indicador (KPI)"] or "Desperdicio" in r["Indicador (KPI)"]
            cumple = r["Valor Actual"] <= r["Meta"] if menor_mejor else r["Valor Actual"] >= r["Meta"]
            estado = "EN META (SOSTENIBLE)" if cumple else "DESVIADO (ALERTA ACTIVA)"
            pdf.parrafo(f"- {r['Indicador (KPI)']}: Base={r['Línea Base']} | Meta={r['Meta']} | Actual={r['Valor Actual']} {r['Unidad']} -> [{estado}]")
        pdf.seccion("2. Conclusión Gerencial de Sostenibilidad")
        pdf.parrafo("Los estándares operativos y equipos Kaizen han consolidado mejoras significativas en productividad y capacidad Cpk. Se mantiene vigilancia activa sobre los indicadores en alerta mediante auditorías constructivas.")

    elif tipo == 7:
        pdf.seccion("1. Propósito de la Aplicación y Usuarios")
        pdf.parrafo("Esta plataforma digital integra la Gestión de la Calidad (ISO 9001), la Mejora Continua (PDCA, DMAIC, Kaizen, 5S), la Gestión del Cambio Organizacional y la Sostenibilidad (Estandarización, Auditorías y KPIs) en un único sistema ágil y basado en datos objetivos. Está diseñada para Gerentes de Operaciones, Ingenieros de Métodos, Líderes de Calidad, Supervisores y Operarios.")
        pdf.seccion("2. Cómo Empezar: Caso de Demostración vs. Datos Propios")
        pdf.parrafo("- Al abrir la aplicación, se carga automáticamente el caso de estudio 'Plásticos Industriales del Norte'.
- En el panel izquierdo (Barra Lateral), puede editar el nombre de su empresa, el responsable, limpiar los datos de ejemplo ('Limpiar / Iniciar en Blanco') o restaurar la demostración en cualquier momento.
- Todas las tablas son editables directamente haciendo clic sobre las celdas, y los gráficos e índices se recalculan instantáneamente.")
        pdf.seccion("3. Recorrido por los 4 Módulos")
        pdf.parrafo("- Módulo A (Calidad): Registre la Voz del Cliente (interno/externo), gestione documentos ISO 9001 y analice Pareto, Ishikawa 6M, Hoja de Verificación, Histograma y Gráfico de Control.
- Módulo B (Mejora Continua): Administre proyectos PDCA con prueba piloto, cartas DMAIC, buzón Kaizen, cálculo automático de Cp/Cpk y auditoría 5S.
- Módulo C (Gestión del Cambio): Controle las 5 fases de implementación, el mapa de stakeholders y el patrocinio ejecutivo.
- Módulo D (Sostenibilidad): Documente fichas de trabajo estándar, registre hallazgos de auditoría (separando desempeño del trabajador vs. limitación del método) y monitoree alertas KPI.")
        pdf.seccion("4. Interpretación de Resultados Clave")
        pdf.parrafo("- Índice Cpk < 1.00: El proceso no es capaz y genera defectos fuera de especificación.
- Índice 1.00 <= Cpk < 1.33: Proceso mínimamente capaz, requiere control estrecho.
- Índice Cpk >= 1.33: Proceso capaz y centrado (estándar Six Sigma/industrial).
- Causa Común vs. Causa Especial: Puntos dentro de los límites LCS/LCI reflejan variación natural del método; puntos fuera de límites indican eventos puntuales (causa especial) a investigar.")
        pdf.seccion("5. Descarga de Informes y Solución de Problemas")
        pdf.parrafo("En la barra lateral izquierda o en la pestaña 'Centro de Informes PDF' puede descargar los 6 informes ejecutivos y este manual en formato PDF con un solo clic. Si un gráfico no se actualiza tras editar una tabla, presione Enter fuera de la celda editada.")

    return bytes(pdf.output())

# --- BARRA LATERAL (CONFIGURACIÓN Y DESCARGAS RÁPIDAS) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/settings.png", width=60)
    st.markdown("### Configuración General")
    st.session_state.empresa = st.text_input("Empresa:", st.session_state.empresa)
    st.session_state.responsable = st.text_input("Responsable:", st.session_state.responsable)
    st.session_state.fecha_reporte = st.text_input("Fecha:", st.session_state.fecha_reporte)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔄 Cargar Demo", use_container_width=True):
            init_demo_data()
            st.rerun()
    with col_b2:
        if st.button("🗑️ Limpiar Datos", use_container_width=True):
            st.session_state.voc_df = st.session_state.voc_df.iloc[0:0]
            st.session_state.pareto_df = pd.DataFrame([{"Defecto": "Defecto Ejemplo", "Frecuencia": 1}])
            st.session_state.proceso_datos = "50.0, 50.1, 49.9"
            st.rerun()

    st.markdown("---")
    st.markdown("### 📖 Manual de Uso")
    st.download_button(
        label="📥 Descargar Manual (PDF)",
        data=generar_pdf_bytes(7),
        file_name="Manual_Usuario_SGC_Mejora_Continua.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    with st.expander("Ver Guía Rápida Aquí"):
        st.caption("1. Navegue por los 4 módulos en las pestañas superiores.
2. Edite cualquier tabla o dato numérico: las gráficas y Cpk se recalculan solos.
3. Descargue los 6 informes PDF listos para gerencia en la última pestaña.")

# --- ENCABEZADO PRINCIPAL ---
st.markdown('<div class="main-header">Plataforma Digital de Gestión de Calidad, Mejora Continua y Cambio</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Organización activa: <b>{st.session_state.empresa}</b> | Enfoque Capítulo 5: Ingeniería de Métodos & Excelencia Operativa</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Módulo A: Calidad (5.1)",
    "🚀 Módulo B: Mejora Continua (5.2)",
    "🤝 Módulo C: Gestión del Cambio (5.3)",
    "🛡️ Módulo D: Sostenibilidad (5.4)",
    "📄 Centro de Informes PDF"
])

# ==============================================================================
# MÓDULO A: GESTIÓN DE LA CALIDAD
# ==============================================================================
with tabs[0]:
    st.subheader("5.1 Principios y Herramientas de Gestión de la Calidad")
    
    col_a1, col_a2 = st.columns([1.2, 1])
    with col_a1:
        st.markdown("#### 1. Registro de la Voz del Cliente (VOC)")
        st.caption("Distingue cliente interno y externo. Edite o agregue filas directamente:")
        st.session_state.voc_df = st.data_editor(st.session_state.voc_df, num_rows="dynamic", use_container_width=True, key="edit_voc")
        if len(st.session_state.voc_df) > 0:
            c_ext = sum(st.session_state.voc_df["Tipo Cliente"] == "Externo")
            c_int = sum(st.session_state.voc_df["Tipo Cliente"] == "Interno")
            st.info(f"Resumen VOC: **{len(st.session_state.voc_df)} registros** ({c_ext} Externos | {c_int} Internos)")

    with col_a2:
        st.markdown("#### 2. Repositorio Documental ISO 9001")
        st.caption("Control de versiones, responsables y revisión para evidencia de auditoría:")
        st.session_state.iso_df = st.data_editor(st.session_state.iso_df, num_rows="dynamic", use_container_width=True, key="edit_iso")

    st.markdown("---")
    st.markdown("#### 3. Herramientas Básicas de Calidad (Cálculo Dinámico)")
    
    c_p1, c_p2 = st.columns([1, 1.5])
    with c_p1:
        st.markdown("**Datos para Diagrama de Pareto**")
        st.session_state.pareto_df = st.data_editor(st.session_state.pareto_df, num_rows="dynamic", use_container_width=True, key="edit_pareto")
    with c_p2:
        if len(st.session_state.pareto_df) > 0 and st.session_state.pareto_df["Frecuencia"].sum() > 0:
            df_p = st.session_state.pareto_df.sort_values(by="Frecuencia", ascending=False).copy()
            df_p["Acumulado (%)"] = (df_p["Frecuencia"].cumsum() / df_p["Frecuencia"].sum()) * 100
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=df_p["Defecto"], y=df_p["Frecuencia"], name="Frecuencia", marker_color="#2563EB"))
            fig_pareto.add_trace(go.Scatter(x=df_p["Defecto"], y=df_p["Acumulado (%)"], name="% Acumulado", yaxis="y2", mode="lines+markers", marker_color="#DC2626"))
            fig_pareto.update_layout(
                title="Diagrama de Pareto (Priorización 80/20)",
                yaxis=dict(title="Frecuencia"),
                yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 105]),
                height=340, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_pareto, use_container_width=True)

    c_ish, c_chk = st.columns(2)
    with c_ish:
        st.markdown("**Diagrama de Ishikawa (Causa-Efecto 6M)**")
        st.session_state.ishikawa_problema = st.text_input("Efecto / Problema Principal:", st.session_state.ishikawa_problema)
        for cat in ["Mano de Obra", "Maquinaria", "Materiales", "Método", "Medio Ambiente", "Medición"]:
            st.session_state.ishikawa_data[cat] = st.text_input(f"🔹 {cat}:", st.session_state.ishikawa_data[cat], key=f"ish_{cat}")

    with c_chk:
        st.markdown("**Hoja de Verificación Semanal (1 = Cumple, 0 = Desviación)**")
        st.session_state.checklist_df = st.data_editor(st.session_state.checklist_df, num_rows="dynamic", use_container_width=True, key="edit_chk")
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        if all(d in st.session_state.checklist_df.columns for d in dias) and len(st.session_state.checklist_df) > 0:
            total_checks = st.session_state.checklist_df[dias].sum().sum()
            max_checks = len(st.session_state.checklist_df) * 5
            pct_chk = (total_checks / max_checks) * 100
            st.metric("Cumplimiento Semanal en Hoja de Verificación", f"{pct_chk:.1f}%", f"{int(total_checks)}/{max_checks} verificaciones")

# ==============================================================================
# MÓDULO B: MEJORA CONTINUA Y OPTIMIZACIÓN DE PROCESOS
# ==============================================================================
with tabs[1]:
    st.subheader("5.2 Mejora Continua, Lean, Six Sigma y Capacidad del Proceso")

    st.markdown("#### 1. Análisis de Variabilidad y Capacidad del Proceso (Cp y Cpk en Tiempo Real)")
    col_cap1, col_cap2 = st.columns([1, 2])
    with col_cap1:
        st.session_state.lie = st.number_input("Límite Inferior Especificación (LIE):", value=float(st.session_state.lie), step=0.1)
        st.session_state.nominal = st.number_input("Valor Nominal Objetivo:", value=float(st.session_state.nominal), step=0.1)
        st.session_state.lse = st.number_input("Límite Superior Especificación (LSE):", value=float(st.session_state.lse), step=0.1)
        st.session_state.proceso_datos = st.text_area("Mediciones reales del proceso (separadas por coma):", st.session_state.proceso_datos, height=130)

    datos_arr = parse_datos_proceso(st.session_state.proceso_datos)
    cap_res = calcular_capacidad(datos_arr, st.session_state.lie, st.session_state.lse)

    with col_cap2:
        if cap_res:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Media (X̄)", f"{cap_res['media']:.2f}")
            m2.metric("Desv. Estándar (s)", f"{cap_res['std']:.3f}")
            m3.metric("Índice Cp", f"{cap_res['cp']:.2f}")
            m4.metric("Índice Cpk", f"{cap_res['cpk']:.2f}", delta="Capaz" if cap_res['cpk'] >= 1.33 else "Revisar")

            if cap_res["cpk"] < 1.0:
                st.markdown('<div class="alert-danger">⚠️ ALERTA DE CAPACIDAD (Cpk < 1.00): El proceso genera unidades fuera de especificación. Requiere rediseño del método de trabajo.</div>', unsafe_allow_html=True)
            elif cap_res["cpk"] < 1.33:
                st.warning("⚠️ CAPACIDAD MARGINAL (1.00 <= Cpk < 1.33): El proceso cumple por poco margen; reducir variabilidad.")
            else:
                st.markdown('<div class="alert-success">✅ PROCESO CAPAZ (Cpk >= 1.33): Variabilidad controlada dentro de estándares Six Sigma.</div>', unsafe_allow_html=True)

            if cap_res["fuera_control"] > 0:
                st.error(f"🔍 Diagnóstico de Variabilidad: Se detectaron **{cap_res['fuera_control']} puntos fuera de límites de control** -> Presencia de **Variabilidad de Causa Especial** (investigar evento puntual en turno/máquina).")
            else:
                st.info("🔍 Diagnóstico de Variabilidad: Todos los puntos están dentro de los límites de control -> Solo existe **Variabilidad de Causa Común** (inherente al método actual).")

    if cap_res:
        g1, g2 = st.columns(2)
        with g1:
            fig_hist = px.histogram(x=datos_arr, nbins=10, title="Histograma de Distribución vs. Especificaciones", labels={"x": "Medición", "y": "Frecuencia"}, color_discrete_sequence=["#3B82F6"])
            fig_hist.add_vline(x=st.session_state.lie, line_dash="dash", line_color="red", annotation_text="LIE")
            fig_hist.add_vline(x=st.session_state.lse, line_dash="dash", line_color="red", annotation_text="LSE")
            fig_hist.add_vline(x=st.session_state.nominal, line_dash="dot", line_color="green", annotation_text="Nominal")
            fig_hist.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hist, use_container_width=True)
        with g2:
            fig_ctrl = go.Figure()
            fig_ctrl.add_trace(go.Scatter(y=datos_arr, mode="lines+markers", name="Muestra", line=dict(color="#1E40AF")))
            fig_ctrl.add_hline(y=cap_res["media"], line_color="green", annotation_text="Media")
            fig_ctrl.add_hline(y=cap_res["lcs"], line_dash="dash", line_color="red", annotation_text="LCS (+3σ)")
            fig_ctrl.add_hline(y=cap_res["lci"], line_dash="dash", line_color="red", annotation_text="LCI (-3σ)")
            fig_ctrl.update_layout(title="Gráfico de Control Estadístico (Monitoreo de Estabilidad)", xaxis_title="Muestra #", yaxis_title="Valor", height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_ctrl, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 2. Gestor de Proyectos PHVA (PDCA) con Prueba Piloto")
    st.session_state.pdca_df = st.data_editor(st.session_state.pdca_df, num_rows="dynamic", use_container_width=True, key="edit_pdca")

    c_dm, c_kz = st.columns(2)
    with c_dm:
        st.markdown("#### 3. Carta de Proyecto Six Sigma (DMAIC)")
        st.session_state.dmaic["titulo"] = st.text_input("Título del Proyecto DMAIC:", st.session_state.dmaic["titulo"])
        st.session_state.dmaic["objetivo"] = st.text_area("Objetivo Cuantificable:", st.session_state.dmaic["objetivo"], height=70)
        st.session_state.dmaic["equipo"] = st.text_input("Equipo y Roles:", st.session_state.dmaic["equipo"])
        st.session_state.dmaic["cronograma"] = st.text_input("Cronograma por Fases:", st.session_state.dmaic["cronograma"])
        st.session_state.dmaic["beneficios"] = st.text_input("Beneficios Esperados:", st.session_state.dmaic["beneficios"])
        st.session_state.dmaic["fase_actual"] = st.selectbox("Fase Actual:", ["Definir", "Medir", "Analizar", "Mejorar", "Controlar"], index=4)

    with c_kz:
        st.markdown("#### 4. Buzón de Propuestas Kaizen")
        st.session_state.kaizen_df = st.data_editor(st.session_state.kaizen_df, num_rows="dynamic", use_container_width=True, key="edit_kaizen")
        st.markdown("#### 5. Lista de Verificación 5S (Escala 1 a 5)")
        st.session_state.s5_df = st.data_editor(st.session_state.s5_df, num_rows="dynamic", use_container_width=True, key="edit_5s")
        cols_5s = ["Seiri (Clasificar)", "Seiton (Ordenar)", "Seiso (Limpiar)", "Seiketsu (Estandarizar)", "Shitsuke (Sostener)"]
        if len(st.session_state.s5_df) > 0 and all(c in st.session_state.s5_df.columns for c in cols_5s):
            prom_5s = st.session_state.s5_df[cols_5s].mean().mean()
            st.metric("Puntaje Global 5S en Planta", f"{prom_5s:.2f} / 5.00", f"{(prom_5s/5)*100:.0f}% de cumplimiento")

# ==============================================================================
# MÓDULO C: IMPLEMENTACIÓN Y GESTIÓN DEL CAMBIO
# ==============================================================================
with tabs[2]:
    st.subheader("5.3 Implementación y Gestión del Cambio Organizacional")

    st.markdown("#### 1. Seguimiento de Proyecto de Implementación (5 Fases)")
    st.session_state.cambio_fases_df = st.data_editor(st.session_state.cambio_fases_df, num_rows="dynamic", use_container_width=True, key="edit_fases")
    if len(st.session_state.cambio_fases_df) > 0:
        avance_total = st.session_state.cambio_fases_df["Avance (%)"].mean()
        st.progress(int(avance_total) / 100, text=f"Avance Global de Implementación del Cambio: {avance_total:.1f}%")

    st.markdown("---")
    c_stk, c_pat = st.columns(2)
    with c_stk:
        st.markdown("#### 2. Mapa de Partes Interesadas y Plan de Comunicación")
        st.session_state.stakeholders_df = st.data_editor(st.session_state.stakeholders_df, num_rows="dynamic", use_container_width=True, key="edit_stk")

    with c_pat:
        st.markdown("#### 3. Registro de Patrocinio Ejecutivo y Liderazgo Intermedio")
        st.session_state.patrocinio_df = st.data_editor(st.session_state.patrocinio_df, num_rows="dynamic", use_container_width=True, key="edit_pat")

# ==============================================================================
# MÓDULO D: SOSTENIBILIDAD DE LAS MEJORAS
# ==============================================================================
with tabs[3]:
    st.subheader("5.4 Sostenibilidad de las Mejoras y Control Operativo")

    st.markdown("#### 1. Tablero de Indicadores Clave (KPI) con Alertas Automáticas")
    st.session_state.kpi_df = st.data_editor(st.session_state.kpi_df, num_rows="dynamic", use_container_width=True, key="edit_kpi")

    if len(st.session_state.kpi_df) > 0:
        kpi_cols = st.columns(len(st.session_state.kpi_df))
        for idx, row in st.session_state.kpi_df.iterrows():
            menor_mejor = "Tiempo" in str(row["Indicador (KPI)"]) or "Desperdicio" in str(row["Indicador (KPI)"])
            cumple = row["Valor Actual"] <= row["Meta"] if menor_mejor else row["Valor Actual"] >= row["Meta"]
            diff = row["Valor Actual"] - row["Meta"]
            with kpi_cols[idx % len(kpi_cols)]:
                st.metric(
                    label=row["Indicador (KPI)"],
                    value=f"{row['Valor Actual']} {row['Unidad']}",
                    delta=f"{diff:+.2f} vs Meta ({row['Meta']})",
                    delta_color="inverse" if menor_mejor else "normal"
                )
                if not cumple:
                    st.error("🚨 ALERTA: Indicador desviado de la meta")
                else:
                    st.success("✅ En Meta")

    st.markdown("---")
    st.markdown("#### 2. Ficha del Método Estandarizado (Trabajo Estándar)")
    st.session_state.estandar_df = st.data_editor(st.session_state.estandar_df, num_rows="dynamic", use_container_width=True, key="edit_std")
    if len(st.session_state.estandar_df) > 0:
        t_total = st.session_state.estandar_df["Tiempo Estándar (s)"].sum()
        st.info(f"⏱️ Tiempo Estándar Total del Ciclo: **{t_total} segundos** ({t_total/60:.2f} minutos)")

    st.markdown("---")
    st.markdown("#### 3. Auditorías de Cumplimiento y Retroalimentación al Ciclo de Mejora")
    st.caption("Nota metodológica: Si un hallazgo se clasifica como 'Limitación del propio método', el sistema lo canaliza automáticamente como propuesta de mejora.")
    st.session_state.auditorias_df = st.data_editor(st.session_state.auditorias_df, num_rows="dynamic", use_container_width=True, key="edit_aud")

    limitaciones = st.session_state.auditorias_df[st.session_state.auditorias_df["Clasificación"] == "Limitación del propio método"]
    if len(limitaciones) > 0:
        st.warning(f"🔄 **Retroalimentación Activa:** Hay **{len(limitaciones)} hallazgo(s)** clasificados como limitación del método que deben regresar al Módulo B (PDCA/Kaizen) para rediseño.")

# ==============================================================================
# CENTRO DE INFORMES PDF
# ==============================================================================
with tabs[4]:
    st.subheader("Generación de Informes Ejecutivos y Técnicos en PDF")
    st.markdown("Todos los documentos se generan dinámicamente con los datos actuales cargados en la plataforma e incluyen encabezado institucional, responsable, fecha y trazabilidad.")

    informes_meta = [
        (1, "1. Diagnóstico de Calidad", "Voz del cliente, Pareto de problemas e Ishikawa 6M."),
        (2, "2. Proyecto de Mejora", "Ficha DMAIC, estado de fases PDCA y resultados de prueba piloto."),
        (3, "3. Variabilidad y Capacidad", "Cálculo estadístico de Cp, Cpk, límites de control e interpretación."),
        (4, "4. Auditoría de Cumplimiento", "Hallazgos, clasificación (desempeño vs. método), acciones y responsables."),
        (5, "5. Implementación del Cambio", "Fases de implementación, mapa de stakeholders, comunicación y patrocinio."),
        (6, "6. Resumen Ejecutivo KPI", "Tablero de indicadores clave, desviaciones, alertas y sostenibilidad.")
    ]

    c_inf1, c_inf2 = st.columns(2)
    for idx, (num, titulo, desc) in enumerate(informes_meta):
        col_target = c_inf1 if idx % 2 == 0 else c_inf2
        with col_target:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.download_button(
                    label=f"⬇️ Descargar {titulo} (PDF)",
                    data=generar_pdf_bytes(num),
                    file_name=f"Informe_{num}_{titulo.split('.')[1].strip().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_pdf_{num}",
                    use_container_width=True
                )

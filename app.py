import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import os
from fpdf import FPDF

st.set_page_config(page_title="Generador de Escritos", layout="centered")

st.title("📄 Generador de Escritos PJUD")
st.write("Genera automáticamente tus escritos y guárdalos en tu carpeta Documentos.")

# --- Configuración de plantillas y sus campos ---
escritos_config = {
    "Solicitud simple": {
        "template": "plantillas/solicitud_simple.docx",
        "campos": {
            "nombre": "text_input",
            "ciudad": "text_input", 
            "rit": "text_input",
            "materia": "text_input",
            "tribunal": "text_input",
            "descripcion": "text_area"
        }
    },
    "Oficio": {
        "template": "plantillas/oficio.docx",
        "campos": {
            "nombre": "text_input",
            "cargo": "text_input",
            "institucion": "text_input",
            "ciudad": "text_input",
            "asunto": "text_input",
            "contenido": "text_area",
            "destinatario": "text_input"
        }
    },
    "Respuesta a observación": {
        "template": "plantillas/respuesta_observacion.docx", 
        "campos": {
            "nombre": "text_input",
            "rit": "text_input",
            "tribunal": "text_input",
            "fecha_observacion": "date_input",
            "numero_observacion": "text_input",
            "respuesta": "text_area",
            "fundamento": "text_area"
        }
    }
}

# --- Selección del tipo de escrito ---
tipo_escrito = st.selectbox("Selecciona el tipo de escrito:", list(escritos_config.keys()))

# --- Campos variables dinámicos ---
st.subheader("Datos del escrito")

campos_ingresados = {}
config_actual = escritos_config[tipo_escrito]

for campo, tipo in config_actual["campos"].items():
    label = campo.replace("_", " ").title()
    
    if tipo == "text_input":
        campos_ingresados[campo] = st.text_input(f"{label}:")
    elif tipo == "text_area":
        campos_ingresados[campo] = st.text_area(f"{label}:")
    elif tipo == "date_input":
        campos_ingresados[campo] = st.date_input(f"{label}:")
        # Convertir date a string para la plantilla
        campos_ingresados[campo] = campos_ingresados[campo].strftime("%d/%m/%Y")

# --- Generar escrito ---
if st.button("Generar escrito"):
    # Validar campos obligatorios
    campos_vacios = [campo for campo, valor in campos_ingresados.items() if not valor]
    
    if campos_vacios:
        st.error(f"Por favor completa los siguientes campos: {', '.join(campos_vacios)}")
    else:
        try:
            # --- Rellenar plantilla ---
            doc = DocxTemplate(config_actual["template"])
            context = campos_ingresados.copy()
            context["fecha"] = datetime.today().strftime("%d/%m/%Y")
            
            doc.render(context)

            # --- Guardar en Documentos ---
            documentos_path = os.path.join(os.path.expanduser("~"), "Documents")
            carpeta_base = os.path.join(documentos_path, "EscritosPJUD")
            
            # Usar RIT si está disponible, sino usar nombre
            identificador = campos_ingresados.get('rit', campos_ingresados.get('nombre', 'escrito'))
            carpeta_escrito = os.path.join(carpeta_base, identificador)
            os.makedirs(carpeta_escrito, exist_ok=True)

            # Guardar DOCX
            docx_filename = f"{tipo_escrito.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            docx_path = os.path.join(carpeta_escrito, docx_filename)
            doc.save(docx_path)

            # --- Generar PDF ---
            pdf_filename = docx_filename.replace(".docx", ".pdf")
            pdf_path = os.path.join(carpeta_escrito, pdf_filename)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Contenido del PDF
            contenido = f"ESCRITO: {tipo_escrito}\n\n"
            contenido += f"Fecha: {context['fecha']}\n\n"
            
            for campo, valor in campos_ingresados.items():
                label = campo.replace("_", " ").title()
                contenido += f"{label}: {valor}\n"
            
            pdf.multi_cell(0, 10, contenido)
            pdf.output(pdf_path)

            st.success(f"✅ Escrito generado y guardado en:\n{carpeta_escrito}")
            
            # Botones de descarga
            col1, col2 = st.columns(2)
            with col1:
                with open(docx_path, "rb") as f:
                    st.download_button("📥 Descargar DOCX", f, file_name=docx_filename)
            with col2:
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name=pdf_filename)
                    
        except Exception as e:
            st.error(f"Error al generar el escrito: {str(e)}")
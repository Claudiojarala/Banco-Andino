import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv

# =========================================================
# CONFIGURACIÓN DE INFRAESTRUCTURA (CLOUD GOVERNMENT)
# =========================================================
load_dotenv()
DB_URL = os.getenv("DATABASE_URL=postgresql://postgres.ayvcwlgaexdjlnuczycv:Facundo12-12@aws-1-us-east-2.pooler.supabase.com:6543/postgres")


def get_db_connection():
    """Establece conexión con el clúster de AWS/Supabase"""
    try:
        # El timeout es clave para que no se cuelgue en redes lentas
        return psycopg2.connect(DB_URL, connect_timeout=5)
    except Exception as e:
        print(f"DEBUG_LOG: Error de red detectado -> {e}")
        return None


# =========================================================
# UI - BANCO REGIONAL ANDINO (STREAMLIT INTERFACE)
# =========================================================
st.set_page_config(
    page_title="BRA - Scoring System",
    page_icon="🏦",
    layout="centered"
)

# Estilo visual para que parezca una intranet bancaria
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Sistema de Evaluación Crediticia")
st.info("Plataforma de Cloud Computing para aprobación inmediata de solicitudes.")

# Formulario de entrada de datos (Autoservicio por Demanda)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        dni_val = st.text_input("DNI del Solicitante", max_chars=8)
        nombre_val = st.text_input("Nombre Completo")
    with col2:
        monto_val = st.number_input("Monto del Crédito (S/.)", min_value=100.0, step=100.0)
        ingresos_val = st.number_input("Ingresos Mensuales (S/.)", min_value=0.0)

st.divider()

# =========================================================
# LÓGICA DE NEGOCIO Y PERSISTENCIA
# =========================================================
if st.button("🚀 Procesar Evaluación"):
    if not dni_val or not nombre_val or ingresos_val <= 0:
        st.error("⚠️ Datos incompletos. Por favor verifique el DNI y los ingresos.")
    else:
        # Simulación de procesamiento en Nodo Cloud
        with st.status("Evaluando perfil en Nodo AWS Ohio...", expanded=True) as status:
            st.write("Conectando con motor de scoring...")

            # Lógica de scoring (Boris/Databricks logic)
            ratio = ingresos_val / monto_val
            score = 780 if ratio > 0.4 else 450
            final_estado = "APROBADO" if score >= 500 else "RECHAZADO"

            # Persistencia en la Nube
            conn = get_db_connection()
            if conn:
                try:
                    st.write("Escribiendo en base de datos virtualizada...")
                    cur = conn.cursor()

                    # QUERY AJUSTADO A TU TABLE EDITOR
                    sql_query = """
                        INSERT INTO solicitudes (dni, monto_solicitado, score_resultado, estado) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cur.execute(sql_query, (dni_val, monto_val, score, final_estado))
                    conn.commit()

                    cur.close()
                    conn.close()
                    status.update(label="Procesamiento completado", state="complete", expanded=False)

                    # Feedback visual profesional
                    if final_estado == "APROBADO":
                        st.balloons()
                        st.success(f"### ✅ Crédito Pre-Aprobado\n**Cliente:** {nombre_val}  \n**Score:** {score}")
                    else:
                        st.error(f"### ❌ Crédito Rechazado\n**Motivo:** Score insuficiente ({score})")

                except Exception as db_err:
                    st.error(f"Error interno de persistencia: {db_err}")
            else:
                st.error("Error crítico: No se pudo alcanzar el servidor de base de datos.")

# =========================================================
# AUDITORÍA Y CONTROL (SERVICIO MEDIDO)
# =========================================================
st.sidebar.header("Administración")
if st.sidebar.checkbox("Activar Panel de Auditoría"):
    st.subheader("📊 Historial de Transacciones (Servicio Medido)")
    conn = get_db_connection()
    if conn:
        import pandas as pd

        try:
            # Mostramos los últimos 10 registros
            query_audit = "SELECT id, dni, monto_solicitado, score_resultado, estado FROM solicitudes ORDER BY id DESC LIMIT 10"
            df = pd.read_sql_query(query_audit, conn)
            st.table(df)  # st.table se ve más "formal" para reportes
        except Exception as e:
            st.warning(f"No se pudo cargar el historial: {e}")
        finally:
            conn.close()

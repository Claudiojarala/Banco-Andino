import streamlit as st
import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv
from PIL import Image 

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        return psycopg2.connect(DB_URL, connect_timeout=10, sslmode='require')
    except:
        return None

st.set_page_config(
    page_title="Banco Regional Andino - Scoring",
    layout="centered"
)

# CSS Limpio solo para la estructura base
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    
    label, h2 {
        color: #003366 !important;
        font-weight: 600 !important;
    }
    
    .stTextInput input, .stNumberInput input {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] small, [data-testid="stSidebar"] div.stMarkdown {
        color: white !important;
    }

    .stButton>button {
        width: 100%;
        background-color: #003366; 
        color: white;
        border-radius: 6px;
        height: 3.5rem;
        font-weight: 600;
        transition: background-color 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #00509e;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    header_img = Image.open("assets/banco-andino-header.jpg")
    st.image(header_img, use_container_width=True)
except:
    pass

st.write("---")

col_logo, col_title = st.columns((1, 4))

with col_logo:
    try:
        logo_img = Image.open("assets/banco-andino-logo.jpg")
        st.image(logo_img, width=100)
    except:
        pass

with col_title:
    st.markdown("<h2 style='margin-top: 20px; font-family: sans-serif;'>Evaluación de Riesgo Crediticio</h2>", unsafe_allow_html=True)

st.markdown("<p style='color: #2b2b2b; margin-left: 10px;'>Automatización de scoring con confirmación inmediata.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)
with col_f1:
    dni_val = st.text_input("DNI del Solicitante", max_chars=8)
    nombre_val = st.text_input("Nombre Completo")
with col_f2:
    monto_val = st.number_input("Monto Solicitado (S/.)", min_value=100.0, step=100.0)
    ingresos_val = st.number_input("Ingresos Mensuales (S/.)", min_value=0.0)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Evaluar Solicitud"):
    if not dni_val or not nombre_val or ingresos_val <= 0:
        # ALERTA ROJA (Caja y letra rojas forzadas por HTML)
        st.markdown('<div style="background-color: #ffdddd; color: #cc0000; padding: 15px; border-radius: 8px; border: 2px solid #cc0000; font-weight: bold; margin-bottom: 15px;">⚠️ Atención: Complete todos los campos requeridos para proceder.</div>', unsafe_allow_html=True)
    else:
        ratio = ingresos_val / monto_val if monto_val > 0 else 0
        score = 780 if ratio > 0.4 else 450
        final_estado = "APROBADO" if score >= 500 else "RECHAZADO"

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                query = "INSERT INTO solicitudes (dni, monto_solicitado, score_resultado, estado) VALUES (%s, %s, %s, %s)"
                cur.execute(query, (dni_val, monto_val, score, final_estado))
                conn.commit()
                cur.close()
                conn.close()

                if final_estado == "APROBADO":
                    # ALERTA VERDE (Éxito)
                    st.markdown(f'<div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 8px; border: 2px solid #155724; font-weight: bold; margin-bottom: 15px;">✅ Solicitud aceptada. El cliente cuenta con un score de {score}.</div>', unsafe_allow_html=True)
                else:
                    # ALERTA ROJA OSCURA (Rechazado)
                    st.markdown(f'<div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border: 2px solid #721c24; font-weight: bold; margin-bottom: 15px;">❌ Solicitud denegada. El score obtenido ({score}) no alcanza el mínimo.</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div style="background-color: #ffdddd; color: #cc0000; padding: 15px; border-radius: 8px; border: 2px solid #cc0000; font-weight: bold;">⚠️ Error de persistencia en la base de datos cloud.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background-color: #ffdddd; color: #cc0000; padding: 15px; border-radius: 8px; border: 2px solid #cc0000; font-weight: bold;">⚠️ Error de conexión: No se pudo alcanzar el servidor de base de datos AWS.</div>', unsafe_allow_html=True)

st.sidebar.markdown("### Administración")

if st.sidebar.checkbox("Visualizar Historial"):
    st.sidebar.markdown("### Historial de Transacciones")
    
    conn = get_db_connection()
    if conn:
        try:
            filtro = st.sidebar.selectbox("Filtrar por Estado:", ["Todos", "APROBADO", "RECHAZADO"])
            
            if filtro == "Todos":
                query_sql = "SELECT id, dni, monto_solicitado, score_resultado, estado FROM solicitudes ORDER BY id DESC"
                df = pd.read_sql_query(query_sql, conn)
            else:
                query_sql = "SELECT id, dni, monto_solicitado, score_resultado, estado FROM solicitudes WHERE estado = %s ORDER BY id DESC"
                df = pd.read_sql_query(query_sql, conn, params=(filtro,))
                
            st.sidebar.dataframe(df, use_container_width=True, hide_index=True)
            
            st.sidebar.markdown("#### Gestión de Datos")
            id_eliminar = st.sidebar.number_input("ID del registro a eliminar:", min_value=1, step=1)
            
            if st.sidebar.button("Eliminar Registro"):
                cur = conn.cursor()
                cur.execute("DELETE FROM solicitudes WHERE id = %s", (id_eliminar,))
                conn.commit()
                cur.close()
                st.sidebar.markdown('<div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 8px; border: 1px solid #155724; font-weight: bold; margin-bottom: 10px;">✅ Registro eliminado.</div>', unsafe_allow_html=True)
                st.rerun() 

        except Exception as e:
            st.sidebar.markdown('<div style="background-color: #ffdddd; color: #cc0000; padding: 10px; border-radius: 8px; border: 1px solid #cc0000; font-weight: bold;">⚠️ Error al leer datos.</div>', unsafe_allow_html=True)
        finally:
            conn.close()

st.sidebar.markdown("---")
st.sidebar.markdown("### Resumen de Operaciones")

conn_metrics = get_db_connection()
if conn_metrics:
    try:
        cur = conn_metrics.cursor()
        cur.execute("SELECT COUNT(*) FROM solicitudes")
        total = cur.fetchone()
        
        cur.execute("SELECT COUNT(*) FROM solicitudes WHERE estado = 'APROBADO'")
        aprobados = cur.fetchone()
        
        cur.close()
        conn_metrics.close()
        
        col_m1, col_m2 = st.sidebar.columns(2)
        col_m1.metric("Total", total)
        col_m2.metric("Aprobados", aprobados)
        
    except:
        st.sidebar.caption("No se pudieron cargar las métricas.")

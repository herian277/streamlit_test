import time
import pandas as pd
import scipy.stats as stats
import streamlit as st

st.set_page_config(page_title="Lanzar una moneda", page_icon="🪙")

# === Estado de la sesión (persiste entre reruns) ===
if "experiment_no" not in st.session_state:
    st.session_state["experiment_no"] = 0

if "df_experiment_results" not in st.session_state:
    st.session_state["df_experiment_results"] = pd.DataFrame(
        columns=["no", "iteraciones", "media"]
    )

st.header("Lanzar una moneda")
st.caption("Simula lanzamientos de una moneda (0=Cruz, 1=Cara) y observa cómo la media se acerca a 0.5.")

# Gráfico de línea (inicializa con 0.5 como referencia)
chart = st.line_chart([0.5])

# Widgets de entrada
number_of_trials = st.slider("¿Número de intentos?", min_value=1, max_value=1000, value=10, step=1)
start_button = st.button("Ejecutar")

# Barra de progreso y estatus
progress = st.progress(0)
status = st.empty()

def toss_coin(n: int, chart_obj, progress_bar=None, status_placeholder=None) -> float:
    """
    Emula n lanzamientos de una moneda justa y actualiza:
      - media después de cada intento (línea)
      - barra de progreso y texto de estado
    Devuelve la media final.
    """
    # Vector de resultados Bernoulli(0.5): 0/1
    outcomes = stats.bernoulli.rvs(p=0.5, size=n)

    ones = 0
    mean = 0.0

    # Velocidad adaptativa para la animación
    # (n pequeño: animación más visible; n grande: animación más rápida)
    if n <= 100:
        sleep_s = 0.03
    elif n <= 500:
        sleep_s = 0.01
    else:
        sleep_s = 0.005

    for i, r in enumerate(outcomes, start=1):
        if r == 1:
            ones += 1
        mean = ones / i

        # Añade el nuevo punto al gráfico
        chart_obj.add_rows([mean])

        # Actualiza progreso y estado
        if progress_bar:
            progress_bar.progress(i / n)
        if status_placeholder:
            status_placeholder.write(f"Progreso: {i}/{n} — media actual: {mean:.4f}")

        time.sleep(sleep_s)

    return mean

if start_button:
    st.write(f"Experimento con {number_of_trials} intentos en curso…")
    st.session_state["experiment_no"] += 1

    mean_final = toss_coin(
        number_of_trials,
        chart_obj=chart,
        progress_bar=progress,
        status_placeholder=status
    )

    # Guarda resultados acumulados
    new_row = pd.DataFrame(
        [[st.session_state["experiment_no"], number_of_trials, mean_final]],
        columns=["no", "iteraciones", "media"]
    )
    st.session_state["df_experiment_results"] = pd.concat(
        [st.session_state["df_experiment_results"], new_row],
        ignore_index=True
    )

    # Limpia indicadores de progreso
    progress.empty()
    status.empty()

# Tabla de resultados acumulados
st.subheader("Resultados acumulados")
st.dataframe(
    st.session_state["df_experiment_results"].style.format({"media": "{:.4f}"}),
    use_container_width=True
)

# Acciones útiles
col1, col2 = st.columns(2)
with col1:
    csv_data = st.session_state["df_experiment_results"].to_csv(index=False)
    st.download_button(
        "Descargar resultados (CSV)",
        data=csv_data,
        file_name="experimentos_moneda.csv",
        mime="text/csv"
    )
with col2:
    if st.button("Reiniciar resultados"):
        st.session_state["experiment_no"] = 0
        st.session_state["df_experiment_results"] = pd.DataFrame(
            columns=["no", "iteraciones", "media"]
        )
        st.experimental_rerun()

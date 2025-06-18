import streamlit as st
import pandas as pd
from supabase import create_client

# --- Conexión a Supabase ---
url = "https://mziizuppnzrjpijufnhk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16aWl6dXBwbnpyanBpanVmbmhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5MzY5MzIsImV4cCI6MjA2MzUxMjkzMn0.hxCA_1e_5D-Um004TKtRxwRYpSWQV0O2FSAZGRoX7F4"

supabase = create_client(url, key)

st.title("📊 Taller de Preñez Consultas y Estadísticas")

# --- Selección de año y mes ---
#anio = st.selectbox("Seleccioná el año", [2021, 2022, 2023, 2024, 2025], index=3)
#mes = st.selectbox("Seleccioná el mes", list(range(1, 13)), index=10)

# --- Botón para ejecutar consulta ---
#if st.button("Consultar datos"):
#    with st.spinner("Consultando Supabase..."):
#        res = supabase.rpc("obtener_preñez_y_precipitacion_estancias", {
#            "anio_input": anio,
#            "mes_input": mes
#        }).execute()

#        if res.data:
#            df = pd.DataFrame(res.data)
#            st.success(f"✅ {len(df)} estancias encontradas.")
#            st.dataframe(df)

            # Descargar CSV
#            csv = df.to_csv(index=False).encode("utf-8")
#            st.download_button("📥 Descargar CSV", csv, f"preñez_precipitaciones_{anio}_{mes}.csv", "text/csv")
#        else:
#            st.warning("No se encontraron datos para ese mes y año.")

# --- Botón para consultar total de vacas país ---
if st.button("Consultar total de vacas diagnosticadas en el país"):
    with st.spinner("Consultando total de vacas..."):
        res = supabase.table("lotes")\
            .select("vacias,preñez_punta,preñez_cola")\
            .execute()

        if res.data:
            df = pd.DataFrame(res.data)
            df = df.fillna(0)
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].astype(int)
            total = df["vacias"].sum() + df["preñez_punta"].sum() + df["preñez_cola"].sum()
            st.metric(label="🐄 Total de vacas diagnosticadas", value=f"{total:,}")
        else:
            st.warning("No se encontraron datos.")

# --- Botón para consultar el porcentaje de preñez nacional ---
if st.button("Consultar porcentaje de preñez nacional"):
    with st.spinner("Calculando porcentaje de preñez..."):
        res = supabase.table("lotes")\
            .select("vacias,preñez_punta,preñez_cola")\
            .execute()

        if res.data:
            df = pd.DataFrame(res.data)
            df = df.fillna(0)
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].astype(int)

            total = df["vacias"].sum() + df["preñez_punta"].sum() + df["preñez_cola"].sum()
            preñez = df["preñez_punta"].sum() + df["preñez_cola"].sum()

            if total > 0:
                porcentaje = (preñez / total) * 100
                st.metric(label="📈 Porcentaje de preñez nacional", value=f"{porcentaje:.2f}%")
            else:
                st.warning("No hay datos suficientes para calcular el porcentaje.")
        else:
            st.warning("No se encontraron datos.")
# --- Botón para consultar total de animales por departamento ---
import unicodedata

# Función para limpiar texto (tildes, mayúsculas, espacios)
def normalizar_texto(texto):
    if pd.isnull(texto):
        return "SIN_DEPARTAMENTO"
    texto_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    )
    return texto_sin_tildes.upper().strip()

# Botón de consulta
if st.button("Consultar porcentaje de preñez por departamento"):
    with st.spinner("Consultando..."):
        try:
            # Cargar datos desde Supabase
            lotes = supabase.table("lotes").select("*").execute().data
            diagnosticos = supabase.table("diagnosticos").select("id, estancia_id").execute().data
            estancias = supabase.table("estancias").select("id, departamento").execute().data

            # Convertir a DataFrames
            df_lotes = pd.DataFrame(lotes)
            df_diag = pd.DataFrame(diagnosticos)
            df_est = pd.DataFrame(estancias)

            # Unir tablas
            merged = df_lotes.merge(df_diag, left_on="diagnostico_id", right_on="id", suffixes=('', '_diag'))
            merged = merged.merge(df_est, left_on="estancia_id", right_on="id", suffixes=('', '_est'))

            # 🧹 Limpiar y normalizar el campo 'departamento'
            merged["departamento"] = merged["departamento"].apply(normalizar_texto)

            # Rellenar NaN numéricos
            merged[["vacias", "preñez_punta", "preñez_cola"]] = merged[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Agrupar por departamento
            grouped = merged.groupby("departamento").agg(
                total_vacias=("vacias", "sum"),
                total_prep=("preñez_punta", "sum"),
                total_prec=("preñez_cola", "sum")
            ).reset_index()

            # Calcular totales y porcentaje
            grouped["total"] = grouped["total_vacias"] + grouped["total_prep"] + grouped["total_prec"]
            grouped["preñez_total"] = grouped["total_prep"] + grouped["total_prec"]
            grouped["porcentaje_preñez"] = round(grouped["preñez_total"] * 100.0 / grouped["total"].replace(0, pd.NA), 2)

            # Seleccionar columnas finales
            #df_result = grouped[["departamento", "porcentaje_preñez"]].sort_values(by="porcentaje_preñez", ascending=False)
            df_result = grouped[[
                "departamento",
                "total_prep",
                "total_prec",
                "total_vacias",
                "total",
                "porcentaje_preñez"
            ]].sort_values(by="porcentaje_preñez", ascending=False)

            
            
            
            
            st.dataframe(df_result)

            # Botón para descargar CSV
            #csv = df_result.to_csv(index=False).encode("utf-8")
            df_result["porcentaje_preñez"] = df_result["porcentaje_preñez"].astype(str).str.replace(".", ",")

            csv = df_result.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "porcentaje_preñez_departamento.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
# -----------------TOTAL DE VACAS POR DEPARTAMENTO------------------------
if st.button("Consultar total de vacas por departamento"):
    with st.spinner("Consultando..."):
        try:
            # Obtener datos de Supabase
            lotes = supabase.table("lotes").select("*").execute().data
            diagnosticos = supabase.table("diagnosticos").select("id, estancia_id").execute().data
            estancias = supabase.table("estancias").select("id, departamento").execute().data

            # Convertir a DataFrames
            df_lotes = pd.DataFrame(lotes)
            df_diag = pd.DataFrame(diagnosticos)
            df_est = pd.DataFrame(estancias)

            # Unir tablas
            merged = df_lotes.merge(df_diag, left_on="diagnostico_id", right_on="id", suffixes=('', '_diag'))
            merged = merged.merge(df_est, left_on="estancia_id", right_on="id", suffixes=('', '_est'))

            # Normalizar el texto del departamento
            merged["departamento"] = merged["departamento"].apply(normalizar_texto)

            # Rellenar NaN
            merged[["vacias", "preñez_punta", "preñez_cola"]] = merged[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Agrupar por departamento y sumar total de vacas
            grouped = merged.groupby("departamento").agg(
                total_vacas=pd.NamedAgg(column="vacias", aggfunc="sum")
            )
            grouped["total_vacas"] += merged.groupby("departamento")["preñez_punta"].sum()
            grouped["total_vacas"] += merged.groupby("departamento")["preñez_cola"].sum()

            grouped = grouped.reset_index().sort_values(by="total_vacas", ascending=False)

            # Mostrar resultado
            st.dataframe(grouped)

            # Descargar CSV
            csv = grouped.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "total_vacas_por_departamento.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar discriminación vs no discriminación"):
    with st.spinner("Consultando..."):
        try:
            # Traer lotes
            lotes = supabase.table("lotes").select("categoria, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Limpiar nulos
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Clasificar discriminación
            df["tipo_discriminacion"] = df["categoria"].apply(
                lambda x: "No discriminado" if pd.isna(x) or str(x).strip().upper() == "SD" else "Discriminado"
            )

            # Calcular totales
            df["total_vacas"] = df["vacias"] + df["preñez_punta"] + df["preñez_cola"]
            df["total_preñadas"] = df["preñez_punta"] + df["preñez_cola"]

            # Agrupar y calcular porcentajes
            result = df.groupby("tipo_discriminacion").agg({
                "total_vacas": "sum",
                "total_preñadas": "sum"
            }).reset_index()

            result["porcentaje_preñez"] = round(result["total_preñadas"] * 100.0 / result["total_vacas"].replace(0, pd.NA), 2)

            st.dataframe(result)

            # Botón para descargar
            result["porcentaje_preñez"] = result["porcentaje_preñez"].astype(str).str.replace(".", ",")
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "discriminacion_vs_no.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar preñez por categoría (solo discriminados)"):
    with st.spinner("Consultando..."):
        try:
            # Traer lotes
            lotes = supabase.table("lotes").select("categoria, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Limpiar y filtrar solo discriminados
            df = df[df["categoria"].notna()]
            df["categoria"] = df["categoria"].astype(str).str.strip().str.upper()
            df = df[df["categoria"] != "SD"]

            # Reemplazar nulos en los campos numéricos
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Calcular totales
            df["total_vacas"] = df["vacias"] + df["preñez_punta"] + df["preñez_cola"]
            df["total_preñadas"] = df["preñez_punta"] + df["preñez_cola"]

            # Agrupar por categoría
            result = df.groupby("categoria").agg({
                "total_vacas": "sum",
                "total_preñadas": "sum"
            }).reset_index()

            result["porcentaje_preñez"] = round(result["total_preñadas"] * 100.0 / result["total_vacas"].replace(0, pd.NA), 2)

            # Ordenar
            result = result.sort_values(by="porcentaje_preñez", ascending=False)

            st.dataframe(result)

            # Botón para descargar CSV
            result["porcentaje_preñez"] = result["porcentaje_preñez"].astype(str).str.replace(".", ",")
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_por_categoria_discriminados.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar preñez por tipo de manejo"):
    with st.spinner("Consultando..."):
        try:
            lotes = supabase.table("lotes").select("tipo_manejo, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Limpiar tipo_manejo
            df["tipo_manejo"] = df["tipo_manejo"].fillna("Sin manejo").astype(str).str.strip()

            # Rellenar NaN numéricos
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Calcular totales
            df["total_animales"] = df["vacias"] + df["preñez_punta"] + df["preñez_cola"]
            df["total_preñadas"] = df["preñez_punta"] + df["preñez_cola"]

            # Agrupar por tipo_manejo
            result = df.groupby("tipo_manejo").agg({
                "total_animales": "sum",
                "total_preñadas": "sum"
            }).reset_index()

            result["porcentaje_preñez"] = round(result["total_preñadas"] * 100.0 / result["total_animales"].replace(0, pd.NA), 2)

            result = result.sort_values(by="total_animales", ascending=False)

            st.dataframe(result)

            # Exportar CSV
            result["porcentaje_preñez"] = result["porcentaje_preñez"].astype(str).str.replace(".", ",")
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_por_tipo_manejo.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
if st.button("Consultar tipo de manejo por categoría"):
    with st.spinner("Consultando..."):
        try:
            lotes = supabase.table("lotes").select("tipo_manejo, categoria, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Normalización
            df["tipo_manejo"] = df["tipo_manejo"].fillna("Sin manejo").astype(str).str.strip()
            df["categoria"] = df["categoria"].fillna("Sin categoría").astype(str).str.strip()

            # Rellenar NaNs
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Totales
            df["total_animales"] = df["vacias"] + df["preñez_punta"] + df["preñez_cola"]
            df["preñadas"] = df["preñez_punta"] + df["preñez_cola"]

            # Agrupar
            result = df.groupby(["tipo_manejo", "categoria"]).agg(
                total_animales=("total_animales", "sum"),
                total_preñadas=("preñadas", "sum")
            ).reset_index()

            result["porcentaje_preñez"] = round(result["total_preñadas"] * 100.0 / result["total_animales"].replace(0, pd.NA), 2)

            # Ordenar
            result = result.sort_values(by=["tipo_manejo", "total_animales"], ascending=[True, False])
            st.dataframe(result)

            # Exportar CSV
            result["porcentaje_preñez"] = result["porcentaje_preñez"].astype(str).str.replace(".", ",")
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "manejo_por_categoria.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar por condición corporal"):
    with st.spinner("Consultando..."):
        try:
            lotes = supabase.table("lotes").select("condicion_corporal, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Rellenar y convertir
            df["condicion_corporal"] = df["condicion_corporal"].fillna("Sin dato").astype(str)
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            df["total_animales"] = df["vacias"] + df["preñez_punta"] + df["preñez_cola"]
            df["preñadas"] = df["preñez_punta"] + df["preñez_cola"]

            result = df.groupby("condicion_corporal").agg(
                cantidad_lotes=("condicion_corporal", "count"),
                total_animales=("total_animales", "sum"),
                total_preñadas=("preñadas", "sum")
            ).reset_index()

            result["porcentaje_preñez"] = round(result["total_preñadas"] * 100.0 / result["total_animales"].replace(0, pd.NA), 2)
            result = result.sort_values(by="condicion_corporal")

            st.dataframe(result)

            # Exportar CSV
            result["porcentaje_preñez"] = result["porcentaje_preñez"].astype(str).str.replace(".", ",")
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_por_condicion_corporal.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar preñez por categoría y condición corporal (solo discriminados)"):
    with st.spinner("Consultando..."):
        try:
            # Obtener datos desde Supabase
            lotes = supabase.table("lotes").select("categoria, condicion_corporal, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Filtrar solo categorías discriminadas
            df = df[df["categoria"].notna() & (df["categoria"].str.upper() != "SD")]

            # Rellenar NaNs
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Agrupar por categoría y condición corporal
            grouped = df.groupby(["categoria", "condicion_corporal"]).agg(
                total_vacias=("vacias", "sum"),
                total_prep=("preñez_punta", "sum"),
                total_prec=("preñez_cola", "sum")
            ).reset_index()

            # Calcular totales y porcentaje
            grouped["total_animales"] = grouped["total_vacias"] + grouped["total_prep"] + grouped["total_prec"]
            grouped["total_preñadas"] = grouped["total_prep"] + grouped["total_prec"]
            grouped["porcentaje_preñez"] = round(grouped["total_preñadas"] * 100.0 / grouped["total_animales"].replace(0, pd.NA), 2)

            # Reemplazar punto por coma para Excel
            grouped["porcentaje_preñez"] = grouped["porcentaje_preñez"].astype(str).str.replace(".", ",")

            # Mostrar
            st.dataframe(grouped[["categoria", "condicion_corporal", "total_animales", "porcentaje_preñez"]])

            # Descargar CSV
            csv = grouped[["categoria", "condicion_corporal", "total_animales", "porcentaje_preñez"]].to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_categoria_cond_corporal.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            
if st.button("Consultar preñez por manejo y condición corporal"):
    with st.spinner("Consultando..."):
        try:
            # Consultar los datos desde Supabase
            lotes = supabase.table("lotes").select("tipo_manejo, condicion_corporal, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Rellenar valores nulos
            df["tipo_manejo"] = df["tipo_manejo"].fillna("Sin manejo")
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Agrupar por tipo de manejo y condición corporal
            grouped = df.groupby(["tipo_manejo", "condicion_corporal"]).agg(
                total_vacias=("vacias", "sum"),
                total_prep=("preñez_punta", "sum"),
                total_prec=("preñez_cola", "sum")
            ).reset_index()

            # Calcular totales y porcentaje
            grouped["total_animales"] = grouped["total_vacias"] + grouped["total_prep"] + grouped["total_prec"]
            grouped["total_preñadas"] = grouped["total_prep"] + grouped["total_prec"]
            grouped["porcentaje_preñez"] = round(grouped["total_preñadas"] * 100.0 / grouped["total_animales"].replace(0, pd.NA), 2)

            # Reemplazar punto por coma para Excel
            grouped["porcentaje_preñez"] = grouped["porcentaje_preñez"].astype(str).str.replace(".", ",")

            # Mostrar tabla
            st.dataframe(grouped[["tipo_manejo", "condicion_corporal", "total_animales", "porcentaje_preñez"]])

            # Descargar CSV
            csv = grouped[["tipo_manejo", "condicion_corporal", "total_animales", "porcentaje_preñez"]].to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_manejo_condicion.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")


if st.button("Consultar por categoría, manejo y condición corporal"):
    with st.spinner("Consultando..."):
        try:
            # Consultar los datos necesarios desde Supabase
            lotes = supabase.table("lotes").select("categoria, tipo_manejo, condicion_corporal, vacias, preñez_punta, preñez_cola").execute().data
            df = pd.DataFrame(lotes)

            # Filtrar categorías válidas
            df = df[df["categoria"].notna() & ~(df["categoria"].str.upper() == "SD")]

            # Rellenar valores nulos
            df["tipo_manejo"] = df["tipo_manejo"].fillna("Sin manejo")
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Agrupar y calcular totales
            grouped = df.groupby(["categoria", "tipo_manejo", "condicion_corporal"]).agg(
                total_vacias=("vacias", "sum"),
                total_prep=("preñez_punta", "sum"),
                total_prec=("preñez_cola", "sum")
            ).reset_index()

            # Calcular totales y porcentaje
            grouped["total_animales"] = grouped["total_vacias"] + grouped["total_prep"] + grouped["total_prec"]
            grouped["total_preñadas"] = grouped["total_prep"] + grouped["total_prec"]
            grouped["porcentaje_preñez"] = round(grouped["total_preñadas"] * 100.0 / grouped["total_animales"].replace(0, pd.NA), 2)

            # Reemplazar punto decimal por coma
            grouped["porcentaje_preñez"] = grouped["porcentaje_preñez"].astype(str).str.replace(".", ",")

            # Mostrar resultados
            st.dataframe(grouped[["categoria", "tipo_manejo", "condicion_corporal", "total_animales", "porcentaje_preñez"]])

            # Exportar CSV
            csv = grouped[["categoria", "tipo_manejo", "condicion_corporal", "total_animales", "porcentaje_preñez"]].to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_categoria_manejo_condicion.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
if st.button("Consulta por lote (grupo de manejo y porcentaje de preñez)"):
    with st.spinner("Consultando..."):
        try:
            # Obtener datos desde Supabase
            lotes = supabase.table("lotes").select(
                "id, diagnostico_id, tipo_manejo, vacias, preñez_punta, preñez_cola"
            ).execute().data

            df = pd.DataFrame(lotes)

            # Rellenar vacíos con 0 en los campos numéricos
            df[["vacias", "preñez_punta", "preñez_cola"]] = df[["vacias", "preñez_punta", "preñez_cola"]].fillna(0)

            # Calcular totales
            df["total_preñadas"] = df["preñez_punta"] + df["preñez_cola"]
            df["total"] = df["total_preñadas"] + df["vacias"]

            # Filtrar filas donde no hay animales
            df = df[df["total"] > 0]

            # Agrupar tipo de manejo en 'CON MANEJO' o 'SIN MANEJO'
            df["grupo_manejo"] = df["tipo_manejo"].apply(lambda x: "SIN MANEJO" if x == "SM" else "CON MANEJO")

            # Calcular porcentaje de preñez por lote
            df["porcentaje_preñez_lote"] = (df["total_preñadas"] * 100.0 / df["total"]).round(2)

            # Reemplazar punto por coma para Excel
            df["porcentaje_preñez_lote"] = df["porcentaje_preñez_lote"].astype(str).str.replace(".", ",")

            # Eliminar columnas innecesarias
            df_result = df.drop(columns=["id", "diagnostico_id"])

            # Ordenar y mostrar
            df_result = df_result.sort_values(by="porcentaje_preñez_lote", ascending=False)
            st.dataframe(df_result)

            # Descargar CSV
            csv = df_result.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "preñez_por_lote_filtrado.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")


if st.button("Consultar preñez y precipitación mensual (ABRIL 2024 - MARZO 2025)"):
    with st.spinner("Consultando..."):
        try:
            # Llamar a la función RPC sin parámetros
            res = supabase.rpc("preñez_y_precipitacion_mensual").execute()

            # Convertir a DataFrame
            if res.data:
                df = pd.DataFrame(res.data)
                #st.dataframe(df)
                st.dataframe(df, use_container_width=True)


                # Reemplazar punto por coma si hay columnas numéricas como porcentaje
                if "porcentaje_preñez" in df.columns:
                    df["porcentaje_preñez"] = df["porcentaje_preñez"].astype(str).str.replace(".", ",")

                # Exportar CSV
                csv = df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button("📥 Descargar CSV", csv, "preñez_y_precipitacion_mensual.csv", "text/csv")
            else:
                st.warning("No se obtuvieron resultados.")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")


if st.button("📊 Análisis de dispersión de predios con más de un lote"):
    with st.spinner("Consultando Supabase..."):
        try:
            # Consulta 1: Preñez por estancia con más de un lote
            response_predios = supabase.rpc("preñez_estancias_con_mas_de_un_lote").execute()
            data_predios = response_predios.data
            df_predios = pd.DataFrame(data_predios)

            # Consulta 2: Dispersión entre esas estancias
            response_dispersion = supabase.rpc("dispersión_preñez_estancias_completas").execute()
            data_dispersion = response_dispersion.data[0]  # Es solo una fila

            # Reemplazar punto decimal por coma para exportación CSV
            df_predios["porcentaje_preeniez"] = df_predios["porcentaje_preeniez"].astype(str).str.replace(".", ",")

            # Mostrar tabla de estancias
            st.subheader("✅ Predios con más de un lote")
            st.dataframe(df_predios)

            # Mostrar resultados estadísticos
            st.subheader("📈 Indicadores de dispersión entre estancias")
            st.markdown(f"""
            - **Promedio de preñez**: {data_dispersion['promedio_preeniez']}%
            - **Desvío estándar**: {data_dispersion['desvio_estandar']} puntos
            - **Coeficiente de variación**: {data_dispersion['coef_variacion_pct']}%
            - **Brecha P90 - P10**: {data_dispersion['brecha_p90_p10']} puntos
            """)

            # Botón para descarga CSV
            csv = df_predios.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV de estancias", csv, "predios_mas_de_un_lote.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error al consultar las funciones: {e}")
if st.button("📊 Ver dispersión por manejo"):
    with st.spinner("Consultando..."):
        try:
            # Ejecutar función SQL directamente
            result = supabase.rpc("dispersion_por_grupo_manejo").execute().data
            
            # Convertir a DataFrame
            df = pd.DataFrame(result)

            # Formatear porcentaje con coma decimal
            df["coef_variacion_pct"] = df["coef_variacion_pct"].astype(str).str.replace(".", ",")
            df["brecha_p90_p10"] = df["brecha_p90_p10"].astype(str).str.replace(".", ",")
            df["promedio_preeniez"] = df["promedio_preeniez"].astype(str).str.replace(".", ",")
            df["desvio_estandar"] = df["desvio_estandar"].astype(str).str.replace(".", ",")

            # Mostrar tabla
            st.dataframe(df)

            # CSV de descarga
            csv = df.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, "dispersion_por_manejo.csv", "text/csv")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# Botón para obtener correlación por grupo de manejo
if st.button("📈 Ver correlación tamaño vs preñez por manejo"):
    try:
        response = supabase.rpc("correlacion_preñez_por_manejo").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            st.success("✅ Correlación calculada correctamente")
            st.dataframe(df)
            

            # Opción de descarga
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Descargar CSV", csv, "correlacion_manejo.csv", "text/csv")
        else:
            st.warning("No se encontraron datos.")
    except Exception as e:
        st.error(f"Error al calcular la correlación: {e}")
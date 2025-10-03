import streamlit as st
import fitz  # PyMuPDF
import io, zipfile, os

st.set_page_config(page_title="Conversor PDF → PNG", page_icon="🖼️")

st.title("Conversor PDF → PNG 🖼️")

# Configuração do DPI
dpi = st.number_input("DPI (qualidade da imagem)", min_value=72, max_value=1200, value=300, step=24)

# Upload de múltiplos PDFs
arquivos = st.file_uploader("Envie 1 ou mais PDFs", type=["pdf"], accept_multiple_files=True)

# Botão de conversão
if st.button("Converter"):
    if not arquivos:
        st.warning("Envie pelo menos um PDF.")
    else:
        progresso = st.progress(0, text="Iniciando…")
        zip_buffer = io.BytesIO()
        erros = []

        # Criar o ZIP em memória
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for i, up in enumerate(arquivos, start=1):
                try:
                    # Abrir PDF direto da memória
                    doc = fitz.open(stream=up.read(), filetype="pdf")
                    zoom = dpi / 72.0
                    mat = fitz.Matrix(zoom, zoom)
                    base = os.path.splitext(up.name)[0]

                    for pno in range(doc.page_count):
                        page = doc.load_page(pno)
                        pix = page.get_pixmap(matrix=mat, alpha=False)
                        zf.writestr(f"{base}/pagina_{pno+1:03d}.png", pix.tobytes("png"))

                    doc.close()
                    st.write(f"✅ {up.name} convertido com sucesso.")
                except Exception as e:
                    erros.append((up.name, str(e)))
                    st.error(f"❌ Falha ao converter {up.name}: {e}")

                progresso.progress(i / len(arquivos), text=f"{i}/{len(arquivos)} convertido(s)")

        # Finalização
        zip_buffer.seek(0)
        st.success("Conversão concluída! 🎉")

        # Se houver erros, mostrar resumo
        if erros:
            st.warning("Alguns PDFs falharam:")
            for n, m in erros:
                st.text(f"- {n}: {m}")

        # Botão para baixar
        st.download_button(
            "⬇️ Baixar PNGs (ZIP)",
            data=zip_buffer,
            file_name="pdf_para_png.zip",
            mime="application/zip"
        )
        #streamlit run app_streamlit.py

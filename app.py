import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

st.set_page_config(page_title="Image Downloader", layout="wide")
st.markdown("<h1 style='color:#800000'>Image Downloader</h1>", unsafe_allow_html=True)
st.write("任意のWebページURLを入力すると、画像を一覧表示しダウンロードできます。")

url = st.text_input("WebページのURLを入力してください（http/https）:", value="")

if url:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        st.error("URLは http:// または https:// で始まる必要があります。")
    else:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            imgs = soup.find_all("img")
            img_urls = []
            for img in imgs:
                src = img.get("src")
                if not src:
                    continue
                abs_url = urljoin(url, src)
                img_urls.append(abs_url)

            if not img_urls:
                st.warning("画像が見つかりませんでした。")
            else:
                cols = st.columns(4)
                for idx, img_url in enumerate(img_urls):
                    col = cols[idx % 4]
                    try:
                        img_resp = requests.get(img_url)
                        img_resp.raise_for_status()
                        img_bytes = img_resp.content
                        ext = img_url.split('.')[-1].split('?')[0]
                        filename = f"image_{idx+1}.{ext}" if ext else f"image_{idx+1}"
                        col.image(img_bytes, use_column_width=True)
                        col.download_button(label="保存", data=img_bytes, file_name=filename, mime="image/*")
                    except Exception as e:
                        col.write(f"読み込み失敗: {e}")
        except Exception as e:
            st.error(f"ページ取得エラー: {e}")

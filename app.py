import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# -------------------------------------------
# ページ設定
# -------------------------------------------
st.set_page_config(page_title="Image Downloader", layout="wide")

# -------------------------------------------
# CSS（スマホ対応＋見た目整形＋行高さ揃え）
# -------------------------------------------
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }
        .stButton > button {
            background-color: #0075c2;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 16px;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #005a94;
        }
        h1, h2, h3 {
            color: #003366;
        }
        /* カードコンテナ */
        .image-card {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 280px;
            padding-bottom: 8px;
        }
        .image-card img {
            max-height: 180px;
            object-fit: cover;
            width: 100%;
        }
        @media screen and (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------
# タイトル・説明文
# -------------------------------------------
st.markdown("<h1>Image Downloader</h1>", unsafe_allow_html=True)
st.markdown("""
### 📸 Webページの画像を一覧表示＆保存  
- URLを入力すると、ページ内の画像を自動で取得します  
- サムネイルで画像を確認し、「保存」ボタンでダウンロードできます  
""")

# -------------------------------------------
# メイン処理：画像取得＆表示
# -------------------------------------------
url = st.text_input("画像を取得したいWebページのURLを入力してください（http/https）:")

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
                st.success(f"{len(img_urls)}件の画像を見つけました。")
                cols = st.columns(2 if st.session_state.get('mobile') else 4)

                for idx, img_url in enumerate(img_urls):
                    col = cols[idx % len(cols)]
                    with col:
                        try:
                            img_resp = requests.get(img_url)
                            img_resp.raise_for_status()
                            img_bytes = img_resp.content
                            ext = img_url.split('.')[-1].split('?')[0]
                            filename = f"image_{idx+1}.{ext}" if ext else f"image_{idx+1}"

                            with st.container():
                                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                                st.image(img_bytes, use_container_width=True)
                                st.download_button(label="保存", data=img_bytes, file_name=filename, mime="image/*")
                                st.markdown('</div>', unsafe_allow_html=True)
                        except Exception as e:
                            col.write(f"読み込み失敗: {e}")
        except Exception as e:
            st.error(f"ページ取得エラー: {e}")

# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cUxbbSDAcs9Pu_xj7WNMAt_6uwRDyLnw
"""

import streamlit as st
import pandas as pd
import openai
import re
import sys

# Konfigurasi OpenAI
openai.api_key = 'Your_API_KeY'  # Ganti dengan API key Anda

class ProductRecommendationChatbot:
    def __init__(self, catalog_path='Dataset/asus_clean.csv'):
        # Baca katalog
        self.catalog = pd.read_csv(catalog_path)

        # Preproses katalog
        self.catalog['SearchText'] = self.catalog.apply(
            lambda row: f"{row['NamaBarang']} {row['DeskripsiBarang']}".lower(),
            axis=1
        )

    def parse_query(self, query):
        query_lower = query.lower()

        if "paling bagus" in query_lower or "termahal" in query_lower:
            return "termahal", None, None

        price_patterns = [
            r'\b(di bawah|kurang dari|<=)\s*([\d.,]+)\s*(ribu|rb|juta)?',
            r'\b(di atas|lebih dari|>=)\s*([\d.,]+)\s*(ribu|rb|juta)?'
        ]

        price = None
        price_comparison = None
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                price_comparison = match.group(1)
                price_str = match.group(2)
                multiplier = match.group(3) or ''

                price = float(price_str.replace(',', ''))
                if 'ribu' in multiplier or 'rb' in multiplier:
                    price *= 1000
                elif 'juta' in multiplier:
                    price *= 1000000
                break

        spec_keywords = [
            'core i3', 'core i5', 'core i7', 'core i9',
            'ryzen 3', 'ryzen 5', 'ryzen 7', 'ryzen 9',
            'rtx', 'gtx', 'gaming', 'ssd',
            r'ram \d+gb'
        ]
        specs = re.findall('|'.join(spec_keywords), query_lower)

        return price, price_comparison, specs

    def find_products(self, query):
        price, price_comparison, specs = self.parse_query(query)

        if price == "termahal":
            return self.catalog.sort_values('Harga', ascending=False).head(5)

        filtered_catalog = self.catalog.copy()

        if price is not None:
            if price_comparison in ['di bawah', 'kurang dari', '<=']:
                filtered_catalog = filtered_catalog[filtered_catalog['Harga'] <= price]
            elif price_comparison in ['di atas', 'lebih dari', '>=']:
                filtered_catalog = filtered_catalog[filtered_catalog['Harga'] >= price]

        if specs:
            mask = filtered_catalog['SearchText'].str.contains('|'.join(specs), case=False)
            filtered_catalog = filtered_catalog[mask]

        filtered_catalog = filtered_catalog.sort_values('terjual', ascending=False)

        return filtered_catalog.head(5)

    def generate_response(self, query):
        # Cari produk yang sesuai
        matched_products = self.find_products(query)

        # Sistem prompt untuk OpenAI
        system_prompt = """
        Kamu adalah asisten AI untuk rekomendasi produk laptop di toko kami. Gunakan gaya bahasa santai khas penjual Medan, dengan interaksi akrab dan penuh semangat. Fokus membantu pelanggan menemukan laptop sesuai kebutuhan mereka, terutama memperhatikan budget dan spesifikasi laptop.

        Aturan:
        - Jika pelanggan bertanya \"laptop mana yang paling bagus\" atau \"laptop termahal\", prioritaskan untuk selalu memberikan laptop dengan harga tertinggi dari katalog yang tersedia beserta spesifikasinya. Pastikan jawaban langsung dan spesifik, sesuai format.
        - Gunakan maksimal 300 token tanpa memotong kalimat atau informasi penting.
        - Gunakan gaya bahasa ramah khas Medan. Contoh gaya bahasa:
          "Apa carik, kak?", "Laptop Asusnya kaaak?", "Cari apa nih kakak, tengok aja dulu?", "ROG, TUF-nya bang, buat gaming?", "Yang cocok buat kerja juga ada, kak."
        - Jika tidak ada produk sesuai, sampaikan dengan sopan bahwa produk tersebut tidak tersedia.
        - Bantu pelanggan dengan pertanyaan spesifik tentang kebutuhan laptop mereka.
        - Hindari membahas topik di luar katalog produk toko. Pastikan untuk memprioritaskan jawaban atas permintaan tentang harga atau spesifikasi produk tertentu sesuai data katalog.
        - Selalu gunakan format jawaban berikut untuk setiap rekomendasi:
        
          Nama barang: {NamaBarang}
          Harga: {Harga}
          Link: {Link}
          Deskripsi Singkat: {DeskripsiBarang}
        
        Contoh Interaksi:
        - Pelanggan: "Bang, laptop untuk gaming ada?"
        - Jawaban: "Laptop gaming mantap ada nih, kak! Tengok dulu yaa:
          Nama barang: ASUS ROG Strix G15
          Harga: Rp 20.000.000
          Link: www.contoh.com/asus-rog-strix-g15
          Deskripsi Singkat: Laptop gaming keren dengan Ryzen 9, RAM 16GB, SSD 1TB, dan RTX 3060. Cocok kali buat ngegame berat, kak!"
        
        - Pelanggan: "Laptop termahal ada nggak?"
        - Jawaban: "Yang paling mahal ada ini, kak, mantap kali laptopnya:
          Nama barang: MacBook Pro 16-inch M2 Max
          Harga: Rp 50.000.000
          Link: www.contoh.com/macbook-pro-16
          Deskripsi Singkat: Laptop premium dari Apple dengan chip M2 Max, RAM 32GB, SSD 2TB. Pas kali untuk kerja berat atau konten kreator profesional, kak!"
        """

        try:
            # Generate respon menggunakan OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": f"Produk yang ditemukan:\n{matched_products.to_string()}"},
                    {"role": "user", "content": "Berikan rekomendasi yang sesuai dengan query pelanggan."}
                ],
                max_tokens=400,
                temperature=0.7
            )

            # Ambil respon dari GPT
            gpt_response = response.choices[0].message.content.strip()

            return gpt_response, matched_products

        except Exception as e:
            return f"Maaf, terjadi kesalahan dalam pemrosesan: {str(e)}", pd.DataFrame()

def make_clickable(link):
    # Fungsi untuk membuat link dapat diklik
    return f'<a target="_blank" href="{link}">Beli Sekarang</a>'

# Dalam fungsi main(), ganti bagian tampilan produk dengan:
def main():
    st.set_page_config(page_title="Laptop Recommendation", page_icon="💻")
    
    # Judul Aplikasi
    st.title("🖥️ Asisten Rekomendasi Laptop")
    st.subheader("Temukan Laptop Impian Anda!")
    
    # Inisialisasi chatbot
    chatbot = ProductRecommendationChatbot()
    
    # Input pencarian
    query = st.text_input("Masukkan kebutuhan laptop Anda:", 
                          placeholder="Contoh: laptop gaming di bawah 15 juta")
    
    # Tombol cari
    if st.button("Cari Laptop") or query:
        if query:
            # Tampilkan loading
            with st.spinner('Sedang mencari rekomendasi...'):
                # Generate rekomendasi
                ai_response, products = chatbot.generate_response(query)
                
                # Tampilkan respon AI
                st.subheader("Rekomendasi AI:")
                st.write(ai_response)
                
                # Tampilkan produk
                st.subheader("Produk Rekomendasi:")
                if not products.empty:
                    # Buat salinan dataframe untuk manipulasi
                    display_df = products[['NamaBarang', 'Harga', 'Link']].copy()
                    
                    # Format harga
                    display_df['Harga'] = display_df['Harga'].apply(lambda x: f'Rp{x:,.0f}')
                    
                    # Ubah kolom Link menjadi tombol klik
                    display_df['Aksi'] = display_df['Link'].apply(make_clickable)
                    
                    # Tampilkan dataframe dengan HTML
                    st.write(display_df[['NamaBarang', 'Harga', 'Aksi']].to_html(escape=False), unsafe_allow_html=True)
                else:
                    st.warning("Tidak ada produk yang sesuai ditemukan.")

# Jalankan aplikasi
if __name__ == '__main__':
    main()

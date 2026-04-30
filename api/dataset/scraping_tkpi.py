"""
Web Scraping - Tabel Komposisi Pangan Indonesia (TKPI)
Sumber: https://www.andrafarm.com/_andra.php?_i=daftar-tkpi
Data yang diambil: Nama Bahan Makanan, Porsi, Kalori, Karbohidrat, Protein, Lemak, Serat
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# ────────────────────────────────────────────────
# Konfigurasi
# ────────────────────────────────────────────────
BASE_URL = "https://www.andrafarm.com/_andra.php"
ITEMS_PER_PAGE = 40
TOTAL_PAGES = 29          # halaman 1–29  (1.148 item ÷ 40 ≈ 29)
OUTPUT_FILE = "tkpi_data.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
    "Referer": "https://www.andrafarm.com/",
}

# ────────────────────────────────────────────────
# Fungsi bantu
# ────────────────────────────────────────────────

def build_url(page: int) -> str:
    """Buat URL untuk halaman tertentu (1-indexed)."""
    if page == 1:
        return f"{BASE_URL}?_i=daftar-tkpi"
    no1 = (page - 2) * ITEMS_PER_PAGE + 1
    no2 = (page - 1) * ITEMS_PER_PAGE
    return (
        f"{BASE_URL}?_i=daftar-tkpi"
        f"&jobs=&perhal={ITEMS_PER_PAGE}"
        f"&urut=1&asc=0000000000"
        f"&sby=&no1={no1}&no2={no2}&kk={page}"
        f"#Tabel%20TKPI"
    )


def clean_value(text: str) -> str:
    """Bersihkan whitespace dan tanda '-' yang berarti tidak ada data."""
    val = text.strip()
    if val in ("-", "", "–"):
        return ""
    return val


def parse_page(html: str) -> list[dict]:
    """
    Parse satu halaman HTML dan kembalikan list dict berisi data gizi.

    Urutan kolom (0-based, berdasarkan inspeksi HTML):
        0  → No.
        1  → Kode Baru
        2  → Nama Bahan Makanan  (ada tag <b> di dalam <a>)
        3  → Air (g)
        4  → Energi / Kalori (kal)
        5  → Protein (g)
        6  → Lemak (g)
        7  → Karbohidrat (g)
        8  → Serat (g)
        9+ → kolom lain (diabaikan)
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    # Cari semua <tr> yang punya setidaknya 9 <td>
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 9:
            continue

        # Kolom 0 harus berupa angka (nomor urut)
        no_text = clean_value(tds[0].get_text())
        if not no_text.isdigit():
            continue

        # Nama bahan makanan
        nama_tag = tds[2].find("b")
        nama = clean_value(nama_tag.get_text()) if nama_tag else clean_value(tds[2].get_text())

        # Nilai gizi
        rows.append({
            "No"           : no_text,
            "Nama_Bahan"   : nama,
            "Porsi_g"      : "100",   # semua data per 100 g BDD
            "Kalori_kal"   : clean_value(tds[4].get_text()),
            "Karbohidrat_g": clean_value(tds[7].get_text()),
            "Protein_g"    : clean_value(tds[5].get_text()),
            "Lemak_g"      : clean_value(tds[6].get_text()),
            "Serat_g"      : clean_value(tds[8].get_text()),
        })

    return rows


# ────────────────────────────────────────────────
# Main scraping loop
# ────────────────────────────────────────────────

def main():
    all_data: list[dict] = []
    session = requests.Session()
    session.headers.update(HEADERS)

    print("=" * 60)
    print("  SCRAPING TKPI - Tabel Komposisi Pangan Indonesia")
    print("  Sumber: andrafarm.com")
    print("=" * 60)

    for page in range(1, TOTAL_PAGES + 1):
        url = build_url(page)
        print(f"\n[Halaman {page:>2}/{TOTAL_PAGES}]  {url}")

        try:
            resp = session.get(url, timeout=20)
            resp.encoding = "utf-8"          # pastikan encoding benar
            if resp.status_code != 200:
                print(f"  [!] HTTP {resp.status_code} - halaman dilewati.")
                continue

            rows = parse_page(resp.text)
            print(f"  [OK] {len(rows)} baris ditemukan.")
            all_data.extend(rows)

        except requests.RequestException as exc:
            print(f"  [ERR] Error: {exc}")

        # Jeda sopan agar tidak membebani server
        time.sleep(1.2)

    # ────────────────────────────────────────────
    # Simpan ke CSV
    # ────────────────────────────────────────────
    if not all_data:
        print("\n⚠  Tidak ada data yang berhasil diambil.")
        return

    df = pd.DataFrame(all_data)

    # Konversi kolom numerik (pakai koma sebagai desimal → titik)
    numeric_cols = ["Kalori_kal", "Karbohidrat_g", "Protein_g", "Lemak_g", "Serat_g"]
    for col in numeric_cols:
        df[col] = (
            df[col]
            .str.replace(",", ".", regex=False)   # 32,2 → 32.2
            .replace("", None)
            .astype(float, errors="ignore")
        )

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print(f"  [SELESAI] Total: {len(df)} baris data")
    print(f"  Disimpan ke: {OUTPUT_FILE}")
    print("=" * 60)

    # Preview 5 baris pertama
    print("\nPreview data:")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()

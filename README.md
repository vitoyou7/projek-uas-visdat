# Visualisasi Multi-Level Struktur Pengeluaran dan Pemetaan Geospasial Inflasi Daerah di Indonesia Berbasis Web Interaktif Disertai Text Mining BRS BPS

Proyek UAS **Visualisasi Data dan Informasi** (K203407), Program Studi Komputasi Statistik, Politeknik Statistika STIS, Semester Genap TA. 2025/2026.

- **Tautan dashboard (GitHub Pages):** <https://vitoyou7.github.io/projek-uas-visdat/>
- **Repositori:** <https://github.com/vitoyou7/projek-uas-visdat/tree/main>
- **Penulis:** <Muhammad Arkan Anzuye> (NIM <222313229>, Kelas <3SD2>)

Dashboard dapat diakses publik tanpa *login* maupun instalasi, dan dapat dibuka di laptop maupun ponsel.

---

## Deskripsi

Dashboard ini memvisualisasikan Indeks Harga Konsumen (IHK, 2022=100) dan inflasi bulanan (*month-to-month*, m-to-m) Indonesia tahun 2025 pada tiga tingkat wilayah (nasional, 38 provinsi, dan 150 kabupaten/kota sampel), ditambah *text mining* terhadap 114 Berita Resmi Statistik (BRS) inflasi provinsi periode Juli–September 2026.

Dashboard memadukan **tiga dari enam topik visualisasi** pada soal UAS:

| Topik | Visualisasi | Interaksi |
| :--- | :--- | :--- |
| **Geospasial** | *Choropleth* provinsi yang berubah menjadi *choropleth* kab/kota sampel saat peta diperbesar; peta *proportional symbol* | Filter variabel (IHK/inflasi), bulan, dan kelompok pengeluaran; zoom/pan; *tooltip*; klik provinsi untuk melihat tren bulanan |
| **Hierarki** | *Treemap*, *sunburst*, *icicle*, dan dendrogram untuk struktur IHK nasional (Umum → Kelompok → Subkelompok) | Filter warna (inflasi/IHK) dan bulan pada setiap grafik; *drill-down* dengan *breadcrumb* (treemap, icicle); klik kelompok pada dendrogram untuk memperbesar subkelompoknya |
| **Teks** | *Word cloud*, topik LDA, tren topik, dan jaringan *bigram* dari 114 BRS | Filter periode (word cloud), pemilihan topik, filter bobot minimum dan kata kunci (jaringan *bigram*) |

---

## Struktur Repositori

```
.
├── index.html                                 # dashboard (HTML native, satu berkas)
├── Inflasi_IHK_2025_Final_dengan_UMUM.xlsx    # data BPS terolah (dibaca langsung oleh dashboard)
├── brs_textmining.json                        # hasil text mining (dibuat oleh preprocess_brs.py)
├── preprocess_brs.py                          # skrip pra-pemrosesan dan analisis teks BRS
└── README.md
```

---

## Sumber Data

Data utama bersumber dari **Badan Pusat Statistik (BPS)**. Seluruh data diakses pada **3 Oktober 2026** melalui [bps.go.id](https://www.bps.go.id).

| Data | Judul tabel/publikasi | Tahun data |
| :--- | :--- | :--- |
| IHK dan inflasi provinsi | Indeks Harga Konsumen 38 Provinsi di Indonesia 2025 (2022=100) | 2025 |
| IHK dan inflasi kab/kota sampel | Indeks Harga Konsumen 150 Kabupaten/Kota di Indonesia 2025 (2022=100) | 2025 |
| IHK dan inflasi nasional (kelompok dan subkelompok) | Indeks Harga Konsumen Nasional menurut Kelompok dan Subkelompok 2025 (2022=100) | 2025 |
| Teks (*text mining*) | Berita Resmi Statistik Indeks Harga Konsumen 38 Provinsi di Indonesia, Juli–September 2026 (114 dokumen) | 2026 |

**Data pendukung non-BPS** (batas wilayah digital, dimuat dashboard saat dibuka):

- Batas 38 provinsi: <https://github.com/ardian28/GeoJson-Indonesia-38-Provinsi>
- Batas kabupaten/kota (514 wilayah): <https://github.com/eppofahmi/geojson-indonesia>

> Berkas 114 PDF BRS **tidak disertakan** di repositori ini. BRS dapat diunduh dari situs BPS (lihat tabel di atas). Hasil pengolahannya tersedia pada `brs_textmining.json`.

### Isi berkas Excel

Berkas `Inflasi_IHK_2025_Final_dengan_UMUM.xlsx` memiliki tujuh lembar:

| Lembar | Isi |
| :--- | :--- |
| `Inflasi mtm Provinsi` / `IHK Provinsi` | Inflasi m-to-m dan IHK 38 provinsi menurut kelompok pengeluaran, Januari–Desember 2025 |
| `Inflasi mtm KabKot` / `IHK KabKot` | Inflasi m-to-m dan IHK 150 kab/kota sampel menurut kelompok pengeluaran |
| `inflasi nasional` / `ihk nasional` | Inflasi m-to-m dan IHK nasional: umum, kelompok, dan subkelompok |
| `Log Koreksi` | Catatan koreksi yang dilakukan pada data hasil ekstraksi (tidak dibaca dashboard) |

Kolom `Sumber` pada tiap lembar menandai asal data (publikasi PDF BPS).

---

## Pra-pemrosesan

### Data numerik

- Data diekstraksi dari publikasi PDF BPS ke berkas Excel; koreksi dicatat pada lembar `Log Koreksi`.
- Nilai inflasi "~0" pada publikasi dibaca sebagai **0,001** oleh dashboard agar tetap terbaca pada skala warna.
- Nama kab/kota dipadankan dengan GeoJSON melalui normalisasi nama (huruf kecil, tanpa tanda baca, penanda Kota/Kabupaten) dan tabel alias untuk kota IHK yang namanya berbeda dari nama administratif (misalnya Tanjung → Tabalong, Luwuk → Banggai).
- Provinsi bagi tiap kab/kota ditentukan secara spasial (*point-in-polygon* pada titik tengah wilayah), dengan cadangan provinsi terdekat untuk wilayah pesisir.

### Teks (`preprocess_brs.py`)

Tahapan pra-pemrosesan:

1. Ekstraksi teks PDF (`pypdf`) dan pengambilan tanggal terbit dari isi dokumen.
2. *Case folding*.
3. Tokenisasi (hanya huruf; token berpanjang tiga karakter atau kurang dibuang).
4. Penghapusan *stopword* Bahasa Indonesia (Sastrawi) ditambah *stopword* domain: nama bulan, angka dalam huruf, angka romawi, kata tabel/penomoran, dan nama wilayah (`HAPUS_NAMA_WILAYAH = True`).
5. *Stemming* Bahasa Indonesia (Sastrawi).
6. Penghapusan *stopword* ulang pada kata dasar hasil *stemming*.

Analisis:

- **Word cloud:** 120 kata dasar terbanyak, dihitung menurut periode (Juli, Agustus, September, dan semua). Kata dasar ditampilkan dengan bentuk asli yang paling sering muncul.
- **Topik:** LDA (`scikit-learn`) lima topik; istilah yang muncul di lebih dari 50% dokumen tidak dipakai (`max_df=0.5`, `min_df=3`).
- **Tren topik:** rerata proporsi topik dokumen pada tiap minggu terbit.
- **Jaringan *bigram*:** 150 *bigram* terbanyak (`min_df=4`) sebagai graf berbobot (`NetworkX`), tata letak *spring*, komunitas dengan *greedy modularity*.

---

## Cara Menjalankan

### 1. Membuka dashboard secara lokal

Dashboard memuat data dengan `fetch`, sehingga perlu dijalankan lewat server lokal (tidak cukup dengan klik dua kali pada `index.html`):

```bash
python -m http.server
```

Lalu buka <http://localhost:8000> di peramban. Diperlukan koneksi internet untuk memuat pustaka JavaScript (CDN) dan GeoJSON.

> Bila `index.html` dibuka langsung dari folder, dashboard menampilkan kotak untuk memilih berkas `.xlsx` dan `.json` secara manual.

### 2. Membuat ulang `brs_textmining.json`

```bash
pip install pypdf Sastrawi scikit-learn networkx
python preprocess_brs.py folder_pdf_brs
```

`folder_pdf_brs` adalah folder berisi PDF BRS (subfolder ikut dibaca). Skrip mencetak jumlah dokumen yang terbaca (`114 dokumen`) dan menghasilkan `brs_textmining.json` di folder kerja. Proses *stemming* dapat memakan beberapa menit.

---

## Teknologi

| Komponen | Pustaka |
| :--- | :--- |
| Peta, treemap, sunburst, icicle, dendrogram, grafik teks | [Plotly.js](https://plotly.com/javascript/) 2.35.2 |
| *Word cloud* | [D3.js](https://d3js.org/) 7.9.0 dan d3-cloud 1.2.7 |
| Pembacaan berkas Excel di peramban | [SheetJS](https://sheetjs.com/) 0.18.5 |
| Pra-pemrosesan teks | Python: pypdf, Sastrawi, scikit-learn, NetworkX |
| *Deployment* | GitHub Pages |

Pustaka JavaScript dimuat dari CDN (jsDelivr, dengan cadangan cdnjs). Palet warna: biru-putih-jingga (inflasi, divergen simetris terhadap nol), *viridis* (IHK), dan Okabe–Ito (kategori), semuanya ramah buta warna.

---

## Keterbatasan

- Data kab/kota hanya mencakup **150 kota sampel IHK**, bukan seluruh 514 kab/kota; peta tingkat kab/kota tidak utuh.
- Batas wilayah bersifat non-BPS dan penggabungan memakai nama wilayah, bukan kode wilayah BPS.
- Data diekstraksi dari PDF dan dapat memuat anomali; verifikasi terhadap publikasi sumber disarankan.
- Ukuran blok pada *treemap*/*sunburst*/*icicle* memakai IHK, bukan bobot pengeluaran atau andil inflasi.
- Hasil pemodelan topik dipengaruhi kualitas ekstraksi teks PDF (kata dapat terpotong) dan keseragaman templat BRS.

---

## Deklarasi Penggunaan Alat Bantu AI

Pembuatan kode (HTML/JavaScript dan skrip Python) dibantu asisten AI (Claude) sebatas alat bantu. Penulis bertanggung jawab penuh atas seluruh isi proyek dan dapat menjelaskan serta mendemonstrasikan hasilnya.

---

## Hak dan Atribusi

Data statistik: **Sumber: Badan Pusat Statistik (BPS)**. Batas wilayah: GeoJSON non-BPS dari repositori publik yang disebutkan di atas. Mohon cantumkan sumber bila data atau visualisasi digunakan kembali.

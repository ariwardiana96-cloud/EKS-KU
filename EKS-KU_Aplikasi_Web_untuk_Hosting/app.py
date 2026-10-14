import gradio as gr
import pandas as pd
import sqlite3
from datetime import datetime
from html import escape

DB_PATH = "pendaftar_eks_ku.db"
EKSKUL = ["Drumband", "Pramuka", "Rohis", "Multimedia", "Pasbrana", "Olahraga", "PMR", "KIR", "Seni"]

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pendaftar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor TEXT UNIQUE,
            waktu TEXT,
            nama TEXT,
            nis TEXT UNIQUE,
            kelas TEXT,
            jenis_kelamin TEXT,
            ekstrakurikuler TEXT,
            alasan TEXT
        )
        """)
init_db()

CSS = """
.gradio-container {max-width: 1050px !important; margin: auto !important;}
#hero {background: linear-gradient(120deg,#164A2D,#3D9B62); color:white; padding:28px; border-radius:18px; text-align:center; margin-bottom:12px;}
#hero h1 {color:white!important; margin:0; font-size:2.2em;}
#hero p {color:#E8FFEF!important; margin:8px 0 0;}
.notice {background:#EAF7EE; border-left:5px solid #247447; padding:13px 16px; border-radius:8px; color:#164A2D; margin:10px 0 16px;}
"""

def count_total():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM pendaftar").fetchone()[0]

def daftar(nama, nis, kelas, jk, ekskul, alasan):
    nama = (nama or "").strip()
    nis = (nis or "").strip()
    alasan = (alasan or "").strip()
    if not nama or not nis or not kelas or not jk or not ekskul:
        return "⚠️ Mohon lengkapi semua kolom wajib.", bukti_terbaru()
    if kelas not in ("10", "11"):
        return "⛔ Maaf, pendaftaran hanya untuk siswa kelas 10 dan 11.", bukti_terbaru()
    with sqlite3.connect(DB_PATH) as conn:
        existing = conn.execute("SELECT 1 FROM pendaftar WHERE nis=?", (nis,)).fetchone()
        if existing:
            return "ℹ️ NIS tersebut sudah terdaftar. Setiap NIS hanya boleh mendaftar satu kali.", bukti_terbaru()
        nomor = f"EKS-{datetime.now().strftime('%Y%m%d')}-{count_total()+1:03d}"
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M")
        try:
            conn.execute(
                "INSERT INTO pendaftar (nomor,waktu,nama,nis,kelas,jenis_kelamin,ekstrakurikuler,alasan) VALUES (?,?,?,?,?,?,?,?)",
                (nomor, waktu, nama, nis, kelas, jk, ekskul, alasan)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return "⚠️ Pendaftaran tidak dapat disimpan. Periksa kembali NIS.", bukti_terbaru()
    bukti = f"""### 🌿 Pendaftaran Berhasil!
**Nomor pendaftaran:** {nomor}

- **Nama:** {escape(nama)}
- **NIS:** {escape(nis)}
- **Kelas:** {kelas}
- **Jenis kelamin:** {jk}
- **Ekstrakurikuler:** {ekskul}
- **Waktu daftar:** {waktu}

✅ Simpan nomor pendaftaran ini sebagai bukti."""
    return "🎉 Pendaftaran berhasil dicatat!", bukti

def bukti_terbaru():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT nomor, waktu, nama, nis, kelas, jenis_kelamin, ekstrakurikuler FROM pendaftar ORDER BY id DESC LIMIT 1", conn)
    if df.empty:
        return "Belum ada pendaftaran."
    row = df.iloc[0]
    return f"""### 🧾 Bukti Pendaftaran Terbaru
**Nomor:** {row['nomor']}  
**Nama:** {row['nama']}  
**NIS:** {row['nis']}  
**Kelas:** {row['kelas']}  
**Jenis kelamin:** {row['jenis_kelamin']}  
**Ekstrakurikuler:** {row['ekstrakurikuler']}  
**Waktu:** {row['waktu']}"""

def rekap():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT nomor AS 'No. Pendaftaran', waktu AS 'Waktu Daftar', nama AS 'Nama', nis AS 'NIS', kelas AS 'Kelas', jenis_kelamin AS 'Jenis Kelamin', ekstrakurikuler AS 'Ekstrakurikuler', alasan AS 'Alasan' FROM pendaftar ORDER BY id DESC", conn)
    if df.empty:
        return "Belum ada data pendaftar.", pd.DataFrame(columns=["Ekstrakurikuler","Jumlah"]), None
    summary = df["Ekstrakurikuler"].value_counts().reindex(EKSKUL, fill_value=0).rename_axis("Ekstrakurikuler").reset_index(name="Jumlah")
    csv_path = "rekap_pendaftar_eks_ku.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return f"### 📊 Total pendaftar: {len(df)}", summary, csv_path

with gr.Blocks(theme=gr.themes.Soft(primary_hue="green", secondary_hue="emerald"), css=CSS, title="EKS-KU | Pendaftaran Ekstrakurikuler") as demo:
    gr.HTML("""
    <div id="hero">
      <h1>🌿 EKS-KU</h1>
      <p>Sistem Pendaftaran Ekstrakurikuler Sekolah</p>
      <p><b>Daftar Minatmu, Kembangkan Bakatmu!</b></p>
    </div>
    <div class="notice">🍃 <b>Informasi penting:</b> pendaftaran hanya dibuka untuk siswa kelas 10 dan 11. Setiap NIS hanya dapat mendaftar satu kali.</div>
    """)
    with gr.Tabs():
        with gr.Tab("🏠 Beranda"):
            gr.Markdown("## Selamat datang di EKS-KU!")
            gr.Markdown("Pilih kegiatan yang sesuai dengan minat dan bakatmu.")
            with gr.Row():
                for emoji, label in [("🎺","Drumband"),("🏕️","Pramuka"),("🕌","Rohis")]:
                    gr.Markdown(f"### {emoji} {label}")
            with gr.Row():
                for emoji, label in [("🎬","Multimedia"),("🎖️","Pasbrana"),("⚽","Olahraga")]:
                    gr.Markdown(f"### {emoji} {label}")
            with gr.Row():
                for emoji, label in [("❤️","PMR"),("🔬","KIR"),("🎨","Seni")]:
                    gr.Markdown(f"### {emoji} {label}")
            gr.Markdown("✅ Isi formulir dengan benar · 🌿 Pilih satu ekstrakurikuler · 🧾 Simpan bukti pendaftaranmu")
        with gr.Tab("📝 Pendaftaran"):
            gr.Markdown("## Formulir Pendaftaran\nKolom bertanda * wajib diisi.")
            with gr.Row():
                nama = gr.Textbox(label="Nama lengkap *", placeholder="Masukkan nama lengkap")
                nis = gr.Textbox(label="NIS *", placeholder="Masukkan nomor induk siswa")
            with gr.Row():
                kelas = gr.Dropdown(["10","11","12"], label="Kelas *", value=None, info="Hanya kelas 10 dan 11 yang diizinkan")
                jk = gr.Radio(["Laki-laki","Perempuan"], label="Jenis kelamin *")
            ekskul = gr.Dropdown(EKSKUL, label="Pilihan ekstrakurikuler *", value=None)
            alasan = gr.Textbox(label="Alasan memilih (opsional)", placeholder="Ceritakan minat atau alasanmu", lines=3)
            kirim = gr.Button("🌱 Kirim Pendaftaran", variant="primary")
            status = gr.Markdown()
            bukti_hasil = gr.Markdown()
            kirim.click(daftar, inputs=[nama,nis,kelas,jk,ekskul,alasan], outputs=[status,bukti_hasil])
        with gr.Tab("🧾 Bukti"):
            gr.Markdown("## Bukti pendaftaran terbaru")
            btn_bukti = gr.Button("Tampilkan Bukti Terbaru", variant="secondary")
            bukti_output = gr.Markdown()
            btn_bukti.click(bukti_terbaru, outputs=bukti_output)
        with gr.Tab("📊 Rekap Admin"):
            gr.Markdown("## Rekap Pendaftar\nMenu ini menampilkan data pendaftar. Untuk penggunaan nyata, batasi akses admin dengan autentikasi.")
            btn_rekap = gr.Button("Perbarui Rekap", variant="primary")
            total = gr.Markdown()
            tabel = gr.Dataframe(headers=["Ekstrakurikuler","Jumlah"], interactive=False)
            unduh = gr.File(label="Unduh file rekap CSV")
            btn_rekap.click(rekap, outputs=[total,tabel,unduh])
    gr.Markdown("---\n🌱 **EKS-KU** · Dibuat dengan Python dan Gradio · Tema hijau daun")

if __name__ == "__main__":
    demo.launch()

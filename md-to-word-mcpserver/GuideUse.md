# Panduan Penggunaan MCP Markdown to Word & PDF di n8n

Dokumen ini menjelaskan cara menghubungkan server MCP Python yang telah kita buat ke dalam alur kerja (workflow) n8n di sistem NixOS.

## Metode 1: Menggunakan n8n AI Agent (Node MCP Client Tool)

n8n mendukung koneksi ke server MCP melalui protokol **SSE (Server-Sent Events)**.

### 1. Jalankan Server MCP dalam Mode SSE
Di terminal NixOS Anda (di dalam folder `md-to-word-mcpserver`), jalankan server:
```bash
nix develop --command python server.py --sse
```
Server akan berjalan di: `http://0.0.0.0:1996/md-to-word-mcpserver/sse`

### 2. Konfigurasi di n8n
1.  Buka n8n dan buat workflow baru.
2.  Tambahkan node **AI Agent**.
3.  Hubungkan AI Agent ke node **MCP Client Tool** (di bagian Tools).
4.  Isi konfigurasi pada node **MCP Client Tool**:
    - **SSE URL**: `http://localhost:1996/md-to-word-mcpserver/sse`
    - *(Ganti `localhost` dengan IP mesin NixOS Anda jika n8n berjalan di mesin berbeda atau Docker).*
5.  Klik **Connect/Fetch Tools**. n8n akan mendeteksi tool berikut:
    - `convert_markdown_to_docx`: Mengonversi teks Markdown ke Word.
    - `convert_markdown_to_pdf`: Mengonversi teks Markdown ke PDF.
    - `convert_md_file_to_docx`: Mengonversi file `.md` ke Word.
    - `convert_md_file_to_pdf`: Mengonversi file `.md` ke PDF.

---

## Metode 2: Menggunakan Node "Execute Command"

Jika Anda ingin melakukan konversi tanpa menjalankan server MCP secara terus-menerus (stateless), Anda bisa menggunakan perintah terminal langsung dari n8n.

1.  Tambahkan node **Execute Command**.
2.  Gunakan perintah (sesuaikan path ke folder proyek):
    ```bash
    nix develop /path/ke/folder/md-to-word-mcpserver --command python -c "import pypandoc; pypandoc.convert_text('# Judul Baru', 'docx', format='md', outputfile='output.docx')"
    ```

---

## Contoh Skenario Workflow n8n

1.  **Chat Trigger**: Pengguna mengirimkan catatan dalam format Markdown via Telegram.
2.  **AI Agent**: Menerima input teks, lalu memanggil tool `convert_markdown_to_pdf`.
3.  **MCP Server**: Menghasilkan file `.pdf` di folder proyek.
4.  **Read Binary File**: n8n membaca file `.pdf` yang baru dibuat.
5.  **Telegram Send Document**: Mengirimkan file PDF kembali ke pengguna secara otomatis.

## Tips untuk NixOS & Docker
- **Docker**: Jika n8n berjalan di Docker, pastikan container n8n dapat menjangkau host (biasanya via `http://host.docker.internal:1996/...` atau IP lokal).
- **Environment**: Keunggulan menggunakan `nix develop` adalah n8n tidak perlu menginstal `pandoc` atau `texlive` secara global; semuanya sudah terisolasi di dalam lingkungan proyek.

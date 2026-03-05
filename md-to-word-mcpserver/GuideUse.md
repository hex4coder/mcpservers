# Panduan Penggunaan MCP Markdown to Word & PDF di n8n

Dokumen ini menjelaskan cara menghubungkan server MCP Python yang telah kita buat ke dalam alur kerja (workflow) n8n di sistem NixOS.

## Metode 1: Menggunakan n8n AI Agent (Node MCP Client Tool)

n8n mendukung koneksi ke server MCP melalui protokol **SSE (Server-Sent Events)**.

### 1. Jalankan Server MCP dalam Mode SSE
Di terminal NixOS Anda (di dalam folder `md-to-word-mcpserver`), jalankan server:
```bash
# Ganti <IP_SERVER> dengan IP lokal Anda jika ingin link download bisa diklik dari luar
export SERVER_IP=192.168.1.x 
nix develop --command python server.py --sse
```
Server akan berjalan di: `http://0.0.0.0:1996/md-to-word-mcpserver/sse`

### 2. Konfigurasi di n8n
1.  Buka n8n dan buat workflow baru.
2.  Tambahkan node **AI Agent**.
3.  Hubungkan AI Agent ke node **MCP Client Tool** (di bagian Tools).
4.  Isi konfigurasi pada node **MCP Client Tool**:
    - **SSE URL**: `http://localhost:1996/md-to-word-mcpserver/sse`
5.  Klik **Connect/Fetch Tools**. n8n akan mendeteksi tool konversi.

### 3. Mengunduh File Hasil Konversi
Setiap kali AI Agent memanggil tool konversi, server akan mengembalikan pesan berisi:
- Pesan Sukses.
- **Download Link**: Link URL langsung (Contoh: `http://192.168.1.x:1996/md-to-word-mcpserver/download/laporan.pdf`).

Di n8n, Anda bisa menggunakan node **HTTP Request** untuk mengunduh file dari link tersebut jika ingin mengirimkannya ke Telegram sebagai binary file.

---

## Contoh Skenario Workflow n8n

1.  **Chat Trigger**: Pengguna mengirimkan teks Markdown via Telegram.
2.  **AI Agent**: Memanggil tool `convert_markdown_to_pdf`.
3.  **MCP Server**: Mengonversi teks dan memberikan link download.
4.  **HTTP Request (n8n)**: Melakukan `GET` ke link download tersebut (Pilih Response Format: **File**).
5.  **Telegram Send Document**: Mengirimkan hasil binary file dari HTTP Request ke pengguna.

## Tips Keamanan
- File yang dihasilkan akan tersimpan di folder `outputs/` di server Anda.
- Pastikan menghapus file lama secara berkala agar storage tidak penuh.

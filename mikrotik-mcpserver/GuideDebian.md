# Panduan Penggunaan Mikrotik MCP di Debian

Dokumen ini menjelaskan cara menyiapkan lingkungan dan menjalankan Mikrotik MCP server di sistem berbasis Debian (termasuk Ubuntu, Linux Mint, dll.).

## Prasyarat

### 1. Instal Dependensi Sistem
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

### 2. Aktifkan API di Mikrotik
Pastikan service API sudah aktif di Mikrotik Anda:
```bash
/ip service enable api
```

---

## Persiapan Proyek

### 1. Buat Virtual Environment
Masuk ke folder proyek dan buat environment:
```bash
cd mikrotik-mcpserver
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instal Library Python
```bash
pip install "mcp[cli]" routeros-api python-dotenv uvicorn starlette sse-starlette
```

### 3. Konfigurasi Environment
Salin file `.env.example` menjadi `.env` dan edit isinya:
```bash
cp .env.example .env
nano .env
```
Isi sesuai dengan IP, Username, dan Password Mikrotik sekolah Anda.

---

## Menjalankan Server

### Fitur Baru untuk Mikrotik
Kini Anda dapat melakukan tes jaringan langsung:
- **Cek IP**: Gunakan `get_mikrotik_ip_addresses` untuk daftar interface.
- **Tes Koneksi**: Gunakan `ping_mikrotik` untuk melakukan ping dari router.

### Mode 1: Untuk Claude Desktop (stdio)
```bash
python3 server.py
```

### Mode 2: Untuk n8n (SSE)
```bash
python3 server.py --sse
```
Server akan berjalan di `http://0.0.0.0:1997/mikrotik-mcpserver/sse`.

---

## Konfigurasi Claude Desktop di Debian

Edit file `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mikrotik-mgmt": {
      "command": "/path/to/project/mikrotik-mcpserver/.venv/bin/python3",
      "args": [
        "/path/to/project/mikrotik-mcpserver/server.py"
      ]
    }
  }
}
```
*Pastikan `/path/to/project/` diganti dengan alamat folder yang benar di sistem Anda.*

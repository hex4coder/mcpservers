# Panduan Penggunaan MCP Markdown to Word di Debian

Dokumen ini menjelaskan cara menyiapkan lingkungan dan menjalankan server MCP di sistem berbasis Debian (termasuk Ubuntu, Linux Mint, dll.).

## Prasyarat

Berbeda dengan NixOS, di Debian Anda perlu menginstal dependensi sistem secara manual.

### 1. Instal Dependensi Sistem
Buka terminal dan jalankan perintah berikut:
```bash
sudo apt update
sudo apt install - joy python3 python3-venv python3-pip pandoc -y
```

### 2. Instal `uv` (Opsional tapi Direkomendasikan)
`uv` adalah pengelola paket yang sangat cepat. Instal dengan perintah:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

---

## Persiapan Proyek

### 1. Buat Virtual Environment
Masuk ke folder proyek dan buat environment:
```bash
cd md-to-word-mcpserver
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instal Library Python
Instal SDK MCP dan wrapper Pandoc:
```bash
pip install "mcp[cli]" pypandoc uvicorn starlette
```

---

## Menjalankan Server

### Mode 1: Untuk Claude Desktop (stdio)
Jalankan perintah ini:
```bash
python3 server.py
```

### Mode 2: Untuk n8n (SSE)
Jalankan perintah ini agar bisa diakses via network:
```bash
python3 server.py --sse
```
Server akan berjalan di `http://0.0.0.0:1996/md-to-word-mcpserver/sse`.

---

## Konfigurasi Claude Desktop di Debian

Edit file `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "md-to-word": {
      "command": "/path/to/project/md-to-word-mcpserver/.venv/bin/python3",
      "args": [
        "/path/to/project/md-to-word-mcpserver/server.py"
      ]
    }
  }
}
```
*Pastikan `/path/to/project/` diganti dengan alamat folder yang benar di sistem Anda.*

## Catatan Penting
- **Pandoc**: Pastikan perintah `pandoc --version` berfungsi setelah instalasi. `pypandoc` membutuhkan binary pandoc di sistem untuk bekerja.
- **Port**: Jika Anda menggunakan Firewall (UFW), pastikan port `1996` diizinkan: `sudo ufw allow 1996/tcp`.

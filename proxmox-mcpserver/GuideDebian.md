# Panduan Penggunaan Proxmox MCP di Debian

Dokumen ini menjelaskan cara menyiapkan lingkungan dan menjalankan Proxmox MCP server di sistem berbasis Debian (termasuk Ubuntu, Linux Mint, dll.).

## Prasyarat

### 1. Instal Dependensi Sistem
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

---

## Persiapan Proyek

### 1. Buat Virtual Environment
Masuk ke folder proyek dan buat environment:
```bash
cd proxmox-mcpserver
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instal Library Python
```bash
pip install "mcp[cli]" proxmoxer requests python-dotenv uvicorn starlette sse-starlette
```

### 3. Konfigurasi Environment
Salin file `.env.example` menjadi `.env` dan edit isinya:
```bash
cp .env.example .env
nano .env
```
Isi sesuai dengan IP host Proxmox, User, dan Password Anda.

---

## Menjalankan Server

### Fitur Baru untuk Debian/Proxmox
Kini Anda dapat mengelola sistem Debian Proxmox langsung dari MCP:
- **Cek Jaringan**: Gunakan `get_proxmox_node_networks` untuk melihat IP.
- **Tes Koneksi**: Gunakan `check_proxmox_connectivity` untuk ping ke Google atau lokal.
- **Update Repo**: Jalankan `update_proxmox_repositories` untuk `apt update`.
- **Cek Paket**: Gunakan `list_proxmox_packages` untuk melihat daftar update yang tersedia.

### Mode 1: Untuk Claude Desktop (stdio)
```bash
python3 server.py
```

### Mode 2: Untuk n8n (SSE)
```bash
python3 server.py --sse
```
Server akan berjalan di `http://0.0.0.0:1998/proxmox-mcpserver/sse`.

---

## Konfigurasi Claude Desktop di Debian

Edit file `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "proxmox-mgmt": {
      "command": "/path/to/project/proxmox-mcpserver/.venv/bin/python3",
      "args": [
        "/path/to/project/proxmox-mcpserver/server.py"
      ]
    }
  }
}
```
*Pastikan `/path/to/project/` diganti dengan alamat folder yang benar di sistem Anda.*

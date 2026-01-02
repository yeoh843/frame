# How to Install Docker Desktop on Windows

## Quick Install Steps

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Save the installer file

2. **Run the Installer**
   - Double-click the downloaded `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - Make sure "Use WSL 2 instead of Hyper-V" is checked (recommended)
   - Click "Ok" to finish

3. **Restart Your Computer**
   - Docker Desktop requires a restart to complete installation

4. **Start Docker Desktop**
   - After restart, launch Docker Desktop from Start menu
   - Accept the service agreement if prompted
   - Wait for Docker to start (whale icon in system tray)

5. **Verify Installation**
   ```powershell
   docker --version
   docker-compose --version
   ```

## After Installation

Once Docker is installed, start your database:

```powershell
cd C:\FRAME
docker compose up -d
```

Then run database migrations:

```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
```

## Troubleshooting

- **WSL 2 not found**: Install WSL 2 from Microsoft Store or run:
  ```powershell
  wsl --install
  ```
- **Virtualization disabled**: Enable virtualization in BIOS
- **Installation fails**: Check Windows updates, ensure you have admin rights













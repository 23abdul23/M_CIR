# SOLDIER SUPPORT SYSTEM

## WSL + Docker Run

### 1. Install WSL

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

Then restart Windows when prompted.

After reboot:

1. Open the new Ubuntu terminal.
2. Finish the first-run Ubuntu setup.
3. Verify WSL is running version 2:

```powershell
wsl -l -v
```

If your Ubuntu distro is not on version 2:

```powershell
wsl --set-version Ubuntu 2
```

### 2. Install Docker inside WSL (Ubuntu)

Run these commands in the Ubuntu shell:

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo service docker start
sudo docker run hello-world
```

If `hello-world` works, Docker is ready.

### 3. Start the containers

Clone this repo inside WSL or open the existing checkout from your Ubuntu shell, then go to the repo root:

```bash
cd /path/to/M_CIR
```

Create the env file:

```bash
cp .env.example .env
```

Edit `.env` and set a real `JWT_SECRET`.

Build and start:

```bash
sudo docker compose up --build -d
```

Check that all containers are up:

```bash
sudo docker compose ps
```

If something fails during boot:

```bash
sudo docker compose logs -f
```

### 4. Ingest the data

The backend container includes a database init script. Run it once after the containers are up:

```bash
sudo docker compose exec backend npm run init-db
```

This loads the JSON files from `warrior-support-system/test-data/` into MongoDB.

If you want to wipe and reload the database later:

```bash
sudo docker compose exec backend npm run reset-db
```

## URLs

After startup:

- Frontend: `http://localhost:8080`
- Node API: `http://localhost:5000`
- Python API: `http://localhost:8000`
- MongoDB: `localhost:27017`

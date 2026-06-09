# Home PC quickstart

1. Install Ubuntu 24.04 or WSL2 Ubuntu 24.04.
2. Clone this repo.
3. Copy `.env.example` to `.env` and adjust values.
4. Run:

```bash
bash scripts/00-install-prereqs.sh
bash scripts/01-install-paperclip-home.sh
bash scripts/02-start-paperclip-home.sh
python3 scripts/03-seed-basic-company.py
```

5. Check health:

```bash
curl http://localhost:3100/api/health
curl http://localhost:3100/api/companies
```

6. If you want it to survive reboot:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/paperclip-home.service ~/.config/systemd/user/paperclip-home.service
systemctl --user daemon-reload
systemctl --user enable --now paperclip-home.service
sudo loginctl enable-linger "$USER"
```

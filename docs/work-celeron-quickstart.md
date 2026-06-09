# Work Celeron quickstart

This machine is the CEO worker node.

1. Clone this repo.
2. Copy `.env.example` to `.env`.
3. Run:

```bash
bash scripts/04-install-hermes-worker.sh
```

4. Make sure SSH is reachable from home PC:

```bash
hostname -I
systemctl status ssh --no-pager
```

5. Add the home PC public key to the Celeron user's `~/.ssh/authorized_keys`.

6. From home PC, test:

```bash
ssh -i ~/.ssh/lyw_paperclip_ceo automation@WORK_IP 'hostname && pwd && command -v hermes'
```

7. From home PC, register the SSH environment:

```bash
python3 scripts/05-register-work-ceo-env.py
```

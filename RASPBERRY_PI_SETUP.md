# Raspberry Pi Setup

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

## 2. Run the server

```bash
uv run python server.py
```

Open http://localhost:8080 in your browser (or via Raspberry Pi Connect).

## 3. Autostart on boot (optional)

The `learning.service` file in this repo assumes the repo is cloned to
`/home/pi/repos/learning`. Adjust `User` and `WorkingDirectory` if different.

```bash
sudo cp learning.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable learning
sudo systemctl start learning
```

Check status:
```bash
sudo systemctl status learning
```

View logs:
```bash
journalctl -u learning -f
```

## Notes

- Default port is **8080**. Override with `PORT=9000 uv run python server.py`.
- New topic folders (e.g. `math/20260401_topic/index.html`) are picked up
  automatically on the next page refresh — no restart needed.

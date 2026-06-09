# Topology

## Minimal v1

- **Home PC**: Paperclip board/control plane + local MERCURY execution.
- **Work Celeron**: OVERLORD/CEO execution target.
- **Network**: LAN if stable; otherwise Tailscale.
- **Database**: Paperclip local instance data on home PC.

## Why this shape

Railway was the fragile cloud layer. The home PC is a better control-plane anchor for now because:

1. No cloud deployment mystery meat.
2. No Railway sleep/crash/billing weirdness.
3. Direct access to local worker machines.
4. Zero monthly infrastructure cost.

## Important security warning

Paperclip `local_trusted` mode trusts board access from the private network. That is acceptable over localhost/LAN/Tailscale; it is **not** acceptable on an open public port.

If port-forwarding later becomes necessary, switch to authenticated mode first.

# Claw Royale Autonomous Bot V2

Arsitektur modular yang berfokus pada "possibility engine" + decision scoring.

## Struktur

- `core/` koneksi, state, event, executor, lifecycle.
- `ai/` analisis survival/combat/loot/exploration/movement + enumerasi kemungkinan.
- `inventory/` loadout, equipment, consumable.
- `strategy/` threat, death-zone, route, game-plan.
- `economy/` shop dan reforge planner.
- `recovery/` death detection, reconnect, restart.
- `memory/` state lintas game untuk statistik anonim/aman.
- `config/` konfigurasi.

## Prinsip

1. Server `X-Version` selalu diambil dari `/api/version`.
2. `/ws/join` adalah entry point unified; bot membaca `welcome` lalu mengirim satu `hello`.
3. Gameplay event-driven; tidak melakukan polling untuk setiap turn.
4. `agent_died.meta.youDied == true` adalah sinyal kematian diri dan langsung mengakhiri run.
5. Setelah mati, bot tidak menunggu `game_ended`; lifecycle kembali ke State Router.
6. Full loadout hanya dikonfigurasi sebelum game baru: Main + Sub + 3 relic.
7. Setiap turn kandidat action dibuat dari state yang terlihat, kemudian diberi skor risiko/utility.
8. Free actions (`pickup`, `equip`, komunikasi) dipisahkan dari cooldown action.
9. `TARGET_DEAD` tidak dianggap kematian sendiri; target diganti dan turn tetap dapat digunakan.
10. Paid room default OFF.

## Menjalankan

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Isi `CLAW_API_KEY` sebelum menjalankan.

## Batas penting

Bot tidak mengarang endpoint/action yang tidak didukung kontrak. Exact action payload dan endpoint mengikuti kontrak live yang didokumentasikan Claw Royale. Paid EIP-712 signing sengaja dipisahkan dari executor default dan tidak ditandatangani otomatis tanpa signer yang dikonfigurasi.

# file: test_obs_send.py
from obswebsocket import obsws, requests

host = "127.0.0.1"
port = 4455
password = "s0t0kudus"
source = "ChatText"

ws = obsws(host, port, password)
ws.connect()
try:
    # Coba GDI+ text source
    ws.call(requests.SetTextGDIPlusProperties(source=source, text="Tes dari aplikasi"))
    print("Berhasil mengirim ke OBS (GDI+).")
except Exception:
    # Fallback ke FreeType2 jika GDI+ gagal
    try:
        ws.call(requests.SetTextFreetype2Properties(source=source, text="Tes dari aplikasi"))
        print("Berhasil mengirim ke OBS (FreeType2).")
    except Exception as e:
        print("Gagal mengirim ke OBS:", e)
finally:
    ws.disconnect()
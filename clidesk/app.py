# app.py
from pathlib import Path
from ui_main import MainUI
from crypto_ops import run_encrypt_and_sign


def on_run(**kwargs):
    ui.clear_log()
    try:
        rsa_pub_pem = Path(kwargs["rsa_pub_path"]).read_bytes()
        ed_priv_pem = Path(kwargs["ed_priv_path"]).read_bytes()

        res = run_encrypt_and_sign(
            input_files=kwargs["input_files"],
            rsa_pub_pem=rsa_pub_pem,
            ed_priv_pem=ed_priv_pem,
            output_dir=kwargs["out_dir"],
            bidder=kwargs["bidder"],
            call_id=kwargs["call_id"],
            key_id=kwargs["key_id"],
        )

        ui.logln("✅ Proceso completado.")
        ui.logln("Carpeta de salida: " + res["output_dir"])
        for p in res["outputs"]:
            ui.logln("  • " + p)

        ui.logln("\nRecuerda: para enviar al convocante debes POSTear:")
        ui.logln("  meta (meta.json), payload (payload.enc), wrapped_key (wrapped_key.bin), nonce (nonce.bin), tag (tag.bin)")

    except Exception as e:
        ui.logln("❌ Error: " + str(e))


if __name__ == "__main__":
    ui = MainUI(on_run)
    ui.show()

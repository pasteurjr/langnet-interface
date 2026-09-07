#!/usr/bin/env python3
"""Caixa postal SMTP LOCAL — um servidor SMTP de verdade (aiosmtpd) que recebe as mensagens e as
guarda como arquivos .eml em /tmp/biobyte_caixa_postal/. É o destino dos e-mails do BioByte em
demonstração: o sistema envia por SMTP como enviaria a um provedor; aqui dá para abrir e ler o que
saiu. Rodar:  python caixa_postal_smtp.py   (porta 1025)"""
import asyncio, os, time
from aiosmtpd.controller import Controller

PASTA = os.getenv("CAIXA_POSTAL_DIR", "/tmp/biobyte_caixa_postal")
PORT = int(os.getenv("CAIXA_POSTAL_PORT", "1025"))


class Guardar:
    async def handle_DATA(self, server, session, envelope):
        os.makedirs(PASTA, exist_ok=True)
        nome = f"{int(time.time() * 1000)}_{envelope.rcpt_tos[0].replace('@', '_at_') if envelope.rcpt_tos else 'sem_destino'}.eml"
        with open(os.path.join(PASTA, nome), "wb") as fh:
            fh.write(envelope.content)
        print(f"[caixa postal] de {envelope.mail_from} para {envelope.rcpt_tos} → {nome}", flush=True)
        return "250 Message accepted for delivery"


if __name__ == "__main__":
    ctl = Controller(Guardar(), hostname="127.0.0.1", port=PORT)
    ctl.start()
    print(f"caixa postal SMTP em 127.0.0.1:{PORT}, mensagens em {PASTA}", flush=True)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        ctl.stop()

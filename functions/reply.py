from whatsapp import *
from remote_config import get_status, update_template


def welcome(phone_number: str):
    send_interactive_message(
        phone_number,
        body="Halo, salam hangat dari SIDEBAR Assist!\n\nSaya di sini untuk membantu Anda mengaktifkan dan menonaktifkan fitur-fitur dalam aplikasi SIDEBAR Mobile sesuai kebutuhan Anda.\n\nApakah ada fitur tertentu yang Anda ingin aktifkan atau nonaktifkan saat ini?",
        buttons=[
            {
                "type": "reply",
                "reply": {
                    "id": Button.AKTIFKAN.value,
                    "title": Button.AKTIFKAN.name,
                },
            },
            {
                "type": "reply",
                "reply": {
                    "id": Button.NONAKTIFKAN.value,
                    "title": Button.NONAKTIFKAN.name,
                },
            },
            {
                "type": "reply",
                "reply": {
                    "id": Button.STATUS.value,
                    "title": Button.STATUS.name,
                },
            },
        ],
    )


def button(phone_number: str, id: str):
    if id == Button.AKTIFKAN.value:
        return send_interactive_message(
            phone_number,
            body="Silakan pilih fitur yang ingin Anda aktifkan!",
            buttons=[
                {
                    "type": "reply",
                    "reply": {
                        "id": Button.AKTIFKAN_TTE.value,
                        "title": "FITUR TTE",
                    },
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": Button.AKTIFKAN_MAINTENANCE.value,
                        "title": "FITUR MAINTENANCE",
                    },
                },
            ],
        )

    elif id == Button.NONAKTIFKAN.value:
        return send_interactive_message(
            phone_number,
            body="Silakan pilih fitur yang ingin Anda nonaktifkan!",
            buttons=[
                {
                    "type": "reply",
                    "reply": {
                        "id": Button.NONAKTIFKAN_TTE.value,
                        "title": "FITUR TTE",
                    },
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": Button.NONAKTIFKAN_MAINTENANCE.value,
                        "title": "FITUR MAINTENANCE",
                    },
                },
            ],
        )

    elif id == Button.STATUS.value:
        status = get_status()
        if status is not None:
            return send_text_message(
                phone_number,
                f'Berikut update terkini status layanan pada aplikasi SIDEBAR:\n\n*TTE*: {status["status_tte"]}\n*Maintenance*: {status["status_maintenance"]}',
            )
        else:
            return None

    else:
        _remote_config_action(phone_number, id)


def _remote_config_action(phone_number: str, id: str):
    response = None
    if id == Button.AKTIFKAN_TTE.value:
        response = update_template(Button.AKTIFKAN_TTE)
    elif id == Button.AKTIFKAN_MAINTENANCE.value:
        response = update_template(Button.AKTIFKAN_MAINTENANCE)
    elif id == Button.NONAKTIFKAN_TTE.value:
        response = update_template(Button.NONAKTIFKAN_TTE)
    elif id == Button.NONAKTIFKAN_MAINTENANCE.value:
        response = update_template(Button.NONAKTIFKAN_MAINTENANCE)

    if response is not None:
        return send_text_message(
            phone_number,
            f"Remote config berhasil diupdate. {response}",
        )
    else:
        return send_text_message(
            phone_number,
            "Remote config gagal diupdate",
        )

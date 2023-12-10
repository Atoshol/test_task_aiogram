from pathlib import Path
import polib


def _(mk, l_code):
    if l_code != "en":
        locales_folder = Path('locales/')

        po_file_path = locales_folder / f'{l_code}/LC_MESSAGES/messages.po'
        po = polib.pofile(str(po_file_path))
        # Find the translation for the specified message key
        for entry in po:
            if entry.msgid == mk:
                return entry.msgstr
    # Return the message key itself if not found
    return mk

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
from django.conf import settings
import time
import pickle
import HS_server_django.settings as HSsettings

IS_GUI = False

def delete_download():
    print("delete download files")
    download_dir = settings.MEDIA_ROOT
    last_delete_record = os.path.join(download_dir, "delete_log.log")
    if not os.path.exists(last_delete_record):
        record = {"time":int(time.time())}
        with open(last_delete_record, "wb") as f:
            pickle.dump(record, f)
    else:
        with open(last_delete_record, "rb") as f:
            record = pickle.load(f)
            hour = (int(time.time()) - record["time"])/3600
            if hour>24:
                for i in os.listdir(download_dir):
                    current_path =  os.path.join(download_dir, i)
                    if i != "delete_log.log" and os.path.isdir(current_path):
                        for j in os.listdir(current_path):
                            os.remove(os.path.join(current_path, j))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HS_server_django.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if not IS_GUI:
        execute_from_command_line(sys.argv)
    else:
        threading.Thread(target=delete_download).start()
        execute_from_command_line([__file__, "runserver", "127.0.0.1:7799","--noreload"])

if __name__ == '__main__' and not IS_GUI:
    main()
import psutil
import json
import datetime
import time
import logging


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config["apps"], list):
        raise ValueError("'apps' должен быть списком")

    return config


def get_remote_apps(remote_apps):
    found = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            for app in remote_apps:
                if app.lower() in name.lower():
                    found.append(name)
        except:
            continue

    return found


def monitor_worker(stop_flag, message_queue, config_path="config.json"):
    config = load_config(config_path)
    logging.basicConfig(
        filename=config["log_file"],
        level=logging.INFO,
        format="%(message)s"
    )
    
    while not stop_flag():
        config = load_config(config_path)
        interval = config["Check_seconds"]
        remote_apps = config["apps"]

        start_time = datetime.datetime.now()
        found = get_remote_apps(remote_apps)
        end_time = datetime.datetime.now()

        if found:
            text = "Активные удалённые приложения: " + ", ".join(found) + "[ALERT]"
        else:
            text = "Активные удалённые приложения: нет"


        log_block = (
            f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}]\n"
            f"Start time: {start_time.strftime('%H:%M:%S')}\n"
            f"End time: {end_time.strftime('%H:%M:%S')}\n"
            f"{text}\n"
            "------------------------------\n"
        )

        logging.info(log_block)
        message_queue.put(log_block)

        time.sleep(interval)
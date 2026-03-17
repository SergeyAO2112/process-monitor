from queue import Queue
import tkinter as tk
import threading
import json
from task import monitor_worker
from task import load_config
import tkinter.simpledialog as simpledialog
monitor_thread = None 
stop_thread = False 
is_running = False
message_queue = Queue()

def start_monitoring():
    global monitor_thread,stop_thread,is_running
    if is_running:
        return
    stop_thread = False
    def stop_flag():
        return stop_thread
    monitor_thread = threading.Thread(
        target=monitor_worker, 
        args= (stop_flag, message_queue), 
        daemon=True 
        )
    monitor_thread.start()
    is_running = True
    status_label.config(text = "RUNNING", bg = "green")
    message_queue.put("Мониторинг запущен.")
def stop_monitoring():
    global stop_thread,is_running
    if not is_running:
        return
    stop_thread = True
    is_running = False
    status_label.config(text = "STOPPED", bg = "red")
    log_text.insert("end", "мониторинг остановлен\n")

def check_queue():
    while not message_queue.empty():
        msg = message_queue.get()
        log_text.insert("end", msg + "\n")
        log_text.see("end")
    root.after(100,check_queue)

def add_app():
    new_app = simpledialog.askstring("Добавить приложение","Введите название процесса:")
    if not new_app:
        return
    apps_listbox.insert("end",new_app)

    config = load_config("config.json")
    config["apps"].append(new_app)

    with open('config.json','w',encoding='utf-8') as f:
        json.dump(config,f,indent=4,ensure_ascii=False)
def delete_app():
    selected = apps_listbox.curselection()
    if not selected:
        return 
    index = selected[0]
    app_name = apps_listbox.get(index)

    apps_listbox.delete(index)

    config = load_config("config.json")
    if app_name in config["apps"]:
        config['apps'].remove(app_name)
    with open('config.json','w',encoding='utf-8') as f:
        json.dump(config,f,indent=4,ensure_ascii=False)
root = tk.Tk()
root.title("Remote monitor")
root.geometry('900x600') 
top_frame = tk.Frame(root, height=50)
top_frame.pack(fill='x')

start_button = tk.Button(top_frame, text = 'start', width=12, command= start_monitoring)
start_button.pack(side = "left", padx=5,pady = 10) 
stop_button = tk.Button(top_frame, text = 'stop', width=12, command= stop_monitoring )
stop_button.pack(side = "left", padx=5,pady = 10) 

status_label = tk.Label(top_frame, text = "STOPPED", bg = "red", fg= "white", width = 10 )
status_label.pack(side="right", padx = 5, pady = 10)
 
midle_frame = tk.Frame(root)
midle_frame.pack(fill = 'both', expand = True)


apps_frame = tk.Frame(midle_frame, width = 250)
apps_frame.pack(side='left',fill='y',padx =10, pady = 10 )

apps_label = tk.Label(apps_frame, text = 'Отслеживаемые приложения')
apps_label.pack(anchor='w')

apps_listbox = tk.Listbox(apps_frame, height= 15)
apps_listbox.pack(fill='both',expand=True,pady = 5)
config = load_config('config.json')
apps = config["apps"]
for app in apps:
    apps_listbox.insert("end", app)

apps_buttons = tk.Frame(apps_frame)
apps_buttons.pack(fill='x')

add_button = tk.Button(apps_buttons,text = 'Add', width = 10)
add_button.pack(side='left',padx=5)
add_button.config(command=add_app)
delete_button = tk.Button(apps_buttons,text = 'Delete', width = 10)
delete_button.pack(side='left',padx=5)
delete_button.config(command = delete_app)

log_frame = tk.Frame(midle_frame,width=250)
log_frame.pack(side='right', fill='both', expand=True)

log_text = tk.Text(log_frame, wrap='word')
log_text.pack(side='left',fill = 'both', expand = True)


scrolbar = tk.Scrollbar(log_frame, command=log_text.yview) 
scrolbar.pack(side = 'right', fill = 'y') 
log_text.config(yscrollcommand=scrolbar.set) 

def copy_log():
    root.clipboard_clear()
    root.clipboard_append(log_text.get("1.0","end"))
    copy_button.config(text = 'Copy')
    root.after(1000, lambda: copy_button.config(text="Copy"))
copy_button = tk.Button(root,text = "Copy",width = 12, command=copy_log)
copy_button.pack(side='right',padx = 10,pady=5)

check_queue()
root.mainloop()
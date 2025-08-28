from asyncio import run as a_run

from os import listdir, remove, mkdir, getenv
from os.path import exists
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64 as encode_attachment
from colorama import Fore as F, Style as S, init as color_init, just_fix_windows_console
from pyfiglet import print_figlet
from segno import make_qr
from time import sleep

from dotenv import load_dotenv
from sys import argv

from scripts import j2, exelink
from data import config as cfg, txt

from main import send_message_ as main_send_message
from main import edit_text_ as main_edit_text

from stores import send_message_ as lpsb_send_message
from stores import send_cheque_ as lpsb_send_cheque
from stores import download_photo_ as lpsb_download_photo
from stores import edit_text_ as lpsb_edit_text

from admins import send_message_ as lpaa_send_message
from admins import download_photo_ as lpaa_download_photo
from admins import edit_text_ as lpaa_edit_text

# from server import send_message_ as srv_send_message

color_init(autoreset=True)
just_fix_windows_console()
load_dotenv()
fixed_files = list()

alerts = set()


async def solve_task(filename: str):
    js = j2.fromfile(cfg.PATHS.EXE + filename)
    task = js["task"].split()
    subtasks_counter = 0

    task_name = filename[:filename.find('.')]
    process_id = hash(task_name)

    path = cfg.PATHS.EXE + filename
    sub_path = cfg.PATHS.EXE + task_name

    sub_request = js["sub"]

    print("\nTask", F.LIGHTBLUE_EX + task_name, end=':\n')
    print(F.GREEN + "DATA:       ", F.LIGHTBLACK_EX + j2.to_(js, string_mode=True))

    print(F.YELLOW + "PATH:       ", F.LIGHTBLACK_EX + path)
    print(F.YELLOW + "SUB_REQUEST:", F.LIGHTBLACK_EX + ("YES" if sub_request > 0 else S.DIM + "NO"))

    subtask_data_array = list()
    subtask_data_files = list()
    can_proceed = True
    if sub_request:
        for subt in range(sub_request):
            try:
                with open(sub_path + f'_{subt}.sub', encoding='utf8') as subt_file:
                    subtask_data_array.append(subt_file.read())
                    subtask_data_files.append(sub_path + f'_{subt}.sub')
                    subtasks_counter += 1
                    print(F.CYAN + S.DIM + f"[subtask {subtasks_counter} found]")
            except FileNotFoundError:
                exelink.warn(
                    text=txt.EXE.ALERTS.SUBTASK_MISSING.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + f"[subtask file {subtasks_counter} was not found]",
                      F.RED + S.DIM + "[skipping]", sep='\n')
                can_proceed = False
                break

    if can_proceed:
        if task[0] == "message":
            try:
                bot = task[1].upper()
                participant = int(task[2])
                reset_keyboard = bool(int(task[3]))
                # text = subtask_data_array[0]
                # file_mode = subtask_data_array[1]
                # file_path = subtask_data_array[2]
                if bot not in ("MAIN", "LPSB", "LPAA", "SRV"):
                    raise ValueError
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                sleep(1/30)
                if bot == "MAIN":
                    if len(subtask_data_array) > 1:
                        await main_send_message(
                            participant,
                            subtask_data_array[0],
                            subtask_data_array[2],
                            subtask_data_array[1],
                            reset_keyboard=reset_keyboard
                        )
                    else:
                        await main_send_message(
                            participant,
                            subtask_data_array[0],
                            reset_keyboard=reset_keyboard
                        )
                elif bot == "LPAA":
                    if len(subtask_data_array) > 1:
                        await lpaa_send_message(
                            participant,
                            subtask_data_array[0],
                            subtask_data_array[2],
                            subtask_data_array[1],
                            reset_keyboard=reset_keyboard
                        )
                    else:
                        await lpaa_send_message(
                            participant,
                            subtask_data_array[0],
                            reset_keyboard=reset_keyboard
                        )
                elif bot == "LPSB":
                    if len(subtask_data_array) > 1:
                        await lpsb_send_message(
                            participant,
                            subtask_data_array[0],
                            subtask_data_array[2],
                            subtask_data_array[1],
                            reset_keyboard=reset_keyboard
                        )
                    else:
                        await lpsb_send_message(
                            participant,
                            subtask_data_array[0],
                            reset_keyboard=reset_keyboard
                        )
                '''
                elif bot == "SRV":
                    if len(subtask_data_array) > 1:
                        await srv_send_message(
                            participant,
                            subtask_data_array[0],
                            subtask_data_array[2],
                            subtask_data_array[1],
                            reset_keyboard=reset_keyboard
                        )
                    else:
                        await srv_send_message(
                            participant,
                            subtask_data_array[0],
                            reset_keyboard=reset_keyboard
                        )
                '''

        elif task[0] == "cheque":
            try:
                to_ = task[1]
                cheque_id_ = task[2]
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                await lpsb_send_cheque(to_, cheque_id_)

        elif task[0] == "email":
            try:
                participant = task[1]
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                with open(subtask_data_array[0], encoding='utf8') as html:
                    text_input = html.read()
                if len(subtask_data_array) > 2:
                    for key, value in j2.from_(subtask_data_array[2]).items():
                        text_input = text_input.replace(f'{{:{key}:}}', str(value))
                message = MIMEMultipart()
                message["Subject"] = subtask_data_array[1]
                message["From"] = "LyPay Electronics"
                message["To"] = participant
                message.attach(MIMEText(text_input, 'html'))

                for i in range(3, len(subtask_data_array)):  # files
                    attachment_path = subtask_data_array[i].replace('/', '\\')
                    attachment_name = attachment_path[attachment_path.rfind('\\') + 1:]
                    file = MIMEBase('application', 'octet-stream')
                    with open(attachment_path, 'rb') as raw:
                        file.set_payload(raw.read())
                    encode_attachment(file)
                    file.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
                    message.attach(file)

                with SMTP(getenv("LYPAY_EMAIL_HOST"), int(getenv("LYPAY_EMAIL_PORT"))) as email:
                    email.starttls()
                    email.login(getenv("LYPAY_EMAIL_MAIL"), getenv("LYPAY_EMAIL_PASSWORD"))
                    email.send_message(message)

        elif task[0] == "qr":
            try:
                value = int(task[1])
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                make_qr(value).save(cfg.PATHS.QR + task[1] + ".png", scale=5, border=5)

        elif task[0] == "photo":
            try:
                bot = task[1].upper()
                file_id = task[2]
                if bot not in ["LPSB", "LPAA"]:
                    raise ValueError
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                if bot == "LPSB":
                    await lpsb_download_photo(file_id, subtask_data_array[0])
                elif bot == "LPAA":
                    await lpaa_download_photo(file_id, subtask_data_array[0])

        elif task[0] == "sublist":  # task[1] - add | remove;  task[2] - name;  task[3] - key;  subtask[0] - data
            try:
                mode = task[1]
                name = task[2]
                key = task[3]
                if mode not in ('add', 'remove'):
                    raise ValueError
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                try:
                    js = await j2.fromfile_async(cfg.PATHS.LISTS + name + '.json')
                except FileNotFoundError:
                    js = dict()

                if mode == 'add':
                    js[key] = subtask_data_array[0]
                elif key in js.keys():  # mode == 'remove'
                    js.pop(key)

                sublist_path = name.replace('\\', '/')
                directory_check = sublist_path.split('/')
                for i in range(1, len(directory_check)):
                    if not exists(cfg.PATHS.LISTS + '/'.join(directory_check[:i])):
                        mkdir(cfg.PATHS.LISTS + '/'.join(directory_check[:i]))
                with open(cfg.PATHS.LISTS + sublist_path + '.json', 'w', encoding='utf8') as f:
                    f.write(j2.to_(js))

        elif task[0] == "ccc_edit":
            try:
                bot = task[1].upper()
                if bot not in ("MAIN", "LPSB", "LPAA"):
                    raise ValueError
            except:
                exelink.warn(
                    text=txt.EXE.ALERTS.WRONG_VALUE.format(
                        pid=process_id,
                        task=task_name,
                        data=js,
                        subtask_c=subtasks_counter
                    ),
                    userID=0
                )
                exelink.send_snapshot(
                    *subtask_data_files,
                    pid=process_id,
                    userID=0
                )
                print(F.RED + "WRONG VALUES/TYPES")
            else:
                if bot == "MAIN":
                    await main_edit_text(int(task[2]), int(task[3]), subtask_data_array[0], ccc_refresh_keyboard=True)
                elif bot == "LPAA":
                    await lpaa_edit_text(int(task[2]), int(task[3]), subtask_data_array[0])
                else:
                    await lpsb_edit_text(int(task[2]), int(task[3]), subtask_data_array[0])

        else:
            exelink.warn(
                text=txt.EXE.ALERTS.UNKNOWN_TASK.format(
                    pid=process_id,
                    task=task_name,
                    data=js,
                    subtask_c=subtasks_counter
                ),
                userID=0
            )
            exelink.send_snapshot(
                *subtask_data_files,
                pid=process_id,
                userID=0
            )
            print(F.RED + "UNKNOWN TASK")

    remove(path)
    for subtask_file in subtask_data_files:
        remove(subtask_file)
    print(F.LIGHTBLACK_EX + S.DIM + "[removed]")


def update_fixed():
    global fixed_files
    fixed_files = {file for file in listdir(cfg.PATHS.EXE) if file.find('json') == -1}


print_figlet("EXECUTOR 4")
print("Sync Ascent Edition")
print_figlet(' '.join(list(cfg.VERSION)))
print(cfg.NAME)
update_fixed()


async def main():
    num = 1
    while True:
        settings = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
        if not (settings["launch"] and argv[1] == settings["launch_stamp"]):
            break

        update_fixed()
        while j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["launch"] and len(listdir(cfg.PATHS.EXE)) == len(fixed_files):
            sleep(.05)

        print(F.GREEN + S.NORMAL + "\n\nLoop run №", num, sep='')
        num += 1
        update_fixed()

        print(F.YELLOW + S.DIM + "Contents: ")
        contents = sorted([name for name in listdir(cfg.PATHS.EXE) if name not in fixed_files and name.count('_') < 2])
        print('-', '\n- '.join(contents))
        for name in contents:
            await solve_task(name)


if __name__ == "__main__":
    a_run(main())

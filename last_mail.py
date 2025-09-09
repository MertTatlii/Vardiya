import os
import glob
import win32com.client as win32
from datetime import datetime
import time

# === KLASÖRLER ===
VARDIYA_KLASORU = r""
LOG_FILE = r""

# === LOG OKUMA ===
def read_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

# === LOG YAZMA ===
def write_log(filename):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(filename + "\n")

# === EN GÜNCEL DOSYAYI BUL ===
def get_latest_vardiya_file():
    pattern = os.path.join(VARDIYA_KLASORU, "*_Vardiya_Listesi.xlsx")
    files = glob.glob(pattern)

    files_with_dates = []
    for file in files:
        basename = os.path.basename(file)
        try:
            date_str = basename.split("_")[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            files_with_dates.append((date_obj, file))
        except ValueError:
            continue

    if not files_with_dates:
        return None

    latest_file = sorted(files_with_dates, key=lambda x: x[0], reverse=True)[0][1]
    return latest_file

# === E-POSTA GÖNDER ===
def send_email():
    try:
        output_file = get_latest_vardiya_file()
        if not output_file:
            print("Gönderilecek uygun dosya bulunamadı.")
            return

        log = read_log()
        filename = os.path.basename(output_file)
        if filename in log:
            print(f"{filename} daha önce gönderilmiş. Atlanıyor.")
            return

        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = ""
        mail.CC = ""
        mail.Subject = f"Vardiya Listesi - {datetime.now().strftime('%Y-%m-%d')}"
        mail.Body = "Merhaba,\n\nSon haftanın vardiya listesi ekte yer almaktadır.\n\nİyi çalışmalar."
        mail.Attachments.Add(os.path.abspath(output_file))
        mail.Send()

        print(f"{datetime.now()} - E-posta gönderildi: {filename}")
        write_log(filename)

    except Exception as e:
        print(f"E-posta gönderilirken hata oluştu: {e}")

# === ANA DÖNGÜ (Her dakika kontrol eder, sadece Cuma 18:00'de çalışır) ===
while True:
    try:
        now = datetime.now()
        if now.weekday() == 4 and now.hour == 18 and now.minute == 0:  # Cuma 18:00
            print(f"{now} - Görev başlatılıyor...")
            send_email()
            time.sleep(60)  # 1 dakika bekle, 18:01'e geçsin
        else:
            time.sleep(20)  # Sık kontrol için her 20 saniyede bir bak
    except Exception as e:
        print(f"Ana döngü hatası: {e}")
        time.sleep(60)

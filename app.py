import time
import pandas as pd
from multiprocessing import Process, Manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================== CONFIG ==================
BASE_URL = "https://pixabay.com/es/music/search/sleep/"
MAX_CANCIONES = 1000
MAX_PAGINAS = 100
SLEEP_TIME = 2

# ================== FUNCION SCRAPEO ==================
def scrape_canciones(song_urls, shared_list, proceso_id):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 25)

    for i, url in enumerate(song_urls, start=1):
        print(f"🧵 Proceso {proceso_id} | Canción {i}/{len(song_urls)}")
        driver.get(url)
        time.sleep(3)

        try:
            # -------- GENERO (CORRECTO) --------
            try:
                genero = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a.theme--QD6nj")
                    )
                ).text
            except:
                genero = None

            # -------- TITULO --------
            titulo = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "title--VRujt")
                )
            ).text

            # -------- AUTOR --------
            autor = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "userName--tkwoR")
                )
            ).text

            # -------- PLAY --------
            play_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class,'playIcon')]")
                )
            )
            driver.execute_script("arguments[0].click();", play_button)

            # -------- AUDIO --------
            audio = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "audio"))
            )
            mp3_url = audio.get_attribute("src")

            if not mp3_url:
                print("⚠️ MP3 no encontrado")
                continue

            # -------- IMAGEN --------
            try:
                image_url = driver.find_element(
                    By.XPATH,
                    "//img[contains(@src,'cdn.pixabay.com')]"
                ).get_attribute("src")
            except:
                image_url = None

            shared_list.append({
                "Genero": genero,
                "Titulo": titulo,
                "Autor": autor,
                "MP3_URL": mp3_url,
                "Imagen_URL": image_url,
                "Pagina_Origen": url
            })

            print(f"✅ {titulo} | Género: {genero}")

        except Exception as e:
            print(f"❌ Proceso {proceso_id} error en {url}: {e}")

        time.sleep(SLEEP_TIME)

    driver.quit()

# ================== MAIN ==================
if __name__ == "__main__":

    # -------- DRIVER PARA LINKS --------
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # -------- OBTENER LINKS --------
    song_urls = []
    pagina = 1

    while len(song_urls) < MAX_CANCIONES and pagina <= MAX_PAGINAS:
        url = f"{BASE_URL}?pagi={pagina}"
        print(f"\n📄 Leyendo página {pagina}")
        driver.get(url)
        time.sleep(3)

        nuevos_links = driver.execute_script("""
            return [...new Set(
                Array.from(document.querySelectorAll("a.title--7N7Nr"))
                    .map(a => a.href)
            )];
        """)

        for link in nuevos_links:
            if link not in song_urls:
                song_urls.append(link)
            if len(song_urls) >= MAX_CANCIONES:
                break

        pagina += 1
        time.sleep(SLEEP_TIME)

    driver.quit()

    print(f"\n🎧 TOTAL LINKS: {len(song_urls)}")

    # -------- MULTIPROCESO --------
    mitad = len(song_urls) // 2
    urls_1 = song_urls[:mitad]
    urls_2 = song_urls[mitad:]

    manager = Manager()
    tracks = manager.list()

    p1 = Process(target=scrape_canciones, args=(urls_1, tracks, 1))
    p2 = Process(target=scrape_canciones, args=(urls_2, tracks, 2))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # -------- EXPORTAR --------
    df = pd.DataFrame(list(tracks))
    df.to_excel("pixabay_sleep_music.xlsx", index=False)

    print("\n📁 Excel generado correctamente")

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================== CONFIG ==================
BASE_URL = "https://pixabay.com/es/music/search/sleep/"
MAX_CANCIONES = 20      # 🔢 limite total
MAX_PAGINAS = 20         # 📄 limite de paginas
SLEEP_TIME = 1           # ⏳ anti Cloudflare

# ================== SETUP ==================
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 25)

# ================== OBTENER LINKS CON PAGINACION ==================
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

    print(f"🎵 Encontradas {len(nuevos_links)} canciones")

    for link in nuevos_links:
        if link not in song_urls:
            song_urls.append(link)
        if len(song_urls) >= MAX_CANCIONES:
            break

    pagina += 1
    time.sleep(SLEEP_TIME)

print(f"\n🎧 TOTAL LINKS RECOLECTADOS: {len(song_urls)}")

# ================== EXTRAER DATOS DE CADA CANCION ==================
tracks = []

for i, url in enumerate(song_urls, start=1):
    print(f"\n➡️ Procesando canción {i}/{len(song_urls)}")
    driver.get(url)
    time.sleep(3)

    try:
        # -------- GENERO (DESCRIPCION REAL) --------
        try:
            genero = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "text--lk7nQ")
                )
            ).text
        except:
            genero = None

        # -------- TITULO REAL --------
        titulo = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "title--VRujt")
            )
        ).text

        # -------- AUTOR REAL --------
        autor = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "userName--tkwoR")
            )
        ).text

        # -------- CLICK PLAY --------
        play_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class,'playIcon')]")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            play_button
        )
        time.sleep(1)
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

        tracks.append({
            "Genero": genero,
            "Titulo": titulo,
            "Autor": autor,
            "MP3_URL": mp3_url,
            "Imagen_URL": image_url,
            "Pagina_Origen": url
        })

        print(f"✅ {titulo} | {autor}")
        time.sleep(SLEEP_TIME)

    except Exception as e:
        print(f"❌ Error en {url}: {e}")

driver.quit()

# ================== EXPORTAR A EXCEL ==================
df = pd.DataFrame(tracks)
df.to_excel("pixabay_sleep_music.xlsx", index=False)

print("\n📁 Excel generado correctamente: pixabay_sleep_music.xlsx")

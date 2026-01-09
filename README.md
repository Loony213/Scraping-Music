# 🎧 Pixabay Music Scraper

Scraper en **Python + Selenium** para extraer música **libre de regalías** desde Pixabay, obteniendo información completa de cada canción y exportándola a **Excel**.

---

## ⬇️ Descargar el Proyecto

### Descargar ZIP
👉 **Code → Download ZIP**

---

## 📦 Instalación

```bash
pip install -r requirements.txt
```

Asegúrate de tener **Google Chrome** instalado.

---

## ▶️ Uso

```bash
python app.py
```

El scraper:
- Navega automáticamente por varias páginas
- Reproduce cada canción para obtener la URL real del audio
- Extrae:
  - Género (descripción de la canción)
  - Título
  - Autor
  - URL del audio
- Guarda todo en un archivo **Excel (.xlsx)**

---

## 📊 Salida

El archivo generado:
```
pixabay_music.xlsx
```

Columnas:
- Genero
- Titulo
- Autor
- AudioURL

---

## ⚙️ Tecnologías

- Python 3.10+
- Selenium
- Pandas
- WebDriver Manager
- Google Chrome

---

## ⚠️ Notas

- Se utiliza `sleep(1)` entre procesos para evitar bloqueos de Cloudflare
- El número de canciones a extraer es configurable
- Totalmente compatible con Windows

---

## 📄 Licencia

Uso educativo y personal.
Los audios pertenecen a Pixabay bajo su licencia correspondiente.
import requests
from bs4 import BeautifulSoup
import mysql.connector
from urllib.parse import urljoin

# Koneksi ke database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Ganti dengan user MySQL-mu
    password="",  # Ganti dengan password MySQL-mu
    database="web_crawler"
)
cursor = db.cursor()

# URL awal
start_url = "http://localhost/website/index.html"

# Set untuk menyimpan URL yang telah dikunjungi
visited = set()

# Fungsi DFS untuk crawling halaman web
def dfs_crawl(url):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to access {url} - Status Code: {response.status_code}")
            return
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.title.string if soup.title else "No Title"
    paragraph = soup.find("p").text if soup.find("p") else "No Content"

    print(f"Inserting into database: URL={url}, Title={title}, Paragraph={paragraph}")

    try:
        cursor.execute("INSERT INTO pages (url, title, paragraph) VALUES (%s, %s, %s)", (url, title, paragraph))
        db.commit()
        print("Insert berhasil!")
    except mysql.connector.Error as err:
        print(f"Insert gagal: {err}")

    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        dfs_crawl(next_url)


# Jalankan DFS dari halaman utama
dfs_crawl(start_url)

# Tutup koneksi database
cursor.close()
db.close()

print("Crawling selesai dan data telah disimpan ke database.")

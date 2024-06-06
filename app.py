from flask import Flask, render_template, jsonify, request
from ping3 import ping, verbose_ping
import threading
import time
import re

app = Flask(__name__)

# Inisialisasi data status
websites = [
    'https://unsub.ac.id/',
    'https://surabaya.telkomuniversity.ac.id/',
    'https://petra.ac.id/',
    'https://www.ubaya.ac.id/',
    'https://telkomuniversity.ac.id/',
    'https://www.unpak.ac.id/',
    'https://www.unida.ac.id/',
    'https://www.unjani.ac.id/',
    'https://www.ciputra.ac.id/',
    'https://binus.ac.id/malang/',
    'https://www.unnur.ac.id/',
    'https://www.unsur.ac.id/',
    'https://www.pasim.ac.id/',
    'https://unmabanten.ac.id/',
    'https://unpam.ac.id/?d=1',
    'https://www.widyatama.ac.id/',
    'https://unpi-cianjur.ac.id/struktur-unpi',
    'https://www.unfari.ac.id/',
    'https://president.ac.id/',
    'https://unma.ac.id/',
    'https://usbypkp.ac.id/',
    'https://unibi.ac.id/',
    'http://www.iwu.ac.id/',
    'https://unsera.ac.id/',
    'https://utn.ac.id/',
    'https://umt.ac.id',
    'http://www.upj.ac.id/',
    'https://www.unbaja.ac.id/',
    'https://www.iuli.ac.id/',
    'http://unisa.ac.id/',
    'http://www.unfari.ac.id/',
    'https://www.umtas.ac.id/',
    'http://unper.ac.id/',
    'https://www.panca-sakti.ac.id/',
    'https://umbanten.ac.id/',
    'https://utb-univ.ac.id/',
    'https://www.stikesceriabuana.ac.id/',
    'https://www.deakin.edu.au/',
    'http://www.itenas.ac.id/',
    'http://www.ithb.ac.id/',
    'http://www.ibm.ac.id/',
    'http://www.imwi.ac.id/',
    'http://www.institutpendidikan.ac.id/',
    'https://itts.ac.id/',
    'https://ikbisannisa.ac.id/',
]

# Fungsi untuk membersihkan URL dari skema
def extract_hostname(url):
    # Menghapus skema dan trailing slash
    hostname = re.sub(r'^https?://', '', url).rstrip('/')
    return hostname

# Normalisasi URL
cleaned_websites = [extract_hostname(url) for url in websites]

status_data = {url: {'status': 'Unknown', 'is_up': False, 'ping': None} for url in cleaned_websites}

def check_server(url):
    hostname = extract_hostname(url)
    try:
        response_time = ping(hostname, timeout=2, unit='ms')  # Timeout in milliseconds
        if response_time is not None:
            status_data[url] = {
                'status': 'Up',
                'is_up': True,
                'ping': response_time
            }
        else:
            status_data[url] = {
                'status': 'Down',
                'is_up': False,
                'ping': None
            }
    except Exception as err:
        print(f"Error checking URL {url}: {err}")
        status_data[url] = {
            'status': 'Down',
            'is_up': False,
            'ping': None
        }

def check_all_servers():
    while True:
        for website in websites:
            check_server(website)
        time.sleep(30)  # Periksa setiap 30 detik

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    return jsonify(status_data)

@app.route('/check', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url')
    hostname = extract_hostname(url)

    if url not in status_data:
        status_data[url] = {'status': 'Unknown', 'is_up': False, 'ping': None}

    try:
        ping_result = verbose_ping(hostname, count=1, timeout=2)
        if ping_result:
            status_data[url] = {
                'status': 'Up',
                'is_up': True,
                'ping': ping_result
            }
        else:
            status_data[url] = {
                'status': 'Down',
                'is_up': False,
                'ping': None
            }
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error checking URL {url}: {e}")
        status_data[url] = {
            'status': 'Down',
            'is_up': False,
            'ping': None
        }
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    threading.Thread(target=check_all_servers, daemon=True).start()
    app.run(debug=True)

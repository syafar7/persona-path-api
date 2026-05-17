from flask import Flask, request, jsonify

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Rute (Endpoint) utama untuk mengecek skill gap
@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    # 1. Tangkap data JSON dari frontend
    data = request.get_json()
    
    # Tangkap DUA variabel sekarang
    target_role = data.get('target_role', '')
    user_skills = data.get('user_skills', '')

    # 2. Data contoh sementara (Dummy Data) yang disesuaikan
    response = {
        "status": "success",
        "pesan": "API berhasil terhubung!",
        "target_role": target_role,
        "input_user": user_skills,
        "match_score": 75,
        "skill_gap": ["Python", "SQL", "Pandas", "Scikit-Learn"]
    }

    # 3. Kembalikan hasil ke frontend dalam format JSON
    return jsonify(response)

# Jalankan server
if __name__ == '__main__':
    # debug=True membuat server otomatis restart jika ada perubahan pada kode
    app.run(debug=True)
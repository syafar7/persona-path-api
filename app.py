from flask import Flask, request, jsonify

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Rute (Endpoint) utama untuk mengecek skill gap
@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    # 1. Tangkap data JSON dari frontend
    data = request.get_json()
    
    # Ambil nilai 'user_skills' dari JSON, jika kosong beri nilai default string kosong
    user_skills = data.get('user_skills', '')

    # 2. Data contoh sementara (Dummy Data) sebelum model AI dari temanmu siap
    response = {
        "status": "success",
        "pesan": "API berhasil terhubung!",
        "input_user": user_skills,
        "matched_job": "Backend Developer",
        "match_score": 90,
        "skill_gap": ["Python", "Flask", "Machine Learning"]
    }

    # 3. Kembalikan hasil ke frontend dalam format JSON
    return jsonify(response)

# Jalankan server
if __name__ == '__main__':
    # debug=True membuat server otomatis restart jika ada perubahan pada kode
    app.run(debug=True)
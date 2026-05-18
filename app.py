from flask import Flask, request, jsonify
from flask_cors import CORS  # 1. Impor modul CORS

app = Flask(__name__)
CORS(app)  # 2. Aktifkan CORS untuk mengizinkan akses dari Frontend React

# Kamus standar kompetensi untuk profesi (Sebagai acuan sementara sebelum model TensorFlow siap)
MASTER_JOB_SKILLS = {
    "Data Scientist": ["Python", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "Statistics"],
    "Backend Developer": ["PHP", "MySQL", "Python", "Flask", "Laravel", "Git", "REST API"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Tailwind CSS", "Bootstrap"]
}

@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    # Tangkap data JSON dari frontend
    data = request.get_json()
    
    target_role = data.get('target_role', 'Data Scientist')
    user_skills_raw = data.get('user_skills', '')

    # 3. Logika Pemrosesan Teks & Filter Dinamis
    # Mengubah string input user menjadi list huruf kecil dan menghapus spasi di ujungnya
    user_skills_list = [s.strip().lower() for s in user_skills_raw.split(',') if s.strip()]

    # Ambil standar kompetensi berdasarkan profesi yang dipilih (jika tidak terdaftar, default ke Data Scientist)
    required_skills = MASTER_JOB_SKILLS.get(target_role, MASTER_JOB_SKILLS["Data Scientist"])

    skill_gap = []
    matched_count = 0

    # Periksa setiap syarat kompetensi profesi
    for skill in required_skills:
        if skill.lower() in user_skills_list:
            matched_count += 1  # Jika user sudah punya kompetensi tersebut
        else:
            skill_gap.append(skill)  # Jika belum punya, masukkan ke daftar skill gap

    # 4. Logika Perhitungan Skor Otomatis
    total_required = len(required_skills)
    match_score = int((matched_count / total_required) * 100) if total_required > 0 else 0

    # Susun JSON respons kembali ke frontend
    response = {
        "status": "success",
        "pesan": "API berhasil diproses secara dinamis!",
        "target_role": target_role,
        "input_user": user_skills_raw,
        "match_score": match_score,
        "skill_gap": skill_gap
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
import os
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# Import Class baru buatan Susi
from inference import SkillGapAnalyzer

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Inisialisasi Model Susi HANYA SEKALI saat server menyala
try:
    analyzer = SkillGapAnalyzer(
        tfidf_path='models/tfidf_vectorizer.pkl',
        tfidf_matrix_path='models/tfidf_matrix.pkl',
        df_path='models/df_processed.csv'
    )
except Exception as e:
    print("GAGAL MEMUAT MODEL SUSI:", e)
    analyzer = None

def get_ai_recommendation(target_role, target_level, missing_skills):
    if not missing_skills:
        return "Luar biasa! Kamu sudah memiliki semua kualifikasi skill yang dibutuhkan. Waktunya fokus membangun proyek portofolio yang kompleks!"
    
    if not client:
        return "Sistem AI sedang disiapkan. Silakan mulai belajar dari YouTube atau dokumentasi resmi."

    skills_text = ", ".join(missing_skills)
    prompt = f"""
    Berperanlah sebagai mentor IT. User ingin menjadi {target_role} level {target_level}, 
    tapi belum menguasai skill berikut: {skills_text}. 
    Berikan 3 langkah ringkas dan praktis untuk mulai mempelajari skill tersebut.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"ERROR GROQ: {e}")
        return "Asisten AI sedang sibuk. Silakan cari referensi skill tersebut di internet."

@app.route('/api/analyze-gap', methods=['POST'])
def analyze_gap():
    try:
        # 1. PERLINDUNGAN EKSTRA UNTUK FORMAT JSON
        try:
            data = request.get_json(force=True)
        except Exception:
            data = request.data.decode('utf-8')

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
        
        if not isinstance(data, dict):
            return jsonify({
                "status": "error", 
                "pesan": "Format JSON tidak valid."
            }), 400

        # Ambil input user
        target_role = data.get('target_role')
        target_level = data.get('target_level') 
        user_skills_raw = data.get('user_skills', '')

        if not target_role or not target_level:
            return jsonify({"status": "error", "pesan": "Data target_role atau target_level tidak boleh kosong"}), 400

        # 2. FILTER INPUT: Paksa jadi string huruf kecil semua agar cocok dengan AI
        if isinstance(user_skills_raw, list):
            input_skills_list = [str(s).strip().lower() for s in user_skills_raw]
            user_skills_raw_str = ", ".join(input_skills_list)
        else:
            user_skills_raw_str = str(user_skills_raw).lower()
            input_skills_list = [s.strip() for s in user_skills_raw_str.split(',')]

        if not analyzer:
             return jsonify({"status": "error", "pesan": "Model AI gagal dimuat di server."}), 500

        # Tembak ke model Susi
        hasil_ml = analyzer.predict(target_role, user_skills_raw_str, target_level)

        if isinstance(hasil_ml, str):
            try:
                hasil_ml = json.loads(hasil_ml)
            except json.JSONDecodeError:
                return jsonify({"status": "error", "pesan": hasil_ml}), 400

        if isinstance(hasil_ml, dict) and "error" in hasil_ml:
            return jsonify({"status": "error", "pesan": hasil_ml["error"]}), 404

        # 3. PENYELAMATAN DATA Susi (Persentase & Filter Skill)
        if isinstance(hasil_ml, dict):
            raw_score = hasil_ml.get("match_score", 0)
            skill_gap = hasil_ml.get("skill_gap", [])
            learning_materials = hasil_ml.get("learning_materials", [])

            # FIX PERSENTASE: Ubah format 0.186 menjadi 18.6
            try:
                if float(raw_score) <= 1.0:
                    match_score = round(float(raw_score) * 100, 1)
                else:
                    match_score = round(float(raw_score), 1)
            except:
                match_score = 0

            # Catatan: Filter skill_gap sudah dilakukan di inference.py
            # JANGAN filter ulang di sini agar tidak ada inkonsistensi

            # Jika semua skill sudah dikuasai (gap kosong), beri rekomendasi default
            if not skill_gap:
                skill_gap = ["membangun proyek portofolio skala besar"]
        else:
            match_score = 0
            skill_gap = ["membangun proyek portofolio skala besar"]
            learning_materials = []

        # Rekomendasi AI Groq
        ai_recommendation = get_ai_recommendation(target_role, target_level, skill_gap)

        return jsonify({
            "status": "success",
            "pesan": "Analisis skill gap berhasil!",
            "target_role": target_role,
            "target_level": target_level,
            "match_score": match_score,
            "skill_gap": skill_gap,
            "learning_materials": learning_materials,
            "ai_recommendation": ai_recommendation 
        })

    except Exception as e:
        print("\n=== TERJADI ERROR DI SERVER ===")
        traceback.print_exc()
        print("===============================\n")
        return jsonify({"status": "error", "pesan": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
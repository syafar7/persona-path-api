import re
from collections import Counter

# Daftar skill IT yang akan dikenali dari teks deskripsi lowongan
SKILL_KEYWORDS = [
    # Web Frontend
    'html', 'css', 'javascript', 'typescript', 'react', 'vue', 'angular',
    'tailwind', 'bootstrap', 'jquery', 'next.js', 'nuxt', 'webpack', 'vite',
    # Backend
    'nodejs', 'node.js', 'php', 'laravel', 'python', 'django', 'flask',
    'java', 'spring', 'golang', 'ruby', 'rails',
    # Database
    'mysql', 'postgresql', 'mongodb', 'sql', 'redis', 'sqlite', 'oracle',
    # DevOps & Cloud
    'git', 'github', 'docker', 'kubernetes', 'aws', 'gcp', 'azure',
    'ci/cd', 'linux', 'nginx', 'jenkins', 'terraform',
    # API & Arch
    'api', 'rest api', 'graphql', 'microservices',
    # Mobile
    'kotlin', 'swift', 'flutter', 'dart', 'react native',
    # Design & Tools
    'figma', 'ui/ux', 'agile', 'scrum',
    # Data & ML
    'tableau', 'power bi', 'excel', 'pandas', 'numpy', 'tensorflow', 'pytorch',
    'machine learning', 'deep learning', 'data visualization', 'statistics',
    # Security
    'networking', 'firewall', 'penetration testing', 'ethical hacking',
    'kali linux', 'wireshark', 'nmap', 'metasploit', 'owasp',
    'cryptography', 'siem', 'ids/ips', 'vulnerability assessment',
    'incident response', 'security audit', 'iso 27001', 'ceh', 'cissp',
    # iOS & Others
    'ios', 'android', 'firebase',
]

def normalize_level(level_str):
    """
    Normalisasi input level dari user ke nilai yang ada di CSV.
    CSV menggunakan: 'entry', 'middle', 'senior'
    User bisa input: 'entry level', 'entry-level', 'junior', dll.
    """
    s = str(level_str).lower().strip()
    if 'entry' in s or 'junior' in s or 'fresh' in s:
        return 'entry'
    if 'middle' in s or 'mid' in s or 'intermediate' in s:
        return 'middle'
    if 'senior' in s or 'sr' in s:
        return 'senior'
    return s  # kembalikan apa adanya jika tidak cocok

def normalize_role(role_str):
    """
    Normalisasi nama posisi dari input user ke format yang ada di CSV.
    CSV menggunakan spasi: 'full stack developer', 'data analyst', dll.
    User bisa input: 'fullstack developer', 'Fullstack Developer', dll.
    """
    s = str(role_str).lower().strip()
    # Normalisasi variasi penulisan umum
    s = re.sub(r'fullstack', 'full stack', s)
    s = re.sub(r'full-stack', 'full stack', s)
    s = re.sub(r'frontend', 'front end', s)
    s = re.sub(r'front-end', 'front end', s)
    s = re.sub(r'backend', 'back end', s)
    s = re.sub(r'back-end', 'back end', s)
    # Hapus spasi berlebih
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_skills_from_text(text):
    """
    Ekstrak skill dari teks deskripsi lowongan menggunakan keyword matching.
    Mengembalikan list skill yang ditemukan.
    """
    text = str(text).lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # Gunakan word boundary agar 'sql' tidak match 'mysql' secara terpisah
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.append(skill)
    return found


class SkillGapAnalyzer:
    def __init__(self, tfidf_path=None, tfidf_matrix_path=None, df_path=None):
        import csv as _csv
        self.df_path = df_path
        self.rows = []
        self.columns = []
        try:
            # Load database CSV saat server menyala (tanpa pandas)
            with open(df_path, encoding='utf-8', errors='replace') as f:
                reader = _csv.DictReader(f)
                self.columns = reader.fieldnames or []
                for row in reader:
                    # Normalisasi posisi & level ke lowercase saat load
                    row['posisi'] = str(row.get('posisi', '')).lower().strip()
                    row['level'] = str(row.get('level', '')).lower().strip()
                    self.rows.append(row)
            print(f"[INFO] CSV berhasil dimuat: {len(self.rows)} baris")
            print(f"[INFO] Kolom: {self.columns}")
        except Exception as e:
            print(f"[ERROR] Gagal memuat CSV: {e}")
            self.rows = []
            self.columns = []

    def predict(self, target_role, user_skills, target_level):
        # Normalisasi input agar cocok dengan data CSV
        target_role_norm = normalize_role(target_role)
        target_level_norm = normalize_level(target_level)

        print(f"[DEBUG] Role input: '{target_role}' => normalized: '{target_role_norm}'")
        print(f"[DEBUG] Level input: '{target_level}' => normalized: '{target_level_norm}'")

        # Ubah input skill user jadi set (himpunan) lowercase
        list_user = [s.strip().lower() for s in user_skills.split(",") if s.strip()]
        set_user = set(list_user)

        # SKILL ALIAS: skill yang diinput user diekspansi ke skill standar yang setara.
        # Format: { skill_input: [(target_skill, {domain_keywords} | None)] }
        # domain_keywords=None artinya berlaku di semua domain
        # domain_keywords={'data','ml'} artinya hanya berlaku jika role mengandung kata tsb
        SKILL_ALIASES = {
            # Python ecosystem — hanya berlaku di domain data/ML
            'pandas':            [('python', {'data', 'machine learning'}),
                                  ('data visualization', {'data', 'machine learning'})],
            'numpy':             [('python', {'data', 'machine learning'})],
            'matplotlib':        [('python', {'data', 'machine learning'}),
                                  ('data visualization', {'data', 'machine learning'})],
            'seaborn':           [('python', {'data', 'machine learning'}),
                                  ('data visualization', {'data', 'machine learning'})],
            'scikit-learn':      [('python', {'data', 'machine learning'}),
                                  ('machine learning', {'data', 'machine learning'})],
            'sklearn':           [('python', {'data', 'machine learning'}),
                                  ('machine learning', {'data', 'machine learning'})],
            'scipy':             [('python', {'data', 'machine learning'}),
                                  ('statistics', {'data', 'machine learning'})],
            # ML frameworks — hanya domain data/ML
            'tensorflow':        [('machine learning', {'data', 'machine learning'}),
                                  ('deep learning',    {'data', 'machine learning'}),
                                  ('python',           {'data', 'machine learning'})],
            'pytorch':           [('machine learning', {'data', 'machine learning'}),
                                  ('deep learning',    {'data', 'machine learning'}),
                                  ('python',           {'data', 'machine learning'})],
            'keras':             [('machine learning', {'data', 'machine learning'}),
                                  ('deep learning',    {'data', 'machine learning'}),
                                  ('python',           {'data', 'machine learning'})],
            # BI & Visualization — hanya domain data
            'power bi':          [('data visualization', {'data', 'machine learning'}),
                                  ('excel',              {'data', 'machine learning'})],
            'tableau':           [('data visualization', {'data', 'machine learning'})],
            'looker':            [('data visualization', {'data', 'machine learning'})],
            'google data studio':[('data visualization', {'data', 'machine learning'})],
            'metabase':          [('data visualization', {'data', 'machine learning'})],
            # Data tools
            'excel':             [('data visualization', {'data', 'machine learning'}),
                                  ('statistics',         {'data', 'machine learning'})],
            'google sheets':     [('excel', {'data', 'machine learning'})],
            'r':                 [('statistics', {'data', 'machine learning'}),
                                  ('data visualization', {'data', 'machine learning'})],
            'spss':              [('statistics', {'data', 'machine learning'})],
            'stata':             [('statistics', {'data', 'machine learning'})],
            # SQL variants — berlaku di semua domain yang punya sql
            'mysql':             [('sql', None)],
            'postgresql':        [('sql', None)],
            'sqlite':            [('sql', None)],
            'oracle':            [('sql', None)],
            'mssql':             [('sql', None)],
            'sql server':        [('sql', None)],
            'bigquery':          [('sql', None), ('gcp', None)],
            'redshift':          [('sql', None), ('aws', None)],
            # JS frameworks — hanya domain web/mobile
            'react':             [('javascript', {'frontend', 'front end', 'full stack', 'web', 'mobile', 'ui/ux'})],
            'vue':               [('javascript', {'frontend', 'front end', 'full stack', 'web', 'ui/ux'})],
            'angular':           [('javascript', {'frontend', 'front end', 'full stack', 'web', 'ui/ux'})],
            'next.js':           [('javascript', {'frontend', 'front end', 'full stack', 'web'}),
                                  ('react',      {'frontend', 'front end', 'full stack', 'web'})],
            'nuxt':              [('javascript', {'frontend', 'front end', 'full stack', 'web'}),
                                  ('vue',        {'frontend', 'front end', 'full stack', 'web'})],
            'jquery':            [('javascript', {'frontend', 'front end', 'full stack', 'web', 'php'})],
            'typescript':        [('javascript', {'frontend', 'front end', 'full stack', 'web'})],
            # CSS frameworks
            'tailwind':          [('css', {'frontend', 'front end', 'full stack', 'web', 'ui/ux', 'php'})],
            'bootstrap':         [('css', {'frontend', 'front end', 'full stack', 'web', 'ui/ux', 'php'})],
            # Node/backend
            'nodejs':            [('javascript', {'frontend', 'front end', 'full stack', 'web', 'backend', 'back end'})],
            'node.js':           [('javascript', {'frontend', 'front end', 'full stack', 'web', 'backend', 'back end'})],
            'express':           [('nodejs', {'backend', 'back end', 'full stack', 'web'}),
                                  ('javascript', {'backend', 'back end', 'full stack', 'web'})],
            'laravel':           [('php', {'backend', 'back end', 'full stack', 'web', 'php'})],
            'django':            [('python', {'backend', 'back end', 'full stack', 'web'})],
            'flask':             [('python', {'backend', 'back end', 'full stack', 'web'})],
            'spring':            [('java', {'backend', 'back end', 'full stack', 'java'})],
            'rails':             [('ruby', {'backend', 'back end', 'full stack'})],
            # DevOps
            'kubernetes':        [('docker', {'devops', 'cloud', 'backend', 'back end'})],
            'jenkins':           [('ci/cd', {'devops', 'cloud', 'backend', 'back end'})],
            'github actions':    [('ci/cd', {'devops', 'cloud'}), ('git', None)],
            'gitlab ci':         [('ci/cd', {'devops', 'cloud'}), ('git', None)],
            'terraform':         [('aws', {'devops', 'cloud'})],
            # Mobile
            'dart':              [('flutter', {'mobile', 'flutter', 'android'})],
            'react native':      [('javascript', {'mobile', 'frontend', 'front end', 'full stack'})],
            'xcode':             [('swift', {'mobile', 'ios'}), ('ios', {'mobile', 'ios'})],
            # Security tools — hanya domain security
            'kali linux':        [('linux', {'security', 'cybersecurity', 'devops', 'cloud'}),
                                  ('penetration testing', {'security', 'cybersecurity'})],
            'metasploit':        [('penetration testing', {'security', 'cybersecurity'})],
            'wireshark':         [('networking', {'security', 'cybersecurity', 'network'})],
            'nmap':              [('networking', {'security', 'cybersecurity', 'network'}),
                                  ('penetration testing', {'security', 'cybersecurity'})],
            'burp suite':        [('penetration testing', {'security', 'cybersecurity'}),
                                  ('owasp', {'security', 'cybersecurity'})],
            'ceh':               [('penetration testing', {'security', 'cybersecurity'}),
                                  ('ethical hacking', {'security', 'cybersecurity'})],
            'cissp':             [('security audit', {'security', 'cybersecurity'}),
                                  ('cryptography', {'security', 'cybersecurity'})],
        }

        print(f"[DEBUG] Skills asli user: {list_user}")


        skill_standar = []

        # 1. PENCARIAN DI DATABASE CSV
        if self.rows and 'posisi' in self.columns and 'level' in self.columns:
            # Cari baris yang cocok dengan posisi & level (sudah dinormalisasi)
            rows_filtered = [
                r for r in self.rows
                if r.get('posisi') == target_role_norm and r.get('level') == target_level_norm
            ]

            print(f"[DEBUG] Baris ditemukan di CSV: {len(rows_filtered)}")

            if rows_filtered:
                # Tentukan kolom deskripsi yang tersedia
                if 'deskripsi_clean' in self.columns:
                    kolom_desc = 'deskripsi_clean'
                elif 'deskripsi' in self.columns:
                    kolom_desc = 'deskripsi'
                elif 'skills' in self.columns:
                    kolom_desc = 'skills'
                else:
                    kolom_desc = None

                if kolom_desc:
                    # Ekstrak skill dari semua deskripsi lowongan yang cocok
                    counter_skill = Counter()
                    for row in rows_filtered:
                        teks = str(row.get(kolom_desc, ''))
                        skill_ditemukan = extract_skills_from_text(teks)
                        for sk in skill_ditemukan:
                            counter_skill[sk] += 1

                    # Ambil 10 skill teratas: frekuensi tertinggi, lalu alfabet (deterministik)
                    skill_standar = [
                        skill for skill, count in
                        sorted(counter_skill.items(), key=lambda x: (-x[1], x[0]))
                    ][:10]

                    print(f"[DEBUG] Skill standar dari CSV: {skill_standar}")

        # 2. SISTEM FALLBACK berdasarkan role
        # Diaktifkan jika: CSV tidak ada data ATAU data CSV terlalu sedikit (< 5 skill)
        FALLBACK_SKILLS = {
            "full stack": ["html", "css", "javascript", "react", "php", "mysql", "git", "api", "nodejs", "jquery"],
            "frontend": ["html", "css", "javascript", "react", "tailwind", "git", "figma", "typescript", "vue", "bootstrap"],
            "front end": ["html", "css", "javascript", "react", "tailwind", "git", "figma", "typescript", "vue", "bootstrap"],
            "backend": ["php", "mysql", "python", "nodejs", "git", "docker", "api", "sql", "laravel", "postgresql"],
            "back end": ["php", "mysql", "python", "nodejs", "git", "docker", "api", "sql", "laravel", "postgresql"],
            "mobile": ["flutter", "dart", "javascript", "api", "git", "kotlin", "figma", "ui/ux", "firebase", "android"],
            "data analyst": ["python", "sql", "mysql", "postgresql", "tableau", "power bi", "excel", "statistics", "aws", "data visualization"],
            "data": ["python", "sql", "mysql", "postgresql", "git", "tableau", "power bi", "excel", "statistics", "aws"],
            "machine learning": ["python", "sql", "tensorflow", "pytorch", "pandas", "numpy", "machine learning", "deep learning", "aws", "docker"],
            "cybersecurity": ["networking", "linux", "python", "firewall", "penetration testing", "ethical hacking", "wireshark", "nmap", "owasp", "vulnerability assessment"],
            "security": ["networking", "linux", "python", "firewall", "penetration testing", "wireshark", "nmap", "owasp", "cryptography", "siem"],
            "devops": ["linux", "docker", "kubernetes", "git", "ci/cd", "aws", "terraform", "jenkins", "nginx", "python"],
            "cloud": ["aws", "gcp", "azure", "docker", "kubernetes", "terraform", "linux", "ci/cd", "git", "python"],
            "ui/ux": ["figma", "ui/ux", "html", "css", "javascript", "tailwind", "bootstrap", "react", "vue", "agile"],
            "java": ["java", "spring", "mysql", "sql", "git", "api", "docker", "maven", "postgresql", "aws"],
            "flutter": ["flutter", "dart", "firebase", "api", "git", "android", "ios", "kotlin", "figma", "ui/ux"],
            "php": ["php", "laravel", "mysql", "html", "css", "javascript", "git", "api", "sql", "bootstrap"],
            "android": ["kotlin", "java", "android", "firebase", "api", "git", "sql", "figma", "ui/ux", "agile"],
            "ios": ["swift", "ios", "xcode", "firebase", "api", "git", "sql", "figma", "ui/ux", "agile"],
        }

        def get_fallback(role_norm):
            """Cari fallback yang paling cocok untuk role tertentu."""
            for key, skills in FALLBACK_SKILLS.items():
                if key in role_norm:
                    return skills
            # Default fallback jika tidak ada yang cocok
            return ["python", "git", "sql", "linux", "api", "docker", "agile", "scrum", "aws", "javascript"]

        if not skill_standar:
            print(f"[DEBUG] Fallback penuh aktif untuk role: '{target_role_norm}'")
            skill_standar = get_fallback(target_role_norm)
        elif len(skill_standar) < 5:
            # Data CSV ada tapi sangat sedikit — tambahkan fallback agar total skill cukup
            print(f"[DEBUG] Data CSV hanya {len(skill_standar)} skill, menambah fallback.")
            fallback = get_fallback(target_role_norm)
            # Tambahkan skill fallback yang belum ada di skill_standar (urutan prioritas: CSV dulu)
            existing = set(skill_standar)
            for sk in fallback:
                if sk not in existing:
                    skill_standar.append(sk)
                    existing.add(sk)
                if len(skill_standar) >= 10:
                    break
            print(f"[DEBUG] Skill standar setelah gabung fallback: {skill_standar}")

        # 3. EKSPANSI ALIAS — domain-aware & standar-aware
        # Syarat alias dihitung:
        #   (a) target skill ada di skill_standar role ini, DAN
        #   (b) domain alias cocok dengan role (atau domain=None = universal)
        set_skill_standar = set(skill_standar)
        expanded_user = set(set_user)
        for skill in list_user:
            if skill in SKILL_ALIASES:
                for (alias_target, alias_domains) in SKILL_ALIASES[skill]:
                    # Cek (a): target harus ada di skill_standar role ini
                    if alias_target not in set_skill_standar:
                        continue
                    # Cek (b): domain cocok
                    if alias_domains is None:
                        # Universal — berlaku di semua role
                        expanded_user.add(alias_target)
                    elif any(domain in target_role_norm for domain in alias_domains):
                        # Hanya berlaku jika role mengandung kata domain yang diizinkan
                        expanded_user.add(alias_target)
        set_user = expanded_user
        print(f"[DEBUG] Skills setelah ekspansi alias (domain-aware): {sorted(set_user)}")


        # 4. PENGURANGAN HIMPUNAN: Standar Industri - Skill User = Gap
        skill_gap = [s for s in skill_standar if s not in set_user]

        # 5. PERHITUNGAN SKOR
        skill_cocok = [s for s in skill_standar if s in set_user]
        skor_persen = (len(skill_cocok) / len(skill_standar)) * 100 if skill_standar else 0.0

        print(f"[DEBUG] User skills: {list_user}")
        print(f"[DEBUG] Skill cocok: {skill_cocok}")
        print(f"[DEBUG] Skill gap: {skill_gap}")
        print(f"[DEBUG] Skor: {skor_persen:.1f}%")

        return {
            "match_score": round(skor_persen, 1),
            "skill_gap": skill_gap,
            "learning_materials": []
        }
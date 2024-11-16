from django.shortcuts import render
import csv
import os
import json
from datetime import datetime
from django.conf import settings

def indexM(request):
    # Ambil keyword, keyword method, dan rentang tahun dari query parameter
    keyword = request.GET.get('keyword', '').lower()
    keyword_method = request.GET.get('keyword_method', '').lower()  # Filter khusus metode
    keyword_objective = request.GET.get('keyword_objective', '').lower()  # Filter khusus metode
    from_year = request.GET.get('from_year', '').strip()
    to_year = request.GET.get('to_year', '').strip()

    # Jika keyword tidak diisi, tampilkan pesan error
    if not keyword:
        return render(request, 'indexM.html', {'error': 'Keyword harap diisi.'})

    # Jika tahun tidak diisi, biarkan tetap sebagai kosong
    # Jika diisi, konversi menjadi integer
    try:
        from_year = int(from_year) if from_year else None
        to_year = int(to_year) if to_year else None
    except ValueError:
        return render(request, 'indexM.html', {'error': 'Rentang tahun tidak valid.'})

    # Path ke file CSV
    csv_path = os.path.join(settings.BASE_DIR, 'carina_search', 'static', 'csv', 'journal_data.csv')

    journals = []
    links = []  # Relasi antar jurnal

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title_lower = row['Title'].lower()
                keyword_lower = keyword.lower()

                # Parsing kolom 'Year' sebagai tahun
                try:
                    journal_year = datetime.strptime(row['Year'], '%B %d, %Y').year
                except ValueError:
                    continue

                # Gabungkan kolom yang relevan menjadi satu "abstract" gabungan
                abstract_combined = " ".join([
                    row.get('Background', ''), row.get('Objective', ''), 
                    row.get('Methods', ''), row.get('Results', ''), 
                    row.get('Conclusion', '')
                ]).lower()

                # Tambahan: Filter berdasarkan keyword method khusus di kolom 'Methods'
                methods_content = row.get('Methods', '').lower()
                if keyword_method and keyword_method not in methods_content:
                    continue  
                
                objective_content = row.get('Objective', '').lower()
                if keyword_objective and keyword_objective not in objective_content:
                    continue  

                # Filter berdasarkan keyword dan rentang tahun jika diisi
                if keyword_lower in title_lower or keyword_lower in abstract_combined:
                    # Jika rentang tahun diisi, filter berdasarkan tahun
                    if (from_year is None or journal_year >= from_year) and (to_year is None or journal_year <= to_year):
                        relevansi = title_lower.count(keyword_lower) + abstract_combined.count(keyword_lower)
                        pdf_link = row.get('PDF Link', '')

                        if relevansi > 0:
                            journal_node = {
                                'j': {
                                    'title': row['Title'],
                                    'abstract': abstract_combined,
                                    'author': row['Authors'],
                                    'relevansi': relevansi,
                                    'pdf_link': pdf_link,
                                    'method': methods_content,
                                    'goal': objective_content
                                }
                            }
                            journals.append(journal_node)

                            # Membuat relasi antar node berdasarkan kesamaan Goals dan Methods
                            for other_journal in journals[:-1]:  # Check against previously added journals
                                # Cek kesamaan methods
                                if (methods_content and other_journal['j']['method'] and
                                    any(method.strip() in other_journal['j']['method'].lower() 
                                        for method in methods_content.split(','))):
                                    # Link antar node method yang sama
                                    links.append({
                                        'source': f"{row['Title']}_method",
                                        'target': f"{other_journal['j']['title']}_method",
                                        'type': 'method'
                                    })

                                # Cek kesamaan goals/objectives
                                if (objective_content and other_journal['j']['goal'] and
                                    any(goal.strip() in other_journal['j']['goal'].lower() 
                                        for goal in objective_content.split(','))):
                                    # Link antar node goal yang sama
                                    links.append({
                                        'source': f"{row['Title']}_goal",
                                        'target': f"{other_journal['j']['title']}_goal",
                                        'type': 'goal'
                                    })
                                    


    except FileNotFoundError:
        return render(request, 'indexM.html', {'error': f'File CSV tidak ditemukan pada path: {csv_path}'})

    if not journals:
        return render(request, 'indexM.html', {'error': f'Tidak ditemukan jurnal untuk "{keyword}" dalam rentang tahun yang ditentukan.'})

    # Konversi data journals ke JSON dan kirimkan ke template
    context = {
        'journals': json.dumps(journals),
        'links': json.dumps(links),
        'keyword': keyword
    }

    return render(request, 'indexM.html', context)


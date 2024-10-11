from django.shortcuts import render
import csv
import os
import json
from datetime import datetime
from django.conf import settings

def indexM(request):
    # Ambil keyword dan rentang tahun dari query parameter
    keyword = request.GET.get('keyword', '').lower()
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

                # Coba parsing kolom 'Year' sebagai tanggal
                try:
                    journal_year = datetime.strptime(row['Year'], '%B %d, %Y').year
                except ValueError:
                    continue

                # Gabungkan kolom yang relevan menjadi satu "abstrak" gabungan
                abstract_combined = " ".join([
                    row.get('Background', ''), row.get('Objective', ''), 
                    row.get('Methods', ''), row.get('Results', ''), 
                    row.get('Conclusion', '')
                ]).lower()

                # Filter berdasarkan keyword dan rentang tahun jika diisi
                if keyword_lower in title_lower or keyword_lower in abstract_combined:
                    # Jika rentang tahun diisi, filter berdasarkan tahun
                    if (from_year is None or journal_year >= from_year) and (to_year is None or journal_year <= to_year):
                        relevansi = title_lower.count(keyword_lower) + abstract_combined.count(keyword_lower)
                         # Ambil link atau PDF dari database
                        pdf_link = row.get('PDF_Link', '')

                        if relevansi > 0:
                            journals.append({
                                'j': {
                                    'title': row['Title'],
                                    'abstract': abstract_combined,
                                    'author': row['Authors'],
                                    'relevansi': relevansi,
                                    'pdf_link': row.get('PDF Link')  # Ambil link PDF
                                }
                            })


                            # Membuat relasi antar node berdasarkan relevansi lebih dari 1
                            if relevansi > 1:
                                for other_journal in journals[:-1]:
                                    if other_journal['j']['relevansi'] > 1:
                                        links.append({
                                            'source': row['Title'],
                                            'target': other_journal['j']['title']
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

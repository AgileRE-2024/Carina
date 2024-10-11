from django.shortcuts import render
from .neo4j_helper import Neo4jConnection

# Function untuk menampilkan halaman utama
def index(request):
    context = {
        'nama': 'hello world',
    }
    return render(request, 'index.html', context)

# Function untuk menyimpan jurnal ke Neo4j
def add_journal(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')
        author = request.POST.get('author')

        if title and abstract and author:  # Pastikan semua data terisi
            # Inisialisasi koneksi Neo4j
            neo4j = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", password="your_password")
            
            # Query untuk membuat node jurnal baru
            query_create_journal = """
            CREATE (j:Jurnal {title: $title, abstract: $abstract, author: $author})
            """
            parameters = {"title": title, "abstract": abstract, "author": author}
            neo4j.query(query_create_journal, parameters)
            
            # Query untuk membuat relasi antar jurnal berdasarkan kemiripan abstrak
            query_create_relation = """
            MATCH (j:Jurnal), (other_journal:Jurnal)
            WHERE j.abstract CONTAINS 'machine learning' AND other_journal.abstract CONTAINS 'machine learning' AND j <> other_journal
            CREATE (j)-[:RELATED_TO]->(other_journal)
            """
            neo4j.query(query_create_relation)

            neo4j.close()  # Tutup koneksi ke Neo4j setelah selesai
            
            return render(request, 'journal/success.html', {'message': 'Jurnal berhasil ditambahkan'})
        else:
            return render(request, 'journal/add.html', {'error': 'Semua field harus diisi'})
    
    return render(request, 'journal/add.html')

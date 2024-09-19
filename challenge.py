import sqlite3
import csv
import os
from pathlib import Path
import shutil
from datetime import datetime

DB_PATH = Path('data/livraria.db')
BACKUP_DIR = Path('meu_sistema_livraria/backups')
EXPORTS_DIR = Path('meu_sistema_livraria/exports')

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    ano_publicacao INTEGER NOT NULL,
    preco REAL NOT NULL
)
''')
conn.commit()


def AdicionarLivro(titulo, autor, ano_publicacao, preco):
    BackupDatabase()  # Backup antes de adicionar
    cursor.execute('''
    INSERT INTO livros (titulo, autor, ano_publicacao, preco)
    VALUES (?, ?, ?, ?)
    ''', (titulo, autor, ano_publicacao, preco))
    conn.commit()


def ExibirLivros():
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    for livro in livros:
        print(f'ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}')


def AtualizarPreco(titulo, novo_preco):
    BackupDatabase()  # Backup antes de atualizar
    cursor.execute('''
    UPDATE livros
    SET preco = ?
    WHERE titulo = ?
    ''', (novo_preco, titulo))
    conn.commit()


def RemoverLivro(titulo):
    BackupDatabase()
    cursor.execute('''
    DELETE FROM livros
    WHERE titulo = ?
    ''', (titulo,))
    conn.commit()


def BuscarLivrosPorAutor(autor):
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    if livros:
        for livro in livros:
            print(f'ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}')
    else:
        print("Nenhum livro encontrado para este autor.")


def ExportarParaCSV():
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()

    with open(EXPORTS_DIR / 'livros_exportados.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)

    print("Dados exportados com sucesso para 'livros_exportados.csv'.")


def ImportarDeCSV():
    with open(EXPORTS_DIR / 'livros_exportados.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            AdicionarLivro(row[1], row[2], int(row[3]), float(row[4]))


def BackupDatabase():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = BACKUP_DIR / f'backup_livraria_{timestamp}.db'
    shutil.copy(DB_PATH, backup_file)
    LimparBackupsAntigos()


def LimparBackupsAntigos():
    backups = sorted(BACKUP_DIR.glob('backup_livraria_*.db'), key=os.path.getmtime)
    for backup in backups[:-5]:
        os.remove(backup)


def menu():
    while True:
        print("\nMenu:")
        print("1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de publicação: "))
            preco = float(input("Preço: "))
            AdicionarLivro(titulo, autor, ano_publicacao, preco)
            print("Livro adicionado com sucesso!")

        elif opcao == '2':
            print("Livros na livraria:")
            ExibirLivros()

        elif opcao == '3':
            titulo = input("Título do livro que deseja atualizar o preço: ")
            novo_preco = float(input("Novo preço: "))
            AtualizarPreco(titulo, novo_preco)
            print("Preço atualizado com sucesso!")

        elif opcao == '4':
            titulo = input("Título do livro que deseja remover: ")
            RemoverLivro(titulo)
            print("Livro removido com sucesso!")

        elif opcao == '5':
            autor = input("Autor que deseja buscar: ")
            BuscarLivrosPorAutor(autor)

        elif opcao == '6':
            ExportarParaCSV()

        elif opcao == '7':
            ImportarDeCSV()
            print("Dados importados com sucesso!")

        elif opcao == '8':
            BackupDatabase()
            print("Backup realizado com sucesso!")

        elif opcao == '9':
            print("Saindo do sistema...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()

conn.close()

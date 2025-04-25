# System Kopii Zapasowych / Backup System

## 🇵🇱 Polski

### Opis
System Kopii Zapasowych to wszechstronne narzędzie do zarządzania kopiami zapasowymi plików i baz danych. Program umożliwia tworzenie i przywracanie kopii zapasowych z wykorzystaniem różnych metod przechowywania: lokalnie, przez FTP lub SSH.

### Funkcje
- Tworzenie kopii zapasowych plików:
  - Lokalne kopie zapasowe
  - Kopie zapasowe przez FTP
  - Kopie zapasowe przez SSH
- Obsługa kopii zapasowych baz danych:
  - MySQL
  - PostgreSQL
- Kompresja kopii zapasowych
- Automatyczne zarządzanie liczbą przechowywanych kopii
- Przywracanie kopii zapasowych
- Konfigurowalny interfejs

### Wymagania systemowe
- Python 3.x
- Wymagane biblioteki Python:
  - paramiko (dla połączeń SSH)
  - ftplib (wbudowana, dla połączeń FTP)
  - tarfile (wbudowana, dla kompresji)

### Instalacja
1. Sklonuj repozytorium:
```bash
git clone [adres-repozytorium]
cd backupftp
```

2. Zainstaluj wymagane zależności:
```bash
pip install paramiko
```

### Konfiguracja
1. Przy pierwszym uruchomieniu program utworzy domyślny plik konfiguracyjny `config.json`
2. Możesz skonfigurować następujące ustawienia:
   - Lokalizacje kopii zapasowych (źródło i cel)
   - Ustawienia FTP (host, port, dane logowania)
   - Ustawienia SSH (host, port, użytkownik, ścieżka do klucza)
   - Ustawienia bazy danych (typ, host, port, nazwa bazy, dane logowania)
   - Parametry kopii zapasowych (maksymalna liczba kopii, kompresja)

### Użycie
1. Uruchom program:
```bash
python3 backup_manager.py
```

2. Wybierz odpowiednią opcję z menu:
   - Wykonaj kopię zapasową
   - Przywróć kopię zapasową
   - Konfiguracja

## 🇬🇧 English

### Description
Backup System is a versatile tool for managing file and database backups. The program enables creating and restoring backups using various storage methods: locally, via FTP, or SSH.

### Features
- File backup creation:
  - Local backups
  - FTP backups
  - SSH backups
- Database backup support:
  - MySQL
  - PostgreSQL
- Backup compression
- Automatic backup retention management
- Backup restoration
- Configurable interface

### System Requirements
- Python 3.x
- Required Python libraries:
  - paramiko (for SSH connections)
  - ftplib (built-in, for FTP connections)
  - tarfile (built-in, for compression)

### Installation
1. Clone the repository:
```bash
git clone [repository-address]
cd backupftp
```

2. Install required dependencies:
```bash
pip install paramiko
```

### Configuration
1. On first run, the program will create a default `config.json` file
2. You can configure the following settings:
   - Backup locations (source and destination)
   - FTP settings (host, port, login credentials)
   - SSH settings (host, port, username, key path)
   - Database settings (type, host, port, database name, login credentials)
   - Backup parameters (maximum number of backups, compression)

### Usage
1. Run the program:
```bash
python3 backup_manager.py
```

2. Choose the appropriate option from the menu:
   - Create backup
   - Restore backup
   - Configuration
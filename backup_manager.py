#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

CONFIG_FILE = 'config.json'

class BackupManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print('Błąd: Plik konfiguracyjny nie istnieje!')
            return self.create_default_config()
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print('Błąd: Nieprawidłowy format pliku konfiguracyjnego!')
            return self.create_default_config()

    def create_default_config(self):
        default_config = {
            'backup_locations': {
                'source': '',
                'destination': '',
                'type': 'local'
            },
            'ftp_settings': {
                'host': '',
                'port': 21,
                'username': '',
                'password': ''
            },
            'ssh_settings': {
                'host': '',
                'port': 22,
                'username': '',
                'key_path': ''
            },
            'database_settings': {
                'type': '',
                'host': '',
                'port': '',
                'database': '',
                'username': '',
                'password': ''
            },
            'backup_settings': {
                'max_backups': 10,
                'compress': True,
                'backup_schedule': 'daily'
            }
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def show_menu(self):
        while True:
            print('\n=== System Kopii Zapasowych ===')
            print('1. Wykonaj kopię zapasową')
            print('2. Przywróć kopię zapasową')
            print('3. Konfiguracja')
            print('4. Wyjście')
            
            choice = input('\nWybierz opcję: ')
            
            if choice == '1':
                self.backup_menu()
            elif choice == '2':
                self.restore_menu()
            elif choice == '3':
                self.config_menu()
            elif choice == '4':
                print('Do widzenia!')
                sys.exit(0)
            else:
                print('Nieprawidłowa opcja!')

    def backup_menu(self):
        from file_handler import FileHandler
        from db_handler import DatabaseHandler
        
        print('\n=== Menu Kopii Zapasowej ===')
        print('1. Kopia zapasowa plików')
        print('2. Kopia zapasowa bazy danych')
        print('3. Powrót')
        
        choice = input('\nWybierz opcję: ')
        
        if choice == '1':
            file_handler = FileHandler(self.config)
            source = self.config['backup_locations']['source']
            dest = self.config['backup_locations']['destination']
            backup_type = self.config['backup_locations']['type']
            
            if not source or not dest:
                print('Błąd: Nie skonfigurowano ścieżek źródłowej i docelowej!')
                return
            
            print(f'\nTworzenie kopii zapasowej z {source}')
            success = False
            message = ''
            
            if backup_type == 'local':
                success, message = file_handler.backup_local(source, dest)
            elif backup_type == 'ftp':
                success, message = file_handler.backup_ftp(source)
            elif backup_type == 'ssh':
                success, message = file_handler.backup_ssh(source)
            
            print(message)
            
        elif choice == '2':
            db_handler = DatabaseHandler(self.config)
            if not self.config['database_settings']['type']:
                print('Błąd: Nie skonfigurowano bazy danych!')
                return
            
            print('\nTworzenie kopii zapasowej bazy danych...')
            success, message = db_handler.backup_database()
            print(message)

    def restore_menu(self):
        from file_handler import FileHandler
        from db_handler import DatabaseHandler
        
        print('\n=== Menu Przywracania ===')
        print('1. Przywróć pliki')
        print('2. Przywróć bazę danych')
        print('3. Powrót')
        
        choice = input('\nWybierz opcję: ')
        
        if choice == '1':
            file_handler = FileHandler(self.config)
            backup_type = self.config['backup_locations']['type']
            dest = self.config['backup_locations']['destination']
            
            # Pobierz listę dostępnych kopii zapasowych
            backups = file_handler.list_backups(backup_type)
            
            if not backups:
                print('Nie znaleziono kopii zapasowych!')
                return
            
            print('\nDostępne kopie zapasowe:')
            for i, backup in enumerate(backups, 1):
                print(f'{i}. {backup}')
            
            try:
                choice = int(input('\nWybierz numer kopii do przywrócenia: ')) - 1
                if 0 <= choice < len(backups):
                    backup_name = backups[choice]
                    print(f'\nPrzywracanie kopii zapasowej {backup_name}...')
                    
                    success = False
                    message = ''
                    
                    if backup_type == 'local':
                        success, message = file_handler.restore_local(
                            os.path.join(dest, backup_name),
                            dest
                        )
                    elif backup_type == 'ftp':
                        success, message = file_handler.restore_ftp(backup_name, dest)
                    elif backup_type == 'ssh':
                        success, message = file_handler.restore_ssh(backup_name, dest)
                    
                    print(message)
                else:
                    print('Nieprawidłowy numer kopii zapasowej!')
            except ValueError:
                print('Nieprawidłowy wybór!')
                
        elif choice == '2':
            db_handler = DatabaseHandler(self.config)
            if not self.config['database_settings']['type']:
                print('Błąd: Nie skonfigurowano bazy danych!')
                return
            
            # Lista plików .sql w bieżącym katalogu
            backups = [f for f in os.listdir('.') if f.endswith('.sql')]
            
            if not backups:
                print('Nie znaleziono kopii zapasowych bazy danych!')
                return
            
            print('\nDostępne kopie zapasowe bazy danych:')
            for i, backup in enumerate(backups, 1):
                print(f'{i}. {backup}')
            
            try:
                choice = int(input('\nWybierz numer kopii do przywrócenia: ')) - 1
                if 0 <= choice < len(backups):
                    backup_name = backups[choice]
                    print(f'\nPrzywracanie bazy danych z kopii {backup_name}...')
                    success, message = db_handler.restore_database(backup_name)
                    print(message)
                else:
                    print('Nieprawidłowy numer kopii zapasowej!')
            except ValueError:
                print('Nieprawidłowy wybór!')

    def config_menu(self):
        print('\n=== Menu Konfiguracji ===')
        print('1. Ustawienia lokalizacji')
        print('2. Ustawienia FTP')
        print('3. Ustawienia SSH')
        print('4. Ustawienia bazy danych')
        print('5. Ustawienia kopii zapasowych')
        print('6. Powrót')
        
        choice = input('\nWybierz opcję: ')
        
        if choice == '1':
            print('\nUstawienia lokalizacji')
            self.config['backup_locations']['source'] = input('Ścieżka źródłowa: ')
            self.config['backup_locations']['destination'] = input('Ścieżka docelowa: ')
            print('\nTyp kopii zapasowej:')
            print('1. Lokalna')
            print('2. FTP')
            print('3. SSH')
            type_choice = input('Wybierz typ: ')
            if type_choice == '1':
                self.config['backup_locations']['type'] = 'local'
            elif type_choice == '2':
                self.config['backup_locations']['type'] = 'ftp'
            elif type_choice == '3':
                self.config['backup_locations']['type'] = 'ssh'
            self.save_config()
            
        elif choice == '2':
            print('\nUstawienia FTP')
            self.config['ftp_settings']['host'] = input('Host FTP: ')
            self.config['ftp_settings']['port'] = int(input('Port FTP (domyślnie 21): ') or 21)
            self.config['ftp_settings']['username'] = input('Nazwa użytkownika: ')
            self.config['ftp_settings']['password'] = input('Hasło: ')
            self.save_config()
            
        elif choice == '3':
            print('\nUstawienia SSH')
            self.config['ssh_settings']['host'] = input('Host SSH: ')
            self.config['ssh_settings']['port'] = int(input('Port SSH (domyślnie 22): ') or 22)
            self.config['ssh_settings']['username'] = input('Nazwa użytkownika: ')
            self.config['ssh_settings']['key_path'] = input('Ścieżka do klucza SSH: ')
            self.save_config()
            
        elif choice == '4':
            print('\nUstawienia bazy danych')
            print('Typ bazy danych:')
            print('1. MySQL')
            print('2. PostgreSQL')
            db_choice = input('Wybierz typ: ')
            if db_choice == '1':
                self.config['database_settings']['type'] = 'mysql'
            elif db_choice == '2':
                self.config['database_settings']['type'] = 'postgresql'
            
            self.config['database_settings']['host'] = input('Host bazy danych: ')
            self.config['database_settings']['port'] = input('Port bazy danych: ')
            self.config['database_settings']['database'] = input('Nazwa bazy danych: ')
            self.config['database_settings']['username'] = input('Nazwa użytkownika: ')
            self.config['database_settings']['password'] = input('Hasło: ')
            self.save_config()
            
        elif choice == '5':
            print('\nUstawienia kopii zapasowych')
            self.config['backup_settings']['max_backups'] = int(input('Maksymalna liczba kopii zapasowych: '))
            compress = input('Kompresować kopie zapasowe? (t/n): ').lower()
            self.config['backup_settings']['compress'] = compress == 't'
            self.save_config()

def main():
    manager = BackupManager()
    manager.show_menu()

if __name__ == '__main__':
    main()
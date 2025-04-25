#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

class DatabaseHandler:
    def __init__(self, config):
        self.config = config

    def create_backup_name(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'backup_db_{timestamp}.sql'

    def backup_mysql(self):
        try:
            backup_name = self.create_backup_name()
            db_settings = self.config['database_settings']
            
            # Przygotuj komendę mysqldump
            command = [
                'mysqldump',
                f'--host={db_settings["host"]}',
                f'--port={db_settings["port"]}',
                f'--user={db_settings["username"]}',
                f'--password={db_settings["password"]}',
                db_settings['database']
            ]
            
            # Wykonaj backup
            with open(backup_name, 'w') as f:
                subprocess.run(command, stdout=f, check=True)
            
            return True, backup_name
        except subprocess.CalledProcessError as e:
            return False, f'Błąd podczas tworzenia kopii zapasowej bazy danych: {str(e)}'
        except Exception as e:
            return False, f'Nieoczekiwany błąd: {str(e)}'

    def restore_mysql(self, backup_file):
        try:
            db_settings = self.config['database_settings']
            
            # Przygotuj komendę mysql
            command = [
                'mysql',
                f'--host={db_settings["host"]}',
                f'--port={db_settings["port"]}',
                f'--user={db_settings["username"]}',
                f'--password={db_settings["password"]}',
                db_settings['database']
            ]
            
            # Wykonaj przywracanie
            with open(backup_file, 'r') as f:
                subprocess.run(command, stdin=f, check=True)
            
            return True, 'Baza danych została przywrócona pomyślnie'
        except subprocess.CalledProcessError as e:
            return False, f'Błąd podczas przywracania bazy danych: {str(e)}'
        except Exception as e:
            return False, f'Nieoczekiwany błąd: {str(e)}'

    def backup_postgresql(self):
        try:
            backup_name = self.create_backup_name()
            db_settings = self.config['database_settings']
            
            # Ustaw zmienne środowiskowe dla hasła
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['password']
            
            # Przygotuj komendę pg_dump
            command = [
                'pg_dump',
                f'--host={db_settings["host"]}',
                f'--port={db_settings["port"]}',
                f'--username={db_settings["username"]}',
                f'--dbname={db_settings["database"]}',
                '--format=plain',
                f'--file={backup_name}'
            ]
            
            # Wykonaj backup
            subprocess.run(command, env=env, check=True)
            
            return True, backup_name
        except subprocess.CalledProcessError as e:
            return False, f'Błąd podczas tworzenia kopii zapasowej bazy danych: {str(e)}'
        except Exception as e:
            return False, f'Nieoczekiwany błąd: {str(e)}'

    def restore_postgresql(self, backup_file):
        try:
            db_settings = self.config['database_settings']
            
            # Ustaw zmienne środowiskowe dla hasła
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['password']
            
            # Przygotuj komendę psql
            command = [
                'psql',
                f'--host={db_settings["host"]}',
                f'--port={db_settings["port"]}',
                f'--username={db_settings["username"]}',
                f'--dbname={db_settings["database"]}',
                f'--file={backup_file}'
            ]
            
            # Wykonaj przywracanie
            subprocess.run(command, env=env, check=True)
            
            return True, 'Baza danych została przywrócona pomyślnie'
        except subprocess.CalledProcessError as e:
            return False, f'Błąd podczas przywracania bazy danych: {str(e)}'
        except Exception as e:
            return False, f'Nieoczekiwany błąd: {str(e)}'

    def backup_database(self):
        db_type = self.config['database_settings']['type'].lower()
        if db_type == 'mysql':
            return self.backup_mysql()
        elif db_type == 'postgresql':
            return self.backup_postgresql()
        else:
            return False, f'Nieobsługiwany typ bazy danych: {db_type}'

    def restore_database(self, backup_file):
        db_type = self.config['database_settings']['type'].lower()
        if db_type == 'mysql':
            return self.restore_mysql(backup_file)
        elif db_type == 'postgresql':
            return self.restore_postgresql(backup_file)
        else:
            return False, f'Nieobsługiwany typ bazy danych: {db_type}'
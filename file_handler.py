#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
from ftplib import FTP
import paramiko
import tarfile

class FileHandler:
    def __init__(self, config):
        self.config = config

    def create_backup_name(self, backup_type):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'backup_{backup_type}_{timestamp}'

    def compress_directory(self, source_path, backup_name):
        archive_path = f'{backup_name}.tar.gz'
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
        return archive_path

    def backup_local(self, source_path, destination_path):
        try:
            backup_name = self.create_backup_name('local')
            archive_path = self.compress_directory(source_path, backup_name)
            
            # Utwórz katalog docelowy, jeśli nie istnieje
            os.makedirs(destination_path, exist_ok=True)
            
            # Przenieś archiwum do katalogu docelowego
            final_path = os.path.join(destination_path, os.path.basename(archive_path))
            shutil.move(archive_path, final_path)
            
            # Usuń stare kopie zapasowe, jeśli przekroczono limit
            self.cleanup_old_backups(destination_path)
            
            return True, 'Kopia zapasowa została utworzona pomyślnie'
        except Exception as e:
            return False, f'Błąd podczas tworzenia kopii zapasowej: {str(e)}'

    def backup_ftp(self, source_path):
        archive_path = ''
        try:
            backup_name = self.create_backup_name('ftp')
            archive_path = self.compress_directory(source_path, backup_name)
            
            # Połącz z serwerem FTP
            ftp = FTP()
            ftp.connect(
                host=self.config['ftp_settings']['host'],
                port=self.config['ftp_settings']['port']
            )
            ftp.login(
                user=self.config['ftp_settings']['username'],
                passwd=self.config['ftp_settings']['password']
            )
            
            # Wyślij plik
            with open(archive_path, 'rb') as f:
                ftp.storbinary(f'STOR {os.path.basename(archive_path)}', f)
            
            # Usuń lokalny plik archiwum
            os.remove(archive_path)
            
            ftp.quit()
            return True, 'Kopia zapasowa FTP została utworzona pomyślnie'
        except Exception as e:
            if os.path.exists(archive_path):
                os.remove(archive_path)
            return False, f'Błąd podczas tworzenia kopii zapasowej FTP: {str(e)}'

    def backup_ssh(self, source_path):
        archive_path = ''
        try:
            backup_name = self.create_backup_name('ssh')
            archive_path = self.compress_directory(source_path, backup_name)
            
            # Utwórz klienta SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Połącz z serwerem SSH
            ssh.connect(
                hostname=self.config['ssh_settings']['host'],
                port=self.config['ssh_settings']['port'],
                username=self.config['ssh_settings']['username'],
                key_filename=self.config['ssh_settings']['key_path']
            )
            
            # Utwórz SFTP session
            sftp = ssh.open_sftp()
            
            # Wyślij plik
            sftp.put(archive_path, os.path.basename(archive_path))
            
            # Zamknij połączenia
            sftp.close()
            ssh.close()
            
            # Usuń lokalny plik archiwum
            os.remove(archive_path)
            
            return True, 'Kopia zapasowa SSH została utworzona pomyślnie'
        except Exception as e:
            if os.path.exists(archive_path):
                os.remove(archive_path)
            return False, f'Błąd podczas tworzenia kopii zapasowej SSH: {str(e)}'

    def restore_local(self, backup_path, destination_path):
        try:
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path=destination_path)
            return True, 'Kopia zapasowa została przywrócona pomyślnie'
        except Exception as e:
            return False, f'Błąd podczas przywracania kopii zapasowej: {str(e)}'

    def restore_ftp(self, backup_name, destination_path):
        try:
            # Połącz z serwerem FTP
            ftp = FTP()
            ftp.connect(
                host=self.config['ftp_settings']['host'],
                port=self.config['ftp_settings']['port']
            )
            ftp.login(
                user=self.config['ftp_settings']['username'],
                passwd=self.config['ftp_settings']['password']
            )
            
            # Pobierz plik
            local_path = os.path.join('/tmp', backup_name)
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f'RETR {backup_name}', f.write)
            
            # Rozpakuj archiwum
            success, message = self.restore_local(local_path, destination_path)
            
            # Usuń tymczasowy plik
            os.remove(local_path)
            
            ftp.quit()
            return success, message
        except Exception as e:
            return False, f'Błąd podczas przywracania kopii zapasowej FTP: {str(e)}'

    def restore_ssh(self, backup_name, destination_path):
        try:
            # Utwórz klienta SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Połącz z serwerem SSH
            ssh.connect(
                hostname=self.config['ssh_settings']['host'],
                port=self.config['ssh_settings']['port'],
                username=self.config['ssh_settings']['username'],
                key_filename=self.config['ssh_settings']['key_path']
            )
            
            # Utwórz SFTP session
            sftp = ssh.open_sftp()
            
            # Pobierz plik
            local_path = os.path.join('/tmp', backup_name)
            sftp.get(backup_name, local_path)
            
            # Rozpakuj archiwum
            success, message = self.restore_local(local_path, destination_path)
            
            # Usuń tymczasowy plik
            os.remove(local_path)
            
            # Zamknij połączenia
            sftp.close()
            ssh.close()
            
            return success, message
        except Exception as e:
            return False, f'Błąd podczas przywracania kopii zapasowej SSH: {str(e)}'

    def cleanup_old_backups(self, backup_dir):
        try:
            # Pobierz listę plików kopii zapasowych
            backups = [f for f in os.listdir(backup_dir) if f.startswith('backup_') and f.endswith('.tar.gz')]
            backups.sort(reverse=True)  # Sortuj od najnowszych do najstarszych
            
            # Usuń nadmiarowe kopie
            max_backups = self.config['backup_settings']['max_backups']
            if len(backups) > max_backups:
                for backup in backups[max_backups:]:
                    os.remove(os.path.join(backup_dir, backup))
        except Exception as e:
            print(f'Błąd podczas czyszczenia starych kopii zapasowych: {str(e)}')

    def list_backups(self, backup_type='local'):
        try:
            if backup_type == 'local':
                backup_dir = self.config['backup_locations']['destination']
                if not os.path.exists(backup_dir):
                    return []
                return [f for f in os.listdir(backup_dir) if f.startswith('backup_') and f.endswith('.tar.gz')]
            elif backup_type == 'ftp':
                ftp = FTP()
                ftp.connect(
                    host=self.config['ftp_settings']['host'],
                    port=self.config['ftp_settings']['port']
                )
                ftp.login(
                    user=self.config['ftp_settings']['username'],
                    passwd=self.config['ftp_settings']['password']
                )
                backups = [f for f in ftp.nlst() if f.startswith('backup_') and f.endswith('.tar.gz')]
                ftp.quit()
                return backups
            elif backup_type == 'ssh':
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=self.config['ssh_settings']['host'],
                    port=self.config['ssh_settings']['port'],
                    username=self.config['ssh_settings']['username'],
                    key_filename=self.config['ssh_settings']['key_path']
                )
                sftp = ssh.open_sftp()
                backups = [f for f in sftp.listdir() if f.startswith('backup_') and f.endswith('.tar.gz')]
                sftp.close()
                ssh.close()
                return backups
            return []
        except Exception as e:
            print(f'Błąd podczas listowania kopii zapasowych: {str(e)}')
            return []
"""
Gestión de subida de archivos por FTP/SFTP para CTPFA CMS
"""

import ftplib
import io
import os
import paramiko


def build_web_url(server_config, filename=""):
    """Construye la URL web a partir de la configuración del servidor FTP.
    
    - Quita prefijos como 'ftp.' del host
    - Limpia la ruta remota quitando /public_html, /var/www/html, /htdocs, /www
    """
    host = server_config.get('host', '')
    remote_path = server_config.get('remote_path', '')
    
    # Quitar prefijo ftp. del host
    if host.startswith('ftp.'):
        host = host[4:]
    
    # Limpiar la ruta remota de directorios típicos de hosting
    path_prefixes = [
        '/public_html',
        '/var/www/html',
        '/htdocs',
        '/www',
        '/httpdocs',
        '/web',
    ]
    
    web_path = remote_path
    for prefix in path_prefixes:
        if web_path.startswith(prefix):
            web_path = web_path[len(prefix):]
            break
    
    # Asegurar que la ruta empieza con /
    if web_path and not web_path.startswith('/'):
        web_path = '/' + web_path
    
    # Construir URL
    if filename:
        url = f"http://{host}{web_path}/{filename}"
    else:
        url = f"http://{host}{web_path}/"
    
    # Limpiar dobles barras
    url = url.replace('//', '/').replace('http:/', 'http://')
    
    return url


class FileUploader:
    """Gestiona la subida de archivos por FTP o SFTP"""
    
    def __init__(self, config):
        self.config = config
        server_config = config.get("server")
        self.protocol = server_config.get("protocol", "ftp").lower() if isinstance(server_config, dict) else "ftp"
        # SFTP
        self.ssh_client: paramiko.SSHClient | None = None
        self.sftp: paramiko.SFTPClient | None = None
        # FTP
        self.ftp: ftplib.FTP | None = None
    
    def connect(self):
        """Establece conexión según el protocolo configurado"""
        if self.protocol == "sftp":
            self._connect_sftp()
        else:
            self._connect_ftp()
    
    def _connect_ftp(self):
        """Establece conexión FTP"""
        server = self.config.get("server")
        
        self.ftp = ftplib.FTP()
        self.ftp.set_debuglevel(0)
        # Timeout de 30 segundos
        self.ftp.connect(server["host"], server["port"], timeout=30)
        self.ftp.login(server["username"], server.get("password", ""))
        # Intentar modo pasivo (más compatible con firewalls)
        self.ftp.set_pasv(True)
        # Establecer modo binario
        self.ftp.voidcmd('TYPE I')
    
    def _connect_sftp(self):
        """Establece conexión SFTP"""
        server = self.config.get("server")
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            "hostname": server["host"],
            "port": server["port"],
            "username": server["username"]
        }
        
        # Prioridad: 1. Clave SSH especificada, 2. Contraseña, 3. Claves por defecto del sistema
        key_file = server.get("key_file", "").strip()
        password = server.get("password", "").strip()
        
        if key_file:
            key_file = os.path.expanduser(key_file)
            connect_kwargs["key_filename"] = key_file
        elif password:
            connect_kwargs["password"] = password
        else:
            connect_kwargs["look_for_keys"] = True
            connect_kwargs["allow_agent"] = True
        
        self.ssh_client.connect(**connect_kwargs)
        self.sftp = self.ssh_client.open_sftp()
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.protocol == "sftp":
            if self.sftp:
                self.sftp.close()
            if self.ssh_client:
                self.ssh_client.close()
        else:
            if self.ftp:
                try:
                    self.ftp.quit()
                except:
                    self.ftp.close()
    
    def upload_file(self, local_path, remote_path):
        """Sube un archivo"""
        if self.protocol == "sftp":
            if self.sftp is None:
                raise ConnectionError("No hay conexión SFTP activa")
            self.sftp.put(str(local_path), remote_path)
        else:
            if self.ftp is None:
                raise ConnectionError("No hay conexión FTP activa")
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f)
    
    def upload_string(self, content, remote_path):
        """Sube contenido string como archivo"""
        if self.protocol == "sftp":
            if self.sftp is None:
                raise ConnectionError("No hay conexión SFTP activa")
            with self.sftp.file(remote_path, 'w') as f:
                f.write(content)
        else:
            if self.ftp is None:
                raise ConnectionError("No hay conexión FTP activa")
            # Asegurarse de que el directorio existe
            self._ftp_ensure_dir(os.path.dirname(remote_path))
            # Convertir string a bytes y subirlo
            content_bytes = content.encode('utf-8')
            self.ftp.storbinary(f'STOR {remote_path}', io.BytesIO(content_bytes))
    
    def _ftp_ensure_dir(self, remote_dir):
        """Asegura que el directorio remoto existe (FTP)"""
        if not remote_dir or self.ftp is None:
            return
        try:
            self.ftp.cwd(remote_dir)
        except ftplib.error_perm:
            # Crear directorio recursivamente
            dirs = remote_dir.split('/')
            current = ''
            for d in dirs:
                if d:
                    current += '/' + d
                    try:
                        self.ftp.cwd(current)
                    except ftplib.error_perm:
                        try:
                            self.ftp.mkd(current)
                        except ftplib.error_perm:
                            pass  # Ya existe o no se puede crear
    
    def file_exists(self, remote_path):
        """Verifica si existe un archivo remoto"""
        if self.protocol == "sftp":
            if self.sftp is None:
                raise ConnectionError("No hay conexión SFTP activa")
            try:
                self.sftp.stat(remote_path)
                return True
            except IOError:
                return False
        else:
            if self.ftp is None:
                raise ConnectionError("No hay conexión FTP activa")
            try:
                self.ftp.size(remote_path)
                return True
            except:
                return False
    
    def delete_file(self, remote_path):
        """Elimina un archivo remoto"""
        if self.protocol == "sftp":
            if self.sftp is None:
                raise ConnectionError("No hay conexión SFTP activa")
            self.sftp.remove(remote_path)
        else:
            if self.ftp is None:
                raise ConnectionError("No hay conexión FTP activa")
            self.ftp.delete(remote_path)


# Alias para compatibilidad
SFTPUploader = FileUploader

import os
import shutil
import datetime
import socket

def checkDir(directory):
    """Check if directory exists"""
    return os.path.exists(directory)

def mkdirSamba(directory):
    """Create directory (local implementation for demo)"""
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory created: {directory}")
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False

def putSamba(local_file, remote_path):
    """Copy file to remote location (local implementation for demo)"""
    try:
        # Create remote directory if it doesn't exist
        remote_dir = os.path.dirname(remote_path)
        if remote_dir and not os.path.exists(remote_dir):
            os.makedirs(remote_dir, exist_ok=True)
        
        # Copy file
        shutil.copy2(local_file, remote_path)
        print(f"File copied from {local_file} to {remote_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def getSamba(remote_file, local_path):
    """Copy file from remote location (local implementation for demo)"""
    try:
        # Create local directory if it doesn't exist
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        
        # Copy file
        shutil.copy2(remote_file, local_path)
        print(f"File copied from {remote_file} to {local_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def deleteSamba(file_path):
    """Delete file from remote location (local implementation for demo)"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File deleted: {file_path}")
            return True
        else:
            print(f"File not found: {file_path}")
            return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False

def listSamba(directory):
    """List files in remote directory (local implementation for demo)"""
    try:
        if os.path.exists(directory):
            files = os.listdir(directory)
            print(f"Files in {directory}: {files}")
            return files
        else:
            print(f"Directory not found: {directory}")
            return []
    except Exception as e:
        print(f"Error listing directory {directory}: {e}")
        return []

def get_file_info(file_path):
    """Get file information"""
    try:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.datetime.fromtimestamp(stat.st_ctime)
            }
        else:
            return None
    except Exception as e:
        print(f"Error getting file info for {file_path}: {e}")
        return None

def cleanup_directory(directory, days_old=7):
    """Clean up files older than specified days"""
    try:
        if not os.path.exists(directory):
            return 0
        
        current_time = datetime.datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                file_age = current_time - datetime.datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_age.days > days_old:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted old file: {file_path}")
        
        return deleted_count
    except Exception as e:
        print(f"Error cleaning up directory {directory}: {e}")
        return 0

def get_storage_usage(directory):
    """Get storage usage statistics"""
    try:
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    continue
        
        return {
            'total_size': total_size,
            'file_count': file_count,
            'human_readable_size': format_bytes(total_size)
        }
    except Exception as e:
        print(f"Error getting storage usage for {directory}: {e}")
        return {'total_size': 0, 'file_count': 0, 'human_readable_size': '0 B'}

def format_bytes(bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"

def create_backup(source_dir, backup_dir):
    """Create backup of source directory"""
    try:
        if not os.path.exists(source_dir):
            print(f"Source directory not found: {source_dir}")
            return False
        
        # Create backup directory with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        shutil.copytree(source_dir, backup_path)
        print(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
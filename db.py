import sqlite3
import datetime
import os

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('ppe_detection.db')
    cursor = conn.cursor()
    
    # Create table for undetected items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS undetected_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            hostname TEXT NOT NULL,
            dateandtime DATETIME NOT NULL,
            detectedobject INTEGER NOT NULL,
            object_name TEXT
        )
    ''')
    
    # Create table for detection statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_detections INTEGER DEFAULT 0,
            missing_ppe_count INTEGER DEFAULT 0,
            compliance_rate REAL DEFAULT 0.0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def connect():
    """Create a connection to the database"""
    return sqlite3.connect('ppe_detection.db', check_same_thread=False)

def upload_metadata(filename, filepath, hostname, datetime_obj, detectedobject):
    """Upload detection metadata to database"""
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Map object numbers to names (for demo purposes)
        object_names = {
            1: 'person',
            2: 'bicycle', 
            3: 'car',
            4: 'motorcycle',
            5: 'airplane',
            6: 'bus',
            7: 'train',
            8: 'truck',
            9: 'boat',
            10: 'traffic light'
        }
        
        object_name = object_names.get(detectedobject, f'object_{detectedobject}')
        
        cursor.execute('''
            INSERT INTO undetected_items (filename, filepath, hostname, dateandtime, detectedobject, object_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, filepath, hostname, datetime_obj, detectedobject, object_name))
        
        conn.commit()
        conn.close()
        print(f"Metadata uploaded for {filename}: missing {object_name}")
        return True
    except Exception as e:
        print(f"Error uploading metadata: {e}")
        return False

def get_all_detections():
    """Get all detection records grouped by object type"""
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Get detections for different PPE items
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='person' ORDER BY dateandtime DESC;")
        data1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='bicycle' ORDER BY dateandtime DESC;")
        data2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='car' ORDER BY dateandtime DESC;")
        data3 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='motorcycle' ORDER BY dateandtime DESC;")
        data4 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='airplane' ORDER BY dateandtime DESC;")
        data5 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='bus' ORDER BY dateandtime DESC;")
        data6 = cursor.fetchall()
        
        conn.close()
        
        return {
            'person': data1,
            'bicycle': data2,
            'car': data3,
            'motorcycle': data4,
            'airplane': data5,
            'bus': data6
        }
    except Exception as e:
        print(f"Error getting detections: {e}")
        return {}

def get_recent_detections(limit=15):
    """Get recent detection records grouped by object type"""
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Get recent detections for different PPE items
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='person' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data1 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='bicycle' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data2 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='car' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data3 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='motorcycle' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data4 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='airplane' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data5 = cursor.fetchall()
        
        cursor.execute("SELECT * FROM undetected_items WHERE object_name='bus' ORDER BY dateandtime DESC LIMIT ?;", (limit,))
        data6 = cursor.fetchall()
        
        conn.close()
        
        return {
            'person': data1,
            'bicycle': data2,
            'car': data3,
            'motorcycle': data4,
            'airplane': data5,
            'bus': data6
        }
    except Exception as e:
        print(f"Error getting recent detections: {e}")
        return {}

def get_detection_stats():
    """Get detection statistics"""
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Get today's stats
        today = datetime.date.today()
        cursor.execute('SELECT * FROM detection_stats WHERE date = ?', (today,))
        stats = cursor.fetchone()
        
        if not stats:
            # Create new stats for today
            cursor.execute('''
                INSERT INTO detection_stats (date, total_detections, missing_ppe_count, compliance_rate)
                VALUES (?, 0, 0, 100.0)
            ''', (today,))
            conn.commit()
            stats = (None, today, 0, 0, 100.0)
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting detection stats: {e}")
        return None

def update_detection_stats(total_detections, missing_ppe_count):
    """Update detection statistics"""
    try:
        conn = connect()
        cursor = conn.cursor()
        
        today = datetime.date.today()
        compliance_rate = ((total_detections - missing_ppe_count) / total_detections * 100) if total_detections > 0 else 100
        
        cursor.execute('''
            INSERT OR REPLACE INTO detection_stats (date, total_detections, missing_ppe_count, compliance_rate)
            VALUES (?, ?, ?, ?)
        ''', (today, total_detections, missing_ppe_count, compliance_rate))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating detection stats: {e}")
        return False
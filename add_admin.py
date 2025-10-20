#!/usr/bin/env python3
"""
Admin Kullanıcısı Ekleme Scripti
Kocaeli Üniversitesi Sınav Takvimi Sistemi
"""

import sys
import os
import bcrypt
from datetime import datetime

# Proje root dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from models.user_model import UserModel
from config import DATABASE

def create_admin_user():
    """Admin kullanıcısı oluştur"""
    
    print("Admin Kullanıcısı Oluşturuluyor...")
    print("=" * 50)
    
    # Admin bilgileri
    admin_data = {
        'email': 'admin@kocaeli.edu.tr',
        'password': 'admin123',
        'ad_soyad': 'Sistem Yöneticisi',
        'role': 'Admin',
        'bolum_id': None,  # Admin için bölüm yok
        'aktif': True
    }
    
    try:
        # Veritabanı bağlantısını başlat
        print("Veritabanı bağlantısı başlatılıyor...")
        db.initialize(DATABASE)
        print("Veritabanı bağlantısı başarılı!")
        
        # Mevcut admin kontrolü
        existing_admin = UserModel.find_by_email(admin_data['email'])
        
        if existing_admin:
            print(f"Admin kullanıcısı zaten mevcut: {admin_data['email']}")
            print("Şifre güncelleniyor...")
            
            # Şifreyi güncelle
            new_hash = UserModel.hash_password(admin_data['password'])
            UserModel.update_password(existing_admin['user_id'], new_hash)
            
            print("Admin şifresi güncellendi!")
            
        else:
            print("Yeni admin kullanıcısı oluşturuluyor...")
            
            # Şifreyi hash'le
            password_hash = UserModel.hash_password(admin_data['password'])
            
            # Admin kullanıcısını ekle
            query = """
                INSERT INTO users (
                    email, password_hash, ad_soyad, role, 
                    bolum_id, aktif, son_giris
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING user_id
            """
            
            now = datetime.now()
            result = db.execute_query(
                query,
                (
                    admin_data['email'],
                    password_hash,
                    admin_data['ad_soyad'],
                    admin_data['role'],
                    admin_data['bolum_id'],
                    admin_data['aktif'],
                    now
                ),
                fetch_one=True
            )
            
            if result:
                print(f"Admin kullanıcısı başarıyla oluşturuldu!")
                print(f"   E-posta: {admin_data['email']}")
                print(f"   Şifre: {admin_data['password']}")
                print(f"   Ad Soyad: {admin_data['ad_soyad']}")
                print(f"   Kullanıcı ID: {result['user_id']}")
        
        print("\n" + "=" * 50)
        print("Admin kullanıcısı hazır!")
        print("\nGiriş Bilgileri:")
        print(f"   E-posta: {admin_data['email']}")
        print(f"   Şifre: {admin_data['password']}")
        print("\nGüvenlik için şifreyi değiştirmeyi unutmayın!")
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        print("\nOlası çözümler:")
        print("   1. Veritabanı bağlantı ayarlarını kontrol edin")
        print("   2. PostgreSQL servisinin çalıştığından emin olun")
        print("   3. config.py dosyasındaki DATABASE ayarlarını kontrol edin")
        return False
    
    return True

def create_demo_users():
    """Demo kullanıcıları oluştur"""
    
    print("\nDemo Kullanıcıları Oluşturuluyor...")
    print("=" * 50)
    
    demo_users = [
        {
            'email': 'koordinator@kocaeli.edu.tr',
            'password': 'koordinator123',
            'ad_soyad': 'Test Koordinatör',
            'role': 'Koordinator',
            'bolum_id': 1,  # Bilgisayar Mühendisliği
            'aktif': True
        },
        {
            'email': 'ogretmen@kocaeli.edu.tr',
            'password': 'ogretmen123',
            'ad_soyad': 'Test Öğretmen',
            'role': 'Ogretmen',
            'bolum_id': 1,
            'aktif': True
        }
    ]
    
    for user_data in demo_users:
        try:
            # Mevcut kullanıcı kontrolü
            existing_user = UserModel.find_by_email(user_data['email'])
            
            if existing_user:
                print(f"Kullanıcı zaten mevcut: {user_data['email']}")
                continue
            
            # Şifreyi hash'le
            password_hash = UserModel.hash_password(user_data['password'])
            
            # Kullanıcıyı ekle
            query = """
                INSERT INTO users (
                    email, password_hash, ad_soyad, role, 
                    bolum_id, aktif, son_giris
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING user_id
            """
            
            now = datetime.now()
            result = db.execute_query(
                query,
                (
                    user_data['email'],
                    password_hash,
                    user_data['ad_soyad'],
                    user_data['role'],
                    user_data['bolum_id'],
                    user_data['aktif'],
                    now
                ),
                fetch_one=True
            )
            
            if result:
                print(f"{user_data['role']} kullanıcısı oluşturuldu: {user_data['email']}")
            
        except Exception as e:
            print(f"{user_data['email']} için hata: {str(e)}")

if __name__ == "__main__":
    print("Kocaeli Üniversitesi Sınav Takvimi Sistemi")
    print("Admin Kullanıcısı Oluşturma Scripti")
    print("=" * 60)
    
    # Admin kullanıcısı oluştur
    success = create_admin_user()
    
    if success:
        # Demo kullanıcıları da oluştur
        create_demo_users()
        
        print("\nTüm kullanıcılar hazır!")
        print("Sistemi başlatmak için: python main.py")
    
    print("\n" + "=" * 60)

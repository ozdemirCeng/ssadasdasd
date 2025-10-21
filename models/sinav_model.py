"""
S1nav Model
S1nav program1 CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, time, timedelta
import logging

logger = logging.getLogger(__name__)


class SinavModel:
    """S1nav program1 veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_program(self, bolum_id: int, program_adi: str, sinav_tipi: str,
                       baslangic_tarihi: date, bitis_tarihi: date,
                       varsayilan_sinav_suresi: int = 75,
                       bekleme_suresi: int = 15) -> Optional[int]:
        """Yeni s1nav program1 olu_tur"""
        try:
            query = """
                INSERT INTO sinav_programi
                (bolum_id, program_adi, sinav_tipi, baslangic_tarihi, bitis_tarihi,
                 varsayilan_sinav_suresi, bekleme_suresi)
                VALUES (%s, %s, %s::sinav_tipi_enum, %s, %s, %s, %s)
                RETURNING program_id
            """

            cursor = self.db.execute_query(
                query,
                (bolum_id, program_adi, sinav_tipi, baslangic_tarihi, bitis_tarihi,
                 varsayilan_sinav_suresi, bekleme_suresi)
            )

            if cursor:
                row = cursor.fetchone()
                if row:
                    program_id = row[0]
                    self.db.commit()
                    logger.info(f"Yeni s1nav program1 olu_turuldu: {program_adi} (ID: {program_id})")
                    return program_id

            return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"S1nav program1 olu_turulurken hata: {e}")
            return None

    def create_sinav(self, program_id: int, ders_id: int, tarih: date,
                     baslangic_saati: time, bitis_saati: time) -> Optional[int]:
        """Yeni s1nav olu_tur"""
        try:
            query = """
                INSERT INTO sinavlar
                (program_id, ders_id, tarih, baslangic_saati, bitis_saati)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING sinav_id
            """

            cursor = self.db.execute_query(
                query,
                (program_id, ders_id, tarih, baslangic_saati, bitis_saati)
            )

            if cursor:
                row = cursor.fetchone()
                if row:
                    sinav_id = row[0]
                    self.db.commit()
                    logger.info(f"Yeni s1nav olu_turuldu (ID: {sinav_id})")
                    return sinav_id

            return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"S1nav olu_turulurken hata: {e}")
            return None

    def assign_derslik_to_sinav(self, sinav_id: int, derslik_id: int) -> bool:
        """S1nava derslik ata"""
        try:
            query = """
                INSERT INTO sinav_derslikleri (sinav_id, derslik_id)
                VALUES (%s, %s)
                ON CONFLICT (sinav_id, derslik_id) DO NOTHING
            """

            cursor = self.db.execute_query(query, (sinav_id, derslik_id))

            if cursor:
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Derslik atamas1 hatas1: {e}")
            return False

    def get_program_by_id(self, program_id: int) -> Optional[Dict]:
        """Program bilgilerini getir"""
        try:
            query = """
                SELECT p.program_id, p.bolum_id, b.bolum_adi, p.program_adi,
                       p.sinav_tipi, p.baslangic_tarihi, p.bitis_tarihi,
                       p.varsayilan_sinav_suresi, p.bekleme_suresi
                FROM sinav_programi p
                JOIN bolumler b ON p.bolum_id = b.bolum_id
                WHERE p.program_id = %s
            """

            cursor = self.db.execute_query(query, (program_id,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Program getirilirken hata: {e}")
            return None

    def get_sinavlar_by_program(self, program_id: int) -> List[Dict]:
        """Programa ait s1navlar1 getir"""
        try:
            query = """
                SELECT s.sinav_id, s.ders_id, d.ders_kodu, d.ders_adi,
                       d.ogretim_elemani, s.tarih, s.baslangic_saati,
                       s.bitis_saati, s.ogrenci_sayisi
                FROM sinavlar s
                JOIN dersler d ON s.ders_id = d.ders_id
                WHERE s.program_id = %s
                ORDER BY s.tarih, s.baslangic_saati
            """

            cursor = self.db.execute_query(query, (program_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"S1navlar getirilirken hata: {e}")
            return []

    def get_sinav_with_derslikler(self, sinav_id: int) -> Optional[Dict]:
        """S1nav ve derslik bilgilerini getir"""
        try:
            # �nce s1nav bilgilerini al
            query_sinav = """
                SELECT s.sinav_id, s.program_id, s.ders_id, d.ders_kodu,
                       d.ders_adi, d.ogretim_elemani, s.tarih,
                       s.baslangic_saati, s.bitis_saati, s.ogrenci_sayisi
                FROM sinavlar s
                JOIN dersler d ON s.ders_id = d.ders_id
                WHERE s.sinav_id = %s
            """

            cursor = self.db.execute_query(query_sinav, (sinav_id,))

            if not cursor:
                return None

            row = cursor.fetchone()
            if not row:
                return None

            columns = [desc[0] for desc in cursor.description]
            sinav = dict(zip(columns, row))

            # S1nava atanan derslikleri al
            query_derslikler = """
                SELECT dr.derslik_id, dr.derslik_kodu, dr.derslik_adi,
                       dr.kapasite, sd.yerlesim_sayisi
                FROM sinav_derslikleri sd
                JOIN derslikler dr ON sd.derslik_id = dr.derslik_id
                WHERE sd.sinav_id = %s
            """

            cursor = self.db.execute_query(query_derslikler, (sinav_id,))

            derslikler = []
            if cursor:
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    derslikler.append(dict(zip(columns, row)))

            sinav['derslikler'] = derslikler

            return sinav

        except Exception as e:
            logger.error(f"S1nav detaylar1 getirilirken hata: {e}")
            return None

    def check_ogrenci_cakisma(self, program_id: int, ogrenci_no: str,
                              tarih: date, baslangic_saati: time,
                              bitis_saati: time) -> bool:
        """�rencinin ba_ka bir s1nav1 ile �ak1_ma var m1 kontrol et"""
        try:
            query = """
                SELECT COUNT(*)
                FROM sinavlar s
                JOIN ders_kayitlari dk ON s.ders_id = dk.ders_id
                WHERE s.program_id = %s
                  AND dk.ogrenci_no = %s
                  AND s.tarih = %s
                  AND (
                      (s.baslangic_saati <= %s AND s.bitis_saati > %s) OR
                      (s.baslangic_saati < %s AND s.bitis_saati >= %s) OR
                      (s.baslangic_saati >= %s AND s.bitis_saati <= %s)
                  )
            """

            cursor = self.db.execute_query(
                query,
                (program_id, ogrenci_no, tarih, baslangic_saati,
                 baslangic_saati, bitis_saati, bitis_saati,
                 baslangic_saati, bitis_saati)
            )

            if cursor:
                count = cursor.fetchone()[0]
                return count > 0

            return False

        except Exception as e:
            logger.error(f"�ak1_ma kontrol� hatas1: {e}")
            return True  # Hata durumunda �ak1_ma var say

    def get_programs_by_bolum(self, bolum_id: int) -> List[Dict]:
        """B�l�me ait programlar1 getir"""
        try:
            query = """
                SELECT program_id, program_adi, sinav_tipi,
                       baslangic_tarihi, bitis_tarihi
                FROM sinav_programi
                WHERE bolum_id = %s
                ORDER BY baslangic_tarihi DESC
            """

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Programlar getirilirken hata: {e}")
            return []

    def delete_program(self, program_id: int) -> bool:
        """Program1 sil (cascade ile t�m s1navlar da silinir)"""
        try:
            query = "DELETE FROM sinav_programi WHERE program_id = %s"

            cursor = self.db.execute_query(query, (program_id,))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"Program silindi (ID: {program_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Program silinirken hata: {e}")
            return False

    def update_ogrenci_sayisi(self, sinav_id: int) -> bool:
        """S1nav �renci say1s1n1 g�ncelle"""
        try:
            query = """
                UPDATE sinavlar
                SET ogrenci_sayisi = (
                    SELECT COUNT(DISTINCT dk.ogrenci_no)
                    FROM ders_kayitlari dk
                    JOIN ogrenciler o ON dk.ogrenci_no = o.ogrenci_no
                    WHERE dk.ders_id = sinavlar.ders_id
                      AND o.aktif = TRUE
                )
                WHERE sinav_id = %s
            """

            cursor = self.db.execute_query(query, (sinav_id,))

            if cursor:
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"�renci say1s1 g�ncellenirken hata: {e}")
            return False

"""
�renci Model
�renci CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OgrenciModel:
    """�renci veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: Database balant1 nesnesi
        """
        self.db = db_connection

    def create_ogrenci(self, ogrenci_no: str, bolum_id: int,
                      ad_soyad: str, sinif: int) -> bool:
        """
        Yeni �renci olu_tur

        Args:
            ogrenci_no: �renci numaras1
            bolum_id: B�l�m ID
            ad_soyad: Ad soyad
            sinif: S1n1f (1-5)

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            query = """
                INSERT INTO ogrenciler (ogrenci_no, bolum_id, ad_soyad, sinif)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ogrenci_no) DO UPDATE
                SET bolum_id = EXCLUDED.bolum_id,
                    ad_soyad = EXCLUDED.ad_soyad,
                    sinif = EXCLUDED.sinif,
                    aktif = TRUE
            """

            cursor = self.db.execute_query(
                query,
                (ogrenci_no, bolum_id, ad_soyad, sinif)
            )

            if cursor:
                self.db.commit()
                logger.info(f"�renci olu_turuldu/g�ncellendi: {ogrenci_no}")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"�renci olu_turulurken hata: {e}")
            return False

    def create_ogrenci_batch(self, ogrenciler: List[Dict]) -> Tuple[int, int]:
        """
        Toplu �renci ekleme (Excel'den gelen veriler i�in)

        Args:
            ogrenciler: �renci listesi

        Returns:
            (ba_ar1l1_say1s1, hatal1_say1s1)
        """
        basarili = 0
        hatali = 0

        for ogrenci in ogrenciler:
            try:
                result = self.create_ogrenci(
                    ogrenci['ogrenci_no'],
                    ogrenci['bolum_id'],
                    ogrenci['ad_soyad'],
                    ogrenci.get('sinif', 1)
                )

                if result:
                    basarili += 1
                else:
                    hatali += 1

            except Exception as e:
                logger.error(f"Toplu �renci ekleme hatas1: {e}")
                hatali += 1

        return basarili, hatali

    def add_ders_kayit(self, ogrenci_no: str, ders_id: int) -> bool:
        """
        �renciye ders kayd1 ekle

        Args:
            ogrenci_no: �renci numaras1
            ders_id: Ders ID

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            query = """
                INSERT INTO ders_kayitlari (ogrenci_no, ders_id)
                VALUES (%s, %s)
                ON CONFLICT (ogrenci_no, ders_id) DO NOTHING
            """

            cursor = self.db.execute_query(query, (ogrenci_no, ders_id))

            if cursor:
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ders kayd1 eklenirken hata: {e}")
            return False

    def add_ders_kayit_by_code(self, ogrenci_no: str, ders_kodu: str) -> bool:
        """
        �renciye ders kayd1 ekle (ders kodu ile)

        Args:
            ogrenci_no: �renci numaras1
            ders_kodu: Ders kodu

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            query = """
                INSERT INTO ders_kayitlari (ogrenci_no, ders_id)
                SELECT %s, ders_id
                FROM dersler
                WHERE ders_kodu = %s
                ON CONFLICT (ogrenci_no, ders_id) DO NOTHING
            """

            cursor = self.db.execute_query(query, (ogrenci_no, ders_kodu))

            if cursor:
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ders kayd1 eklenirken hata: {e}")
            return False

    def get_ogrenciler_by_bolum(self, bolum_id: int, only_active=True) -> List[Dict]:
        """
        B�l�me ait �rencileri getir

        Args:
            bolum_id: B�l�m ID
            only_active: Sadece aktif �renciler

        Returns:
            �renci listesi
        """
        try:
            query = """
                SELECT ogrenci_no, bolum_id, ad_soyad, sinif, aktif
                FROM ogrenciler
                WHERE bolum_id = %s
            """

            if only_active:
                query += " AND aktif = TRUE"

            query += " ORDER BY sinif, ad_soyad"

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"�renciler getirilirken hata: {e}")
            return []

    def get_ogrenci_by_no(self, ogrenci_no: str) -> Optional[Dict]:
        """
        Numaraya g�re �renci getir

        Args:
            ogrenci_no: �renci numaras1

        Returns:
            �renci bilgisi veya None
        """
        try:
            query = """
                SELECT o.ogrenci_no, o.bolum_id, b.bolum_adi, o.ad_soyad,
                       o.sinif, o.aktif
                FROM ogrenciler o
                JOIN bolumler b ON o.bolum_id = b.bolum_id
                WHERE o.ogrenci_no = %s
            """

            cursor = self.db.execute_query(query, (ogrenci_no,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"�renci getirilirken hata (No: {ogrenci_no}): {e}")
            return None

    def get_ogrenci_with_dersler(self, ogrenci_no: str) -> Optional[Dict]:
        """
        �renci bilgilerini ve ald11 dersleri getir

        Args:
            ogrenci_no: �renci numaras1

        Returns:
            �renci bilgisi ve ders listesi
        """
        try:
            # �nce �renci bilgilerini al
            ogrenci = self.get_ogrenci_by_no(ogrenci_no)

            if not ogrenci:
                return None

            # �rencinin ald11 dersleri al
            query = """
                SELECT d.ders_id, d.ders_kodu, d.ders_adi, d.ogretim_elemani,
                       d.sinif, d.ders_yapisi
                FROM dersler d
                JOIN ders_kayitlari dk ON d.ders_id = dk.ders_id
                WHERE dk.ogrenci_no = %s AND d.aktif = TRUE
                ORDER BY d.ders_kodu
            """

            cursor = self.db.execute_query(query, (ogrenci_no,))

            dersler = []
            if cursor:
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    dersler.append(dict(zip(columns, row)))

            ogrenci['dersler'] = dersler
            ogrenci['ders_sayisi'] = len(dersler)

            return ogrenci

        except Exception as e:
            logger.error(f"�renci ve dersler getirilirken hata: {e}")
            return None

    def search_ogrenci(self, search_term: str, bolum_id: int = None) -> List[Dict]:
        """
        �renci ara (numara veya ada g�re)

        Args:
            search_term: Arama terimi
            bolum_id: B�l�m ID (opsiyonel)

        Returns:
            �renci listesi
        """
        try:
            query = """
                SELECT o.ogrenci_no, o.bolum_id, b.bolum_adi, o.ad_soyad,
                       o.sinif, o.aktif
                FROM ogrenciler o
                JOIN bolumler b ON o.bolum_id = b.bolum_id
                WHERE o.aktif = TRUE
                  AND (o.ogrenci_no ILIKE %s OR o.ad_soyad ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%"]

            if bolum_id:
                query += " AND o.bolum_id = %s"
                params.append(bolum_id)

            query += " ORDER BY o.ogrenci_no"

            cursor = self.db.execute_query(query, tuple(params))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"�renci aran1rken hata: {e}")
            return []

    def update_ogrenci(self, ogrenci_no: str, **kwargs) -> bool:
        """
        �renci g�ncelle

        Args:
            ogrenci_no: �renci numaras1
            **kwargs: G�ncellenecek alanlar

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            allowed_fields = ['ad_soyad', 'sinif', 'bolum_id', 'aktif']

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    updates.append(f"{key} = %s")
                    params.append(value)

            if not updates:
                logger.warning("G�ncellenecek alan yok")
                return False

            params.append(ogrenci_no)

            query = f"""
                UPDATE ogrenciler
                SET {', '.join(updates)}
                WHERE ogrenci_no = %s
            """

            cursor = self.db.execute_query(query, tuple(params))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"�renci g�ncellendi (No: {ogrenci_no})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"�renci g�ncellenirken hata: {e}")
            return False

    def delete_ogrenci(self, ogrenci_no: str) -> bool:
        """
        �renci sil (soft delete)

        Args:
            ogrenci_no: �renci numaras1

        Returns:
            Ba_ar1l1 ise True
        """
        return self.update_ogrenci(ogrenci_no, aktif=False)

    def get_ogrenciler_by_ders(self, ders_id: int) -> List[Dict]:
        """
        Dersi alan �rencileri getir

        Args:
            ders_id: Ders ID

        Returns:
            �renci listesi
        """
        try:
            query = """
                SELECT o.ogrenci_no, o.ad_soyad, o.sinif
                FROM ogrenciler o
                JOIN ders_kayitlari dk ON o.ogrenci_no = dk.ogrenci_no
                WHERE dk.ders_id = %s AND o.aktif = TRUE
                ORDER BY o.ad_soyad
            """

            cursor = self.db.execute_query(query, (ders_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Ders �rencileri getirilirken hata: {e}")
            return []

    def get_ogrenci_count_by_ders(self, ders_id: int) -> int:
        """
        Dersi alan �renci say1s1n1 getir

        Args:
            ders_id: Ders ID

        Returns:
            �renci say1s1
        """
        try:
            query = """
                SELECT COUNT(*)
                FROM ders_kayitlari dk
                JOIN ogrenciler o ON dk.ogrenci_no = o.ogrenci_no
                WHERE dk.ders_id = %s AND o.aktif = TRUE
            """

            cursor = self.db.execute_query(query, (ders_id,))

            if cursor:
                return cursor.fetchone()[0]

            return 0

        except Exception as e:
            logger.error(f"�renci say1s1 getirilirken hata: {e}")
            return 0

"""
Ders Model
Ders CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DersModel:
    """Ders veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: Database balant1 nesnesi
        """
        self.db = db_connection

    def create_ders(self, bolum_id: int, ders_kodu: str, ders_adi: str,
                    ogretim_elemani: str, sinif: int, ders_yapisi: str) -> Optional[int]:
        """
        Yeni ders olu_tur

        Args:
            bolum_id: Bölüm ID
            ders_kodu: Ders kodu
            ders_adi: Ders ad1
            ogretim_elemani: Öretim eleman1
            sinif: S1n1f (1-5)
            ders_yapisi: Zorunlu/Seçmeli

        Returns:
            Olu_turulan ders ID veya None
        """
        try:
            query = """
                INSERT INTO dersler
                (bolum_id, ders_kodu, ders_adi, ogretim_elemani, sinif, ders_yapisi)
                VALUES (%s, %s, %s, %s, %s, %s::ders_yapisi_enum)
                RETURNING ders_id
            """

            cursor = self.db.execute_query(
                query,
                (bolum_id, ders_kodu, ders_adi, ogretim_elemani, sinif, ders_yapisi)
            )

            if cursor:
                row = cursor.fetchone()
                if row:
                    ders_id = row[0]
                    self.db.commit()
                    logger.info(f"Yeni ders olu_turuldu: {ders_adi} (ID: {ders_id})")
                    return ders_id

            return None

        except psycopg2.IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ders olu_turulurken hata (duplicate): {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ders olu_turulurken hata: {e}")
            return None

    def create_ders_batch(self, dersler: List[Dict]) -> Tuple[int, int]:
        """
        Toplu ders ekleme (Excel'den gelen veriler için)

        Args:
            dersler: Ders listesi

        Returns:
            (ba_ar1l1_say1s1, hatal1_say1s1)
        """
        basarili = 0
        hatali = 0

        for ders in dersler:
            try:
                result = self.create_ders(
                    ders['bolum_id'],
                    ders['ders_kodu'],
                    ders['ders_adi'],
                    ders['ogretim_elemani'],
                    ders['sinif'],
                    ders['ders_yapisi']
                )

                if result:
                    basarili += 1
                else:
                    hatali += 1

            except Exception as e:
                logger.error(f"Toplu ders ekleme hatas1: {e}")
                hatali += 1

        return basarili, hatali

    def get_dersler_by_bolum(self, bolum_id: int, only_active=True) -> List[Dict]:
        """
        Bölüme ait dersleri getir

        Args:
            bolum_id: Bölüm ID
            only_active: Sadece aktif dersler

        Returns:
            Ders listesi
        """
        try:
            query = """
                SELECT ders_id, bolum_id, ders_kodu, ders_adi, ogretim_elemani,
                       sinif, ders_yapisi, aktif
                FROM dersler
                WHERE bolum_id = %s
            """

            if only_active:
                query += " AND aktif = TRUE"

            query += " ORDER BY sinif, ders_kodu"

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Dersler getirilirken hata: {e}")
            return []

    def get_ders_by_id(self, ders_id: int) -> Optional[Dict]:
        """
        ID'ye göre ders getir

        Args:
            ders_id: Ders ID

        Returns:
            Ders bilgisi veya None
        """
        try:
            query = """
                SELECT d.ders_id, d.bolum_id, b.bolum_adi, d.ders_kodu, d.ders_adi,
                       d.ogretim_elemani, d.sinif, d.ders_yapisi, d.aktif
                FROM dersler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
                WHERE d.ders_id = %s
            """

            cursor = self.db.execute_query(query, (ders_id,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Ders getirilirken hata (ID: {ders_id}): {e}")
            return None

    def get_ders_by_code(self, ders_kodu: str) -> Optional[Dict]:
        """
        Koda göre ders getir

        Args:
            ders_kodu: Ders kodu

        Returns:
            Ders bilgisi veya None
        """
        try:
            query = """
                SELECT d.ders_id, d.bolum_id, b.bolum_adi, d.ders_kodu, d.ders_adi,
                       d.ogretim_elemani, d.sinif, d.ders_yapisi, d.aktif
                FROM dersler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
                WHERE d.ders_kodu = %s
            """

            cursor = self.db.execute_query(query, (ders_kodu,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Ders getirilirken hata (Kod: {ders_kodu}): {e}")
            return None

    def search_ders(self, search_term: str, bolum_id: int = None) -> List[Dict]:
        """
        Ders ara (kod, ad veya öretim eleman1na göre)

        Args:
            search_term: Arama terimi
            bolum_id: Bölüm ID (opsiyonel)

        Returns:
            Ders listesi
        """
        try:
            query = """
                SELECT d.ders_id, d.bolum_id, b.bolum_adi, d.ders_kodu, d.ders_adi,
                       d.ogretim_elemani, d.sinif, d.ders_yapisi, d.aktif
                FROM dersler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
                WHERE d.aktif = TRUE
                  AND (d.ders_kodu ILIKE %s OR d.ders_adi ILIKE %s
                       OR d.ogretim_elemani ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

            if bolum_id:
                query += " AND d.bolum_id = %s"
                params.append(bolum_id)

            query += " ORDER BY d.ders_kodu"

            cursor = self.db.execute_query(query, tuple(params))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Ders aran1rken hata: {e}")
            return []

    def get_ders_with_students(self, ders_id: int) -> Optional[Dict]:
        """
        Ders bilgilerini ve bu dersi alan örencileri getir

        Args:
            ders_id: Ders ID

        Returns:
            Ders bilgisi ve örenci listesi
        """
        try:
            # Önce ders bilgilerini al
            ders = self.get_ders_by_id(ders_id)

            if not ders:
                return None

            # Dersi alan örencileri al
            query = """
                SELECT o.ogrenci_no, o.ad_soyad, o.sinif
                FROM ogrenciler o
                JOIN ogrenci_ders od ON o.ogrenci_no = od.ogrenci_no
                WHERE od.ders_id = %s
                ORDER BY o.ad_soyad
            """

            cursor = self.db.execute_query(query, (ders_id,))

            ogrenciler = []
            if cursor:
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    ogrenciler.append(dict(zip(columns, row)))

            ders['ogrenciler'] = ogrenciler
            ders['ogrenci_sayisi'] = len(ogrenciler)

            return ders

        except Exception as e:
            logger.error(f"Ders ve örenciler getirilirken hata: {e}")
            return None

    def update_ders(self, ders_id: int, **kwargs) -> bool:
        """
        Ders güncelle

        Args:
            ders_id: Ders ID
            **kwargs: Güncellenecek alanlar

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            allowed_fields = ['ders_kodu', 'ders_adi', 'ogretim_elemani',
                            'sinif', 'ders_yapisi', 'aktif']

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    if key == 'ders_yapisi':
                        updates.append(f"{key} = %s::ders_yapisi_enum")
                    else:
                        updates.append(f"{key} = %s")
                    params.append(value)

            if not updates:
                logger.warning("Güncellenecek alan yok")
                return False

            params.append(ders_id)

            query = f"""
                UPDATE dersler
                SET {', '.join(updates)}
                WHERE ders_id = %s
            """

            cursor = self.db.execute_query(query, tuple(params))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"Ders güncellendi (ID: {ders_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ders güncellenirken hata: {e}")
            return False

    def delete_ders(self, ders_id: int) -> bool:
        """
        Ders sil (soft delete)

        Args:
            ders_id: Ders ID

        Returns:
            Ba_ar1l1 ise True
        """
        return self.update_ders(ders_id, aktif=False)

    def get_dersler_by_sinif(self, bolum_id: int, sinif: int) -> List[Dict]:
        """
        S1n1fa göre dersleri getir

        Args:
            bolum_id: Bölüm ID
            sinif: S1n1f (1-5)

        Returns:
            Ders listesi
        """
        try:
            query = """
                SELECT ders_id, ders_kodu, ders_adi, ogretim_elemani,
                       sinif, ders_yapisi
                FROM dersler
                WHERE bolum_id = %s AND sinif = %s AND aktif = TRUE
                ORDER BY ders_kodu
            """

            cursor = self.db.execute_query(query, (bolum_id, sinif))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"S1n1f dersleri getirilirken hata: {e}")
            return []

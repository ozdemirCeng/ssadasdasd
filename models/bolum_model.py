"""
Bölüm Model
Bölüm CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BolumModel:
    """Bölüm veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: Database balant1 nesnesi
        """
        self.db = db_connection

    def get_all_bolumler(self, only_active=True) -> List[Dict]:
        """
        Tüm bölümleri getir

        Args:
            only_active: Sadece aktif bölümleri getir

        Returns:
            Bölüm listesi
        """
        try:
            query = """
                SELECT bolum_id, bolum_adi, bolum_kodu, aktif
                FROM bolumler
            """

            if only_active:
                query += " WHERE aktif = TRUE"

            query += " ORDER BY bolum_adi"

            cursor = self.db.execute_query(query)

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Bölümler getirilirken hata: {e}")
            return []

    def get_bolum_by_id(self, bolum_id: int) -> Optional[Dict]:
        """
        ID'ye göre bölüm getir

        Args:
            bolum_id: Bölüm ID

        Returns:
            Bölüm bilgisi veya None
        """
        try:
            query = """
                SELECT bolum_id, bolum_adi, bolum_kodu, aktif
                FROM bolumler
                WHERE bolum_id = %s
            """

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Bölüm getirilirken hata (ID: {bolum_id}): {e}")
            return None

    def get_bolum_by_code(self, bolum_kodu: str) -> Optional[Dict]:
        """
        Koda göre bölüm getir

        Args:
            bolum_kodu: Bölüm kodu

        Returns:
            Bölüm bilgisi veya None
        """
        try:
            query = """
                SELECT bolum_id, bolum_adi, bolum_kodu, aktif
                FROM bolumler
                WHERE bolum_kodu = %s
            """

            cursor = self.db.execute_query(query, (bolum_kodu,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Bölüm getirilirken hata (Kod: {bolum_kodu}): {e}")
            return None

    def create_bolum(self, bolum_adi: str, bolum_kodu: str) -> Optional[int]:
        """
        Yeni bölüm olu_tur

        Args:
            bolum_adi: Bölüm ad1
            bolum_kodu: Bölüm kodu

        Returns:
            Olu_turulan bölüm ID veya None
        """
        try:
            query = """
                INSERT INTO bolumler (bolum_adi, bolum_kodu)
                VALUES (%s, %s)
                RETURNING bolum_id
            """

            cursor = self.db.execute_query(query, (bolum_adi, bolum_kodu))

            if cursor:
                row = cursor.fetchone()
                if row:
                    bolum_id = row[0]
                    self.db.commit()
                    logger.info(f"Yeni bölüm olu_turuldu: {bolum_adi} (ID: {bolum_id})")
                    return bolum_id

            return None

        except psycopg2.IntegrityError as e:
            self.db.rollback()
            logger.error(f"Bölüm olu_turulurken hata (duplicate): {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Bölüm olu_turulurken hata: {e}")
            return None

    def update_bolum(self, bolum_id: int, bolum_adi: str = None,
                     bolum_kodu: str = None, aktif: bool = None) -> bool:
        """
        Bölüm güncelle

        Args:
            bolum_id: Bölüm ID
            bolum_adi: Yeni bölüm ad1 (opsiyonel)
            bolum_kodu: Yeni bölüm kodu (opsiyonel)
            aktif: Aktiflik durumu (opsiyonel)

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            updates = []
            params = []

            if bolum_adi is not None:
                updates.append("bolum_adi = %s")
                params.append(bolum_adi)

            if bolum_kodu is not None:
                updates.append("bolum_kodu = %s")
                params.append(bolum_kodu)

            if aktif is not None:
                updates.append("aktif = %s")
                params.append(aktif)

            if not updates:
                logger.warning("Güncellenecek alan yok")
                return False

            params.append(bolum_id)

            query = f"""
                UPDATE bolumler
                SET {', '.join(updates)}
                WHERE bolum_id = %s
            """

            cursor = self.db.execute_query(query, tuple(params))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"Bölüm güncellendi (ID: {bolum_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Bölüm güncellenirken hata: {e}")
            return False

    def delete_bolum(self, bolum_id: int) -> bool:
        """
        Bölüm sil (soft delete)

        Args:
            bolum_id: Bölüm ID

        Returns:
            Ba_ar1l1 ise True
        """
        return self.update_bolum(bolum_id, aktif=False)

    def get_bolum_statistics(self, bolum_id: int) -> Optional[Dict]:
        """
        Bölüm istatistikleri getir

        Args:
            bolum_id: Bölüm ID

        Returns:
            0statistik bilgileri
        """
        try:
            query = """
                SELECT
                    b.bolum_id,
                    b.bolum_adi,
                    b.bolum_kodu,
                    COUNT(DISTINCT d.ders_id) as toplam_ders,
                    COUNT(DISTINCT o.ogrenci_id) as toplam_ogrenci,
                    COUNT(DISTINCT dr.derslik_id) as toplam_derslik,
                    COUNT(DISTINCT u.user_id) as toplam_koordinator
                FROM bolumler b
                LEFT JOIN dersler d ON b.bolum_id = d.bolum_id
                LEFT JOIN ogrenciler o ON b.bolum_id = o.bolum_id
                LEFT JOIN derslikler dr ON b.bolum_id = dr.bolum_id
                LEFT JOIN users u ON b.bolum_id = u.bolum_id AND u.role = 'Bölüm Koordinatörü'
                WHERE b.bolum_id = %s
                GROUP BY b.bolum_id, b.bolum_adi, b.bolum_kodu
            """

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Bölüm istatistikleri getirilirken hata: {e}")
            return None

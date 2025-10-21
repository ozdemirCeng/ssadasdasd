"""
Derslik Model
Derslik CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DerslikModel:
    """Derslik veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: Database balant1 nesnesi
        """
        self.db = db_connection

    def create_derslik(self, bolum_id: int, derslik_kodu: str, derslik_adi: str,
                       kapasite: int, satir_sayisi: int, sutun_sayisi: int,
                       sira_yapisi: int) -> Optional[int]:
        """
        Yeni derslik olu_tur

        Args:
            bolum_id: Bölüm ID
            derslik_kodu: Derslik kodu
            derslik_adi: Derslik ad1
            kapasite: S1nav kapasitesi
            satir_sayisi: Boyuna s1ra say1s1
            sutun_sayisi: Enine s1ra say1s1
            sira_yapisi: S1ra yap1s1 (2'li, 3'lü vb)

        Returns:
            Olu_turulan derslik ID veya None
        """
        try:
            query = """
                INSERT INTO derslikler
                (bolum_id, derslik_kodu, derslik_adi, kapasite, satir_sayisi,
                 sutun_sayisi, sira_yapisi)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING derslik_id
            """

            cursor = self.db.execute_query(
                query,
                (bolum_id, derslik_kodu, derslik_adi, kapasite, satir_sayisi,
                 sutun_sayisi, sira_yapisi)
            )

            if cursor:
                row = cursor.fetchone()
                if row:
                    derslik_id = row[0]
                    self.db.commit()
                    logger.info(f"Yeni derslik olu_turuldu: {derslik_adi} (ID: {derslik_id})")
                    return derslik_id

            return None

        except psycopg2.IntegrityError as e:
            self.db.rollback()
            logger.error(f"Derslik olu_turulurken hata (duplicate): {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Derslik olu_turulurken hata: {e}")
            return None

    def get_derslikler_by_bolum(self, bolum_id: int, only_active=True) -> List[Dict]:
        """
        Bölüme ait derslikleri getir

        Args:
            bolum_id: Bölüm ID
            only_active: Sadece aktif derslikler

        Returns:
            Derslik listesi
        """
        try:
            query = """
                SELECT derslik_id, bolum_id, derslik_kodu, derslik_adi,
                       kapasite, satir_sayisi, sutun_sayisi, sira_yapisi, aktif
                FROM derslikler
                WHERE bolum_id = %s
            """

            if only_active:
                query += " AND aktif = TRUE"

            query += " ORDER BY derslik_kodu"

            cursor = self.db.execute_query(query, (bolum_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Derslikler getirilirken hata: {e}")
            return []

    def get_all_derslikler(self, only_active=True) -> List[Dict]:
        """
        Tüm derslikleri getir

        Args:
            only_active: Sadece aktif derslikler

        Returns:
            Derslik listesi
        """
        try:
            query = """
                SELECT d.derslik_id, d.bolum_id, b.bolum_adi, d.derslik_kodu,
                       d.derslik_adi, d.kapasite, d.satir_sayisi, d.sutun_sayisi,
                       d.sira_yapisi, d.aktif
                FROM derslikler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
            """

            if only_active:
                query += " WHERE d.aktif = TRUE"

            query += " ORDER BY b.bolum_adi, d.derslik_kodu"

            cursor = self.db.execute_query(query)

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Derslikler getirilirken hata: {e}")
            return []

    def get_derslik_by_id(self, derslik_id: int) -> Optional[Dict]:
        """
        ID'ye göre derslik getir

        Args:
            derslik_id: Derslik ID

        Returns:
            Derslik bilgisi veya None
        """
        try:
            query = """
                SELECT d.derslik_id, d.bolum_id, b.bolum_adi, d.derslik_kodu,
                       d.derslik_adi, d.kapasite, d.satir_sayisi, d.sutun_sayisi,
                       d.sira_yapisi, d.aktif
                FROM derslikler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
                WHERE d.derslik_id = %s
            """

            cursor = self.db.execute_query(query, (derslik_id,))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Derslik getirilirken hata (ID: {derslik_id}): {e}")
            return None

    def search_derslik(self, search_term: str, bolum_id: int = None) -> List[Dict]:
        """
        Derslik ara (kod veya ada göre)

        Args:
            search_term: Arama terimi
            bolum_id: Bölüm ID (opsiyonel)

        Returns:
            Derslik listesi
        """
        try:
            query = """
                SELECT d.derslik_id, d.bolum_id, b.bolum_adi, d.derslik_kodu,
                       d.derslik_adi, d.kapasite, d.satir_sayisi, d.sutun_sayisi,
                       d.sira_yapisi, d.aktif
                FROM derslikler d
                JOIN bolumler b ON d.bolum_id = b.bolum_id
                WHERE d.aktif = TRUE
                  AND (d.derslik_kodu ILIKE %s OR d.derslik_adi ILIKE %s)
            """

            params = [f"%{search_term}%", f"%{search_term}%"]

            if bolum_id:
                query += " AND d.bolum_id = %s"
                params.append(bolum_id)

            query += " ORDER BY d.derslik_kodu"

            cursor = self.db.execute_query(query, tuple(params))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Derslik aran1rken hata: {e}")
            return []

    def update_derslik(self, derslik_id: int, **kwargs) -> bool:
        """
        Derslik güncelle

        Args:
            derslik_id: Derslik ID
            **kwargs: Güncellenecek alanlar

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            allowed_fields = ['derslik_kodu', 'derslik_adi', 'kapasite',
                            'satir_sayisi', 'sutun_sayisi', 'sira_yapisi', 'aktif']

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    updates.append(f"{key} = %s")
                    params.append(value)

            if not updates:
                logger.warning("Güncellenecek alan yok")
                return False

            params.append(derslik_id)

            query = f"""
                UPDATE derslikler
                SET {', '.join(updates)}
                WHERE derslik_id = %s
            """

            cursor = self.db.execute_query(query, tuple(params))

            if cursor and cursor.rowcount > 0:
                self.db.commit()
                logger.info(f"Derslik güncellendi (ID: {derslik_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Derslik güncellenirken hata: {e}")
            return False

    def delete_derslik(self, derslik_id: int) -> bool:
        """
        Derslik sil (soft delete)

        Args:
            derslik_id: Derslik ID

        Returns:
            Ba_ar1l1 ise True
        """
        return self.update_derslik(derslik_id, aktif=False)

    def check_derslik_availability(self, derslik_id: int, tarih: str,
                                   baslangic_saati: str, bitis_saati: str) -> bool:
        """
        Derslik müsaitlik kontrolü

        Args:
            derslik_id: Derslik ID
            tarih: S1nav tarihi
            baslangic_saati: Ba_lang1ç saati
            bitis_saati: Biti_ saati

        Returns:
            Müsait ise True
        """
        try:
            query = """
                SELECT COUNT(*)
                FROM sinav_programi
                WHERE derslik_id = %s
                  AND tarih = %s
                  AND (
                      (baslangic_saati <= %s AND bitis_saati > %s) OR
                      (baslangic_saati < %s AND bitis_saati >= %s) OR
                      (baslangic_saati >= %s AND bitis_saati <= %s)
                  )
            """

            cursor = self.db.execute_query(
                query,
                (derslik_id, tarih, baslangic_saati, baslangic_saati,
                 bitis_saati, bitis_saati, baslangic_saati, bitis_saati)
            )

            if cursor:
                count = cursor.fetchone()[0]
                return count == 0

            return False

        except Exception as e:
            logger.error(f"Derslik müsaitlik kontrolü hatas1: {e}")
            return False

    def get_suitable_derslikler(self, bolum_id: int, required_capacity: int) -> List[Dict]:
        """
        Kapasiteye uygun derslikleri getir

        Args:
            bolum_id: Bölüm ID
            required_capacity: Gerekli kapasite

        Returns:
            Uygun derslik listesi
        """
        try:
            query = """
                SELECT derslik_id, derslik_kodu, derslik_adi, kapasite,
                       satir_sayisi, sutun_sayisi, sira_yapisi
                FROM derslikler
                WHERE bolum_id = %s
                  AND aktif = TRUE
                  AND kapasite >= %s
                ORDER BY kapasite ASC
            """

            cursor = self.db.execute_query(query, (bolum_id, required_capacity))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Uygun derslikler getirilirken hata: {e}")
            return []

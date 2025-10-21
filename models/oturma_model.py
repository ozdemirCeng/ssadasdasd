"""
Oturma Plan1 Model
Oturma düzeni CRUD i_lemleri
"""

import psycopg2
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OturmaModel:
    """Oturma plan1 veritaban1 i_lemleri"""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_oturma(self, sinav_id: int, derslik_id: int, ogrenci_no: str,
                     satir_no: int, sutun_no: int) -> bool:
        """Oturma plan1 olu_tur"""
        try:
            query = """
                INSERT INTO oturma_planlari
                (sinav_id, derslik_id, ogrenci_no, satir_no, sutun_no)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor = self.db.execute_query(
                query,
                (sinav_id, derslik_id, ogrenci_no, satir_no, sutun_no)
            )

            if cursor:
                self.db.commit()
                return True

            return False

        except psycopg2.IntegrityError as e:
            self.db.rollback()
            logger.error(f"Oturma plan1 olu_turma hatas1 (duplicate): {e}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Oturma plan1 olu_turma hatas1: {e}")
            return False

    def create_oturma_batch(self, oturmalar: List[Dict]) -> Tuple[int, int]:
        """Toplu oturma plan1 olu_tur"""
        basarili = 0
        hatali = 0

        for oturma in oturmalar:
            try:
                result = self.create_oturma(
                    oturma['sinav_id'],
                    oturma['derslik_id'],
                    oturma['ogrenci_no'],
                    oturma['satir_no'],
                    oturma['sutun_no']
                )

                if result:
                    basarili += 1
                else:
                    hatali += 1

            except Exception as e:
                logger.error(f"Toplu oturma ekleme hatas1: {e}")
                hatali += 1

        return basarili, hatali

    def get_oturma_by_sinav(self, sinav_id: int) -> List[Dict]:
        """S1nava ait oturma plan1n1 getir"""
        try:
            query = """
                SELECT op.oturma_id, op.sinav_id, op.derslik_id,
                       dr.derslik_kodu, dr.derslik_adi,
                       op.ogrenci_no, o.ad_soyad,
                       op.satir_no, op.sutun_no
                FROM oturma_planlari op
                JOIN derslikler dr ON op.derslik_id = dr.derslik_id
                JOIN ogrenciler o ON op.ogrenci_no = o.ogrenci_no
                WHERE op.sinav_id = %s
                ORDER BY dr.derslik_kodu, op.satir_no, op.sutun_no
            """

            cursor = self.db.execute_query(query, (sinav_id,))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Oturma plan1 getirilirken hata: {e}")
            return []

    def get_oturma_by_sinav_derslik(self, sinav_id: int, derslik_id: int) -> List[Dict]:
        """S1nav ve derslie göre oturma plan1n1 getir"""
        try:
            query = """
                SELECT op.oturma_id, op.ogrenci_no, o.ad_soyad,
                       op.satir_no, op.sutun_no
                FROM oturma_planlari op
                JOIN ogrenciler o ON op.ogrenci_no = o.ogrenci_no
                WHERE op.sinav_id = %s AND op.derslik_id = %s
                ORDER BY op.satir_no, op.sutun_no
            """

            cursor = self.db.execute_query(query, (sinav_id, derslik_id))

            if cursor:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

            return []

        except Exception as e:
            logger.error(f"Derslik oturma plan1 getirilirken hata: {e}")
            return []

    def get_ogrenci_oturma(self, sinav_id: int, ogrenci_no: str) -> Optional[Dict]:
        """Örencinin oturma yerini getir"""
        try:
            query = """
                SELECT op.oturma_id, op.derslik_id, dr.derslik_kodu,
                       dr.derslik_adi, op.satir_no, op.sutun_no
                FROM oturma_planlari op
                JOIN derslikler dr ON op.derslik_id = dr.derslik_id
                WHERE op.sinav_id = %s AND op.ogrenci_no = %s
            """

            cursor = self.db.execute_query(query, (sinav_id, ogrenci_no))

            if cursor:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))

            return None

        except Exception as e:
            logger.error(f"Örenci oturma yeri getirilirken hata: {e}")
            return None

    def delete_oturma_by_sinav(self, sinav_id: int) -> bool:
        """S1nava ait tüm oturma plan1n1 sil"""
        try:
            query = "DELETE FROM oturma_planlari WHERE sinav_id = %s"

            cursor = self.db.execute_query(query, (sinav_id,))

            if cursor:
                self.db.commit()
                logger.info(f"Oturma plan1 silindi (S1nav ID: {sinav_id})")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Oturma plan1 silinirken hata: {e}")
            return False

    def check_koltuk_dolu(self, sinav_id: int, derslik_id: int,
                          satir_no: int, sutun_no: int) -> bool:
        """Koltuk dolu mu kontrol et"""
        try:
            query = """
                SELECT COUNT(*)
                FROM oturma_planlari
                WHERE sinav_id = %s
                  AND derslik_id = %s
                  AND satir_no = %s
                  AND sutun_no = %s
            """

            cursor = self.db.execute_query(
                query,
                (sinav_id, derslik_id, satir_no, sutun_no)
            )

            if cursor:
                count = cursor.fetchone()[0]
                return count > 0

            return False

        except Exception as e:
            logger.error(f"Koltuk kontrol hatas1: {e}")
            return True  # Hata durumunda dolu say

    def generate_oturma_plan(self, sinav_id: int, sira_yapisi: int = 2) -> bool:
        """
        Otomatik oturma plan1 olu_tur

        Args:
            sinav_id: S1nav ID
            sira_yapisi: S1ra yap1s1 (2'li, 3'lü vb)

        Returns:
            Ba_ar1l1 ise True
        """
        try:
            # S1nav bilgilerini al
            query_sinav = """
                SELECT s.ders_id, s.ogrenci_sayisi
                FROM sinavlar s
                WHERE s.sinav_id = %s
            """

            cursor = self.db.execute_query(query_sinav, (sinav_id,))
            if not cursor:
                return False

            row = cursor.fetchone()
            if not row:
                return False

            ders_id, ogrenci_sayisi = row

            # S1nava atanan derslikleri al
            query_derslikler = """
                SELECT dr.derslik_id, dr.satir_sayisi, dr.sutun_sayisi,
                       dr.sira_yapisi, dr.kapasite
                FROM sinav_derslikleri sd
                JOIN derslikler dr ON sd.derslik_id = dr.derslik_id
                WHERE sd.sinav_id = %s
                ORDER BY dr.kapasite
            """

            cursor = self.db.execute_query(query_derslikler, (sinav_id,))
            if not cursor:
                return False

            derslikler = []
            for row in cursor.fetchall():
                derslikler.append({
                    'derslik_id': row[0],
                    'satir_sayisi': row[1],
                    'sutun_sayisi': row[2],
                    'sira_yapisi': row[3],
                    'kapasite': row[4]
                })

            # Dersi alan örencileri al
            query_ogrenciler = """
                SELECT dk.ogrenci_no
                FROM ders_kayitlari dk
                JOIN ogrenciler o ON dk.ogrenci_no = o.ogrenci_no
                WHERE dk.ders_id = %s AND o.aktif = TRUE
                ORDER BY dk.ogrenci_no
            """

            cursor = self.db.execute_query(query_ogrenciler, (ders_id,))
            if not cursor:
                return False

            ogrenciler = [row[0] for row in cursor.fetchall()]

            # Oturma plan1 olu_tur
            ogrenci_index = 0
            oturmalar = []

            for derslik in derslikler:
                if ogrenci_index >= len(ogrenciler):
                    break

                derslik_id = derslik['derslik_id']
                satir_sayisi = derslik['satir_sayisi']
                sutun_sayisi = derslik['sutun_sayisi']
                sira_yap = derslik['sira_yapisi']

                # Her s1ra için örenci yerle_tir
                for satir in range(1, satir_sayisi + 1):
                    for sutun in range(1, sutun_sayisi + 1):
                        if ogrenci_index >= len(ogrenciler):
                            break

                        # S1ra yap1s1na göre atlama (örn: 2'li ise 2. koltuktan sonra bo_luk)
                        if sutun % (sira_yap + 1) == 0:
                            continue

                        oturmalar.append({
                            'sinav_id': sinav_id,
                            'derslik_id': derslik_id,
                            'ogrenci_no': ogrenciler[ogrenci_index],
                            'satir_no': satir,
                            'sutun_no': sutun
                        })

                        ogrenci_index += 1

            # Toplu ekle
            basarili, hatali = self.create_oturma_batch(oturmalar)

            logger.info(f"Oturma plan1 olu_turuldu: {basarili} ba_ar1l1, {hatali} hatal1")

            return basarili > 0

        except Exception as e:
            logger.error(f"Otomatik oturma plan1 olu_turma hatas1: {e}")
            return False

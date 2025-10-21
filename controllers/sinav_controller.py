"""
S1nav Controller
S1nav program1 i_lemleri i�in business logic
"""

from models.database import db
from models.sinav_model import SinavModel
from models.ders_model import DersModel
from models.derslik_model import DerslikModel
from models.ogrenci_model import OgrenciModel
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, time, timedelta
import logging

logger = logging.getLogger(__name__)


class SinavController:
    """S1nav i_lemleri controller"""

    def __init__(self):
        self.sinav_model = SinavModel(db)
        self.ders_model = DersModel(db)
        self.derslik_model = DerslikModel(db)
        self.ogrenci_model = OgrenciModel(db)

    def create_program(self, bolum_id: int, program_adi: str, sinav_tipi: str,
                       baslangic_tarihi: date, bitis_tarihi: date,
                       varsayilan_sinav_suresi: int = 75,
                       bekleme_suresi: int = 15) -> Tuple[bool, str, Optional[int]]:
        """Yeni s1nav program1 olu_tur"""
        try:
            # Validasyon
            if baslangic_tarihi > bitis_tarihi:
                return False, "Ba_lang1� tarihi biti_ tarihinden sonra olamaz", None

            if varsayilan_sinav_suresi <= 0:
                return False, "S1nav s�resi 0'dan b�y�k olmal1d1r", None

            program_id = self.sinav_model.create_program(
                bolum_id, program_adi, sinav_tipi,
                baslangic_tarihi, bitis_tarihi,
                varsayilan_sinav_suresi, bekleme_suresi
            )

            if program_id:
                return True, "S1nav program1 ba_ar1yla olu_turuldu", program_id
            else:
                return False, "S1nav program1 olu_turulamad1", None

        except Exception as e:
            logger.error(f"S1nav program1 olu_turma hatas1: {e}")
            return False, f"Hata: {str(e)}", None

    def generate_sinav_programi(self, program_id: int, ders_ids: List[int],
                                excluded_days: List[int] = None,
                                exam_slots: List[Tuple[int, int]] = None) -> Tuple[bool, str]:
        """
        Otomatik s1nav program1 olu_tur

        Args:
            program_id: Program ID
            ders_ids: Programa dahil edilecek ders ID'leri
            excluded_days: Hari� tutulan g�nler (0=Pazartesi, 6=Pazar)
            exam_slots: S1nav saatleri [(saat, dakika), ...]

        Returns:
            (ba_ar1l1_m1, mesaj)
        """
        try:
            # Program bilgilerini al
            program = self.sinav_model.get_program_by_id(program_id)
            if not program:
                return False, "Program bulunamad1"

            bolum_id = program['bolum_id']
            baslangic = program['baslangic_tarihi']
            bitis = program['bitis_tarihi']
            bekleme_suresi = program['bekleme_suresi']

            # Varsay1lan excluded days (Cumartesi, Pazar)
            if excluded_days is None:
                excluded_days = [5, 6]  # Cumartesi, Pazar

            # Varsay1lan s1nav saatleri
            if exam_slots is None:
                exam_slots = [(9, 0), (11, 0), (13, 30), (15, 30)]

            # Tarih listesi olu_tur (hari� tutulan g�nleri �1kar)
            available_dates = []
            current_date = baslangic

            while current_date <= bitis:
                if current_date.weekday() not in excluded_days:
                    available_dates.append(current_date)
                current_date += timedelta(days=1)

            if not available_dates:
                return False, "Uygun tarih bulunamad1"

            # Her ders i�in s1nav planla
            date_index = 0
            slot_index = 0
            basarili = 0
            hatali = 0

            for ders_id in ders_ids:
                try:
                    # Ders bilgilerini al
                    ders = self.ders_model.get_ders_by_id(ders_id)
                    if not ders:
                        hatali += 1
                        continue

                    # �renci say1s1n1 al
                    ogrenci_sayisi = self.ogrenci_model.get_ogrenci_count_by_ders(ders_id)

                    # Tarih ve saat belirle
                    if date_index >= len(available_dates):
                        hatali += 1
                        logger.warning(f"Ders {ders_id} i�in tarih bulunamad1")
                        continue

                    tarih = available_dates[date_index]
                    saat_tuple = exam_slots[slot_index]
                    baslangic_saati = time(saat_tuple[0], saat_tuple[1])

                    # S1nav s�resi
                    sinav_suresi = program['varsayilan_sinav_suresi']
                    bitis_saati = (datetime.combine(date.today(), baslangic_saati) +
                                   timedelta(minutes=sinav_suresi)).time()

                    # S1nav olu_tur
                    sinav_id = self.sinav_model.create_sinav(
                        program_id, ders_id, tarih, baslangic_saati, bitis_saati
                    )

                    if sinav_id:
                        # �renci say1s1n1 g�ncelle
                        self.sinav_model.update_ogrenci_sayisi(sinav_id)

                        # Uygun derslikleri bul ve ata
                        derslikler = self.derslik_model.get_suitable_derslikler(bolum_id, ogrenci_sayisi)

                        if derslikler:
                            # 0lk uygun derslii ata
                            self.sinav_model.assign_derslik_to_sinav(sinav_id, derslikler[0]['derslik_id'])

                        basarili += 1
                    else:
                        hatali += 1

                    # Sonraki slot'a ge�
                    slot_index += 1
                    if slot_index >= len(exam_slots):
                        slot_index = 0
                        date_index += 1

                except Exception as e:
                    logger.error(f"Ders {ders_id} i�in s1nav olu_turma hatas1: {e}")
                    hatali += 1

            if basarili > 0:
                return True, f"{basarili} s1nav olu_turuldu, {hatali} hatal1"
            else:
                return False, f"S1nav olu_turulamad1. {hatali} hata"

        except Exception as e:
            logger.error(f"S1nav program1 olu_turma hatas1: {e}")
            return False, f"Hata: {str(e)}"

    def get_sinavlar_by_program(self, program_id: int) -> List[Dict]:
        """Programa ait s1navlar1 getir"""
        try:
            return self.sinav_model.get_sinavlar_by_program(program_id)
        except Exception as e:
            logger.error(f"S1nav listesi hatas1: {e}")
            return []

    def get_program_by_id(self, program_id: int) -> Optional[Dict]:
        """Program bilgilerini getir"""
        try:
            return self.sinav_model.get_program_by_id(program_id)
        except Exception as e:
            logger.error(f"Program getirme hatas1: {e}")
            return None

    def get_programs_by_bolum(self, bolum_id: int) -> List[Dict]:
        """B�l�me ait programlar1 getir"""
        try:
            return self.sinav_model.get_programs_by_bolum(bolum_id)
        except Exception as e:
            logger.error(f"Program listesi hatas1: {e}")
            return []

    def delete_program(self, program_id: int) -> Tuple[bool, str]:
        """Program1 sil"""
        try:
            success = self.sinav_model.delete_program(program_id)

            if success:
                return True, "Program ba_ar1yla silindi"
            else:
                return False, "Program silinemedi"

        except Exception as e:
            logger.error(f"Program silme hatas1: {e}")
            return False, f"Hata: {str(e)}"

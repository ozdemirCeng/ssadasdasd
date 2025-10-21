"""
Excel Controller
Excel import/export i_lemleri
"""

import openpyxl
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
from models.database import db
from models.ders_model import DersModel
from models.ogrenci_model import OgrenciModel

logger = logging.getLogger(__name__)


class ExcelController:
    """Excel i_lemleri controller"""

    def __init__(self):
        self.ders_model = DersModel(db)
        self.ogrenci_model = OgrenciModel(db)

    def parse_ders_listesi(self, file_path: str, bolum_id: int) -> Tuple[bool, str, List[Dict]]:
        """
        Ders listesi Excel dosyas1n1 parse et

        Returns:
            (ba_ar1l1_m1, mesaj, ders_listesi)
        """
        try:
            # Excel dosyas1n1 oku
            df = pd.read_excel(file_path)

            logger.info(f"Excel kolonlar1: {df.columns.tolist()}")

            # Kolon isimlerini normalize et
            df.columns = df.columns.str.strip()

            # Gerekli kolonlar1 bul
            ders_kodu_col = self._find_column(df, ['Ders Kodu', 'Ders Kod', 'Kod', 'DersKodu'])
            ders_adi_col = self._find_column(df, ['Ders Ad1', 'Ders Ad', 'Ders', 'DersAdi'])
            ogretim_elemani_col = self._find_column(df, ['Öretim Üyesi', 'Hoca', 'Öretim Eleman1', 'OgretimElemani'])
            sinif_col = self._find_column(df, ['S1n1f', 'Sinif', 'S1n1f1'])
            ders_yapisi_col = self._find_column(df, ['Ders Yap1s1', 'Yap1', 'Zorunlu/Seçmeli', 'DersYapisi'])

            if not all([ders_kodu_col, ders_adi_col, ogretim_elemani_col, sinif_col, ders_yapisi_col]):
                return False, "Gerekli kolonlar bulunamad1. Kolonlar: Ders Kodu, Ders Ad1, Öretim Üyesi, S1n1f, Ders Yap1s1", []

            dersler = []
            hatalar = []

            for index, row in df.iterrows():
                try:
                    ders_kodu = str(row[ders_kodu_col]).strip() if pd.notna(row[ders_kodu_col]) else None
                    ders_adi = str(row[ders_adi_col]).strip() if pd.notna(row[ders_adi_col]) else None
                    ogretim_elemani = str(row[ogretim_elemani_col]).strip() if pd.notna(row[ogretim_elemani_col]) else None
                    sinif = int(row[sinif_col]) if pd.notna(row[sinif_col]) else None
                    ders_yapisi = str(row[ders_yapisi_col]).strip() if pd.notna(row[ders_yapisi_col]) else None

                    if not all([ders_kodu, ders_adi, ogretim_elemani, sinif, ders_yapisi]):
                        hatalar.append(f"Sat1r {index + 2}: Eksik bilgi")
                        continue

                    # Ders yap1s1n1 normalize et
                    if ders_yapisi.lower() in ['zorunlu', 'z']:
                        ders_yapisi = 'Zorunlu'
                    elif ders_yapisi.lower() in ['seçmeli', 'secmeli', 's']:
                        ders_yapisi = 'Seçmeli'

                    dersler.append({
                        'bolum_id': bolum_id,
                        'ders_kodu': ders_kodu,
                        'ders_adi': ders_adi,
                        'ogretim_elemani': ogretim_elemani,
                        'sinif': sinif,
                        'ders_yapisi': ders_yapisi
                    })

                except Exception as e:
                    hatalar.append(f"Sat1r {index + 2}: {str(e)}")

            if hatalar:
                hata_mesaj = "\\n".join(hatalar[:5])  # 0lk 5 hatay1 göster
                return True, f"Uyar1lar var:\\n{hata_mesaj}", dersler
            else:
                return True, f"{len(dersler)} ders ba_ar1yla okundu", dersler

        except Exception as e:
            logger.error(f"Excel parse hatas1: {e}")
            return False, f"Excel okuma hatas1: {str(e)}", []

    def parse_ogrenci_listesi(self, file_path: str, bolum_id: int) -> Tuple[bool, str, List[Dict], List[Dict]]:
        """
        Örenci listesi Excel dosyas1n1 parse et

        Returns:
            (ba_ar1l1_m1, mesaj, ogrenci_listesi, ders_kayit_listesi)
        """
        try:
            df = pd.read_excel(file_path)

            logger.info(f"Excel kolonlar1: {df.columns.tolist()}")

            df.columns = df.columns.str.strip()

            ogrenci_no_col = self._find_column(df, ['Örenci No', 'No', 'Numara', 'OgrenciNo'])
            ad_soyad_col = self._find_column(df, ['Ad Soyad', '0sim', 'Örenci Ad1', 'AdSoyad'])
            sinif_col = self._find_column(df, ['S1n1f', 'Sinif'])
            ders_kodu_col = self._find_column(df, ['Ders Kodu', 'Kod', 'DersKodu'])

            if not all([ogrenci_no_col, ad_soyad_col, sinif_col, ders_kodu_col]):
                return False, "Gerekli kolonlar bulunamad1", [], []

            ogrenciler = {}
            ders_kayitlari = []
            hatalar = []

            for index, row in df.iterrows():
                try:
                    ogrenci_no = str(row[ogrenci_no_col]).strip() if pd.notna(row[ogrenci_no_col]) else None
                    ad_soyad = str(row[ad_soyad_col]).strip() if pd.notna(row[ad_soyad_col]) else None
                    sinif = int(row[sinif_col]) if pd.notna(row[sinif_col]) else 1
                    ders_kodu = str(row[ders_kodu_col]).strip() if pd.notna(row[ders_kodu_col]) else None

                    if not all([ogrenci_no, ad_soyad, ders_kodu]):
                        hatalar.append(f"Sat1r {index + 2}: Eksik bilgi")
                        continue

                    # Örenci listesine ekle (unique)
                    if ogrenci_no not in ogrenciler:
                        ogrenciler[ogrenci_no] = {
                            'ogrenci_no': ogrenci_no,
                            'bolum_id': bolum_id,
                            'ad_soyad': ad_soyad,
                            'sinif': sinif
                        }

                    # Ders kayd1 ekle
                    ders_kayitlari.append({
                        'ogrenci_no': ogrenci_no,
                        'ders_kodu': ders_kodu
                    })

                except Exception as e:
                    hatalar.append(f"Sat1r {index + 2}: {str(e)}")

            ogrenci_listesi = list(ogrenciler.values())

            if hatalar:
                hata_mesaj = "\\n".join(hatalar[:5])
                return True, f"Uyar1lar var:\\n{hata_mesaj}", ogrenci_listesi, ders_kayitlari
            else:
                return True, f"{len(ogrenci_listesi)} örenci ba_ar1yla okundu", ogrenci_listesi, ders_kayitlari

        except Exception as e:
            logger.error(f"Excel parse hatas1: {e}")
            return False, f"Excel okuma hatas1: {str(e)}", [], []

    def import_dersler(self, file_path: str, bolum_id: int) -> Tuple[bool, str, int, int]:
        """
        Ders listesini import et

        Returns:
            (ba_ar1l1_m1, mesaj, ba_ar1l1_say1s1, hatal1_say1s1)
        """
        try:
            success, message, dersler = self.parse_ders_listesi(file_path, bolum_id)

            if not success:
                return False, message, 0, 0

            basarili, hatali = self.ders_model.create_ders_batch(dersler)

            return True, f"{basarili} ders eklendi, {hatali} hatal1", basarili, hatali

        except Exception as e:
            logger.error(f"Ders import hatas1: {e}")
            return False, f"Hata: {str(e)}", 0, 0

    def import_ogrenciler(self, file_path: str, bolum_id: int) -> Tuple[bool, str, int, int]:
        """
        Örenci listesini import et

        Returns:
            (ba_ar1l1_m1, mesaj, ba_ar1l1_say1s1, hatal1_say1s1)
        """
        try:
            success, message, ogrenciler, ders_kayitlari = self.parse_ogrenci_listesi(file_path, bolum_id)

            if not success:
                return False, message, 0, 0

            # Önce örencileri ekle
            basarili_ogr, hatali_ogr = self.ogrenci_model.create_ogrenci_batch(ogrenciler)

            # Sonra ders kay1tlar1n1 ekle
            basarili_ders = 0
            for kayit in ders_kayitlari:
                if self.ogrenci_model.add_ders_kayit_by_code(kayit['ogrenci_no'], kayit['ders_kodu']):
                    basarili_ders += 1

            return True, f"{basarili_ogr} örenci, {basarili_ders} ders kayd1 eklendi", basarili_ogr, basarili_ders

        except Exception as e:
            logger.error(f"Örenci import hatas1: {e}")
            return False, f"Hata: {str(e)}", 0, 0

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """DataFrame'de kolon ad1n1 bul"""
        for col in df.columns:
            if col in possible_names:
                return col
        return None

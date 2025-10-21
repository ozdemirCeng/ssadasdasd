"""
Derslik Controller
Derslik i_lemleri için business logic
"""

from models.database import db
from models.derslik_model import DerslikModel
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DerslikController:
    """Derslik i_lemleri controller"""

    def __init__(self):
        self.model = DerslikModel(db)

    def create_derslik(self, bolum_id: int, derslik_kodu: str, derslik_adi: str,
                       kapasite: int, satir_sayisi: int, sutun_sayisi: int,
                       sira_yapisi: int) -> tuple[bool, str, Optional[int]]:
        """
        Yeni derslik olu_tur

        Returns:
            (ba_ar1l1_m1, mesaj, derslik_id)
        """
        try:
            # Validasyon
            if not derslik_kodu or not derslik_adi:
                return False, "Derslik kodu ve ad1 zorunludur", None

            if kapasite <= 0:
                return False, "Kapasite 0'dan büyük olmal1d1r", None

            if satir_sayisi <= 0 or sutun_sayisi <= 0:
                return False, "S1ra say1lar1 0'dan büyük olmal1d1r", None

            if sira_yapisi <= 0:
                return False, "S1ra yap1s1 0'dan büyük olmal1d1r", None

            # Derslik olu_tur
            derslik_id = self.model.create_derslik(
                bolum_id, derslik_kodu, derslik_adi,
                kapasite, satir_sayisi, sutun_sayisi, sira_yapisi
            )

            if derslik_id:
                return True, "Derslik ba_ar1yla olu_turuldu", derslik_id
            else:
                return False, "Derslik olu_turulamad1 (duplicate olabilir)", None

        except Exception as e:
            logger.error(f"Derslik olu_turma hatas1: {e}")
            return False, f"Hata: {str(e)}", None

    def get_derslikler_by_bolum(self, bolum_id: int) -> List[Dict]:
        """Bölüme ait derslikleri getir"""
        try:
            return self.model.get_derslikler_by_bolum(bolum_id)
        except Exception as e:
            logger.error(f"Derslik listesi hatas1: {e}")
            return []

    def search_derslik(self, search_term: str, bolum_id: int = None) -> List[Dict]:
        """Derslik ara"""
        try:
            return self.model.search_derslik(search_term, bolum_id)
        except Exception as e:
            logger.error(f"Derslik arama hatas1: {e}")
            return []

    def update_derslik(self, derslik_id: int, **kwargs) -> tuple[bool, str]:
        """Derslik güncelle"""
        try:
            success = self.model.update_derslik(derslik_id, **kwargs)

            if success:
                return True, "Derslik ba_ar1yla güncellendi"
            else:
                return False, "Derslik güncellenemedi"

        except Exception as e:
            logger.error(f"Derslik güncelleme hatas1: {e}")
            return False, f"Hata: {str(e)}"

    def delete_derslik(self, derslik_id: int) -> tuple[bool, str]:
        """Derslik sil"""
        try:
            success = self.model.delete_derslik(derslik_id)

            if success:
                return True, "Derslik ba_ar1yla silindi"
            else:
                return False, "Derslik silinemedi"

        except Exception as e:
            logger.error(f"Derslik silme hatas1: {e}")
            return False, f"Hata: {str(e)}"

    def get_derslik_by_id(self, derslik_id: int) -> Optional[Dict]:
        """ID'ye göre derslik getir"""
        try:
            return self.model.get_derslik_by_id(derslik_id)
        except Exception as e:
            logger.error(f"Derslik getirme hatas1: {e}")
            return None

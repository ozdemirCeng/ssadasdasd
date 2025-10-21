"""
Oturma Controller
Oturma plan1 i_lemleri için business logic
"""

from models.database import db
from models.oturma_model import OturmaModel
from models.sinav_model import SinavModel
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OturmaController:
    """Oturma plan1 i_lemleri controller"""

    def __init__(self):
        self.oturma_model = OturmaModel(db)
        self.sinav_model = SinavModel(db)

    def generate_oturma_plan(self, sinav_id: int) -> Tuple[bool, str]:
        """
        Otomatik oturma plan1 olu_tur

        Args:
            sinav_id: S1nav ID

        Returns:
            (ba_ar1l1_m1, mesaj)
        """
        try:
            # Önce mevcut plan1 sil
            self.oturma_model.delete_oturma_by_sinav(sinav_id)

            # Yeni plan olu_tur
            success = self.oturma_model.generate_oturma_plan(sinav_id)

            if success:
                return True, "Oturma plan1 ba_ar1yla olu_turuldu"
            else:
                return False, "Oturma plan1 olu_turulamad1"

        except Exception as e:
            logger.error(f"Oturma plan1 olu_turma hatas1: {e}")
            return False, f"Hata: {str(e)}"

    def get_oturma_by_sinav(self, sinav_id: int) -> List[Dict]:
        """S1nava ait oturma plan1n1 getir"""
        try:
            return self.oturma_model.get_oturma_by_sinav(sinav_id)
        except Exception as e:
            logger.error(f"Oturma plan1 getirme hatas1: {e}")
            return []

    def get_oturma_by_sinav_derslik(self, sinav_id: int, derslik_id: int) -> List[Dict]:
        """S1nav ve derslie göre oturma plan1n1 getir"""
        try:
            return self.oturma_model.get_oturma_by_sinav_derslik(sinav_id, derslik_id)
        except Exception as e:
            logger.error(f"Derslik oturma plan1 getirme hatas1: {e}")
            return []

    def get_ogrenci_oturma(self, sinav_id: int, ogrenci_no: str) -> Optional[Dict]:
        """Örencinin oturma yerini getir"""
        try:
            return self.oturma_model.get_ogrenci_oturma(sinav_id, ogrenci_no)
        except Exception as e:
            logger.error(f"Örenci oturma yeri getirme hatas1: {e}")
            return None

    def delete_oturma_by_sinav(self, sinav_id: int) -> Tuple[bool, str]:
        """S1nava ait oturma plan1n1 sil"""
        try:
            success = self.oturma_model.delete_oturma_by_sinav(sinav_id)

            if success:
                return True, "Oturma plan1 ba_ar1yla silindi"
            else:
                return False, "Oturma plan1 silinemedi"

        except Exception as e:
            logger.error(f"Oturma plan1 silme hatas1: {e}")
            return False, f"Hata: {str(e)}"

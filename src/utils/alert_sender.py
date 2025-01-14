import json
from datetime import datetime
from typing import Optional

import aiohttp

from .config import settings


class AlertSender:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.API_URL
        self.protection_url = f"{self.base_url}/protection"

    async def send_alert(self, class_id: int, confidence: float):
        """
        Envía una alerta asíncrona al servidor
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Determinar tipo de alerta según la clase
            alert_info = self._get_alert_info(class_id, confidence)

            payload = {
                "location": settings.DEFAULT_LOCATION,
                "message": alert_info["message"],
                "emergency_type": alert_info["type"],
                "user_id": settings.CAMERA_ID,
                "timestamp": current_time,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.protection_url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Alerta enviada: {alert_info['type']}")
                        return True
                    else:
                        print(f"❌ Error al enviar alerta: {response.status}")
                        return False

        except Exception as e:
            print(f"❌ Error en AlertSender: {str(e)}")
            return False

    def _get_alert_info(self, class_id: int, confidence: float) -> dict:
        """
        Determina el tipo de alerta y mensaje basado en la clase detectada
        """
        if class_id == 1:  # guns
            return {
                "type": "weapon_detected",
                "message": f"🔫 ALERTA CRÍTICA: Arma detectada con confianza {confidence:.2f}",
            }
        elif class_id == 2:  # risk_woman
            return {
                "type": "woman_risk",
                "message": f"⚠️ ALERTA: Situación de riesgo para mujer detectada con confianza {confidence:.2f}",
            }
        else:  # Sospechoso
            return {
                "type": "suspicious_person",
                "message": f"👤 AVISO: Persona sospechosa detectada con confianza {confidence:.2f}",
            }

    async def send_status_update(self, status: str):
        """
        Envía actualizaciones de estado del sistema
        """
        try:
            url = f"{self.base_url}/status"
            payload = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "camera_id": settings.CAMERA_ID,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception:
            return False

    async def send_bulk_alert(self, class_id: int, confidence: float, count: int):
        """
        Envía una alerta masiva cuando se acumulan suficientes detecciones
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alert_info = self._get_bulk_alert_info(class_id, confidence, count)

            payload = {
                "location": settings.DEFAULT_LOCATION,
                "message": alert_info["message"],
                "emergency_type": alert_info["type"],
                "user_id": settings.CAMERA_ID,
                "timestamp": current_time,
                "detection_count": count,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.protection_url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Alerta masiva enviada: {alert_info['type']}")
                        return True
                    else:
                        print(f"❌ Error al enviar alerta masiva: {response.status}")
                        return False

        except Exception as e:
            print(f"❌ Error en AlertSender: {str(e)}")
            return False

    def _get_bulk_alert_info(
        self, class_id: int, confidence: float, count: int
    ) -> dict:
        """
        Genera mensaje para alertas masivas
        """
        if class_id == 1:  # guns
            return {
                "type": "weapon_detected",
                "message": f"🔫 ALERTA CRÍTICA: Arma detectada con confianza {confidence:.2f}",
            }
        elif class_id == 2:  # risk_woman
            return {
                "type": "woman_risk",
                "message": f"⚠️ ALERTA: Situación de riesgo para mujer detectada con confianza {confidence:.2f}",
            }

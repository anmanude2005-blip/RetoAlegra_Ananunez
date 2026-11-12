
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


COLOMBIA_TZ = ZoneInfo("America/Bogota")


def format_colombia_datetime(value):
    """Convierte una fecha almacenada en UTC a hora de Colombia."""

    if not value:
        return "No disponible"

    try:
        if isinstance(value, datetime):
            date_value = value
        else:
            date_value = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )

        # Las fechas sin zona horaria se interpretan como UTC
        if date_value.tzinfo is None:
            date_value = date_value.replace(tzinfo=timezone.utc)

        local_date = date_value.astimezone(COLOMBIA_TZ)

        hour = local_date.strftime("%I:%M %p")

        if "AM" in hour:
            hour = hour.replace("AM", "a. m.")
        else:
            hour = hour.replace("PM", "p. m.")

        return (
            f"{local_date.strftime('%d/%m/%Y')} - {hour}"
        )

    except (ValueError, TypeError):
        return str(value)

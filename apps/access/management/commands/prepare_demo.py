from django.core.management.base import BaseCommand

from apps.access.demo import DEMO_PASSWORD, DEMO_USERNAME, ensure_demo


class Command(BaseCommand):
    help = "Crea la persona demo con la empresa 1 para consultar el margen de ejemplo."

    def handle(self, *args, **options):
        ensure_demo()
        self.stdout.write(
            f"Persona '{DEMO_USERNAME}' lista. Contraseña local: {DEMO_PASSWORD}."
        )

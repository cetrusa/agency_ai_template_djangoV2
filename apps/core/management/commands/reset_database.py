"""
Comando de management para resetear completamente la base de datos.
Similar al flujo de instalación de WordPress/Moodle.

Uso:
    python manage.py reset_database

Este comando:
1. Elimina la base de datos SQLite (o tablas si es otra BD)
2. Ejecuta migraciones desde cero
3. Resetea el flag setup_complete para mostrar el wizard

ADVERTENCIA: Este comando ELIMINA TODOS LOS DATOS.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
import sys


class Command(BaseCommand):
    help = "Resetea completamente la base de datos y vuelve al wizard de setup"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza el reset sin confirmación (¡PELIGROSO!)',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Confirmación de seguridad
        if not force:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  ADVERTENCIA: Este comando eliminará TODOS los datos de la base.\n"
            ))
            confirm = input("¿Estás seguro? Escribe 'RESETEAR' para continuar: ")
            if confirm != "RESETEAR":
                self.stdout.write(self.style.ERROR("Operación cancelada."))
                return

        self.stdout.write(self.style.WARNING("\n🔄 Iniciando reset de base de datos...\n"))

        # 1. Determinar tipo de base de datos
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if db_engine == 'django.db.backends.sqlite3':
            # SQLite: simplemente eliminar el archivo
            db_path = Path(settings.DATABASES['default']['NAME'])
            if db_path.exists():
                db_path.unlink()
                self.stdout.write(self.style.SUCCESS(f"✓ Base de datos SQLite eliminada: {db_path}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Base de datos no encontrada: {db_path}"))
        
        else:
            # PostgreSQL/MySQL: usar flush y eliminar migraciones
            self.stdout.write(self.style.WARNING(
                "⚠️  Para PostgreSQL/MySQL, debes resetear manualmente.\n"
                "   Sugerencia: DROP DATABASE y CREATE DATABASE, luego ejecuta migrate."
            ))
            sys.exit(1)

        # 2. Ejecutar migraciones desde cero
        self.stdout.write("\n📦 Ejecutando migraciones...\n")
        call_command('migrate', '--noinput', verbosity=1)
        
        # 3. Mensaje de éxito
        self.stdout.write(self.style.SUCCESS(
            "\n✅ Base de datos reseteada correctamente.\n"
            "\n🚀 Próximos pasos:"
            "\n   1. Ejecuta: python manage.py runserver"
            "\n   2. Accede a: http://127.0.0.1:8000/"
            "\n   3. Completa el wizard de configuración inicial\n"
        ))

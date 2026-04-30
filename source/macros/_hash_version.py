import hashlib
from datetime import datetime
from pathlib import Path


def normalizar_contenido_texto(contenido: bytes) -> bytes:
    """
    Normaliza contenido de texto para que el hash sea estable
    entre Windows, Linux y GitHub Actions.
    """
    # Quita BOM UTF-8 si existe
    if contenido.startswith(b"\xef\xbb\xbf"):
        contenido = contenido[3:]

    # Normaliza saltos de línea Windows/Mac/Linux a LF
    contenido = contenido.replace(b"\r\n", b"\n")
    contenido = contenido.replace(b"\r", b"\n")

    # Opcional: elimina espacios finales por línea
    contenido = b"\n".join(linea.rstrip() for linea in contenido.split(b"\n"))

    # Asegura un único salto final
    contenido = contenido.rstrip(b"\n") + b"\n"

    return contenido


def hash_carpeta(
    ruta_carpeta,
    extensiones=None,
    excluir_archivos=None,
    excluir_carpetas=None
):
    """Calcula hash SHA256 robusto considerando rutas relativas y contenido."""
    ruta = Path(ruta_carpeta)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe la carpeta: {ruta.resolve()}")

    extensiones = extensiones or set()
    excluir_archivos = excluir_archivos or set()
    excluir_carpetas = excluir_carpetas or set()

    hash_total = hashlib.sha256()
    cantidad_archivos = 0

    for archivo in sorted(ruta.rglob("*")):
        if not archivo.is_file():
            continue

        ruta_relativa = archivo.relative_to(ruta).as_posix()

        if ruta_relativa in excluir_archivos:
            continue

        if any(parte in excluir_carpetas for parte in archivo.parts):
            continue

        if extensiones and archivo.suffix.lower() not in extensiones:
            continue

        contenido = archivo.read_bytes()
        contenido = normalizar_contenido_texto(contenido)

        hash_archivo = hashlib.sha256(contenido).hexdigest()

        cantidad_archivos += 1

        hash_total.update(ruta_relativa.encode("utf-8"))
        hash_total.update(hash_archivo.encode("utf-8"))

    return hash_total.hexdigest(), cantidad_archivos


def main():
    ruta_source = "source"
    extensiones = {".py", ".sas", ".sql", ".txt", ".yml", ".yaml"}

    output_file = Path("source/version_manifest.yml")

    hash_actual, cantidad_archivos = hash_carpeta(
        ruta_source,
        extensiones=extensiones,
        excluir_archivos={
            "version_manifest.yml",
            "hash_source.txt"
        },
        excluir_carpetas={
            "__pycache__",
            ".ipynb_checkpoints"
        }
    )

    contenido = f"""fecha_generacion: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
carpeta_evaluada: "{ruta_source}"
algoritmo: "SHA256"
archivos: {cantidad_archivos}
clave: "{hash_actual}"
"""

    output_file.write_text(contenido, encoding="utf-8")


if __name__ == "__main__":
    main()

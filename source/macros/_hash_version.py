import hashlib
from datetime import datetime
from pathlib import Path


def hash_archivo(path_archivo):
    """Calcula hash SHA256 de un archivo normalizando saltos de línea."""
    contenido = path_archivo.read_bytes()
    contenido = contenido.replace(b"\r\n", b"\n")
    return hashlib.sha256(contenido).hexdigest()


def hash_carpeta(ruta_carpeta, extensiones=None, excluir_archivos=None, excluir_carpetas=None):
    """Calcula hash general y detalle por archivo."""
    ruta = Path(ruta_carpeta)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe la carpeta: {ruta.resolve()}")

    hash_total = hashlib.sha256()
    excluir_archivos = excluir_archivos or set()
    excluir_carpetas = excluir_carpetas or set()

    detalle_archivos = []

    for archivo in sorted(ruta.rglob("*")):
        if not archivo.is_file():
            continue

        ruta_relativa = archivo.relative_to(ruta).as_posix()

        if ruta_relativa in excluir_archivos:
            continue

        if any(carpeta in archivo.parts for carpeta in excluir_carpetas):
            continue

        if extensiones and archivo.suffix.lower() not in extensiones:
            continue

        hash_individual = hash_archivo(archivo)

        detalle_archivos.append({
            "ruta": ruta_relativa,
            "hash": hash_individual
        })

        hash_total.update(ruta_relativa.encode("utf-8"))
        hash_total.update(hash_individual.encode("utf-8"))

    return hash_total.hexdigest(), detalle_archivos


def main():
    ruta_source = "source"
    extensiones = {".py", ".sas", ".sql", ".txt"}

    output_file = Path("source/version_manifest.yml")

    hash_actual, detalle_archivos = hash_carpeta(
        ruta_source,
        extensiones=extensiones,
        excluir_archivos={
            "version_manifest.yml",
            "macros/_hash_version.py" 
        },
        excluir_carpetas={
            "__pycache__",
            ".ipynb_checkpoints"
        }
    )

    archivos_yml = "\n".join(
        f'  - ruta: "{item["ruta"]}"\n    hash: "{item["hash"]}"'
        for item in detalle_archivos
    )

    contenido = f"""fecha_generacion: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
carpeta_evaluada: "{ruta_source}"
algoritmo: "SHA256"
archivos: {len(detalle_archivos)}
clave: "{hash_actual}"
detalle_archivos:
{archivos_yml}
"""

    output_file.write_text(contenido, encoding="utf-8")


if __name__ == "__main__":
    main()

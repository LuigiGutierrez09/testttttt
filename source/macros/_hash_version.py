import hashlib
from datetime import datetime
from pathlib import Path


def hash_carpeta(ruta_carpeta, extensiones=None, excluir_archivos=None):
    """Calcula un hash SHA256 considerando rutas relativas y contenido."""
    ruta = Path(ruta_carpeta)
    hash_total = hashlib.sha256()

    excluir_archivos = excluir_archivos or set()
    cantidad_archivos = 0

    for archivo in sorted(ruta.rglob("*")):
        if not archivo.is_file():
            continue

        ruta_relativa = archivo.relative_to(ruta).as_posix()

        if ruta_relativa in excluir_archivos:
            continue

        if extensiones and archivo.suffix.lower() not in extensiones:
            continue

        cantidad_archivos += 1

        hash_total.update(ruta_relativa.encode("utf-8"))

        with open(archivo, "rb") as f:
            while bloque := f.read(1024 * 1024):
                hash_total.update(bloque)

    return hash_total.hexdigest(), cantidad_archivos


def main():
    ruta_source = "source"
    extensiones = {".py", ".sas", ".sql", ".txt"}

    source_dir = Path("source")
    source_dir.mkdir(exist_ok=True)

    output_file = source_dir / "version_manifest.yml"

    hash_actual, cantidad_archivos = hash_carpeta(
        ruta_source,
        extensiones=extensiones,
        excluir_archivos={"version_manifest.yml"}
    )

    contenido = f"""fecha_generacion: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
carpeta_evaluada: "{ruta_source}"
algoritmo: "SHA256"
archivos: {cantidad_archivos}
clave: "{hash_actual}"
"""

    output_file.write_text(contenido, encoding="utf-8")

    #print(f"Hash generado: {hash_actual}")
    #print(f"Cantidad de archivos incluidos: {cantidad_archivos}")
    #print(f"Archivo creado: {output_file}")


if __name__ == "__main__":
    main()

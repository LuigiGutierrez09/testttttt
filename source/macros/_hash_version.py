import hashlib
from datetime import datetime
from pathlib import Path


def hash_carpeta(ruta_carpeta, extensiones=None):
    """Calcula un hash SHA256 considerando rutas relativas y contenido."""
    ruta = Path(ruta_carpeta)
    hash_total = hashlib.sha256()

    for archivo in sorted(ruta.rglob("*")):
        if not archivo.is_file():
            continue

        if extensiones and archivo.suffix.lower() not in extensiones:
            continue

        ruta_relativa = archivo.relative_to(ruta).as_posix()
        hash_total.update(ruta_relativa.encode("utf-8"))

        with open(archivo, "rb") as f:
            while bloque := f.read(1024 * 1024):
                hash_total.update(bloque)

    return hash_total.hexdigest()


def main():
    ruta_source = "src"  # En GitHub Actions usa ruta relativa, no C:\...

    hash_actual = hash_carpeta(
        ruta_source,
        extensiones={".py", ".sas", ".sql", ".txt"}
    )

    source_dir = Path("source")
    source_dir.mkdir(exist_ok=True)

    output_file =  source_dir/"hash_source.txt"

    contenido = f"""Hash automático de carpeta source/src

Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Carpeta evaluada: {ruta_source}
Extensiones consideradas: .py, .sas, .sql, .txt

HASH_SHA256:
{hash_actual}
"""

    output_file.write_text(contenido, encoding="utf-8")

    print(f"Hash generado: {hash_actual}")
    print(f"Archivo creado: {output_file}")


if __name__ == "__main__":
    main()

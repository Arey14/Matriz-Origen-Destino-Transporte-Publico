import subprocess
import shutil
import os

def main():
    print("Iniciando la compilación del Trabajo Final de Tesis...")
    
    # Directorio base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)

    # Definir los archivos de entrada ordenados
    input_files = [
        "TPS/secciones/metadata.yaml",
        "TPS/secciones/01_Introduccion.md",
        "TPS/secciones/02_Marco_Teorico.md",
        "TPS/secciones/03_Metodologia.md",
        "TPS/secciones/04_Resultados_y_Discusion.md",
        "TPS/secciones/05_Conclusion.md",
        "TPS/secciones/06_Bibliografia.md",
        "TPS/secciones/07_Anexos.md"
    ]

    output_pdf = "TPS/Trabajo final.pdf"
    copy_pdf = "../Documento Tesis.pdf"

    # Comando de Pandoc
    cmd = [
        "pandoc"
    ] + input_files + [
        "-o", output_pdf,
        "--pdf-engine=xelatex"
    ]

    print(f"Ejecutando comando: {' '.join(cmd)}")
    
    try:
        # Ejecutamos el comando de pandoc
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Compilación en Pandoc finalizada con éxito.")
        
        # Hacemos una copia en el directorio de Tesis principal con el nombre solicitado
        shutil.copy2(output_pdf, copy_pdf)
        print(f"Copia del documento creada con éxito en: {os.path.abspath(copy_pdf)}")
        
        print("\n¡Trabajo Final generado y verificado correctamente!")
        print(f"- Archivo 1: {os.path.abspath(output_pdf)}")
        print(f"- Archivo 2: {os.path.abspath(copy_pdf)}")

    except subprocess.CalledProcessError as e:
        print("\nError durante la compilación de Pandoc:")
        print(e.stderr)
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()

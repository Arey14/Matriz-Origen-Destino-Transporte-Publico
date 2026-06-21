import subprocess
import shutil
import os

def main():
    print("Iniciando la compilación de la Presentación de Tesis...")
    
    # Directorio base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_dir)

    # Definir rutas
    input_md = "TPS/presentacion/presentacion.md"
    output_pdf = "TPS/presentacion/Presentacion_Tesis.pdf"
    copy_pdf = "../Presentacion Tesis.pdf"

    # Comando de Pandoc Beamer
    cmd = [
        "pandoc",
        input_md,
        "-o", output_pdf,
        "-t", "beamer",
        "--pdf-engine=xelatex"
    ]

    print(f"Ejecutando comando: {' '.join(cmd)}")
    
    try:
        # Ejecutamos el comando de pandoc
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Compilación de diapositivas en Pandoc/Beamer finalizada con éxito.")
        
        # Hacemos una copia en el directorio de Tesis principal
        shutil.copy2(output_pdf, copy_pdf)
        print(f"Copia de la presentación creada en: {os.path.abspath(copy_pdf)}")
        
        print("\n¡Presentación en PDF generada y verificada correctamente!")
        print(f"- Archivo 1: {os.path.abspath(output_pdf)}")
        print(f"- Archivo 2: {os.path.abspath(copy_pdf)}")

    except subprocess.CalledProcessError as e:
        print("\nError durante la compilación de Pandoc/Beamer:")
        print(e.stderr)
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()

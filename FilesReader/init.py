import os


def listar_archivos_y_carpetas(ruta):
    for directorio_raiz, directorios, archivos in os.walk(ruta):
        # Ignora la carpeta .git
        if '.git' in directorios:
            directorios.remove('.git')
        if 'OCRIM' in directorios:
            directorios.remove('OCRIM')

        nivel = directorio_raiz.count(os.path.sep)
        indentacion = ' ' * 2 * nivel
        print(f"{indentacion}{os.path.basename(directorio_raiz)}:")
        sub_indentacion = ' ' * 2 * (nivel + 1)

        for archivo in archivos:
            print(f"{sub_indentacion}- {archivo}")

        for carpeta in directorios:
            carpeta_ruta = os.path.join(directorio_raiz, carpeta)
            listar_archivos_y_carpetas(carpeta_ruta)


if __name__ == "__main__":
    ruta = "D:/Repositorios/OpenAIProjects"
    listar_archivos_y_carpetas(ruta)

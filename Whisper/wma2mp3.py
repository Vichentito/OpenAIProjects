import ffmpeg

input_file = "Test.wma"
output_file = "Test.mp3"

# Usamos la función `input` para cargar el archivo de entrada
stream = ffmpeg.input(input_file)

# Usamos la función `output` para especificar el formato de salida y el nombre del archivo de salida
stream = ffmpeg.output(stream, output_file, format='mp3')

# Ejecutamos el comando de conversión
ffmpeg.run(stream)

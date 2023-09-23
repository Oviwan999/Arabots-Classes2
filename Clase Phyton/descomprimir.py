import zipfile
mi_zip = zipfile.ZipFile('mi_gran_directorio.zip', 'w')
mi_zip.write('Instrucciones')

mi_zip.close()
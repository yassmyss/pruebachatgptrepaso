# Docker Desktop / WSL

## Docker Desktop no inicia en Windows
1. Confirmar que la virtualización está habilitada.
2. Ejecutar `wsl --status` y comprobar que WSL está disponible.
3. Ejecutar `wsl --shutdown`, esperar unos segundos y volver a iniciar Docker Desktop.
4. Revisar el estado del servicio Docker Desktop Service desde Servicios de Windows.
5. Si WSL informa de componentes desactualizados, ejecutar `wsl --update` con permisos adecuados.
6. No eliminar distribuciones, imágenes, volúmenes ni datos del usuario como primera medida.
7. Si persiste el error, recopilar el mensaje exacto y los logs antes de escalar.

## Escalado
Escalar a N2 cuando haya corrupción de WSL, errores persistentes del hipervisor o riesgo de pérdida de datos.

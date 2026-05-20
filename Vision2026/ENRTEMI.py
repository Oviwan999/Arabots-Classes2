            return

        ahora = time.time()
        if ganador.label == self.ultimo_ganador_anunciado:
            return
        if ahora - self.ultimo_anuncio_tiempo < self.COOLDOWN_VOZ_SEG:
            return

        porcentaje = int(ganador.conf * 100)
        print(f"[prioridad] {ganador.label} ({porcentaje}%, soporte {ganador.support})")
        hablar_nativo(f"Atencion: {ganador.label}")
        self.ultimo_ganador_anunciado = ganador.label
        self.ultimo_anuncio_tiempo = ahora

    def dibujar(self, frame: np.ndarray, detecciones, fps_ia: float) -> np.ndarray:
        salida = frame.copy()

        for det in detecciones[:8]:
            x1, y1, x2, y2 = det.box.astype(int)
            color = (0, 255, 0) if det.conf >= self.conf_minima(det.label) else (0, 220, 255)
            grosor = 4 if det.support <= 1 else 6

            cv2.rectangle(salida, (x1, y1), (x2, y2), color, grosor)

            texto = f"{det.label} {int(det.conf * 100)}% x{det.support}"
            escala = 0.85
            espesor = 2
            (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, espesor)
            y_texto = max(28, y1 - 10)
            cv2.rectangle(salida, (x1, y_texto - th - 8), (x1 + tw + 8, y_texto + 5), (0, 0, 0), -1)
            cv2.putText(
                salida,
                texto,
                (x1 + 4, y_texto),
                cv2.FONT_HERSHEY_SIMPLEX,
                escala,
                color,
                espesor,
                cv2.LINE_AA,
            )

        total_tta = len(self.angulos) + (4 if self.USAR_PERSPECTIVA_TTA else 0)
        estado = f"IA {fps_ia:04.1f} FPS | det {len(detecciones)} | TTA {total_tta}"
        cv2.rectangle(salida, (10, 10), (430, 48), (0, 0, 0), -1)
        cv2.putText(salida, estado, (20, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        return salida

    def hilo_ia(self):
        print("[ia] Optimizando angulo, perspectiva y estabilidad temporal...")
        ultimo_tiempo = time.time()
        fps_ia = 0.0

        while self.corriendo:
            frame = self.obtener_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            alto, ancho = frame.shape[:2]
            preparado = self.filtro_anti_reflejo(frame)
            frames_batch, matrices_a_original, nombres_tta = self.crear_tta(preparado)

            try:
                results = self.model(
                    frames_batch,
                    conf=self.CONF_INFERENCIA,
                    iou=0.55,
                    verbose=False,
                    imgsz=self.IMGSZ,
                )
            except Exception as exc:
                print(f"[ia] Error en inferencia: {exc}")
                time.sleep(0.05)
                continue

            detecciones_crudas = self.extraer_detecciones(
                results,
                matrices_a_original,
                nombres_tta,
                ancho,
                alto,
            )
            detecciones = self.fusionar_detecciones(detecciones_crudas)

            ahora = time.time()
            dt = max(ahora - ultimo_tiempo, 1e-6)
            fps_ia = (fps_ia * 0.85) + ((1.0 / dt) * 0.15)
            ultimo_tiempo = ahora

            ganador = self.elegir_ganador(detecciones)
            self.anunciar_si_toca(ganador)
            self.actualizar_anotaciones(self.dibujar(frame, detecciones, fps_ia))

            time.sleep(0.001)


def abrir_camara(indice: int, ancho: int, alto: int, exposicion):
    cap = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)

    if exposicion is not None:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, exposicion)

    return cap


def parse_args():
    def parse_exposure(valor: str):
        if valor.lower() in {"none", "auto", "off"}:
            return None
        return float(valor)

    parser = argparse.ArgumentParser(description="Vision de competencia ARABOTS 2026")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, help="Ruta al .engine, .pt u otro peso RT-DETR")
    parser.add_argument("--camera", type=int, default=0, help="Indice de camara")
    parser.add_argument("--width", type=int, default=1280, help="Ancho de captura")
    parser.add_argument("--height", type=int, default=720, help="Alto de captura")
    parser.add_argument("--exposure", type=parse_exposure, default=-7, help="Exposicion manual; usa --exposure none para omitir")
    parser.add_argument("--fast", action="store_true", help="Menos TTA para subir FPS si la GPU va justa")
    parser.add_argument("--no-perspective", action="store_true", help="Desactiva TTA de perspectiva")
    parser.add_argument("--rotate-no-crop", action="store_true", help="Escala rotaciones para evitar recorte en las esquinas")
    return parser.parse_args()


def main():
    args = parse_args()
    model_path = str(args.model)

    if not Path(model_path).exists():
        print(f"[inicio] Aviso: no encuentro el modelo en esta ruta: {model_path}")
        print("[inicio] Si estas en otra PC, pasa la ruta con --model")

    robot = RobotVisionCompetencia(model_path)
    if args.fast:
        robot.angulos = [0, 15, -15, 30, -30, 45, -45]
        robot.USAR_PERSPECTIVA_TTA = False
    if args.no_perspective:
        robot.USAR_PERSPECTIVA_TTA = False
    if args.rotate_no_crop:
        robot.ROTAR_SIN_RECORTAR = True

    hilo = threading.Thread(target=robot.hilo_ia, daemon=True)
    hilo.start()

    exposicion = args.exposure
    cap = abrir_camara(args.camera, args.width, args.height, exposicion)

    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la camara {args.camera}")

    print("[inicio] Listo. Presiona q o ESC para salir.")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("[camara] No se pudo leer frame.")
                break

            robot.actualizar_frame(frame)
            display = robot.obtener_anotaciones()
            if display is None:
                display = frame

            cv2.imshow("ARABOTS 2026 - COMPETENCIA", display)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla in (ord("q"), 27):
                break
    finally:
        robot.corriendo = False
        hilo.join(timeout=1.0)
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
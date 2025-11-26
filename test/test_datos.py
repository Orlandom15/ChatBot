from config.database import NeonDatabase

def verificar_datos():
    print("🔍 VERIFICANDO DATOS EN LA BASE DE DATOS...")
    
    db = NeonDatabase()
    
    # 1. Verificar conexión
    print("1. 🔌 Probando conexión...")
    if db.test_connection():
        print("   ✅ Conexión exitosa")
    else:
        print("   ❌ Error de conexión")
        return
    
    # 2. Verificar estadísticas
    print("2. 📊 Obteniendo estadísticas...")
    estadisticas = db.get_estadisticas_estudiantes()
    print(f"   Estadísticas: {estadisticas}")
    
    # 3. Verificar estudiantes pendientes
    print("3. 📋 Obteniendo estudiantes pendientes...")
    estudiantes = db.get_estudiantes_pendientes_inscripcion()
    print(f"   Estudiantes pendientes: {len(estudiantes)}")
    for est in estudiantes[:3]:  # Mostrar primeros 3
        print(f"      - {est['matricula']}: {est['nombre']} {est['apellido']}")
    
    # 4. Verificar carreras
    print("4. 🎓 Obteniendo carreras...")
    carreras = db.get_carreras()
    print(f"   Carreras: {len(carreras)}")
    for carrera in carreras:
        print(f"      - {carrera['codigo']}: {carrera['nombre']}")

if __name__ == '__main__':
    verificar_datos()
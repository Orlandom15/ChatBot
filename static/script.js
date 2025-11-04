document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const suggestions = document.querySelectorAll('.suggestion');
    const currentTimeElement = document.getElementById('currentTime');
    
    // Generar session ID único si no existe
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
        sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatSessionId', sessionId);
    }
    
    // Mostrar hora actual en el primer mensaje
    const now = new Date();
    currentTimeElement.textContent = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    // Cargar historial del chat si existe
    loadChatHistory();
    
    // Función para agregar mensaje al chat (ahora puede mostrar tablas)
    function addMessage(content, isUser = false, isTable = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const now = new Date();
        const timeString = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        if (isTable) {
            // Si es una tabla, insertar el HTML directamente
            messageDiv.innerHTML = content;
        } else {
            // Mensaje normal
            messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
                <div class="message-time">${timeString}</div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll automático al último mensaje
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Guardar en localStorage para persistencia (solo mensajes normales)
        if (!isTable) {
            saveMessageToHistory(content, isUser, timeString);
        }
    }
    
    // Función para crear tabla de estudiantes pendientes
    function crearTablaEstudiantesPendientes(estudiantes) {
        let html = `
        <div class="message-content">
            <h3>📋 Estudiantes Pendientes de Inscripción</h3>
            <p><strong>Total: ${estudiantes.length} estudiantes</strong></p>
            
            <table class="tabla-universidad">
                <thead>
                    <tr>
                        <th>Matrícula</th>
                        <th>Nombre</th>
                        <th>Carrera</th>
                        <th>Semestre</th>
                        <th>Fecha Inscripción</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        estudiantes.forEach(est => {
            html += `
                    <tr>
                        <td><strong>${est.matricula}</strong></td>
                        <td>${est.nombre} ${est.apellido}</td>
                        <td>${est.carrera}</td>
                        <td>${est.semestre}</td>
                        <td>${new Date(est.fecha_inscripcion).toLocaleDateString()}</td>
                        <td class="estado-pendiente">❌ Pendiente</td>
                    </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
            
            <div style="margin-top: 1rem;">
                <button class="btn-descargar" onclick="descargarReporte()">📥 Descargar Reporte</button>
                <button class="btn-ver-mas" onclick="verTodosEstudiantes()">👥 Ver Todos los Estudiantes</button>
            </div>
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        return html;
    }
    
    // 🔥 NUEVA FUNCIÓN: Tabla de reporte completo con todos los estudiantes
    function crearTablaReporteCompleto(estudiantes) {
        const totalEstudiantes = estudiantes.length;
        const pagados = estudiantes.filter(est => est.estado_pago.includes('✅')).length;
        const pendientes = estudiantes.filter(est => est.estado_pago.includes('❌')).length;
        
        let html = `
        <div class="message-content">
            <h3>📊 REPORTE COMPLETO - TODOS LOS ESTUDIANTES</h3>
            
            <div class="estadisticas-rapidas" style="margin-bottom: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 5px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div>
                        <strong>👥 Total:</strong> ${totalEstudiantes}
                    </div>
                    <div style="color: #28a745;">
                        <strong>✅ Pagados:</strong> ${pagados}
                    </div>
                    <div style="color: #dc3545;">
                        <strong>❌ Pendientes:</strong> ${pendientes}
                    </div>
                    <div>
                        <strong>📅 Fecha:</strong> ${new Date().toLocaleDateString()}
                    </div>
                </div>
            </div>
            
            <div class="filtros-estudiantes">
                <input type="text" id="filtroReporte" placeholder="🔍 Buscar por nombre, matrícula o carrera..." 
                       style="width: 100%; padding: 0.5rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 5px;">
            </div>
            
            <table class="tabla-universidad tabla-reporte-completo">
                <thead>
                    <tr>
                        <th>Matrícula</th>
                        <th>Nombre Completo</th>
                        <th>Carrera</th>
                        <th>Semestre</th>
                        <th>Email</th>
                        <th>Teléfono</th>
                        <th>Estado Pago</th>
                        <th>Fecha Registro</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        estudiantes.forEach(est => {
            const fechaRegistro = est.fecha_registro ? new Date(est.fecha_registro).toLocaleDateString() : 'N/A';
            const claseEstado = est.estado_pago.includes('✅') ? 'estado-pagado' : 'estado-pendiente';
            
            html += `
                    <tr class="fila-reporte">
                        <td><strong>${est.matricula}</strong></td>
                        <td>${est.nombre_completo}</td>
                        <td>${est.carrera}</td>
                        <td>${est.semestre}</td>
                        <td>${est.email || 'N/A'}</td>
                        <td>${est.telefono || 'N/A'}</td>
                        <td class="${claseEstado}">${est.estado_pago}</td>
                        <td>${fechaRegistro}</td>
                    </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
            
            <div style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <button class="btn-descargar" onclick="descargarReporteCompleto()">📥 Descargar Reporte Completo</button>
                <button class="btn-ver-mas" onclick="filtrarSoloPendientesReporte()">❌ Ver Solo Pendientes</button>
                <button class="btn-ver-mas" onclick="filtrarSoloPagadosReporte()">✅ Ver Solo Pagados</button>
                <button class="btn-ver-mas" onclick="mostrarTodosReporte()">👥 Mostrar Todos</button>
            </div>
            
            <div style="margin-top: 1rem; font-size: 0.8rem; color: #666;">
                💡 <strong>Consejos:</strong> Usa el campo de búsqueda para filtrar. Haz clic en los botones para ver estados específicos.
            </div>
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        // Agregar el script de filtrado después de insertar el HTML
        setTimeout(() => {
            inicializarFiltroReporte();
        }, 100);
        
        return html;
    }
    
    // Función para crear cards de estadísticas
    function crearEstadisticasCards(estadisticas) {
        let html = `
        <div class="message-content">
            <h3>📊 Estadísticas Universitarias</h3>
            
            <div class="estadisticas-grid">
                <div class="estadistica-card">
                    <div class="numero">${estadisticas.total_estudiantes}</div>
                    <div class="label">Total Estudiantes</div>
                </div>
                <div class="estadistica-card">
                    <div class="numero">${estadisticas.inscritos_pagados}</div>
                    <div class="label">Inscripción Pagada</div>
                </div>
                <div class="estadistica-card">
                    <div class="numero">${estadisticas.pendientes_inscripcion}</div>
                    <div class="label">Pendientes de Pago</div>
                </div>
            </div>
            
            <h4 style="margin-top: 1.5rem;">🎓 Distribución por Carrera</h4>
            <table class="tabla-universidad">
                <thead>
                    <tr>
                        <th>Carrera</th>
                        <th>Estudiantes</th>
                        <th>Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        estadisticas.por_carrera.forEach(carrera => {
            const porcentaje = ((carrera.cantidad / estadisticas.total_estudiantes) * 100).toFixed(1);
            html += `
                    <tr>
                        <td>${carrera.carrera}</td>
                        <td>${carrera.cantidad}</td>
                        <td>${porcentaje}%</td>
                    </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        return html;
    }
    
    // Función para crear lista de carreras
    function crearListaCarreras(carreras) {
        let html = `
        <div class="message-content">
            <h3>🎓 Carreras Disponibles</h3>
            
            <table class="tabla-universidad">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Carrera</th>
                        <th>Duración</th>
                        <th>Costo Inscripción</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        carreras.forEach(carrera => {
            html += `
                    <tr>
                        <td><strong>${carrera.codigo}</strong></td>
                        <td>${carrera.nombre}</td>
                        <td>${carrera.duracion_semestres} semestres</td>
                        <td>$${carrera.costo_inscripcion}</td>
                    </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
            
            <div class="reporte-section">
                <strong>💡 Información:</strong> Todas las carreras incluyen:
                <br>• Material didáctico digital
                <br>• Acceso a laboratorios
                <br>• Biblioteca virtual
                <br>• Seguro estudiantil
            </div>
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        return html;
    }
    
    // Función para crear sección de reporte
    function crearSeccionReporte(reporte) {
        let html = `
        <div class="message-content">
            <h3>📄 Reporte Generado</h3>
            
            <div class="reporte-section">
                <p><strong>✅ Reporte generado exitosamente</strong></p>
                <p><strong>Tipo:</strong> ${reporte.tipo}</p>
                <p><strong>ID del Reporte:</strong> ${reporte.reporte_id}</p>
                <p><strong>Estudiantes en reporte:</strong> ${reporte.total_pendientes}</p>
                <p><strong>Fecha de generación:</strong> ${new Date(reporte.fecha_generacion).toLocaleDateString()}</p>
            </div>
            
            <div style="margin-top: 1rem;">
                <button class="btn-descargar" onclick="descargarExcel()">📊 Descargar Excel</button>
                <button class="btn-descargar" onclick="descargarPDF()">📄 Descargar PDF</button>
                <button class="btn-ver-mas" onclick="verReporteCompleto()">👀 Ver Reporte Completo</button>
            </div>
            
            <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                💡 El reporte incluye: Matrícula, Nombre, Carrera, Semestre, Fecha de Inscripción
            </div>
        </div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        return html;
    }
    
    window.verTodosEstudiantes = async function() {
        try {
            addMessage('🔍 Cargando reporte completo de todos los estudiantes...', false);
            showTypingIndicator();
            
            // 🔥 CAMBIA ESTA URL por tu endpoint real
            const response = await fetch('/api/estudiantes/todos'); // o la ruta correcta
            const data = await response.json();
            
            hideTypingIndicator();
            
            if (data.success && data.estudiantes && data.estudiantes.length > 0) {
                const tablaHTML = crearTablaReporteCompleto(data.estudiantes);
                addMessage(tablaHTML, false, true);
            } else {
                addMessage('❌ No se pudieron cargar los estudiantes para el reporte.', false);
            }
            
        } catch (error) {
            hideTypingIndicator();
            console.error('Error cargando reporte:', error);
            addMessage('❌ Error al cargar el reporte completo. Verifica la conexión con el servidor.', false);
        }
    };
    
    window.descargarReporteCompleto = function() {
        alert('📥 Descargando reporte completo en Excel...');
        // Aquí iría la lógica real para descargar Excel
    };
    
    window.filtrarSoloPendientesReporte = function() {
        const filas = document.querySelectorAll('.fila-reporte');
        filas.forEach(fila => {
            if (fila.textContent.includes('❌ Pendiente')) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    };
    
    window.filtrarSoloPagadosReporte = function() {
        const filas = document.querySelectorAll('.fila-reporte');
        filas.forEach(fila => {
            if (fila.textContent.includes('✅ Pagado')) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    };
    
    window.mostrarTodosReporte = function() {
        const filas = document.querySelectorAll('.fila-reporte');
        filas.forEach(fila => {
            fila.style.display = '';
        });
    };
    
    // Función para inicializar el filtro del reporte
    function inicializarFiltroReporte() {
        const filtroInput = document.getElementById('filtroReporte');
        if (filtroInput) {
            filtroInput.addEventListener('input', function(e) {
                const texto = e.target.value.toLowerCase();
                const filas = document.querySelectorAll('.fila-reporte');
                
                filas.forEach(fila => {
                    const textoFila = fila.textContent.toLowerCase();
                    if (textoFila.includes(texto)) {
                        fila.style.display = '';
                    } else {
                        fila.style.display = 'none';
                    }
                });
            });
        }
    }
    
    window.descargarReporte = function() {
        alert('📥 Función de descarga activada - En una implementación real, esto generaría un archivo Excel');
    };
    
    window.descargarExcel = function() {
        alert('📊 Descargando reporte en formato Excel...');
    };
    
    window.descargarPDF = function() {
        alert('📄 Descargando reporte en formato PDF...');
    };
    
    window.verReporteCompleto = function() {
        // 🔥 ESTA ES LA FUNCIÓN QUE SE EJECUTA AL HACER CLIC EN "REPORTE"
        window.verTodosEstudiantes();
    };

    // Función para guardar mensajes en el historial local
    function saveMessageToHistory(message, isUser, timestamp) {
        let chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        chatHistory.push({
            message: message,
            isUser: isUser,
            timestamp: timestamp,
            sessionId: sessionId
        });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }
    
    // Función para cargar historial del chat
    function loadChatHistory() {
        const chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');
        const currentSessionHistory = chatHistory.filter(msg => msg.sessionId === sessionId);
        
        // Limpiar mensajes actuales excepto el primero
        const initialMessage = chatMessages.querySelector('.bot-message');
        chatMessages.innerHTML = '';
        if (initialMessage) {
            chatMessages.appendChild(initialMessage);
        }
        
        // Recargar historial
        currentSessionHistory.forEach(msg => {
            addMessage(msg.message, msg.isUser);
        });
        
        // Scroll al final
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Función para mostrar indicador de escritura
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Función para ocultar indicador de escritura
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Función para enviar mensaje al backend (AJAX)
    async function sendMessageToBackend(message) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            return { 
                success: false,
                bot_response: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta nuevamente.'
            };
        }
    }

    // Función principal para procesar mensajes del usuario
    async function processUserMessage(message) {
        // Agregar mensaje del usuario inmediatamente
        addMessage(message, true);
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Mostrar indicador de escritura
        showTypingIndicator();
        
        try {
            // Enviar mensaje al backend
            const data = await sendMessageToBackend(message);
            
            // Ocultar indicador de escritura
            hideTypingIndicator();
            
            if (data.success) {
                // Detectar si la respuesta contiene datos para tablas
                if (data.intent === 'estadisticas_universidad' && data.estadisticas) {
                    const tablaHTML = crearEstadisticasCards(data.estadisticas);
                    addMessage(tablaHTML, false, true);
                } else if (data.intent === 'inscripciones_pendientes' && data.estudiantes) {
                    const tablaHTML = crearTablaEstudiantesPendientes(data.estudiantes);
                    addMessage(tablaHTML, false, true);
                } else if (data.intent === 'carreras' && data.carreras) {
                    const tablaHTML = crearListaCarreras(data.carreras);
                    addMessage(tablaHTML, false, true);
                } else if (data.intent === 'reporte_generado' && data.reporte) {
                    const tablaHTML = crearSeccionReporte(data.reporte);
                    addMessage(tablaHTML, false, true);
                } else if (data.intent === 'todos_estudiantes' && data.estudiantes) {
                    // 🔥 NUEVO: Procesar reporte completo
                    const tablaHTML = crearTablaReporteCompleto(data.estudiantes);
                    addMessage(tablaHTML, false, true);
                } else {
                    // Respuesta normal del bot
                    addMessage(data.bot_response, false);
                }
            } else {
                addMessage(data.bot_response || 'Error en la respuesta del servidor', false);
            }
            
        } catch (error) {
            hideTypingIndicator();
            addMessage('Lo siento, hubo un error al procesar tu mensaje.', false);
        } finally {
            // Rehabilitar entrada
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }
    
    // Evento para enviar mensaje al hacer clic en el botón
    sendButton.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            processUserMessage(message);
        }
    });
    
    // Evento para enviar mensaje al presionar Enter
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                processUserMessage(message);
            }
        }
    });
    
    // Evento para las sugerencias
    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            processUserMessage(question);
        });
    });
    
    // Focus automático en el input al cargar
    userInput.focus();
    
    // Función para limpiar el chat (opcional)
    window.clearChat = function() {
        localStorage.removeItem('chatHistory');
        const initialMessage = chatMessages.querySelector('.bot-message');
        chatMessages.innerHTML = '';
        if (initialMessage) {
            chatMessages.appendChild(initialMessage);
        }
        
        // Regenerar session ID
        sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatSessionId', sessionId);
    };
});
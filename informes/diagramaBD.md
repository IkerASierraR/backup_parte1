# Diagrama Entidad-Relación (Base de Datos)

El siguiente código corresponde al diagrama de entidad-relación de la base de datos principal del proyecto (`01-sisintupt-dump.sql`).

Puedes copiar y pegar este código directamente en [dbdiagram.io](https://dbdiagram.io) para visualizar y editar el diagrama de manera interactiva.

```dbml
Table administrativo {
  IdAdministrativo int(10) [primary key, not null]
  IdUsuario int(10) [not null]
  Escuela int(10)
  Turno enum('Mañana','Tarde','Noche','Completo') [not null]
  Extension varchar(10)
  FechaIncorporacion date [not null]
}

Table auditoriareserva {
  IdAudit int(10) [primary key, not null]
  IdReserva int(10) [not null]
  EstadoAnterior varchar(50) [not null]
  EstadoNuevo varchar(50) [not null]
  FechaCambio datetime [not null]
  UsuarioCambio int(10)
}

Table bloqueshorarios {
  IdBloque int(10) [primary key, not null]
  Orden int(11) [not null]
  Nombre varchar(50) [not null]
  HoraInicio time [not null]
  HoraFinal time [not null]
}

Table cita_policlinico {
  IdCita int(10) [primary key, not null]
  Estudiante int(10) [not null]
  Medico int(10) [not null]
  TipoAtencion int(10) [not null]
  Bloque int(10) [not null]
  Fecha date [not null]
  Motivo text
  Estado varchar(30) [not null]
  FechaSolicitud datetime [not null]
}

Table cita_psicologia {
  IdCita int(10) [primary key, not null]
  Estudiante int(10) [not null]
  Psicologo int(10) [not null]
  Bloque int(10) [not null]
  Fecha date [not null]
  Motivo text
  Estado varchar(30) [not null]
  FechaSolicitud datetime [not null]
}

Table cursos {
  IdCurso int(10) [primary key, not null]
  Nombre varchar(100) [not null]
  Facultad int(10) [not null]
  Escuela int(10) [not null]
  Ciclo varchar(5) [not null]
  Estado tinyint(1) [not null]
}

Table docente {
  IdDocente bigint(20) [primary key, not null]
  IdUsuario int(10) [not null]
  CodigoDocente varchar(255) [not null]
  Escuela int(10)
  TipoContrato enum('Tiempo_Completo','Medio_Tiempo','Contratado') [not null]
  Especialidad varchar(100)
  FechaIncorporacion date [not null]
}

Table escuela {
  IdEscuela int(10) [primary key, not null]
  IdFacultad int(10) [not null]
  Nombre varchar(255) [not null]
}

Table espacio {
  IdEspacio int(10) [primary key, not null]
  Codigo varchar(20) [not null]
  Nombre varchar(100) [not null]
  Tipo enum('Laboratorio','Salon') [not null]
  Capacidad int(11) [not null]
  Equipamiento text
  Escuela int(10) [not null]
  Estado int(11) [not null]
}

Table estudiante {
  IdEstudiante bigint(20) [primary key, not null]
  IdUsuario int(10) [not null]
  Codigo varchar(255) [not null]
  Escuela int(10) [not null]
}

Table facultad {
  IdFacultad int(10) [primary key, not null]
  Nombre varchar(255) [not null]
  Abreviatura varchar(255)
}

Table horario_curso {
  IdHorarioCurso int(10) [primary key, not null]
  Curso int(10) [not null]
  Docente int(10) [not null]
  Espacio int(10) [not null]
  Bloque int(10) [not null]
  DiaSemana enum('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado') [not null]
  FechaInicio date [not null]
  FechaFin date [not null]
  Estado tinyint(1) [not null]
}

Table horarios {
  IdHorario int(10) [primary key, not null]
  espacio int(10) [not null]
  bloque int(10) [not null]
  diaSemana enum('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado') [not null]
  ocupado tinyint(1) [not null]
}

Table incidencia {
  IdIncidencia int(10) [primary key, not null]
  Reserva int(10) [not null]
  Descripcion text [not null]
  FechaReporte datetime
}

Table medico {
  IdMedico int(10) [primary key, not null]
  Nombre varchar(150) [not null]
  Estado tinyint(1) [not null]
}

Table medico_tipo_atencion {
  IdMedicoTipoAtencion int(10) [primary key, not null]
  Medico int(10) [not null]
  TipoAtencion int(10) [not null]
}

Table olimpiada_disciplina {
  IdDisciplina int(10) [primary key, not null]
  Nombre varchar(150) [not null]
  Descripcion text
  TipoParticipacion enum('individual','equipo') [not null]
  TipoPuntuacion enum('partido','posiciones') [not null]
  Reglas text
  CupoMaximoDefault int(10)
  Estado enum('activa','inactiva') [not null]
  FechaRegistro datetime
}

Table olimpiada_edicion {
  IdEdicion int(10) [primary key, not null]
  Nombre varchar(150) [not null]
  AnioInicio smallint(5) [not null]
  SemestreInicio tinyint(3) [not null]
  AnioFin smallint(5)
  SemestreFin tinyint(3)
  Estado enum('planificada','inscripcion_abierta','inscripcion_cerrada','en_curso','finalizada','cancelada') [not null]
  FechaAperturaInscripcion datetime
  FechaCierreInscripcion datetime
  FechaInicioJuegos date
  FechaFinJuegos date
  Observaciones text
  FechaRegistro datetime
}

Table olimpiada_edicion_disciplina {
  IdEdicionDisciplina int(10) [primary key, not null]
  Edicion int(10) [not null]
  Disciplina int(10) [not null]
  Categoria enum('general','varones','damas','mixto') [not null]
  CupoMaximoPorFacultad int(10)
  ReglasEspecificas text
  Lugar varchar(150)
  Estado enum('activa','inactiva') [not null]
}

Table olimpiada_inscripcion {
  IdInscripcion bigint(20) [primary key, not null]
  EdicionDisciplina int(10) [not null]
  Usuario int(10) [not null]
  Facultad int(10) [not null]
  Estado enum('inscrito','cancelado','rechazado') [not null]
  Observaciones text
  FechaInscripcion datetime
}

Table olimpiada_participacion_facultad {
  IdParticipacion int(10) [primary key, not null]
  EdicionDisciplina int(10) [not null]
  Facultad int(10) [not null]
  PartidosJugados int(10) [not null]
  PartidosGanados int(10) [not null]
  PartidosEmpatados int(10) [not null]
  PartidosPerdidos int(10) [not null]
  PuntosAFavor int(10) [not null]
  PuntosEnContra int(10) [not null]
  Puntos int(11) [not null]
  Posicion int(10)
}

Table olimpiada_resultado {
  IdResultado bigint(20) [primary key, not null]
  EdicionDisciplina int(10) [not null]
  FacultadLocal int(10) [not null]
  FacultadVisitante int(10)
  Fase varchar(50) [not null]
  Grupo varchar(50)
  FechaPartido datetime
  Lugar varchar(150)
  PuntajeLocal int(10)
  PuntajeVisitante int(10)
  FacultadGanadora int(10)
  Estado enum('programado','en_curso','finalizado','cancelado','suspendido') [not null]
  Observaciones text
  FechaRegistro datetime
}

Table olimpiada_anotador {
  IdAnotador bigint(20) [primary key, not null]
  EdicionDisciplina int(10) [not null]
  Facultad int(10) [not null]
  NombreJugador varchar(150) [not null]
  Cantidad int(10) [not null]
  Observaciones text
  FechaRegistro datetime
}

Table olimpiada_post {
  IdPost bigint(20) [primary key, not null]
  Edicion int(10) [not null]
  Titulo varchar(200) [not null]
  Contenido text [not null]
  ImagenUrl varchar(500)
  Autor varchar(150)
  FechaPublicacion datetime
}

Table olimpiada_comentario {
  IdComentario bigint(20) [primary key, not null]
  Post bigint(20) [not null]
  Usuario int(10) [not null]
  Contenido text [not null]
  FechaComentario datetime
}

Table olimpiada_resultado_posicion {
  IdResultadoPosicion bigint(20) [primary key, not null]
  EdicionDisciplina int(10) [not null]
  Facultad int(10) [not null]
  Posicion int(10) [not null]
  Puntos int(10) [not null]
  Prueba varchar(100)
  Fecha date
  Lugar varchar(150)
  Observaciones text
  Estado enum('registrado','cancelado') [not null]
  FechaRegistro datetime
}

Table psicologo {
  IdPsicologo int(10) [primary key, not null]
  Nombre varchar(150) [not null]
  Especialidad varchar(150)
  Estado tinyint(1) [not null]
}

Table reserva {
  IdReserva int(10) [primary key, not null]
  usuario int(10) [not null]
  espacio int(10) [not null]
  bloque int(10) [not null]
  curso int(10) [not null]
  fechaReserva date [not null]
  fechaSolicitud datetime [not null]
  DescripcionUso text
  CantidadEstudiantes int(11) [not null]
  Estado enum('Pendiente','Aprobada','Rechazada','Cancelada') [not null]
}

Table reserva_gestion {
  IdGestion int(10) [primary key, not null]
  IdReserva int(10) [not null]
  UsuarioGestion int(10) [not null]
  FechaGestion datetime [not null]
  Accion enum('Aprobar','Rechazar') [not null]
  Motivo text [not null]
  Comentarios text
}

Table reserva_qr {
  id bigint(20) [primary key, not null]
  token varchar(255) [not null]
  reserva_id bigint(20) [not null]
  laboratorio varchar(255) [not null]
  fecha varchar(255) [not null]
  hora varchar(255) [not null]
  estado varchar(255) [not null]
  solicitante_nombre varchar(255) [not null]
  solicitante_codigo varchar(255) [not null]
  generado_en timestamp [not null]
}

Table rol {
  IdRol int(11) [primary key, not null]
  Nombre varchar(15) [not null]
}

Table sancion {
  IdSancion bigint(20) [primary key, not null]
  Usuario int(10) [not null]
  Motivo text [not null]
  FechaInicio date [not null]
  FechaFin date [not null]
  Estado enum('ACTIVA','CUMPLIDA') [not null]
  TipoUsuario enum('DOCENTE','ESTUDIANTE') [not null]
}

Table tipo_atencion {
  IdTipoAtencion int(10) [primary key, not null]
  Nombre varchar(100) [not null]
  Estado tinyint(1) [not null]
}

Table tipodocumento {
  IdTipoDoc int(10) [primary key, not null]
  Nombre varchar(50) [not null]
  Abreviatura varchar(10) [not null]
}

Table users {
  id bigint(20) [primary key, not null]
  name varchar(255) [not null]
  email varchar(255) [not null]
  email_verified_at timestamp
  password varchar(255) [not null]
  remember_token varchar(100)
  created_at timestamp
  updated_at timestamp
}

Table usuario {
  IdUsuario int(10) [primary key, not null]
  Nombre varchar(255) [not null]
  Apellido varchar(255) [not null]
  TipoDoc int(10) [not null]
  NumDoc varchar(255)
  Rol int(11) [not null]
  Celular varchar(11)
  Genero tinyint(1)
  Estado int(11) [not null]
  FechaRegistro datetime
}

Table usuario_auth {
  IdAuth int(10) [primary key, not null]
  IdUsuario int(10) [not null]
  CorreoU varchar(100) [not null]
  Password varchar(255) [not null]
  UltimoLogin datetime
  SesionToken varchar(255)
  SesionExpira datetime
  SesionTipo varchar(20)
}

Table usuario_sesion {
  IdSesion int(10) [primary key, not null]
  IdUsuario int(10) [not null]
  Dispositivo varchar(50)
  IP varchar(45)
  Activa tinyint(1) [not null]
}

Ref: administrativo.Escuela > escuela.IdEscuela
Ref: administrativo.IdUsuario > usuario.IdUsuario
Ref: auditoriareserva.IdReserva > reserva.IdReserva
Ref: auditoriareserva.UsuarioCambio > usuario.IdUsuario
Ref: cita_policlinico.Bloque > bloqueshorarios.IdBloque
Ref: cita_policlinico.Estudiante > usuario.IdUsuario
Ref: cita_policlinico.Medico > medico.IdMedico
Ref: cita_policlinico.TipoAtencion > tipo_atencion.IdTipoAtencion
Ref: cita_psicologia.Bloque > bloqueshorarios.IdBloque
Ref: cita_psicologia.Estudiante > usuario.IdUsuario
Ref: cita_psicologia.Psicologo > psicologo.IdPsicologo
Ref: cursos.Escuela > escuela.IdEscuela
Ref: cursos.Facultad > facultad.IdFacultad
Ref: docente.Escuela > escuela.IdEscuela
Ref: docente.IdUsuario > usuario.IdUsuario
Ref: escuela.IdFacultad > facultad.IdFacultad
Ref: espacio.Escuela > escuela.IdEscuela
Ref: estudiante.Escuela > escuela.IdEscuela
Ref: estudiante.IdUsuario > usuario.IdUsuario
Ref: horario_curso.Bloque > bloqueshorarios.IdBloque
Ref: horario_curso.Curso > cursos.IdCurso
Ref: horario_curso.Docente > usuario.IdUsuario
Ref: horario_curso.Espacio > espacio.IdEspacio
Ref: horarios.bloque > bloqueshorarios.IdBloque
Ref: horarios.espacio > espacio.IdEspacio
Ref: incidencia.Reserva > reserva.IdReserva
Ref: medico_tipo_atencion.Medico > medico.IdMedico
Ref: medico_tipo_atencion.TipoAtencion > tipo_atencion.IdTipoAtencion
Ref: olimpiada_edicion_disciplina.Disciplina > olimpiada_disciplina.IdDisciplina
Ref: olimpiada_edicion_disciplina.Edicion > olimpiada_edicion.IdEdicion
Ref: olimpiada_inscripcion.EdicionDisciplina > olimpiada_edicion_disciplina.IdEdicionDisciplina
Ref: olimpiada_inscripcion.Facultad > facultad.IdFacultad
Ref: olimpiada_inscripcion.Usuario > usuario.IdUsuario
Ref: olimpiada_participacion_facultad.EdicionDisciplina > olimpiada_edicion_disciplina.IdEdicionDisciplina
Ref: olimpiada_participacion_facultad.Facultad > facultad.IdFacultad
Ref: olimpiada_resultado.EdicionDisciplina > olimpiada_edicion_disciplina.IdEdicionDisciplina
Ref: olimpiada_resultado.FacultadGanadora > facultad.IdFacultad
Ref: olimpiada_resultado.FacultadLocal > facultad.IdFacultad
Ref: olimpiada_resultado.FacultadVisitante > facultad.IdFacultad
Ref: olimpiada_anotador.EdicionDisciplina > olimpiada_edicion_disciplina.IdEdicionDisciplina
Ref: olimpiada_anotador.Facultad > facultad.IdFacultad
Ref: olimpiada_post.Edicion > olimpiada_edicion.IdEdicion
Ref: olimpiada_comentario.Post > olimpiada_post.IdPost
Ref: olimpiada_comentario.Usuario > usuario.IdUsuario
Ref: olimpiada_resultado_posicion.EdicionDisciplina > olimpiada_edicion_disciplina.IdEdicionDisciplina
Ref: olimpiada_resultado_posicion.Facultad > facultad.IdFacultad
Ref: reserva.bloque > bloqueshorarios.IdBloque
Ref: reserva.curso > cursos.IdCurso
Ref: reserva.espacio > espacio.IdEspacio
Ref: reserva.usuario > usuario.IdUsuario
Ref: reserva_gestion.IdReserva > reserva.IdReserva
Ref: reserva_gestion.UsuarioGestion > usuario.IdUsuario
Ref: sancion.Usuario > usuario.IdUsuario
Ref: usuario.Rol > rol.IdRol
Ref: usuario.TipoDoc > tipodocumento.IdTipoDoc
Ref: usuario_auth.IdUsuario > usuario.IdUsuario
Ref: usuario_sesion.IdUsuario > usuario.IdUsuario
```

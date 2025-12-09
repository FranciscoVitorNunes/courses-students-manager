from connection import SQLiteConnection


def create_tables():
    connection, cursor = SQLiteConnection.get_connection()

    aluno_table = """
    CREATE TABLE IF NOT EXISTS aluno (
        matricula TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        cr REAL
    );
    """

    curso_table = """
    CREATE TABLE IF NOT EXISTS curso (
        codigo TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        carga_horaria INTEGER,
        ementa TEXT
    );
    """

    curso_prerequisito_table = """
    CREATE TABLE IF NOT EXISTS curso_prerequisito (
        curso_codigo TEXT NOT NULL,
        prerequisito_codigo TEXT NOT NULL,
        FOREIGN KEY (curso_codigo) REFERENCES curso(codigo),
        FOREIGN KEY (prerequisito_codigo) REFERENCES curso(codigo)
    );
    """

    turma_table = """
    CREATE TABLE IF NOT EXISTS turma (
        id TEXT PRIMARY KEY ,
        periodo TEXT,
        vagas INTEGER,
        curso_codigo TEXT,
        FOREIGN KEY (curso_codigo) REFERENCES curso(codigo)
    );
    """

    horario_turma_table = """
    CREATE TABLE IF NOT EXISTS horario_turma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turma_id TEXT NOT NULL,
        dia TEXT,
        intervalo TEXT,
        FOREIGN KEY (turma_id) REFERENCES turma(id)
    );
    """

    matricula_table = """
        CREATE TABLE IF NOT EXISTS matricula (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_matricula TEXT NOT NULL,
            turma_id TEXT NOT NULL,
            situacao TEXT NOT NULL DEFAULT 'cursando',
            FOREIGN KEY(aluno_matricula) REFERENCES aluno(matricula) ON DELETE CASCADE,
            FOREIGN KEY(turma_id) REFERENCES turma(id) ON DELETE CASCADE
    );
    """
    nota_table = """
        CREATE TABLE IF NOT EXISTS nota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_id INTEGER NOT NULL,
            avaliacao TEXT NOT NULL,
            nota REAL NOT NULL,
            FOREIGN KEY(matricula_id) REFERENCES matricula(id) ON DELETE CASCADE
     );
    """
    frequencia_table = """
        CREATE TABLE IF NOT EXISTS frequencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            presenca INTEGER NOT NULL,
            FOREIGN KEY(matricula_id) REFERENCES matricula(id) ON DELETE CASCADE
    );
    """

    try:
        cursor.execute(aluno_table)
        cursor.execute(curso_table)
        cursor.execute(curso_prerequisito_table)
        cursor.execute(turma_table)
        cursor.execute(horario_turma_table)
        cursor.execute(matricula_table)
        cursor.execute(nota_table)
        cursor.execute(frequencia_table)

        connection.commit()
        print("\nTabelas criadas com sucesso!")
        return True
    
    except Exception as e:
        print(f"\n@@@ Erro ao criar as tabelas: {e} @@@")
        return False
    
    finally:
        SQLiteConnection.close_connection()

create_tables()
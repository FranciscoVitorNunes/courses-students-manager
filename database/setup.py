from database.connection import SQLiteConnection


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
        local TEXT,
        status BOOLEAN,
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
            nota REAL,
            frequencia REAL,
            situacao TEXT NOT NULL DEFAULT 'CURSANDO',
            data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_conclusao TIMESTAMP,
            FOREIGN KEY(aluno_matricula) REFERENCES aluno(matricula) ON DELETE CASCADE,
            FOREIGN KEY(turma_id) REFERENCES turma(id) ON DELETE CASCADE,
            UNIQUE(aluno_matricula, turma_id)
        );
    """
    historico_aluno_table = """
    CREATE TABLE IF NOT EXISTS historico_aluno (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_matricula TEXT NOT NULL,
        codigo_curso TEXT NOT NULL,
        nota REAL NOT NULL,
        frequencia REAL NOT NULL,
        carga_horaria INTEGER NOT NULL,
        situacao TEXT NOT NULL,
        semestre TEXT,
        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(aluno_matricula) REFERENCES aluno(matricula) ON DELETE CASCADE,
        FOREIGN KEY(codigo_curso) REFERENCES curso(codigo) ON DELETE SET NULL
    );
    """

    historico_indices = """
    CREATE INDEX IF NOT EXISTS idx_historico_aluno_matricula 
    ON historico_aluno(aluno_matricula);
    
    CREATE INDEX IF NOT EXISTS idx_historico_codigo_curso 
    ON historico_aluno(codigo_curso);
    
    CREATE INDEX IF NOT EXISTS idx_historico_situacao 
    ON historico_aluno(situacao);
    """

    try:
        cursor.execute(aluno_table)
        cursor.execute(curso_table)
        cursor.execute(curso_prerequisito_table)
        cursor.execute(turma_table)
        cursor.execute(horario_turma_table)
        cursor.execute(matricula_table)
        cursor.execute(historico_aluno_table)
        
        for index_sql in historico_indices.split(';'):
            if index_sql.strip():
                cursor.execute(index_sql)
        
        connection.commit()
        print("\nTabelas criadas com sucesso!")
        return True
    
    except Exception as e:
        print(f"\n@@@ Erro ao criar as tabelas: {e} @@@")
        return False
    
    finally:
        SQLiteConnection.close_connection()

create_tables()
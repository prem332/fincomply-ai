import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DATABASE_URL,
    VECTOR_TABLE_NAME,
    VECTOR_DIMENSION,
)

import psycopg2


def init_database() -> None:
    """
    Creates the pgvector extension and the regulatory_embeddings table.
    Safe to run multiple times — uses CREATE IF NOT EXISTS.
    """
    print("Connecting to database...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        print("  ✓ Connected successfully")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        print("\n  Check your DB_HOST, DB_USER, DB_PASSWORD in .env")
        sys.exit(1)

    # ── Enable pgvector extension ─────────────────────────────────────────────
    print("Enabling pgvector extension...")
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("  ✓ pgvector extension enabled")
    except Exception as e:
        print(f"  ✗ Failed to enable pgvector: {e}")
        print("  Make sure your RDS instance has pgvector support.")
        conn.close()
        sys.exit(1)

    # ── Create regulatory embeddings table ───────────────────────────────────
    print(f"Creating table '{VECTOR_TABLE_NAME}'...")
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {VECTOR_TABLE_NAME} (
        id              SERIAL PRIMARY KEY,
        content         TEXT NOT NULL,
        domain          VARCHAR(50) NOT NULL,
        circular_number VARCHAR(200),
        source_url      TEXT,
        published_date  DATE,
        is_gov_verified BOOLEAN DEFAULT TRUE,
        metadata        JSONB DEFAULT '{{}}',
        embedding       VECTOR({VECTOR_DIMENSION}),
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """
    cursor.execute(create_table_sql)
    print(f"  ✓ Table '{VECTOR_TABLE_NAME}' created (or already exists)")

    # ── Create index for fast similarity search ───────────────────────────────
    print("Creating vector similarity index...")
    index_sql = f"""
    CREATE INDEX IF NOT EXISTS {VECTOR_TABLE_NAME}_embedding_idx
    ON {VECTOR_TABLE_NAME}
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    """
    try:
        cursor.execute(index_sql)
        print("  ✓ IVFFlat index created for fast cosine similarity search")
    except Exception as e:
        print(f"  ⚠ Index creation warning (safe to ignore): {e}")

    # ── Create domain index for filtered queries ──────────────────────────────
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS {VECTOR_TABLE_NAME}_domain_idx
        ON {VECTOR_TABLE_NAME} (domain);
    """)
    print("  ✓ Domain index created")

    cursor.close()
    conn.close()

    print("")
    print("Database initialization complete!")
    print(f"  Table: {VECTOR_TABLE_NAME}")
    print(f"  Vector dimension: {VECTOR_DIMENSION}")
    print(f"  RAG TOP_K will retrieve: {__import__('config').RAG_TOP_K} documents per query")
    print("")


def test_connection() -> bool:
    """Quick test to verify database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"Database connection OK: {version[:50]}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    init_database()
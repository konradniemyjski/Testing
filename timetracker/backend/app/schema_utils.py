from sqlalchemy import inspect, text, Integer, Float, String, Boolean, Text
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def ensure_worklog_absences_column(engine):
    """Ensure the worklog_absences table has the hours_worked column."""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    # Check if table exists
    if 'worklog_absences' not in inspector.get_table_names():
        logger.info("Table worklog_absences doesn't exist yet, skipping column check")
        return
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('worklog_absences')]
    
    if "hours_worked" not in columns:
        logger.info("Adding hours_worked column to worklog_absences table")
        dialect = engine.dialect.name
        
        if dialect == 'postgresql':
            alter_sql = text("ALTER TABLE worklog_absences ADD COLUMN hours_worked FLOAT DEFAULT 0.0")
        elif dialect == 'mysql':
            alter_sql = text("ALTER TABLE worklog_absences ADD COLUMN hours_worked FLOAT DEFAULT 0.0")
        else:  # sqlite
            alter_sql = text("ALTER TABLE worklog_absences ADD COLUMN hours_worked REAL DEFAULT 0.0")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added hours_worked column")
        except SQLAlchemyError as e:
            logger.error(f"Error adding hours_worked column: {e}")


def ensure_worklogs_columns(engine):
    """Ensure the worklogs table has all required columns."""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    # Check if table exists
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    # Define required columns with their types
    required_columns = {
        'meals_served': ('INTEGER', 0),
        'overnight_stays': ('INTEGER', 0),
        'absences': ('INTEGER', 0)
    }
    
    dialect = engine.dialect.name
    
    for column_name, (column_type, default_value) in required_columns.items():
        if column_name not in existing_columns:
            logger.info(f"Adding {column_name} column to worklogs table")
            
            # Adjust column type based on dialect
            if dialect == 'postgresql':
                sql_type = column_type
            elif dialect == 'mysql':
                sql_type = column_type
            else:  # sqlite
                sql_type = column_type
            
            alter_sql = text(f"ALTER TABLE worklogs ADD COLUMN {column_name} {sql_type} DEFAULT {default_value}")
            
            try:
                with engine.connect() as conn:
                    conn.execute(alter_sql)
                    conn.commit()
                logger.info(f"Successfully added {column_name} column")
            except SQLAlchemyError as e:
                logger.error(f"Error adding {column_name} column: {e}")


def ensure_all_columns(engine):
    """Main function to ensure all tables have required columns."""
    logger.info("Checking and adding missing columns...")
    ensure_worklog_absences_column(engine)
    ensure_worklogs_columns(engine)
    logger.info("Column check complete")

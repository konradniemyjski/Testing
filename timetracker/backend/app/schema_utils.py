from sqlalchemy import inspect, text, Integer, Float, String, Boolean, Text
from sqlalchemy.exc import SQLAlchemyError
import logging


logger = logging.getLogger(__name__)


def ensure_worklog_absences_column(engine):
    """Ensure the worklog_absences table has the hours_worked column."""
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


def ensure_project_code_column(engine):
    """Ensure the projects table has the code column."""
    inspector = inspect(engine)
    
    if 'projects' not in inspector.get_table_names():
        logger.info("Table projects doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('projects')]
    
    if "code" not in columns:
        logger.info("Adding code column to projects table")
        dialect = engine.dialect.name
        
        if dialect == 'postgresql':
            alter_sql = text("ALTER TABLE projects ADD COLUMN code VARCHAR(50)")
        elif dialect == 'mysql':
            alter_sql = text("ALTER TABLE projects ADD COLUMN code VARCHAR(50)")
        else:  # sqlite
            alter_sql = text("ALTER TABLE projects ADD COLUMN code TEXT")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added code column to projects")
        except SQLAlchemyError as e:
            logger.error(f"Error adding code column: {e}")


def ensure_worklog_site_code_column(engine):
    """Ensure the worklogs table has the site_code column."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    if "site_code" not in columns:
        logger.info("Adding site_code column to worklogs table")
        dialect = engine.dialect.name
        
        if dialect == 'postgresql':
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN site_code VARCHAR(50)")
        elif dialect == 'mysql':
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN site_code VARCHAR(50)")
        else:  # sqlite
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN site_code TEXT")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added site_code column to worklogs")
        except SQLAlchemyError as e:
            logger.error(f"Error adding site_code column: {e}")


def ensure_worklog_employee_count_column(engine):
    """Ensure the worklogs table has the employee_count column."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    if "employee_count" not in columns:
        logger.info("Adding employee_count column to worklogs table")
        alter_sql = text("ALTER TABLE worklogs ADD COLUMN employee_count INTEGER DEFAULT 0")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added employee_count column to worklogs")
        except SQLAlchemyError as e:
            logger.error(f"Error adding employee_count column: {e}")


def ensure_worklog_hours_worked_column(engine):
    """Ensure the worklogs table has the hours_worked column."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    if "hours_worked" not in columns:
        logger.info("Adding hours_worked column to worklogs table")
        dialect = engine.dialect.name
        
        if dialect == 'postgresql':
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN hours_worked FLOAT DEFAULT 0.0")
        elif dialect == 'mysql':
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN hours_worked FLOAT DEFAULT 0.0")
        else:  # sqlite
            alter_sql = text("ALTER TABLE worklogs ADD COLUMN hours_worked REAL DEFAULT 0.0")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added hours_worked column to worklogs")
        except SQLAlchemyError as e:
            logger.error(f"Error adding hours_worked column: {e}")


def ensure_worklog_meals_served_column(engine):
    """Ensure the worklogs table has the meals_served column."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    if "meals_served" not in columns:
        logger.info("Adding meals_served column to worklogs table")
        alter_sql = text("ALTER TABLE worklogs ADD COLUMN meals_served INTEGER DEFAULT 0")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added meals_served column to worklogs")
        except SQLAlchemyError as e:
            logger.error(f"Error adding meals_served column: {e}")


def ensure_worklog_overnight_stays_column(engine):
    """Ensure the worklogs table has the overnight_stays column."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping column check")
        return
    
    columns = [col['name'] for col in inspector.get_columns('worklogs')]
    
    if "overnight_stays" not in columns:
        logger.info("Adding overnight_stays column to worklogs table")
        alter_sql = text("ALTER TABLE worklogs ADD COLUMN overnight_stays INTEGER DEFAULT 0")
        
        try:
            with engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            logger.info("Successfully added overnight_stays column to worklogs")
        except SQLAlchemyError as e:
            logger.error(f"Error adding overnight_stays column: {e}")

def ensure_hours_column_migration(engine):
    """Migrate 'hours' column to 'hours_worked' or make it nullable."""
    inspector = inspect(engine)
    
    if 'worklogs' not in inspector.get_table_names():
        logger.info("Table worklogs doesn't exist yet, skipping hours column migration")
        return
    
    columns = {col['name']: col for col in inspector.get_columns('worklogs')}
    
    # Check if old 'hours' column exists
    if 'hours' in columns and 'hours_worked' in columns:
        # Both columns exist - migrate data from hours to hours_worked and drop hours
        logger.info("Migrating data from 'hours' to 'hours_worked' and dropping 'hours' column")
        try:
            with engine.connect() as conn:
                # Update hours_worked with values from hours where hours_worked is null
                conn.execute(text("UPDATE worklogs SET hours_worked = hours WHERE hours_worked IS NULL OR hours_worked = 0"))
                # Drop the old hours column
                conn.execute(text("ALTER TABLE worklogs DROP COLUMN hours"))
                conn.commit()
            logger.info("Successfully migrated 'hours' column to 'hours_worked'")
        except SQLAlchemyError as e:
            logger.error(f"Error migrating hours column: {e}")
    
    elif 'hours' in columns and 'hours_worked' not in columns:
        # Only old column exists - rename it
        logger.info("Renaming 'hours' column to 'hours_worked'")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE worklogs RENAME COLUMN hours TO hours_worked"))
                conn.commit()
            logger.info("Successfully renamed 'hours' to 'hours_worked'")
        except SQLAlchemyError as e:
            logger.error(f"Error renaming hours column: {e}")
    
    elif 'hours' in columns:
        # Make hours column nullable if it exists
        logger.info("Making 'hours' column nullable")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE worklogs ALTER COLUMN hours DROP NOT NULL"))
                conn.commit()
            logger.info("Successfully made 'hours' column nullable")
        except SQLAlchemyError as e:
            logger.error(f"Error making hours column nullable: {e}")

def ensure_all_columns(engine):
    """Main function to ensure all tables have required columns."""
    logger.info("Checking and adding missing columns...")
    
    # IMPORTANT: Run this FIRST before other column checks
    ensure_hours_column_migration(engine)
    
    ensure_worklog_absences_column(engine)
    ensure_worklogs_columns(engine)
    logger.info("Column check complete")


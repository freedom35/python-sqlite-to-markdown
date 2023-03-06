#################################################
# App to export SQLite query results to markdown.
#
# Alan Barr (GitHub: freedom35)
# March 2023
#################################################
import sqlite3
import sys
import os


#######################################
# Main method
#######################################
def main():
    try:
        # Check for expected arguments
        if len(sys.argv) < 3:
            display_help()
            return

        # Get paths - first arg is file name
        db_file = sys.argv[1]
        sql_file = sys.argv[2]

        # Check database exists otherwise SQLite lib will create an empty one
        if not os.path.isfile(db_file):
            print('Database not found: {}'.format(db_file))
            return

        if not os.path.isfile(sql_file):
            print('SQL file not found: {}'.format(sql_file))
            return

        # Separate directory/filename
        tmp = os.path.split(sql_file)
        sql_file_dir = tmp[0]
        sql_file_with_ext = tmp[1]

        # Separate filename/ext
        tmp = os.path.splitext(sql_file_with_ext)
        sql_file_without_ext = tmp[0]
        sql_file_ext = tmp[1]

        # Export to same directory as SQL file if optional dir not specified
        export_dir = sys.argv[3] if len(sys.argv) > 3 else sql_file_dir

        # File ext for output file
        MARKDOWN_EXT = '.md'
        
        # Check input file is not markdown or will be overwritten
        if sql_file_dir == export_dir and sql_file_ext == MARKDOWN_EXT:
            print('SQL file ({}) cannot have same ext as markdown file ({}) '
                  '- SQL file would be overwritten!'
                  .format(sql_file_with_ext, MARKDOWN_EXT))
            return
        
        # Get contents of SQL file
        sql = read_query(sql_file)

        # Query DB
        conn = sqlite3.connect(db_file)

        results = get_results(conn, sql)

        # Check for SQL comments in file
        comments = get_header_comments(sql)

        # Format results as markdown
        markdown = create_markdown(sql_file_without_ext, comments, results)

        # Check to create dir for output file
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        # Get output path
        export_file = sql_file_without_ext + MARKDOWN_EXT
        export_path = os.path.join(export_dir, export_file)

        export_to_file(export_path, markdown)

        # Tidy up
        conn.close()

        print('Export complete: {}'.format(export_file))

    except Exception as e:
        print('Error: {}'.format(str(e)))


#######################################
# Help
#######################################
def display_help():
    python_file = os.path.basename(__file__)
    print('Expecting <database path> <sql path> [optional: <export dir>]')
    print('Example:')
    print('  python3 {} sample.db query.sql'.format(python_file))
    print('or')
    print('  python3 {} sample.db query.sql export-dir'.format(python_file))


#######################################
# Read SQL file contents
#######################################
def read_query(path):
    sql = ''

    # Open file as read-only
    with open(path, 'r') as f:
        sql = f.read()

    return sql


#######################################
# Get any header comments from sql
#######################################
def get_header_comments(sql):
    comments = []

    # Check start of file for comments
    for line in sql.splitlines():
        if line.startswith('--'):
            # Remove comment marker and any spaces
            comments.append(line.lstrip('- ').rstrip(' \r\n'))
        else:
            break

    return comments


#######################################
# Get results from database
#######################################
def get_results(conn, sql):
    # Get database cursor
    cur = conn.cursor()

    # Execute SQL statement
    cur.execute(sql)
  
    # Get list of column names for query
    names = list(map(lambda x: x[0], cur.description))

    # Get results into a table (list of lists)
    selected_results = cur.fetchall()

    # Return tuple
    return (names, selected_results)


#######################################
# Create markdown content
#######################################
def create_markdown(title, body, table):
    lines = []
    
    # Title
    lines.append('# {}'.format(title))
    lines.append('')

    # Optional body
    if len(body) > 0:
        for s in body:
            lines.append(s)

        # Add extra line if added body
        lines.append('')

    # Table
    if len(table) < 2:
        return lines

    fields = table[0]
    rows = table[1]

    # Check for row data
    if len(rows) == 0:
        return lines

    # Build table markdown:
    # Start with table headings
    headings = '|'

    for field in fields:
        # Add field name, replace underscores
        headings += field.replace('_', ' ') + '|'

    lines.append(headings)

    # Create table alignment
    alignment = '|'

    # Loop fields by index
    for i in range(len(fields)):
        field_alignment = None

        # Iterate each row until a non-null value is found
        for row in rows:
            # Get value for current field
            val = row[i]

            if val is None:
                continue
            
            # Align fields based on data type
            # Center align if numeric, left align if not
            if isinstance(val, int) or isinstance(val, float):
                field_alignment = ':-:|'
            else:
                field_alignment = '---|'

            break
        
        # Default alignment left if data type unknown
        alignment += (field_alignment if field_alignment is not None 
                      else '---|')

    # Add table alignment row
    lines.append(alignment)

    # Row data
    for row in rows:
        lines.append('|{}|'.format('|'.join(
            [str(i) if i is not None else '' for i in row])))

    return lines


#######################################
# Export to file
#######################################
def export_to_file(path, markdown):
    # Create file for writing
    with open(path, 'w') as f:
        # Insert newline char between each item
        # (Otherwise list will be concatenated into one line)
        separate_lines = map(lambda x: f"{x}\n", markdown)

        # Write all lines to file
        f.writelines(separate_lines)


#######################################
# Local entrypoint
#######################################
if __name__ == "__main__":
    main()

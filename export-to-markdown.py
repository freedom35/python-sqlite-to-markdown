#################################################
# App to export SQLite query results to markdown.
#
# Alan Barr (GitHub: freedom35)
# Jan 2023
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
        dbFile = sys.argv[1]
        sqlFile = sys.argv[2]

        # Check database exists otherwise SQLite lib will create an empty one
        if not os.path.isfile(dbFile):
            print('Database not found: {}'.format(dbFile))
            return

        if not os.path.isfile(sqlFile):
            print('SQL file not found: {}'.format(sqlFile))
            return

        # Separate directory/filename
        tmp = os.path.split(sqlFile)
        sqlFileDir = tmp[0]
        sqlFileWithExt = tmp[1]

        # Separate filename/ext
        tmp = os.path.splitext(sqlFileWithExt)
        sqlFileWithoutExt = tmp[0]
        sqlFileExt = tmp[1]

        # Export to same directory as SQL file if optional dir not specified
        exportDir = sys.argv[3] if len(sys.argv) > 3 else sqlFileDir

        # File ext for output file
        MARKDOWN_EXT = '.md'
        
        # Check input file is not markdown or will be overwritten
        if sqlFileDir == exportDir and sqlFileExt == MARKDOWN_EXT:
            print('SQL file ({}) cannot have same ext as markdown file ({}) - SQL file would be overwritten!'.format(sqlFileWithExt, MARKDOWN_EXT))
            return
        
        # Get contents of SQL file
        sql = read_query(sqlFile)

        # Query DB
        conn = sqlite3.connect(dbFile)

        results = get_results(conn, sql)

        # Check for SQL comments in file
        comments = get_header_comments(sql)

        # Format results as markdown
        markdown = create_markdown(sqlFileWithoutExt, comments, results)

        # Check to create dir for output file
        if not os.path.exists(exportDir):
            os.makedirs(exportDir)

        # Get output path
        exportFile = sqlFileWithoutExt + MARKDOWN_EXT
        exportPath = os.path.join(exportDir, exportFile)

        export_to_file(exportPath, markdown)

        # Tidy up
        conn.close()

        print('Export complete: {}'.format(exportFile))

    except Exception as e:
        print('Error: {}'.format(str(e)))


#######################################
# Help
#######################################
def display_help():
    pythonFile = os.path.basename(__file__)
    print('Expecting <database path> <sql path> [optional: <export dir>]')
    print('Example:')
    print(' python3 {} sample.db query.sql'.format(pythonFile))
    print('or')
    print(' python3 {} sample.db query.sql export-dir'.format(pythonFile))


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
    selectedResults = cur.fetchall()

    # Return tuple
    return (names, selectedResults)


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

    # Build table markdown
    headings = '|'
    alignment = '|'

    # Table headings
    for field in fields:
        # Add field name, replace underscores
        headings += field.replace('_', ' ') + '|'

    lines.append(headings)

    # Align table based on data type
    # (center align if numeric)
    for val in rows[0]:
        if isinstance(val, int) or isinstance(val, float):
            alignment += ':-:|'
        else:
            alignment += '---|'

    lines.append(alignment)

    # Row data
    for row in rows:
        lines.append('|{}|'.format('|'.join([str(i) if i is not None else '' for i in row])))

    return lines


#######################################
# Export to file
#######################################
def export_to_file(exportPath, markdown):
    # Create file for writing
    with open(exportPath, 'w') as f:
        # Insert newline char between each item
        # (Otherwise list will be concatenated into one line)
        separateLines = map(lambda x: f"{x}\n", markdown)

        # Write all lines to file
        f.writelines(separateLines)


#######################################
# Local entrypoint
#######################################
if __name__ == "__main__":
    main()

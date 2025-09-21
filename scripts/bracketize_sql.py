#!/usr/bin/env python3
import sys
import sqlglot
from sqlglot import exp
import re

def bracket_identifier(name: str) -> str:
    """Normalize any identifier into [name]."""
    #print(f"IN: {name}")
    if not isinstance(name, str):
        name = str(name)
    # remove balanced brackets repeatedly
    while name.startswith("[") and name.endswith("]"):
        name = name[1:-1].strip()

    # clean stray extras
    name = name.strip("[]")

    #print(f"OUT: [{name}]")
    return f"[{name}]"

def transform(node: exp.Expression, parent=None) -> exp.Expression:
    """
    Recursively transform the AST:
    - Bracket identifiers (schema, table, column, CTE names, etc.)
    - Skip explicit aliases (Alias, TableAlias) so aliases like `u`/`r` remain unbracketed.
    - For Table nodes, bracket db/catalog/this.
    - For Column nodes, bracket the column name but leave the table qualifier (to avoid alias-bracketing).
    """
    print(f"Node: {node}")
    print(f"Nodethis: {str(node.this)}")

    # Handle Identifier nodes
    if isinstance(node, exp.Identifier):
        # Don't touch aliases
        if isinstance(parent, (exp.Alias, exp.TableAlias)):
            return node

        return exp.Identifier(this=bracket_identifier(node.this))

    # Handle Table nodes
    if isinstance(node, exp.Table):
        db = node.args.get("db")
        print(f"NodeDB: {db}")
        if isinstance(db, exp.Identifier):
            node.set("db", exp.Identifier(this=bracket_identifier(db.this)))
        elif isinstance(db, str):
            node.set("db", exp.Identifier(this=bracket_identifier(db)))
        catalog = node.args.get("catalog")
        print(f"Nodecatalog: {catalog}")
        if isinstance(catalog, exp.Identifier):
            node.set("catalog", exp.Identifier(this=bracket_identifier(catalog.this)))
        elif isinstance(catalog, str):
            node.set("catalog", exp.Identifier(this=bracket_identifier(catalog)))
        t = node.this
        print(f"Node-t: {t}")
        if isinstance(t, exp.Identifier):
            node.set("this", exp.Identifier(this=bracket_identifier(t.this)))
        elif isinstance(t, str):
            node.set("this", exp.Identifier(this=bracket_identifier(t)))

    # Handle Column nodes (bracket column only, not alias qualifier)
    if isinstance(node, exp.Column):
        col = node.this
        print(f"Nodecol: {col}")
        if isinstance(col, exp.Identifier):
            node.set("this", exp.Identifier(this=bracket_identifier(col.this)))
        elif isinstance(col, str):
            node.set("this", exp.Identifier(this=bracket_identifier(col)))
        # note: skip node.table (that may be an alias like "u" or "c")

    # Recurse
    for k, v in node.args.items():
        if isinstance(v, list):
            node.set(k, [transform(x, node) for x in v])
        elif isinstance(v, exp.Expression):
            node.set(k, transform(v, node))

    return node

def bracketize(sql: str) -> str:
    """Parse T-SQL and return bracketed version."""
    try:
        parsed = sqlglot.parse_one(sql, read="tsql")
    except Exception as e:
        print(f"Failed to parse SQL: {e}")
        return sql
    transformed = transform(parsed)
    return transformed.sql(dialect="tsql", pretty=True)

def process_file(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        sql_text = f.read()

    # Split by GO separator (case-insensitive, line-only)
    batches = re.split(r'(?im)^\s*GO\s*$', sql_text, flags=re.MULTILINE)
    processed_batches = [bracketize(batch) for batch in batches]
    sql_out = 'GO\n'.join(processed_batches)

#    with open(filename, "w", encoding="utf-8") as f:
#        f.write(sql_out)

if __name__ == "__main__":
    import sys
    for file in sys.argv[1:]:
        if file.endswith(".sql"):
            process_file(file)

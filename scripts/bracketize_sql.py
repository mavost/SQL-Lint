#!/usr/bin/env python3
import sys
import sqlglot
from sqlglot import exp
import re

def bracket_identifier(name: str) -> str:
    """Wrap an identifier in brackets if not already bracketed."""
    if name.startswith("[") and name.endswith("]"):
        return name
    return f"[{name}]"

def transform(node: exp.Expression) -> exp.Expression:
    """
    Recursively walk the AST and bracket schema, table, and column names.
    Skip table/column aliases.
    """
    # Bracket table/schema
    if isinstance(node, exp.Table):
        # Bracket schema if present
        if node.args.get("db"):
            node.set("db", exp.Identifier(this=bracket_identifier(node.args["db"].this)))
        if node.args.get("catalog"):
            node.set("catalog", exp.Identifier(this=bracket_identifier(node.args["catalog"].this)))
        # Bracket table name
        if node.this:
            node.set("this", exp.Identifier(this=bracket_identifier(node.this.this)))
    
    # Bracket column names, but skip aliases
    if isinstance(node, exp.Column):
        if node.this:
            node.set("this", exp.Identifier(this=bracket_identifier(node.this.this)))
        # Bracket table reference if present
        if node.table:
            node.set("table", exp.Identifier(this=bracket_identifier(node.table.this)))

    # Recurse into children
    for k, v in node.args.items():
        if isinstance(v, list):
            node.set(k, [transform(x) for x in v])
        elif isinstance(v, exp.Expression):
            node.set(k, transform(v))
    return node

def bracketize(sql: str) -> str:
    """Parse T-SQL and return bracketed version."""
    try:
        parsed = sqlglot.parse_one(sql, read="tsql")
    except Exception as e:
        print(f"Failed to parse SQL: {e}")
        return sql
    transformed = transform(parsed)
    return transformed.sql(dialect="tsql")

def process_file(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        sql_text = f.read()

    # Split by GO separator (case-insensitive, line-only)
    batches = re.split(r'(?im)^\s*GO\s*$', sql_text, flags=re.MULTILINE)
    processed_batches = [bracketize(batch) for batch in batches]
    sql_out = 'GO\n'.join(processed_batches)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(sql_out)

if __name__ == "__main__":
    import sys
    for file in sys.argv[1:]:
        if file.endswith(".sql"):
            process_file(file)
